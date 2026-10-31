# AI-Based Indian Sign Language Alphabet Recognition and Voice Conversion System

[![Phase 1 Status](https://img.shields.io/badge/Phase%201-TESTED%20%26%20VERIFIED-emerald)](#implementation-roadmap)
[![Target Scope](https://img.shields.io/badge/Scope-ISL%20Fingerspelling%20A--Z-blue)](#scope--limitations)
[![Architecture](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI%20%7C%20CNN-indigo)](#technology-stack)
[![Academic Level](https://img.shields.io/badge/Academic-B.Tech%203rd--Year%20AI%2FML-slate)](#)

An educational accessibility prototype developed for B.Tech 3rd-year AI/ML, designed to recognize Indian Sign Language (ISL) fingerspelling alphabet hand poses (A–Z) from camera frames or images, build recognized letters into text, and speak the accumulated text aloud in English using browser-native speech synthesis.

---

## 1. Approved Project Documents
This project is built strictly according to our approved design specifications:
- **Project Design Report (PDR):** [ISL_Alphabet_Recognition_PDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/project-documents/ISL_Alphabet_Recognition_PDR.pdf)
- **Technical Design Report (TDR):** [ISL_Alphabet_Recognition_TDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/project-documents/ISL_Alphabet_Recognition_TDR.pdf)
- **Design Refinements Log:** [DESIGN_CHANGES_LOG.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/project-documents/DESIGN_CHANGES_LOG.md)

---

## 2. Team Knowledge Hub & Viva Center
For team member onboarding, code walkthroughs, and viva defense:
- [START_HERE_TEAM_GUIDE.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/START_HERE_TEAM_GUIDE.md) - Project overview & member responsibilities
- [setup_guide.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/setup_guide.md) - Local Python & Node.js environment configuration
- [workflow.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/workflow.md) - Git commit conventions and verification checklist
- [learning_roadmap.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/learning_roadmap.md) - CNN and computer vision concepts explained simply
- [code_explanations.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/code_explanations.md) - Modular breakdown of the codebase
- [viva_preparation.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/viva_preparation.md) - 10 essential viva questions, answers, and examiner defense

---

## 3. High-Level Architecture

```
[Hand Sign] ──> [Frame Capture] ──> [OpenCV Preprocessing] ──> [CNN Inference] ──> [Debounce Text Builder] ──> [English Voice Output]
```

- **Frontend:** React 19 + Vite 8 + Tailwind CSS v4
- **Backend:** Python FastAPI + OpenCV + Uvicorn
- **ML Engine:** TensorFlow / Keras CNN (26 Output Classes)
- **Voice Output:** Browser Native Web Speech API (`window.speechSynthesis`)
- **Database:** Optional SQLite (Deferred until core recognition is verified)

---

## 4. Implementation Roadmap & Current Status

| Phase | Description | Deliverable | Status |
|---|---|---|---|
| **Phase 1** | **Setup & Project Foundation** | Clean structure, PDR/TDR docs, Vite+Tailwind verified, Git hygiene | **`TESTED_AND_VERIFIED`** |
| **Phase 2** | **Dataset Collection & Audit Gate** | RealSign audit, label verification, dynamic sign inspection (J & Z) | `PLANNED` |
| **Phase 3** | **Image Preprocessing Pipeline** | Resize (128x128), RGB consistency, normalization, safe augmentation | `PLANNED` |
| **Phase 4** | **CNN Model Training** | Baseline CNN training, validation callbacks, weights saving | `PLANNED` |
| **Phase 5** | **Evaluation & Metrics** | Test set evaluation, genuine confusion matrix, precision/recall | `PLANNED` |
| **Phase 6** | **FastAPI Backend** | REST endpoints (`/predict`, `/predict-frame`, `/metrics`), model service | `PLANNED` |
| **Phase 7** | **React Frontend** | Navigation, Home, Learning flashcards, Recognition workspace | `PLANNED` |
| **Phase 8** | **Integration & Voice** | Webcam feed connection, debounce stability filter, SpeechSynthesis | `PLANNED` |
| **Phase 9** | **Documentation & Viva** | Final project report, presentation slides, unseen signer tests | `PLANNED` |

---

## 5. Scope & Honest Academic Limitations
- **Alphabet-Level Prototype:** Scope is restricted to static ISL fingerspelling gestures (A–Z).
- **Movement Signs (J & Z):** Dynamic letters that require spatial movement cannot be modeled fully by a 2D still-image CNN. This is audited in Phase 2 and recorded as an academic limitation.
- **No Fabricated Metrics:** All evaluation numbers presented in results and dashboards are generated strictly from actual model evaluation on unseen test data.

---

## 6. How to Run Frontend (Verified)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173/` in your browser.
