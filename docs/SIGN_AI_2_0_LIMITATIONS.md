# SignAI 2.0 — Scientific Limitations & Ethical Principles

Academic and scientific integrity requires transparent disclosure of model boundary conditions, dataset limitations, and scope constraints.

---

## 1. Static Representation vs. Dynamic Gesture Trajectories

### The Physical Reality of ISL
In authentic Indian Sign Language, the alphabet consists primarily of static manual postures. However:
- The letter **J** requires a dynamic downward hook trace of the pinky or index finger.
- The letter **Z** requires tracing a 3-segment zig-zag trajectory in the air with the index fingertip.

### Model Limitation
- **CNN V4, Landmark MLP, and Multimodal Fusion** operate strictly on single stationary frames ($128 \times 128 \times 3$ or static 78-d vectors).
- Consequently, static evaluation on **J** and **Z** evaluates only a frozen snapshot of the gesture, yielding artificially lower F1 scores (e.g., Z: 66.7% F1).
- While SignAI 2.0 introduces **BiLSTM and BiGRU recurrent temporal infrastructure**, full multi-signer video capture is ongoing.

---

## 2. In-Distribution Validation vs. Signer Independence

### Dataset Provenance
The underlying RealSign dataset comprises 25,085 processed images partitioned into:
- Training: 17,407 images
- Validation: 2,517 images
- Testing: 5,161 images

### Limitation
The original dataset does not annotate individual signer identification tags. Consequently:
- Although exact duplicate images were removed during initial auditing, near-duplicate frames from the same recording session may exist across splits.
- Reported accuracies (CNN V4: 86.34% test accuracy; Multimodal Fusion: 86.32% validation accuracy) represent **in-distribution evaluation on held-out test splits**.
- They do not represent person-independent cross-validation across unseen populations. When deployed in real-world settings with novel signers, accuracy may drop to 50–70% depending on hand anatomy and lighting.

---

## 3. Optical, Environmental & Sensor Sensitivities

Empirical robustness stress-tests on altered validation sets revealed:
1. **Low Illumination:** Accuracy falls to **32.82%** in dim lighting (< 45 lux) because RGB pixel gradients lose contrast and MediaPipe confidence drops.
2. **High Glare / Overexposure:** Drops to **47.12%** due to saturation in skin highlight regions.
3. **Motion Blur:** Hand movement across standard 30 fps webcams reduces edge definition (sharpness < 65 Laplacian variance), dropping accuracy to **47.12%**.
4. **Camera Framing:** If the hand occupies less than 7% of the viewfinder frame, resolution is insufficient for accurate fingerspelling.

SignAI 2.0 mitigates these factors via the **Camera Quality Analyzer**, which provides real-time user advisories before inference.

---

## 4. Ethical & Accessibility Scope

- **Assistive Prototype:** SignAI 2.0 is an educational and assistive research prototype designed for fingerspelling practice and basic alphabet translation.
- **Not an Interpreter Replacement:** It does not translate continuous Indian Sign Language, grammar, spatial morphology, or non-manual markers (facial expressions and torso tilt). It must never be used as a substitute for certified human sign language interpreters in critical legal, medical, or educational environments.
