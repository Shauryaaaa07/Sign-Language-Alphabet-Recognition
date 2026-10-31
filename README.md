# AI-Based Indian Sign Language Alphabet Recognition and Voice Conversion System

An educational accessibility system engineered to recognize Indian Sign Language (ISL) fingerspelling alphabet hand poses (A–Z) from camera streams and images, assemble recognized letters into text with real-time gesture stabilization, and read the resulting text aloud in English using browser-native speech synthesis.

---

## 1. Project Reference & Approved Reports
This implementation adheres strictly to approved design documentation:
- **Project Design Report (PDR):** [ISL_Alphabet_Recognition_PDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/ISL_Alphabet_Recognition_PDR.pdf)
- **Technical Design Report (TDR):** [ISL_Alphabet_Recognition_TDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/ISL_Alphabet_Recognition_TDR.pdf)
- **Master Project Blueprint:** [ISL_Project_Planning_and_Architecture.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/ISL_Project_Planning_and_Architecture.pdf)
- **Parameter Refinements Log:** [DESIGN_CHANGES_LOG.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/DESIGN_CHANGES_LOG.md)

---

## 2. Technical Documentation Hub
- **Architecture & System Design:** [docs/architecture/ARCHITECTURE.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/architecture/ARCHITECTURE.md)
- **Developer Environment Setup:** [docs/development/SETUP.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/development/SETUP.md)
- **Contribution & Git Discipline:** [CONTRIBUTING.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/CONTRIBUTING.md)
- **Technical Learning Guide:** [docs/internal/LEARNING_GUIDE.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/internal/LEARNING_GUIDE.md)

---

## 3. High-Level Architecture

```
[Hand Sign] ──> [Frame Capture] ──> [OpenCV Preprocessing] ──> [CNN Inference] ──> [Debounce Text Builder] ──> [English Voice Output]
```

- **Frontend:** React 19, Vite 8, Tailwind CSS v4
- **Backend:** Python FastAPI, OpenCV, Uvicorn
- **ML Core:** TensorFlow / Keras Convolutional Neural Network (26 Output Classes)
- **Voice Engine:** Browser Native Web Speech API (`window.speechSynthesis`)
- **Persistence:** Optional SQLite (Deferred until recognition core is verified)

---

## 4. Implementation Roadmap & Current Status

| Phase | Description | Deliverable | Current Status |
|---|---|---|---|
| **Phase 1** | **Setup & Project Foundation** | Clean structure, verified Vite+Tailwind setup, Git configuration | **`TESTED_AND_VERIFIED`** |
| **Phase 2** | **Dataset Collection & Audit Gate** | RealSign audit script, label verification, dynamic sign inspection (J & Z) | `PLANNED` |
| **Phase 3** | **Image Preprocessing Pipeline** | Standard resize, RGB consistency, normalization, safe augmentation | `PLANNED` |
| **Phase 4** | **CNN Model Training** | Baseline CNN training, validation callbacks, weights saving | `PLANNED` |
| **Phase 5** | **Evaluation & Metrics** | Test set evaluation, genuine confusion matrix, precision/recall | `PLANNED` |
| **Phase 6** | **FastAPI Backend** | REST endpoints (`/predict`, `/predict-frame`, `/metrics`), model service | `PLANNED` |
| **Phase 7** | **React Frontend** | Navigation, Home, Learning flashcards, Recognition workspace | `PLANNED` |
| **Phase 8** | **Integration & Voice** | Webcam feed connection, debounce stability filter, SpeechSynthesis | `PLANNED` |
| **Phase 9** | **Documentation & Submission** | Final engineering reports, presentation materials, unseen signer testing | `PLANNED` |

---

## 5. Scope & Engineering Boundaries
- **Alphabet-Level Prototype:** Initial scope is strictly fingerspelled ISL characters (A–Z). Full natural ISL sentence translation (which involves grammar, facial expressions, and dynamic movement) is outside the initial scope.
- **Dynamic Signs (J & Z):** Inherently movement-based signs require temporal audit in Phase 2. Static 2D CNN boundaries will be reported honestly.
- **Academic Integrity:** Zero synthetic or fabricated evaluation metrics. All performance numbers derive from actual test runs on held-out data.

---

## 6. Running the Frontend Locally (Verified)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173/` in your browser.
