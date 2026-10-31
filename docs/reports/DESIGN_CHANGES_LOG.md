# Design Changes & Decisions Log

This document tracks implementation adjustments, experimental findings, and parameter refinements that evolve from the baseline specifications in [ISL_Alphabet_Recognition_PDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/ISL_Alphabet_Recognition_PDR.pdf) and [ISL_Alphabet_Recognition_TDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/ISL_Alphabet_Recognition_TDR.pdf).

---

## Baseline Reference Documents
- **Project Design Report (PDR):** `docs/reports/ISL_Alphabet_Recognition_PDR.pdf` (SHA-256: `C32ABC3073DD4811CB43CE2F989632F9259647F39D538A78B5B33594F5C6A414`)
- **Technical Design Report (TDR):** `docs/reports/ISL_Alphabet_Recognition_TDR.pdf` (SHA-256: `7CF867A40D374AFF229F62CDE0C87B0775111904D3434E1C8CAFD010DF0145B5`)
- **Master Project Blueprint:** `docs/reports/ISL_Project_Planning_and_Architecture.pdf` (SHA-256: `1F415C674641206C9A867DE95EB8C59E7F2F9CB4310F5D5B3F9380433EAC1DFA`)

---

## Log of Design Decisions & Refinements

| Date | Phase | Parameter / Component | Baseline (PDR/TDR) | Refined Decision | Rationale |
|---|---|---|---|---|---|
| 2026-10-31 | Phase 1 | Database (SQLite) | Specified as optional | Strictly deferred until core recognition pipeline is verified | Prevents premature database overhead before ML inference is functional |
| 2026-10-31 | Phase 1 | Movement Signs (J & Z) | A–Z classification | Subject to Dataset Audit Gate before training | Static 2D CNN cannot directly capture temporal movement; requires explicit audit and limitation documentation |
| 2026-10-31 | Phase 1 | Repository Structure | Initial folder proposal | Reorganized into domain-driven structure (`docs/architecture`, `docs/reports`, `docs/development`, `docs/internal`) | Adheres to software engineering best practices, isolates formal reports, and maintains clean repository root |
