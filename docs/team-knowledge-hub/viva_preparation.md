# Viva Preparation: Questions, Answers & Academic Defense

This document prepares the project group for the B.Tech project viva and technical questioning by external examiners.

---

## 1. Project Motivation & Scope Questions

### Q1: What is the main objective of this project?
**Answer:**
"Our objective is to develop an educational accessibility prototype that recognizes Indian Sign Language (ISL) fingerspelling alphabet hand poses (A–Z) from camera frames using a Convolutional Neural Network (CNN). The system accumulates the recognized letters into an editable text area and converts the final text into English speech using the browser's native SpeechSynthesis API."

### Q2: Is this a complete Indian Sign Language translator?
**Answer:**
"No, sir/ma'am. We explicitly state in our documentation that this is an alphabet-level fingerspelling recognition system, not a full ISL sentence translator. Natural ISL involves complex grammar, facial expressions, body orientation, two-handed motion, and temporal context that cannot be solved by a static 2D CNN alone."

### Q3: How do you handle movement-dependent letters like 'J' and 'Z'?
**Answer:**
"In ISL, letters like J and Z typically require a tracing motion. Because a 2D CNN processes single still frames, it cannot directly model temporal movement. We have an explicit Dataset Audit Gate in Phase 2 to inspect how the public dataset represents J and Z. In our project defense, we honestly report that dynamic gestures are a fundamental limitation of static CNNs and form our primary future scope (requiring sequence models such as CNN-LSTM or 3D CNNs)."

---

## 2. Machine Learning & Computer Vision Questions

### Q4: Why did you choose a CNN over traditional Machine Learning (like SVM or Random Forest)?
**Answer:**
"Traditional ML algorithms require manual feature extraction (such as HOG or SIFT), which struggles with variations in hand size, skin tones, and lighting conditions. CNNs automatically learn hierarchical spatial features directly from raw pixels—low-level features like edges in early layers, and high-level features like finger bends and hand contours in deeper layers."

### Q5: Why divide pixel values by 255.0?
**Answer:**
"Pixel values range from 0 to 255. Normalizing them to the [0, 1] range keeps gradient updates during backpropagation stable and uniform across layers, preventing vanishing or exploding gradients and ensuring faster convergence."

### Q6: Why is horizontal flipping disabled in your data augmentation?
**Answer:**
"While horizontal flipping is common for generic object recognition (like cats or cars), in sign language, hand orientation and left/right distinctions carry semantic meaning. Flipping an image horizontally can alter or invalidate the sign convention."

---

## 3. System Integration & Web Architecture Questions

### Q7: Why FastAPI instead of Flask or Django?
**Answer:**
"FastAPI is lightweight, natively asynchronous, and significantly faster than Flask. It automatically validates request data using Pydantic, generates interactive Swagger documentation (`/docs`), and is ideal for high-throughput image inference endpoints."

### Q8: How is the model loaded in the backend? Does it reload for every frame?
**Answer:**
"No. We use a singleton service pattern where the trained model weights are loaded into memory once when the FastAPI server initializes. Subsequent requests execute predictions against the existing in-memory model, minimizing latency."

### Q9: How do you prevent duplicate letters during live webcam streaming?
**Answer:**
"We implement a debounce and gesture stability algorithm in the frontend. A letter is only appended if its confidence exceeds our threshold, it remains consistent across consecutive frames, and a repeat-lock ensures the same letter is not re-added until the user changes or releases their hand."

### Q10: Why use the browser SpeechSynthesis API instead of a cloud TTS service?
**Answer:**
"Browser `window.speechSynthesis` is entirely client-side, zero-cost, requires no external API keys or paid cloud subscriptions, and introduces zero network latency for audio generation."
