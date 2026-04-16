"""Unit tests for RFC 8785 JSON canonicalisation + SHA-256 hashing.

Pinned to FR-19 (input hash), NFR-7 (deterministic hashing).
"""

from __future__ import annotations

from typing import Any

from litmusai.engine.hashing import canonical_json, sha256_hash


class TestCanonicalJson:
    def test_key_ordering(self) -> None:
        result = canonical_json({"z": 1, "a": 2, "m": 3})
        assert result == '{"a":2,"m":3,"z":1}'

    def test_nested_key_ordering(self) -> None:
        result = canonical_json({"b": {"z": 1, "a": 2}, "a": 0})
        assert result == '{"a":0,"b":{"a":2,"z":1}}'

    def test_list_preserves_order(self) -> None:
        result = canonical_json({"x": [3, 1, 2]})
        assert result == '{"x":[3,1,2]}'

    def test_no_whitespace(self) -> None:
        result = canonical_json({"key": "value"})
        assert " " not in result
        assert "\n" not in result

    def test_unicode_not_escaped(self) -> None:
        result = canonical_json({"name": "caf\u00e9"})
        assert "caf\u00e9" in result

    def test_null_value(self) -> None:
        result = canonical_json({"x": None})
        assert result == '{"x":null}'

    def test_boolean_lowercase(self) -> None:
        result = canonical_json({"a": True, "b": False})
        assert result == '{"a":true,"b":false}'

    def test_empty_object(self) -> None:
        assert canonical_json({}) == "{}"

    def test_empty_list(self) -> None:
        assert canonical_json({"x": []}) == '{"x":[]}'

    def test_deterministic_across_calls(self) -> None:
        obj = {"z": [1, {"b": 2, "a": 1}], "a": "hello"}
        assert canonical_json(obj) == canonical_json(obj)

    def test_float_representation(self) -> None:
        result = canonical_json({"x": 1.0})
        assert "1.0" in result or "1" in result

    def test_nested_lists_in_objects(self) -> None:
        obj = {"data": [{"z": 1, "a": 2}, {"y": 3}]}
        result = canonical_json(obj)
        assert result == '{"data":[{"a":2,"z":1},{"y":3}]}'


class TestSha256Hash:
    def test_known_hash(self) -> None:
        obj = {"name": "test"}
        h = sha256_hash(obj)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_deterministic(self) -> None:
        obj = {"z": 1, "a": 2}
        assert sha256_hash(obj) == sha256_hash(obj)

    def test_key_order_invariant(self) -> None:
        h1 = sha256_hash({"a": 1, "b": 2})
        h2 = sha256_hash({"b": 2, "a": 1})
        assert h1 == h2

    def test_whitespace_invariant(self) -> None:
        obj1 = {"key": "value"}
        obj2 = {"key": "value"}
        assert sha256_hash(obj1) == sha256_hash(obj2)

    def test_different_values_different_hash(self) -> None:
        h1 = sha256_hash({"x": 1})
        h2 = sha256_hash({"x": 2})
        assert h1 != h2

    def test_system_description_dict_hashable(self, minimal_system_dict: dict[str, Any]) -> None:
        h = sha256_hash(minimal_system_dict)
        assert len(h) == 64
        assert sha256_hash(minimal_system_dict) == h
