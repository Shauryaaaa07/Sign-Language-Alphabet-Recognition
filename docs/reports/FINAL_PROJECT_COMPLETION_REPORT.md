# SignAI — Final Project Completion & Academic Capstone Report

**Project Title:** AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion Platform  
**Product Identity:** **SignAI** — Indian Sign Language Recognition Platform  
**Tagline:** Your Hands. Your Voice.  
**Submission Date:** November 2026  
**Status:** **PROJECT COMPLETED — READY FOR ACADEMIC SUBMISSION**  
**Software Verification:** 69 / 69 Automated Tests Passed (100%)  
**Hardware Verification:** Software & State Machines Verified; Physical Optical/Audio Stream: `PENDING_USER_VERIFICATION`  

---

## 1. Executive Summary

According to national census statistics, more than **18 million individuals** in India live with hearing and speech impairments. Because the vast majority of hearing citizens do not comprehend Indian Sign Language (ISL), communication barriers in public facilities, educational institutions, healthcare centers, and workplaces remain severe.

**SignAI** was conceptualized, engineered, and experimentally validated to eliminate this accessibility barrier. The platform provides a production-grade, multimodal bridge from fingerspelled ISL signs to natural spoken English.

### Core Achievements
1. **Model Optimization & Independent Generalization:** Developed 5 controlled iterations of deep convolutional neural networks. Selected **CNN V4** as the champion architecture (308,218 parameters), achieving **86.34% Test Accuracy** and **83.96% Macro F1** on 5,161 strictly held-out test images (+27.30 percentage points accuracy and +27.22 percentage points Macro F1 over the 59.04% baseline).
2. **Production FastAPI Service:** Built an asynchronous, high-throughput backend service featuring single-instance lifespan model caching, safe Pillow bilinear rasterization, and strict input validation guards (rejecting 0-byte, corrupt, non-image, and oversized >10 MB payloads).
3. **Six-Page React 19 SaaS Application:** Transformed the user experience into a modern web platform featuring six dedicated views (`/`, `/studio`, `/learn`, `/dashboard`, `/performance`, `/about`), a robust Light/Dark/System theme system (`useSyncExternalStore`), reticle viewfinder, and an educational alphabet guide with 26 verified dataset photos.
4. **Deterministic Gesture Stabilization:** Designed and validated a client-side 3-consecutive-frame buffer ($\tau \ge 0.75$) with repeat-lock mechanics and in-flight request guards, completely eliminating transitory frame flicker and character flooding.
5. **Interactive Sentence Construction & Voice Synthesis:** Integrated an editable Text Builder with space insertion and backspacing, paired with browser-native Web Speech API (`window.speechSynthesis`) for natural English vocalization.
6. **Academic Rigor & Testing Discipline:** Conducted all evaluations under strict data isolation, achieving a 100% passing record across 69 automated tests (57 frontend + 12 backend), zero linter warnings, and a clean production build.

---

## 2. Complete Phase Progression & Milestone Summary

```mermaid
flowchart LR
    P1[Phase 1<br/>Foundation & Setup] --> P2[Phase 2<br/>Dataset Audit Gate]
    P2 --> P3[Phase 3<br/>Baseline CNN V1]
    P3 --> P4[Phase 4<br/>Full Stack Prototype]
    P4 --> P5[Phase 5<br/>Integration Audit]
    P5 --> P6[Phase 6<br/>Controlled ML Series<br/>V2 → V5 & V4 Final]
    P6 --> P7[Phase 7<br/>V4 Integration &<br/>SignAI Redesign]
    P7 --> P8[Phase 8<br/>Final System Validation]
    P8 --> P9[Phase 9<br/>Academic Docs & Wrapup]
```

### Phase 1: Project Setup & Technical Foundation
- Established directory structure, Git configuration, and strict `.gitignore` rules (excluding datasets, heavy `.keras` weights, and virtual environments).
- Initialized React 19 + Vite + Tailwind CSS frontend and Python 3.11 virtual environment.
- Authoring of Project Design Report (PDR), Technical Design Report (TDR), and Architecture specifications.

### Phase 2: Dataset Collection & Audit Gate
- Audited the Indian Sign Language alphabet dataset across 26 classes (A–Z).
- Addressed dataset anomalies: identified duplicates, verified class label uniformity, and established the ground-truth class mapping `training/label_classes.json`.
- Formulated the academic policy on motion-dependent signs (**J** and **Z**), acknowledging static 2D CNN boundaries honestly.

### Phase 3: Image Preprocessing Pipeline & Baseline Model (CNN V1)
- Standardized image dimensions to $128 \times 128 \times 3$ RGB normalized to $[0.0, 1.0]$.
- Built `training/data_pipeline.py` with deterministic validation generator and dynamic training augmentation.
- Trained baseline CNN V1 (3 single-conv layers, Flatten, Dense 128):
  - Validation Accuracy: 61.27% | Validation Loss: 1.8340 | Validation Macro F1: 58.10%
  - Test Accuracy: 59.04% | Test Macro F1: 56.74%
- Produced Baseline Error Analysis and Improvement Plan identifying severe spatial parameter bottlenecks in the Flatten layer.

### Phase 4: Full-Stack Integration Prototype
- Implemented FastAPI backend service (`backend/main.py`, `backend/prediction.py`) exposing `/health` and `/predict`.
- Built React frontend prototype with image file uploader and live webcam viewfinder.
- Engineered the client-side 3-consecutive-frame stability filter and repeat-lock state machine.
- Integrated the interactive Text Builder and browser-native Web Speech API voice synthesis.

### Phase 5: System Integration Audit & Hardware Testing Protocol
- Executed a 16-step simulated end-to-end integration audit ("HELLO WORLD" word construction, repeated 'L' handling, speech synthesis execution, and audio cancellation).
- Created the formal Manual Hardware Testing Checklist (`docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md`) and declared physical hardware status as `PENDING_USER_VERIFICATION`.

### Phase 6: Controlled CNN Experimentation & Final Model Selection
Conducted 4 controlled scientific experiments modifying a single independent variable per iteration:
- **Experiment 1 (CNN V2 - Architectural Modernization):** Replaced Flatten with Global Average Pooling (GAP) and introduced 3 Double-Conv blocks with Batch Normalization.
  - *Result:* Validation accuracy jumped from 61.27% to **80.10%** (+18.83 pp); Macro F1 improved to **73.10%**.
- **Experiment 2 (CNN V3 - Photometric Data Augmentation):** Added brightness, contrast, hue, and saturation perturbations to training generators.
  - *Result:* Validation loss dropped from 1.6701 to **1.3732** (-17.8%); validation accuracy reached **80.29%**; Macro F1 rose to **75.52%**.
- **Experiment 3 (CNN V4 - L2 Kernel Regularization):** Applied L2 weight penalty ($\lambda = 1.0 \times 10^{-4}$) to all 8 convolutional and dense weight kernels.
  - *Result:* Achieved lowest validation loss of **1.3507**; Macro F1 surged to **77.68%** (+2.16 pp over V3); weight distributions stabilized.
- **Experiment 4 (CNN V5 - SpatialDropout2D):** Tested spatial channel dropout ($p = 0.15$) in conv blocks.
  - *Result:* Validation accuracy declined to 75.29% and Macro F1 fell to 70.08%, indicating feature underfitting. Experiment rigorously halted and rejected.
- **Milestone 6.6 (Final Model Selection & Independent Test Evaluation):**
  - Selected **CNN V4** (`saved_models/experiments/isl_alphabet_cnn_v4_best.keras`).
  - Evaluated once on strictly held-out test split (`dataset/processed/Testing/`, 5,161 images):
    - **Test Accuracy: 86.34%** (+27.30 pp over baseline).
    - **Test Macro F1: 83.96%** (+27.22 pp over baseline).
    - **Test Weighted F1: 83.87%** | **Test Macro Precision: 85.22%** | **Test Macro Recall: 86.42%**.

### Phase 7: Production Backend Integration & Complete UI/UX Redesign
- **Milestone 7.1:** Integrated CNN V4 into FastAPI backend with lifespan model loading, 10MB payload guards, and full response schemas (`predicted_letter`, `predicted_class`, `confidence`, `top_predictions`, `inference_time_ms`). Verified with 12/12 passing pytest checks.
- **Milestone 7.2:** Verified React frontend compatibility against CNN V4 contract across 5 automated test suites (57 tests passed).
- **UI/UX Redesign (SignAI):** Created a premium SaaS web platform ("Your Hands. Your Voice.") featuring:
  - 6 dedicated views (`/`, `/studio`, `/learn`, `/dashboard`, `/performance`, `/about`).
  - Dark, Light, and System themes via `useSyncExternalStore`.
  - 26 verified dataset reference photographs in `/alphabet_samples/`.
  - High-resolution embedded evaluation charts in `/performance_artifacts/`.

### Phase 8: Final System Validation
- Conducted full repository integrity audit: confirmed zero dataset tampering, model weights integrity (SHA-256 verified), and clean `.gitignore`.
- Passed all automated tests (69 / 69 passed).
- Passed Oxlint with 0 errors and 0 warnings.
- Compiled clean production build in 1.35s.
- Verified live dual-server execution on `http://127.0.0.1:8000` (FastAPI) and `http://127.0.0.1:5173/` (Vite).
- Generated `docs/reports/PHASE_8_FINAL_SYSTEM_VALIDATION_REPORT.md`.

### Phase 9: Final Academic Documentation & Capstone Wrap-up
- Updated all core technical documents: `README.md`, `frontend/README.md`, `backend/README.md`, `docs/architecture/ARCHITECTURE.md`, `docs/development/SETUP.md`.
- Produced this comprehensive Final Project Completion Report.

---

## 3. Grounded Final Performance Metrics Matrix

All reported metrics derive strictly from the final independent evaluation on 5,161 held-out test images (`dataset/processed/Testing/`):

### 3.1 Global Performance Comparison (Baseline V1 vs Final CNN V4)

| Metric | Baseline V1 | Final CNN V4 | Delta ($\Delta$) | Relative Improvement |
|---|---|---|---|---|
| **Independent Test Accuracy** | 59.04% | **86.34%** | **+27.30 pp** | **+46.2%** |
| **Independent Test Macro F1** | 56.74% | **83.96%** | **+27.22 pp** | **+48.0%** |
| **Independent Test Weighted F1**| 56.41% | **83.87%** | **+27.46 pp** | **+48.7%** |
| **Independent Test Macro Precision** | 63.85% | **85.22%** | **+21.37 pp** | **+33.5%** |
| **Independent Test Macro Recall**| 59.13% | **86.42%** | **+27.29 pp** | **+46.2%** |
| **Total Model Parameters** | 1,085,850 | **308,218** | **-777,632** | **-71.6% (More Efficient)** |
| **Trainable Parameters** | 1,085,850 | **307,322** | **-778,528** | **-71.7%** |
| **Model Disk Size** | 13.06 MB | **3.81 MB** | **-9.25 MB** | **-70.8%** |
| **Mean Inference Latency** | ~115 ms | **~109 ms** | **-6 ms** | CPU Real-Time Capable |

### 3.2 Per-Class Performance Highlights (CNN V4)

- **Flawless Classes (100% Precision, 100% Recall, 100% F1):**
  - **D** (F1: 1.0000 | 199/199 correct)
  - **H** (F1: 1.0000 | 200/200 correct)
  - **L** (F1: 1.0000 | 198/198 correct)
  - **R** (F1: 1.0000 | 198/198 correct)
- **High-Performing Classes (>90% F1):**
  - **K** (F1: 0.9950 | 198/198 correct, Precision: 0.990)
  - **J** (F1: 0.9392 | 193/198 correct, Precision: 0.885)
  - **G** (F1: 0.9365 | 191/199 correct, Precision: 0.884)
  - **P** (F1: 0.9300 | 193/200 correct, Precision: 0.869)
  - **M** (F1: 0.9252 | 198/198 correct, Precision: 0.861)
  - **O** (F1: 0.9160 | 191/198 correct, Precision: 0.853)
  - **B** (F1: 0.9023 | 194/199 correct, Precision: 0.826)
- **Challenging Classes & Honest Boundary Analysis:**
  - **W (F1: 0.0000):** Planar silhouette projection overlaps heavily with E, I, and X in 2D space.
  - **S (F1: 0.4000):** Closed fist with thumb across fingers; frequently confused with compact fist signs (A and E).
  - **Z (F1: 0.6667):** Dynamic zigzag stroke flattened into a 2D static keyframe; exhibits expected temporal ambiguity.

---

## 4. Software Verification Summary (100% Pass)

| Scope | Tool / Runner | Checks | Execution Details | Status |
|---|---|---|---|---|
| **Frontend Linting** | Oxlint v1.89.0 | 34 files, 104 rules | Completed in 94 ms; 0 errors, 0 warnings | **PASS** |
| **Frontend Production Build** | Vite v8.3.5 | 2,076 modules | Output: `index.html` (0.66kB), `assets` (468.67kB total) in 1.35s | **PASS** |
| **Frontend Test Suite** | Node.js Test Runner | 57 automated tests | 5 test suites covering API compatibility, E2E workflow, speech synthesis, text builder, webcam stability | **PASS** |
| **Backend Test Suite** | Pytest 9.2.0 | 12 test cases | Tested model loading, `/health`, `/predict`, dimensions, channels, error cases, test isolation | **PASS** |
| **Backend Integration Audit** | Standalone Script | 4 verification stages | Model cache, CORS headers, synthetic inference, 400/413 error handling | **PASS** |
| **Live Backend Service** | Uvicorn (Port 8000) | `GET /health` | Returned HTTP 200 with `isl_alphabet_cnn_v4_best.keras` and 26 classes | **PASS** |
| **Live Frontend Service** | Vite Dev (Port 5173) | `GET /` | Returned HTTP 200 with HMR enabled | **PASS** |

---

## 5. Pending User Tasks: Physical Hardware Verification

In strict accordance with academic integrity guidelines, automated test suites do not fabricate physical hardware signals. The following manual tests remain to be verified by the user on physical equipment:

| Item # | Verification Task | Test Procedure | Expected Physical Outcome | Status |
|---|---|---|---|---|
| **HW-1** | Physical Webcam Stream Initiation | Navigate to `/studio`, click "Live Webcam", accept browser permissions. | Laptop/USB camera light activates; video feed renders inside reticle without distortion. | `PENDING_USER_VERIFICATION` |
| **HW-2** | Real-Time Hand Sign Detection | Display ISL sign 'L' (index finger and thumb extended) inside reticle. | Prediction Hero updates to 'L' with confidence $\ge 0.75$; top-3 candidate cards populate. | `PENDING_USER_VERIFICATION` |
| **HW-3** | Stability Filter & Repeat-Lock | Hold 'L' sign steady for 5 seconds. | 'L' appends to Text Builder **exactly once** after 3 matching frames; no runaway flooding. | `PENDING_USER_VERIFICATION` |
| **HW-4** | Sentence Composition | Form word "HI", click Space, form "ALL". | Text Builder displays "HI ALL" with word count: 2, character count: 6. | `PENDING_USER_VERIFICATION` |
| **HW-5** | Physical Audio Playback | Click the "Speak" button. | Device speaker produces audible English pronunciation of "HI ALL"; Stop button terminates speech immediately. | `PENDING_USER_VERIFICATION` |
| **HW-6** | Camera Teardown & Privacy | Switch back to "Image Upload" mode or close tab. | Hardware camera indicator light immediately turns off (MediaStream tracks stopped). | `PENDING_USER_VERIFICATION` |

*Refer to the full protocol in [docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md).*

---

## 6. How to Run the System Locally

### Step 1: Backend Service (Terminal 1)
```bash
# Activate your Python 3.11 environment (e.g. fortress)
conda activate fortress

# Run Uvicorn server from the repository root
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Endpoint: `http://127.0.0.1:8000/health`
- Swagger Docs: `http://127.0.0.1:8000/docs`

### Step 2: Frontend Service (Terminal 2)
```bash
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```
- Open in Browser: `http://127.0.0.1:5173/`

### Step 3: Run All Verification Suites
```bash
# Frontend tests (57 tests)
npm --prefix frontend test

# Frontend linting
npm --prefix frontend run lint

# Backend pytest (12 tests)
pytest backend/tests/test_api.py -v
```

---

## 7. Final Repository Structure

```
c:\Users\shaur\OneDrive\Desktop\Sign Language Alphabet Recognition\
├── .gitignore                      # Comprehensive exclusions (weights, datasets, node_modules)
├── README.md                       # Master project overview, benchmarks, quickstart
├── CONTRIBUTING.md                 # Contribution guidelines
├── backend/
│   ├── config.py                   # Backend paths, CORS, 10MB limits, dimensions
│   ├── main.py                     # FastAPI app, lifespan singleton loader, endpoints
│   ├── model_loader.py             # Single-instance model caching
│   ├── prediction.py               # Preprocessing, normalization, inference execution
│   ├── requirements.txt            # Python dependencies
│   ├── schemas.py                  # Pydantic v2 schemas
│   ├── README.md                   # Backend documentation guide
│   └── tests/
│       ├── audit_system_integration.py # Standalone integration audit script
│       └── test_api.py             # 12 Pytest test cases
├── dataset/
│   ├── dataset_info.md             # Dataset documentation
│   └── processed/
│       ├── Training/               # 26 folders (A–Z) used for model training
│       ├── Validation/             # 26 folders (A–Z) used for tuning
│       └── Testing/                # 26 folders (A–Z) strictly held-out test split (5,161 images)
├── docs/
│   ├── architecture/
│   │   └── ARCHITECTURE.md         # Three-tier architecture & state machines
│   ├── development/
│   │   └── SETUP.md                # Developer environment setup & execution guide
│   ├── internal/
│   │   └── LEARNING_GUIDE.md       # Technical learning documentation
│   └── reports/                    # Complete audit trail (PDR, TDR, V1–V5 experiments, Phase 7–9 reports)
│       ├── PHASE_8_FINAL_SYSTEM_VALIDATION_REPORT.md
│       ├── FINAL_PROJECT_COMPLETION_REPORT.md
│       ├── MANUAL_HARDWARE_TESTING_CHECKLIST.md
│       └── ...
├── frontend/
│   ├── public/
│   │   ├── alphabet_samples/       # 26 verified reference photos (A–Z)
│   │   └── performance_artifacts/  # High-res confusion matrix & evaluation charts
│   ├── src/
│   │   ├── components/             # Reusable UI components
│   │   ├── context/                # ThemeContext (Dark, Light, System)
│   │   ├── hooks/                  # useTheme custom hook
│   │   ├── pages/                  # 6 route pages (Home, Studio, Learn, Dashboard, Performance, About)
│   │   ├── services/               # API service client
│   │   ├── tests/                  # 5 frontend test suites (57 tests)
│   │   ├── utils/                  # Pure utility functions (text mutations, speech)
│   │   ├── App.jsx                 # Route configurations & layout shell
│   │   └── index.css               # Tailwind CSS 4 theme design tokens
│   ├── package.json
│   ├── vite.config.js
│   └── README.md                   # Frontend documentation guide
├── results/
│   ├── confusion_matrix.png        # Evaluated confusion matrix
│   ├── per_class_metrics.png       # Evaluated per-class metric distribution
│   └── experiments/                # Training histories and metric plots for V1–V5
├── saved_models/
│   └── experiments/
│       └── isl_alphabet_cnn_v4_best.keras # Selected production model checkpoint (3.81 MB)
└── training/
    ├── build_clean_dataset.py
    ├── data_pipeline.py            # Data generator with augmentations
    ├── evaluate_model.py           # Independent evaluation script
    ├── inspect_dataset.py
    ├── label_classes.json          # 26 verified classes (A–Z)
    ├── model.py                    # Baseline CNN model architecture
    ├── train_model.py              # Baseline training pipeline
    └── experiments/                # Model architectures and trainers for V2, V3, V4, V5
```

---

## 8. Academic Integrity & Project Submission Readiness

### Submission Certification
- **Dataset Isolation:** The held-out test split (`dataset/processed/Testing/`) was strictly sealed after the final independent evaluation in Phase 6.6. Zero evaluation data was used for model tuning or backend inference.
- **Model Checkpoint Integrity:** The active production checkpoint `saved_models/experiments/isl_alphabet_cnn_v4_best.keras` has remained completely untampered (SHA-256: `4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762`).
- **Transparency of Metrics:** Zero synthetic or exaggerated performance numbers. All metrics reported derive directly from reproducible test script execution.
- **Software Stability:** 69 / 69 automated tests pass with 100% success rate, 0 linter warnings, and clean production builds.

The **SignAI** platform is officially certified as **COMPLETE** and **READY FOR ACADEMIC SUBMISSION**.
