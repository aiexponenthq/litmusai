"""Constrained expression language for LitmusAI rulesets.

Hand-rolled tokeniser -> recursive-descent parser -> AST -> safe interpreter.

Supports:
  - Field access: system.inputs.biometric
  - Comparisons: ==, !=
  - Boolean: and, or, not
  - Set membership: "x" in system.mitigations, "x" not in system.mitigations
  - Whitelisted functions: contains(), starts_with(), has_jurisdiction(),
    targets_population()
  - String literals: "..."
  - Boolean literals: true, false
  - Parenthesised sub-expressions

Does NOT support: any Python builtin, subscript access, assignment,
lambda, comprehension, f-string, arithmetic, import, or attribute
access outside the 'system.*' namespace.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union


class ExpressionError(Exception):
    """Raised for syntactically invalid or forbidden expressions."""


# ── Tokeniser ──

_WHITELISTED_FUNCTIONS = frozenset(
    {
        "contains",
        "starts_with",
        "has_jurisdiction",
        "targets_population",
    }
)
_FORBIDDEN_IDENTS = frozenset(
    {
        "__import__",
        "__builtins__",
        "__class__",
        "__mro__",
        "__subclasses__",
        "globals",
        "locals",
        "getattr",
        "setattr",
        "delattr",
        "open",
        "compile",
        "type",
        "isinstance",
        "issubclass",
        "breakpoint",
        "dir",
        "vars",
        "id",
        "hash",
        "lambda",
        "yield",
        "await",
        "async",
        "def",
        "class",
        "import",
        "return",
        "raise",
        "del",
        "pass",
        "break",
        "continue",
        "for",
        "while",
        "if",
        "else",
        "elif",
        "try",
        "except",
        "finally",
        "with",
        "as",
        "from",
        "nonlocal",
        "global",
        "assert",
        "exit",
        "quit",
        "help",
        "print",
        "input",
        "eval",
        "exec",
    }
)
_FORBIDDEN_CHARS = frozenset(";[]{}`@#$~\\")


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    value: str
    pos: int


def _tokenize(expr: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(expr)

    if not expr.strip():
        raise ExpressionError("Empty expression")

    for ch in expr:
        if ch in _FORBIDDEN_CHARS:
            raise ExpressionError(f"Forbidden character {ch!r} at position {expr.index(ch)}")

    while i < n:
        if expr[i].isspace():
            i += 1
            continue

        if expr[i] == "(":
            tokens.append(Token("LPAREN", "(", i))
            i += 1
        elif expr[i] == ")":
            tokens.append(Token("RPAREN", ")", i))
            i += 1
        elif expr[i] == ",":
            tokens.append(Token("COMMA", ",", i))
            i += 1
        elif expr[i] == "!" and i + 1 < n and expr[i + 1] == "=":
            tokens.append(Token("NEQ", "!=", i))
            i += 2
        elif expr[i] == "=" and i + 1 < n and expr[i + 1] == "=":
            tokens.append(Token("EQ", "==", i))
            i += 2
        elif expr[i] == '"':
            j = i + 1
            while j < n and expr[j] != '"':
                j += 1
            if j >= n:
                raise ExpressionError(f"Unclosed string literal starting at position {i}")
            tokens.append(Token("STRING", expr[i + 1 : j], i))
            i = j + 1
        elif expr[i].isalpha() or expr[i] == "_":
            j = i
            while j < n and (expr[j].isalnum() or expr[j] in "_."):
                j += 1
            word = expr[i:j]

            if any(part.startswith("__") for part in word.split(".")):
                raise ExpressionError(f"Dunder access forbidden: {word!r}")

            bare_name = word.split(".")[0]
            if bare_name in _FORBIDDEN_IDENTS:
                raise ExpressionError(f"Forbidden identifier: {bare_name!r}")

            if word == "true":
                tokens.append(Token("BOOL", "true", i))
            elif word == "false":
                tokens.append(Token("BOOL", "false", i))
            elif word == "and":
                tokens.append(Token("AND", "and", i))
            elif word == "or":
                tokens.append(Token("OR", "or", i))
            elif word == "not":
                tokens.append(Token("NOT", "not", i))
            elif word == "in":
                tokens.append(Token("IN", "in", i))
            elif word in _WHITELISTED_FUNCTIONS:
                tokens.append(Token("FUNC", word, i))
            elif word.startswith("system.") or word == "system":
                tokens.append(Token("FIELD", word, i))
            else:
                raise ExpressionError(
                    f"Unknown identifier {word!r} at position {i}. "
                    f"Only 'system.*' fields, boolean literals, and whitelisted "
                    f"functions are allowed."
                )
            i = j
        elif expr[i].isascii() and expr[i].isdigit():
            j = i
            while j < n and expr[j].isascii() and (expr[j].isdigit() or expr[j] == "."):
                j += 1
            tokens.append(Token("NUMBER", expr[i:j], i))
            i = j
        elif expr[i] in "*/-+":
            raise ExpressionError(f"Forbidden operator {expr[i]!r} at position {i}")
        elif expr[i] in "<>":
            raise ExpressionError(f"Comparison {expr[i]!r} not yet supported")
        elif expr[i] == "!":
            raise ExpressionError(f"Unexpected '!' at position {i}")
        elif expr[i] == ":":
            raise ExpressionError(f"Forbidden character ':' at position {i}")
        elif expr[i] == "'":
            raise ExpressionError(f"Single quotes not supported. Use double quotes at position {i}")
        else:
            raise ExpressionError(f"Unexpected character {expr[i]!r} at position {i}")

    return tokens


# ── AST ──

ASTNode = Union[
    "BoolLiteral",
    "StringLiteral",
    "NumberLiteral",
    "FieldAccess",
    "BinaryOp",
    "UnaryOp",
    "FuncCall",
    "InOp",
]


@dataclass(frozen=True, slots=True)
class BoolLiteral:
    value: bool


@dataclass(frozen=True, slots=True)
class StringLiteral:
    value: str


@dataclass(frozen=True, slots=True)
class NumberLiteral:
    value: float


@dataclass(frozen=True, slots=True)
class FieldAccess:
    path: str


@dataclass(frozen=True, slots=True)
class BinaryOp:
    op: str
    left: ASTNode
    right: ASTNode


@dataclass(frozen=True, slots=True)
class UnaryOp:
    op: str
    operand: ASTNode


@dataclass(frozen=True, slots=True)
class FuncCall:
    name: str
    args: list[ASTNode]


@dataclass(frozen=True, slots=True)
class InOp:
    element: ASTNode
    collection: ASTNode
    negated: bool


# ── Recursive-descent parser ──


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect(self, kind: str) -> Token:
        tok = self._peek()
        if tok is None or tok.kind != kind:
            got = tok.kind if tok else "EOF"
            raise ExpressionError(f"Expected {kind}, got {got}")
        return self._advance()

    def parse(self) -> ASTNode:
        node = self._parse_or()
        if self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            raise ExpressionError(f"Unexpected token {tok.value!r} at position {tok.pos}")
        return node

    def _parse_or(self) -> ASTNode:
        left = self._parse_and()
        while (t := self._peek()) and t.kind == "OR":
            self._advance()
            left = BinaryOp("or", left, self._parse_and())
        return left

    def _parse_and(self) -> ASTNode:
        left = self._parse_not()
        while (t := self._peek()) and t.kind == "AND":
            self._advance()
            left = BinaryOp("and", left, self._parse_not())
        return left

    def _parse_not(self) -> ASTNode:
        if (t := self._peek()) and t.kind == "NOT":
            self._advance()
            return UnaryOp("not", self._parse_not())
        return self._parse_comparison()

    def _parse_comparison(self) -> ASTNode:
        left = self._parse_in()
        if (t := self._peek()) and t.kind in ("EQ", "NEQ"):
            op_tok = self._advance()
            return BinaryOp(op_tok.value, left, self._parse_in())
        return left

    def _parse_in(self) -> ASTNode:
        left = self._parse_primary()
        t = self._peek()
        if t and t.kind == "IN":
            self._advance()
            return InOp(left, self._parse_primary(), negated=False)
        if t and t.kind == "NOT":
            nt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if nt and nt.kind == "IN":
                self._advance()
                self._advance()
                return InOp(left, self._parse_primary(), negated=True)
        return left

    def _parse_primary(self) -> ASTNode:
        tok = self._peek()
        if tok is None:
            raise ExpressionError("Unexpected end of expression")

        if tok.kind == "LPAREN":
            self._advance()
            node = self._parse_or()
            self._expect("RPAREN")
            return node
        if tok.kind == "BOOL":
            self._advance()
            return BoolLiteral(tok.value == "true")
        if tok.kind == "STRING":
            self._advance()
            return StringLiteral(tok.value)
        if tok.kind == "NUMBER":
            self._advance()
            try:
                return NumberLiteral(float(tok.value))
            except ValueError as exc:
                raise ExpressionError(f"Invalid number literal: {tok.value!r}") from exc
        if tok.kind == "FIELD":
            self._advance()
            return FieldAccess(tok.value)
        if tok.kind == "FUNC":
            return self._parse_func_call()

        raise ExpressionError(f"Unexpected token {tok.value!r} at position {tok.pos}")

    def _parse_func_call(self) -> FuncCall:
        name_tok = self._advance()
        self._expect("LPAREN")
        args: list[ASTNode] = []
        if (t := self._peek()) and t.kind != "RPAREN":
            args.append(self._parse_or())
            while (t2 := self._peek()) and t2.kind == "COMMA":
                self._advance()
                args.append(self._parse_or())
        self._expect("RPAREN")
        return FuncCall(name_tok.value, args)


def parse(expr: str) -> ASTNode:
    """Parse a constrained expression into an AST."""
    tokens = _tokenize(expr)
    return _Parser(tokens).parse()


# ── Safe interpreter ──


def _resolve_field(path: str, ctx: dict[str, Any]) -> Any:
    current: Any = ctx
    for part in path.split("."):
        if not isinstance(current, dict):
            raise ExpressionError(f"Cannot access field {part!r} on non-dict value")
        if part not in current:
            raise ExpressionError(f"Unknown field {path!r} - {part!r} not found")
        current = current[part]
    return current


def _interpret(node: ASTNode, ctx: dict[str, Any]) -> Any:
    if isinstance(node, BoolLiteral):
        return node.value
    if isinstance(node, StringLiteral):
        return node.value
    if isinstance(node, NumberLiteral):
        return node.value
    if isinstance(node, FieldAccess):
        return _resolve_field(node.path, ctx)

    if isinstance(node, UnaryOp):
        if node.op == "not":
            return not _interpret(node.operand, ctx)
        raise ExpressionError(f"Unknown unary op: {node.op}")  # pragma: no cover

    if isinstance(node, BinaryOp):
        left = _interpret(node.left, ctx)
        if node.op == "and":
            return bool(left and _interpret(node.right, ctx))
        if node.op == "or":
            return bool(left or _interpret(node.right, ctx))
        right = _interpret(node.right, ctx)
        if node.op == "==":
            return left == right
        if node.op == "!=":
            return left != right
        raise ExpressionError(f"Unknown binary op: {node.op}")  # pragma: no cover

    if isinstance(node, InOp):
        element = _interpret(node.element, ctx)
        collection = _interpret(node.collection, ctx)
        if not isinstance(collection, list):
            raise ExpressionError(f"'in' requires a list, got {type(collection).__name__}")
        result = element in collection
        return not result if node.negated else result

    if isinstance(node, FuncCall):
        return _call_function(node, ctx)

    raise ExpressionError(f"Unknown AST node: {type(node).__name__}")  # pragma: no cover


def _call_function(node: FuncCall, ctx: dict[str, Any]) -> Any:
    args = [_interpret(a, ctx) for a in node.args]

    if node.name == "contains":
        if len(args) != 2 or not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ExpressionError("contains() requires two string arguments")
        return args[1] in args[0]

    if node.name == "starts_with":
        if len(args) != 2 or not isinstance(args[0], str) or not isinstance(args[1], str):
            raise ExpressionError("starts_with() requires two string arguments")
        return args[0].startswith(args[1])

    if node.name == "has_jurisdiction":
        if len(args) != 2:
            raise ExpressionError("has_jurisdiction() requires two arguments")
        sys_data, jurisdiction = args
        if not isinstance(sys_data, dict) or not isinstance(jurisdiction, str):
            raise ExpressionError("has_jurisdiction(system, jurisdiction_string)")
        return jurisdiction in sys_data.get("deployment_jurisdictions", [])

    if node.name == "targets_population":
        if len(args) != 2:
            raise ExpressionError("targets_population() requires two arguments")
        sys_data, population = args
        if not isinstance(sys_data, dict) or not isinstance(population, str):
            raise ExpressionError("targets_population(system, population_string)")
        pop = sys_data.get("subject_population", {})
        cats = pop.get("categories", []) if isinstance(pop, dict) else []
        return population in cats

    raise ExpressionError(f"Unknown function: {node.name}")  # pragma: no cover


def evaluate(expr: str, ctx: dict[str, Any]) -> Any:
    """Parse and evaluate a constrained expression against a context dict.

    Returns bool, str, int, float, list, or None.
    Raises ExpressionError for invalid or forbidden expressions.
    """
    return _interpret(parse(expr), ctx)
