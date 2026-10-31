# Technical & Conceptual Learning Guide

This document covers the fundamental principles of Computer Vision, Deep Learning, and Indian Sign Language (ISL) fingerspelling utilized in this project.

---

## 1. Indian Sign Language (ISL) Fingerspelling Overview
- Fingerspelling represents individual alphabet characters (A to Z) through standardized static or dynamic hand configurations.
- Unlike American Sign Language (ASL), which primarily relies on one hand, ISL frequently uses two hands and distinct finger intersections.
- Dynamic characters (such as J and Z) incorporate spatial motion trajectories, representing a clear technical distinction from purely static postures.

---

## 2. Convolutional Neural Networks (CNNs) in Computer Vision
- Standard fully connected networks flatten 2D images, losing spatial relationships.
- CNNs preserve spatial structure through parameter sharing and local receptive fields:
  1. **Convolutional Layers (`Conv2D`):** Compute spatial convolutions using learnable kernels to extract low-level features (edges, textures) and high-level features (finger orientations, contours).
  2. **Activation (`ReLU`):** Implements $f(x) = \max(0, x)$ to introduce non-linearity while mitigating vanishing gradients.
  3. **Pooling (`MaxPooling2D`):** Reduces feature map spatial dimensions, providing translation invariance and computational efficiency.
  4. **Dropout:** Randomly zeroes out activations during training to discourage feature co-adaptation and prevent overfitting.
  5. **Dense Softmax Output:** Normalizes logit outputs into a probability distribution across 26 target classes.

---

## 3. Image Preprocessing Principles
- **Spatial Normalization ($128 \times 128$):** Ensures uniform tensor dimensions across variable camera resolutions.
- **Color Space Consistency (RGB):** OpenCV defaults to BGR format; explicit conversion to RGB ensures alignment with web standards and pre-trained conventions.
- **Pixel Normalization ($[0, 1]$):** Dividing by 255.0 scales input features to uniform magnitude, accelerating gradient descent convergence.
- **Augmentation Constraints:** Small rotations ($\pm 10^\circ$) and subtle zooms enhance invariance to camera distance and tilt. *Horizontal mirroring is explicitly prohibited* as it alters left/right hand semantics in sign language.
