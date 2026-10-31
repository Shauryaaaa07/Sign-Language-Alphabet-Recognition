# Learning Roadmap: Computer Vision & ISL Recognition

This document provides a simple, conceptual guide for 3rd-year students to grasp the key machine learning and computer vision principles used in this project.

---

## 1. What is Indian Sign Language (ISL) Fingerspelling?
- Sign language uses hand gestures, orientations, and movements to convey information.
- **Fingerspelling:** Each alphabet letter (A to Z) is mapped to a standardized static or dynamic hand shape.
- Unlike American Sign Language (ASL), which is largely one-handed, ISL frequently employs two hands and distinct finger configurations.

---

## 2. Convolutional Neural Networks (CNNs) Explained Simply
- Traditional machine learning flattens images into 1D vectors, losing spatial relationships.
- CNNs preserve 2D grid structure using:
  1. **Convolutional Layers (`Conv2D`):** Learn small visual filters (edges, corner curves, finger junctions).
  2. **Activation Function (`ReLU`):** Introduces non-linearity ($f(x) = \max(0, x)$).
  3. **Pooling Layers (`MaxPooling2D`):** Downsamples feature maps, providing spatial translation invariance.
  4. **Dropout:** Randomly deactivates neurons during training to prevent memorization (overfitting).
  5. **Dense + Softmax Layer:** Outputs probability distribution across 26 target classes.

---

## 3. Image Preprocessing Fundamentals
- **Resizing (Proposed 128 &times; 128):** Neural networks require fixed tensor dimensions.
- **Color Consistency (RGB):** OpenCV loads images as BGR by default, so explicit conversion to RGB is mandatory.
- **Normalization ($[0, 1]$):** Dividing pixel values by 255.0 prevents exploding gradients and speeds up gradient descent convergence.
- **Safe Augmentation:** Rotations ($\pm 10^\circ$) and slight zooms help the model generalize across different user distances. *Horizontal flipping is disabled* because flipping a hand sign can change its semantic class in ISL.

---

## 4. Real-Time Camera Debounce & Stability Logic
- A webcam feeds 15 to 30 frames per second.
- Without a stabilization filter, a single 1-second gesture would append 20 duplicate letters.
- **Debounce Algorithm:**
  1. Prediction must exceed a confidence threshold (e.g., $\ge 80\%$).
  2. The candidate letter must remain identical across $N$ consecutive frames.
  3. Once accepted, a repeat-lock triggers until the hand is removed or modified.
