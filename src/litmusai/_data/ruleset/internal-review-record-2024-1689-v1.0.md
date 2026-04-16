# Internal Ruleset Review Record

**Ruleset version:** `ruleset-2024-1689-v0.1`
**Regulation:** Regulation (EU) 2024/1689 (EU AI Act)
**Review date:** 2026-04-16
**Status:** Internal panel review — NOT external legal review

---

## Panel Members

| Role | Name | Affiliation |
|------|------|-------------|
| Compliance Engineer | AiExponent Internal | AiExponent LLC |
| AI Governance Analyst | AiExponent Internal | AiExponent LLC |
| Corporate Legal Advisor | AiExponent Internal (Anthropic persona) | AiExponent LLC |
| Responsible AI Lead | AiExponent Internal | AiExponent LLC |
| Head of AI Governance (Chair) | AiExponent Internal | AiExponent LLC |
| Security Engineer | AiExponent Internal | AiExponent LLC |

**None of the above are qualified EU AI Act lawyers. This record is an engineering review by AiExponent staff, not legal advice to any specific customer and not a substitute for qualified EU AI Act counsel.**

---

## Per-Category Sign-Off

### 5.1.a — Harmful manipulation (3 rules)
- `rule_a_influences_behaviour`: AMBER when system predicts behaviour. **Approved.**
- `rule_a_subliminal_inputs`: RED when emotional inference + behaviour prediction combined. **Approved.**
- `rule_a_freetext_manipulation`: AMBER when freetext generation + behaviour prediction. **Approved.**
- **Panel note:** conservative — flags any behaviour prediction as amber even without evidence of subliminal techniques.

### 5.1.b — Exploitation of vulnerabilities (3 rules)
- `rule_b_targets_minors`: RED when targeting minors + behaviour predictions. **Approved.**
- `rule_b_vulnerable_population`: AMBER when system targets persons in vulnerable economic situations. **Approved.**
- `rule_b_targets_minors_freetext`: AMBER when freetext generation targeting minors. **Approved.**
- **Panel note:** "targeting" is inferred from the `subject_population` field which relies on honest self-declaration. No semantic analysis of system behaviour.

### 5.1.c — Social scoring (3 rules)
- `rule_c_social_scoring`: RED when individual scores + behaviour history. **Approved.**
- `rule_c_scoring_from_scraped_data`: RED when individual scores + scraped internet data. **Approved.**
- `rule_c_scoring_general`: AMBER for any individual scoring output. **Approved.**
- **Panel note:** "individual scoring" is broadly flagged. Legitimate credit scoring (Art. 5 exemption) produces amber, not clear — by design.

### 5.1.d — Criminal risk prediction (1 rule)
- `rule_d_criminal_risk`: RED for any criminal risk prediction output. **Approved.**
- **Panel note:** no exception path in the ruleset. Criminal risk prediction based on profiling is a blanket prohibition.

### 5.1.e — Untargeted facial image scraping (2 rules)
- `rule_e_untargeted_facial_scraping`: RED when facial images + scraped internet data. **Approved.**
- `rule_e_facial_from_cctv`: AMBER when facial images + public space. **Approved.**

### 5.1.f — Emotion inference (4 rules)
- `rule_f_workplace_emotion`: RED in workplace. **Approved.**
- `rule_f_education_emotion`: RED in education. **Approved.**
- `rule_f_emotion_healthcare_exception`: AMBER in healthcare (exception noted). **Approved.**
- `rule_f_emotion_general`: AMBER for any emotion inference. **Approved.**
- **Panel note:** healthcare exception is flagged amber, not clear, because the exception requires specific medical/safety justification that LitmusAI cannot verify.

### 5.1.g — Biometric categorisation (3 rules)
- `rule_g_biometric_sensitive_classification`: RED when biometric + sensitive attributes. **Approved.**
- `rule_g_facial_sensitive_classification`: RED when facial images + sensitive attributes. **Approved.**
- `rule_g_sensitive_classification_general`: AMBER for any sensitive attribute classification. **Approved.**

### 5.1.h — Real-time remote biometric identification (3 rules)
- `rule_h_realtime_rbi_public_space`: RED for real-time biometric in public space. **Approved.**
- `rule_h_facial_public_realtime`: RED for real-time facial recognition in public space. **Approved.**
- `rule_h_law_enforcement_rbi_exception`: AMBER for law enforcement use (narrow exception). **Approved.**
- **Panel note:** Art. 5(2)-(3) law enforcement exceptions are complex and jurisdiction-specific. Flagging as amber ensures legal review.

---

## Known Interpretive Weaknesses

1. **Self-declaration dependency:** the ruleset relies on the `system.yaml` fields being honestly filled. It cannot detect undeclared capabilities.
2. **No semantic analysis of `purpose` or `system_description`:** the `--describe` keyword inference is heuristic, not NLP. Ambiguous descriptions may produce false negatives.
3. **"Individual scoring" is broad:** legitimate analytics that produce scores (e.g. relevance ranking) may trigger amber on 5.1.c. This is conservative by design.
4. **Emotion inference in healthcare:** the exception requires medical/safety justification. We flag amber because we cannot verify the justification.
5. **No recital-level disambiguation:** some categories have nuanced recital guidance (e.g. Recital 31 on social scoring scope). Our rules do not capture every nuance.

---

## Acknowledgment

This review was conducted by AiExponent's internal compliance panel. **It is not legal advice. It has not been reviewed by a qualified EU AI Act lawyer. It does not constitute a certification of any kind.** Organisations requiring legal certainty should have qualified counsel review the ruleset via the BYO-ruleset path documented in `docs/ruleset-authoring.md`.

---

*Signed off by AiExponent Internal Panel · 2026-04-16*
