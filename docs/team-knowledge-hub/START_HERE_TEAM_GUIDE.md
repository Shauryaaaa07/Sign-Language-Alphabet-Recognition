# Team Knowledge Hub: Start Here Guide

Welcome to the **AI-Based Indian Sign Language Alphabet Recognition and Voice Conversion System** project repository!

This guide is designed for our B.Tech 3rd-year project group so that every member understands the system architecture, team responsibilities, and how to run and explain the project.

---

## 1. Quick Project Summary (30-Second Viva Pitch)
> "We are building an educational web application that recognizes Indian Sign Language (ISL) fingerspelling alphabet hand signs (A–Z) using a trained Convolutional Neural Network (CNN). The recognized letters are assembled into words/sentences via an editable Text Builder (with debounce and stability controls), and converted to English voice output using the browser's native SpeechSynthesis API."

---

## 2. Team Member Roles & Primary Deliverables

| Role | Primary Ownership | Core Responsibilities | Key Viva Focus |
|---|---|---|---|
| **Member 1 (ML & Vision)** | Phase 2, 3, 4, 5 | Dataset audit gate, OpenCV preprocessing, CNN model training, evaluation metrics & confusion matrix | Convolution operations, activation functions, overfitting control, safe augmentation |
| **Member 2 (Backend & System)** | Phase 1, 6, 8 | FastAPI endpoints, image decoding bridge, model singleton loader, optional SQLite | REST architecture, asynchronous endpoints, memory management, CORS |
| **Member 3 (Frontend & UI/UX)** | Phase 1, 7, 8 | React UI, webcam integration (`getUserMedia`), debounce stability logic, Text-to-Speech API | Camera stream handling, state management, repeat-lock algorithm, Speech API |
| **Member 4 (Data Quality & Viva Hub)** | Phase 2, 5, 8, 9 | Custom volunteer data consent, unseen signer testing, documentation, slide deck, viva defense | Dataset provenance, static vs dynamic ISL signs (J/Z limitation), evaluation metrics |

---

## 3. Approved Project Scope & Crucial Limitations
- **In-Scope:** Static ISL alphabet gestures from A to Z, image upload, browser webcam input, text building with editing controls, and English voice playback.
- **Out-of-Scope (Important Viva Point):** Full natural ISL sentence translation. Real Indian Sign Language involves two-handed dynamic movements, facial expressions, spatial orientation, and unique grammar that cannot be captured by a static 2D CNN.
- **Dynamic Signs (J & Z):** In ISL, J and Z typically require movement strokes. Our baseline 2D CNN inspects still images; this limitation is acknowledged honestly in our documentation.

---

## 4. Documentation Map
- [ISL_Alphabet_Recognition_PDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/project-documents/ISL_Alphabet_Recognition_PDR.pdf) - Project Design Report (Approved baseline)
- [ISL_Alphabet_Recognition_TDR.pdf](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/project-documents/ISL_Alphabet_Recognition_TDR.pdf) - Technical Design Report (Approved architecture)
- [DESIGN_CHANGES_LOG.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/project-documents/DESIGN_CHANGES_LOG.md) - Record of implementation refinements
- [setup_guide.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/setup_guide.md) - How to set up Python and Node.js locally
- [workflow.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/workflow.md) - Git commit discipline and PR review rules
- [viva_preparation.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/team-knowledge-hub/viva_preparation.md) - Sample viva questions and answers
