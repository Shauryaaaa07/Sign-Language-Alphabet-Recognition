# SignAI 2.0 — Frontend Web Application

**Product:** SignAI 2.0 — Multimodal Indian Sign Language Alphabet Recognition & Voice Platform  
**Tagline:** Your Hands. Your Voice.  
**Stack:** React 19 (ESM) + Vite v8.3.5 + Tailwind CSS v4.3.3 + HTML5 Canvas + Web Speech API  

---

## 1. Overview

The SignAI 2.0 frontend delivers a clean, **Editorial Modernist** single-page application designed for real-time Indian Sign Language (ISL) accessibility and model inspection. Key capabilities include:

1. **Multimodal Studio (`#studio`):** Real-time webcam recognition and photo upload with dual-stream model switching (**Multimodal Fusion** vs **Pure CNN V4**).
2. **Dual-Hand MediaPipe Skeleton Overlay:** Renders simultaneous 21-point hand skeletons, independent bounding boxes, and non-overlapping handedness badges (**Warm Amber `#EA580C`** for **LEFT HAND**, **Sapphire Blue `#2563EB`** for **RIGHT HAND**).
3. **Explainable AI (Grad-CAM):** Interactive visual heatmap overlay modal showing spatial CNN V4 attention at layer `block3_conv2`.
4. **Camera Optical Quality Telemetry:** Real-time brightness, contrast, and blur sharpness monitoring with actionable user feedback.
5. **Deterministic 3-Frame Stability & Sentence Builder:** Client-side stability filter ($\ge 0.75$ threshold) with repeat-lock prevention, undo, space, backspace, and clear controls.
6. **Speech Synthesis (`window.speechSynthesis`):** Browser-native English voice output with interactive **Speech Pitch** ($0.5\text{--}1.5$) slider and voice selector.
7. **Practice Arena (`#practice`) & Model Lab (`#models`):** Guided sign practice with XP/streak tracking and live side-by-side multi-model comparison.

---

## 2. Tech Stack & Dependencies

| Category | Package | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **UI Framework** | `react`, `react-dom` | `^19.3.1` | Declarative UI components & Canvas rendering |
| **Build Tool** | `vite`, `@vitejs/plugin-react` | `^8.3.5` | Fast HMR dev server & Rollup production bundling |
| **Routing** | `react-router-dom` | `^7.18.5` | Hash-based navigation across all 8 views |
| **Styling** | `tailwindcss`, `@tailwindcss/vite` | `^4.3.3` | Utility CSS & custom design tokens |
| **Icons** | `lucide-react` | `^1.66.0` | Crisp UI iconography |
| **Linter** | `oxlint` | `^1.89.0` | High-speed static JavaScript/JSX linting |

---

## 3. Application Routes (8 Views)

| Hash Route | View | Purpose |
| :--- | :--- | :--- |
| `#home` | **Home** | Hero overview, interactive 4-step pipeline walkthrough, and quick-launch controls |
| `#studio` | **Studio** | Live camera/upload workspace, dual-hand skeleton overlay, Grad-CAM, quality HUD, TTS |
| `#practice` | **Practice** | Guided ISL alphabet drills with verification matching, XP (`+50 XP`), and streak counter |
| `#models` | **Model Lab** | Architecture scorecards and live image testing comparing CNN V4, Landmark MLP, and Fusion |
| `#learn` | **Learn A–Z** | Interactive 26-letter reference gallery backed by verified ISL sample imagery |
| `#dashboard` | **Dashboard** | Quarantined test baseline metrics, backend `/health` status, and session confidence histogram |
| `#performance` | **Performance** | Model V1–V5 ablation chart, perturbation stress-test bars, and confusion matrix |
| `#about` | **About** | Multimodal architecture summary, tech stack, and academic limitations charter |

---

## 4. Directory Structure

```text
frontend/
├── public/
│   ├── signs/                    # 26 verified ISL letter cards (A–Z)
│   ├── alphabet_samples/         # Sample gallery dataset references
│   ├── performance_artifacts/    # Evaluation plots
│   └── results/                  # Confusion matrix assets
├── src/
│   ├── App.jsx                   # Primary Editorial Modernist 8-view application & Canvas overlays
│   ├── App.css                   # Editorial Modernist design system styles
│   ├── index.css                 # Base CSS resets & tokens
│   ├── main.jsx                  # React 19 entry point
│   ├── components/               # Legacy modular UI components (retained for compatibility)
│   ├── context/                  # ThemeContext provider
│   ├── hooks/                    # Speech & theme custom hooks
│   ├── pages/                    # Legacy page modules
│   ├── services/                 # Backend API client helpers
│   ├── utils/                    # Pure functions (speechLogic.js, textBuilderLogic.js)
│   └── tests/                    # 6 automated Node.js test suites
│       ├── v4_api_compatibility.test.mjs
│       ├── e2e_full_workflow.test.mjs
│       ├── speech_synthesis.test.mjs
│       ├── text_builder.test.mjs
│       ├── webcam_stability.test.mjs
│       └── new_ui_components.test.mjs
├── index.html
├── package.json
└── vite.config.js
```

---

## 5. Development, Linting & Testing Commands

```bash
# Install dependencies
npm install

# Start local dev server (http://127.0.0.1:5173/)
npm run dev

# Run all 6 automated test suites (100% pass)
npm test

# Run static code linting with Oxlint (0 errors)
npm run lint

# Build production bundle in frontend/dist/
npm run build
```
