# Article 5 Category Coverage

LitmusAI screens against all eight prohibited-practice categories of Article 5(1)(a)-(h) of Regulation (EU) 2024/1689.

## Categories

### 5.1.a — Harmful manipulation
AI systems that deploy subliminal or manipulative techniques to materially distort behaviour causing significant harm.

**Triggers:** behaviour predictions + emotional inference, freetext manipulation
**Penalty:** Up to €35M or 7% global turnover

### 5.1.b — Exploitation of vulnerabilities
AI systems that exploit vulnerabilities due to age, disability, or socioeconomic status.

**Triggers:** targeting minors/vulnerable populations + behaviour predictions or freetext output
**Key test:** does the system target a specific vulnerable population AND influence behaviour?

### 5.1.c — Social scoring
Individual scoring based on social behaviour for detrimental treatment in unrelated contexts.

**Triggers:** individual scores + behaviour history or scraped internet data
**This is a RED prohibition** — no mitigation path

### 5.1.d — Criminal risk prediction
Predicting individual criminal risk based solely on profiling.

**Triggers:** criminal risk predictions output
**Exception:** specific criminal investigation contexts (rare, requires legal review)

### 5.1.e — Untargeted facial image scraping
Building or expanding facial recognition databases from untargeted internet or CCTV scraping.

**Triggers:** facial images + scraped internet data, or facial images + public space
**This is a RED prohibition** for scraping; AMBER for public-space use

### 5.1.f — Emotion inference in workplace/education
Inferring emotions in workplace or educational settings.

**Triggers:** emotion inferences + workplace or education context
**Exception:** medical/safety use (healthcare context → AMBER, not RED)

### 5.1.g — Biometric categorisation of sensitive attributes
Using biometric data to categorise individuals by race, political opinions, religion, sexual orientation.

**Triggers:** biometric/facial inputs + sensitive attribute classifications
**This is a RED prohibition**

### 5.1.h — Real-time remote biometric identification in public spaces
Real-time biometric identification in publicly accessible spaces.

**Triggers:** biometric/facial inputs + public space + real-time operation
**Exception:** narrow law enforcement exceptions under Art. 5(2)-(3) → AMBER

## Regulatory References

All citations refer to Regulation (EU) 2024/1689 as published in the Official Journal of the European Union, 12 July 2024. Article 5 has been enforceable since 2 February 2025 per Article 113(a).

---

*Not legal advice. Not a notified body.*
