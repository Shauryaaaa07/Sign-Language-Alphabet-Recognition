# Design Changes & Decisions Log

This document tracks any implementation adjustments, experimental findings, or parameter refinements that evolve from the baseline specifications in [ISL_Alphabet_Recognition_PDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/project-documents/ISL_Alphabet_Recognition_PDR.pdf) and [ISL_Alphabet_Recognition_TDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/project-documents/ISL_Alphabet_Recognition_TDR.pdf).

---

## Baseline Reference Documents
- **PDR (Project Design Report):** `docs/project-documents/ISL_Alphabet_Recognition_PDR.pdf`
- **TDR (Technical Design Report):** `docs/project-documents/ISL_Alphabet_Recognition_TDR.pdf`

---

## Log of Design Decisions & Refinements

| Date | Phase | Parameter / Component | Baseline (PDR/TDR) | Refined Decision | Rationale |
|---|---|---|---|---|---|
| 2026-10-31 | Phase 1 | Database (SQLite) | Specified as optional | Strictly deferred until core recognition pipeline is verified | Prevents premature database overhead before ML inference is functional |
| 2026-10-31 | Phase 1 | Movement Signs (J & Z) | A–Z classification | Subject to Dataset Audit Gate before training | Static 2D CNN cannot directly capture temporal movement; requires explicit audit and limitation documentation |
| 2026-10-31 | Phase 1 | Knowledge Management | Standard docs folder | Added dedicated `docs/team-knowledge-hub/` | Centralizes student onboarding, code explanations, and viva defense |
