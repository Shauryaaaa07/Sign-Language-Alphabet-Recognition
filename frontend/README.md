# SignAI — Frontend Web Application

**Product Name:** SignAI — Indian Sign Language Recognition Platform  
**Tagline:** Your Hands. Your Voice.  
**Framework:** React 19 (ESM) + Vite v8.3.5 + Tailwind CSS v4.3.3 + React Router DOM v7  

---

## 1. Overview

The SignAI frontend is a modern, responsive single-page web platform designed for multimodal accessibility. It provides:
1. **Interactive Recognition Studio:** Dual-mode recognition supporting static file uploads and real-time live webcam streams with reticle guidance.
2. **Deterministic Gesture Stabilization:** Client-side 3-frame buffer filtering ($\ge 0.75$ confidence threshold) and repeat-lock mechanism to prevent frame flicker and character flooding.
3. **Interactive Text Builder:** Real-time character assembly with space insertion, single-character backspace, full buffer reset, and live word/character metrics.
4. **Browser-Native Voice Conversion:** High-fidelity speech synthesis using the Web Speech API (`window.speechSynthesis`) with intelligent English voice priority.
5. **Interactive Alphabet Learning Guide:** Visual reference gallery showcasing 26 letters with dataset-grounded sample photos and placement guidance.
6. **Comprehensive System Diagnostics:** Real-time health monitoring of the FastAPI backend and interactive ML benchmark analytics.

---

## 2. Tech Stack & Dependencies

| Category | Technology | Version | Purpose |
|---|---|---|---|
| **UI Framework** | React | `^19.3.1` | Declarative user interface components |
| **Build Tool** | Vite | `^8.3.5` | Fast HMR dev server and optimized rollup production bundling |
| **Routing** | React Router DOM | `^7.18.5` | Client-side routing across 6 application views |
| **Styling** | Tailwind CSS | `^4.3.3` | Utility-first responsive CSS styling with CSS variables |
| **Iconography** | Lucide React | `^1.66.0` | Modern, accessible iconography |
| **Linter** | Oxlint | `^1.89.0` | High-speed Rust-based JavaScript/JSX linter |

---

## 3. Application Directory Structure

```
frontend/
├── public/
│   ├── alphabet_samples/       # 26 verified ISL reference photos (A–Z) from Validation split
│   └── performance_artifacts/  # CNN V4 confusion matrix & per-class evaluation charts
├── src/
│   ├── components/             # Reusable modular UI components
│   │   ├── Header.jsx          # Top navigation bar, active link indicators, theme switcher
│   │   ├── Footer.jsx          # Footer with product identity, links, and system status
│   │   ├── UploadCard.jsx      # Drag-and-drop file upload zone with instant preview
│   │   ├── WebcamReticle.jsx   # Live camera viewfinder with reticle overlay & FPS badge
│   │   ├── PredictionHero.jsx  # Hero prediction display, confidence badge, top-3 candidates
│   │   ├── TextBuilder.jsx     # Editable sentence assembly canvas with action controls
│   │   └── SpeechControls.jsx  # Web Speech synthesis controls (Speak, Stop, Voice selector)
│   ├── context/
│   │   ├── ThemeContext.jsx    # Theme provider supporting Dark, Light, and System modes
│   │   └── themeContextInstance.js # Dedicated React Context instance
│   ├── hooks/
│   │   └── useTheme.js         # Custom hook for consuming theme state and dispatchers
│   ├── pages/
│   │   ├── Home.jsx            # / Landing page: hero banner, interactive pipeline, feature cards
│   │   ├── Studio.jsx          # /studio: Real-time recognition workspace & sentence builder
│   │   ├── Learn.jsx           # /learn: 26 ISL alphabet cards with modal finger guidance
│   │   ├── Dashboard.jsx       # /dashboard: System KPIs, live /health monitor, architecture
│   │   ├── Performance.jsx     # /performance: V1–V5 experiment comparison, confusion matrix
│   │   └── About.jsx           # /about: Mission, team, 3-tier architecture, UN SDG 10
│   ├── services/
│   │   └── api.js              # Fetch client communicating with backend /health and /predict
│   ├── tests/                  # 5 automated test suites (57 checks)
│   │   ├── e2e_full_workflow.test.mjs    # Complete user workflow simulation
│   │   ├── speech_synthesis.test.mjs     # Web Speech state machine & voice filtering
│   │   ├── text_builder.test.mjs         # Text builder mutations & metrics
│   │   ├── v4_api_compatibility.test.mjs # CNN V4 backend contract & schemas
│   │   └── webcam_stability.test.mjs    # Webcam stability filter & concurrency locking
│   ├── utils/
│   │   ├── speechLogic.js      # Pure functions for speech synthesis and voice matching
│   │   └── textBuilderLogic.js # Pure functions for text mutations and analytics
│   ├── App.jsx                 # Route configurations, theme initialization, layout shell
│   ├── index.css               # Tailwind CSS 4 theme tokens, color palettes, animations
│   └── main.jsx                # React root entry point
├── package.json                # Project dependencies, scripts, and metadata
└── vite.config.js              # Vite configuration with React and Tailwind plugins
```

---

## 4. Design System & Theme Architecture

SignAI implements a modern design system with full support for three theme states:

- **Dark Mode (Default):** Deep slate-navy background (`#0B1220`), frosted glass cards (`#111C30`), high-contrast text (`#F8FAFC`).
- **Light Mode:** Crisp off-white background (`#F4F7FC`), pure white cards (`#FFFFFF`), dark slate text (`#0F172A`).
- **System Mode:** Dynamically mirrors OS-level `prefers-color-scheme` using React 19's `useSyncExternalStore` for flicker-free synchronization.

All colors, borders, and transitions leverage Tailwind CSS classes driven by a centralized `theme` state stored in `localStorage`.

---

## 5. Development & Testing Commands

### Start Development Server
```bash
npm run dev
```
Runs at `http://127.0.0.1:5173/` with hot module replacement (HMR).

### Run Oxlint
```bash
npm run lint
```
Executes Oxlint across all 34 source files (0 warnings, 0 errors).

### Compile Production Build
```bash
npm run build
```
Creates an optimized static bundle in `frontend/dist/`.

### Run Automated Test Suites
```bash
npm test
```
Executes all 5 test suites (57 tests) verifying end-to-end user journeys, speech synthesis, text operations, webcam stability, and API contract compatibility.
