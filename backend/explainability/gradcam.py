"""
Grad-CAM (Gradient-Weighted Class Activation Mapping) Engine
============================================================

Computes visual explanations for CNN V4 predictions by calculating gradients
of the winning class score with respect to the activations of the final
convolutional layer (`block3_conv2`).
"""

from typing import Optional, Tuple
import numpy as np
import tensorflow as tf

TARGET_CONV_LAYER = "block3_conv2"


class GradCAMExplainer:
    """Computes Grad-CAM activation heatmaps for CNN V4 without modifying weights."""

    def __init__(self, model: tf.keras.Model, layer_name: str = TARGET_CONV_LAYER):
        self.model = model
        self.layer_name = layer_name

        # Validate that layer exists
        layer_names = [l.name for l in model.layers]
        if layer_name not in layer_names:
            # Fallback to last Conv2D layer found
            conv_layers = [l.name for l in model.layers if isinstance(l, tf.keras.layers.Conv2D)]
            if conv_layers:
                self.layer_name = conv_layers[-1]
            else:
                raise ValueError(f"No convolutional layers found in model: {layer_names}")

        # Construct sub-model mapping inputs to [conv_layer_output, final_prediction]
        self.grad_model = tf.keras.models.Model(
            inputs=self.model.inputs,
            outputs=[self.model.get_layer(self.layer_name).output, self.model.output],
            name="gradcam_submodel",
        )

    def generate_heatmap(
        self,
        input_tensor: np.ndarray,
        class_idx: Optional[int] = None,
    ) -> Tuple[np.ndarray, int, float]:
        """
        Generates a 2D normalized heatmap [0.0, 1.0] for the specified class index.
        If class_idx is None, uses the model's top predicted class.

        Args:
            input_tensor: Normalized image tensor of shape (1, 128, 128, 3)
            class_idx: Integer target class index (0-25)

        Returns:
            Tuple of (heatmap_2d, predicted_class_idx, prediction_confidence)
        """
        if len(input_tensor.shape) == 3:
            input_tensor = np.expand_dims(input_tensor, axis=0)

        tensor = tf.cast(input_tensor, tf.float32)

        with tf.GradientTape() as tape:
            conv_outputs, predictions = self.grad_model(tensor, training=False)
            if class_idx is None:
                class_idx = int(tf.argmax(predictions[0]))
            confidence = float(predictions[0][class_idx])
            loss = predictions[:, class_idx]

        # 1. Compute gradients of class score wrt feature maps
        grads = tape.gradient(loss, conv_outputs)

        # 2. Global average pooling of gradients (importance weights alpha)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # 3. Weighted linear combination of feature maps
        conv_outputs_0 = conv_outputs[0]
        heatmap = conv_outputs_0 @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # 4. Apply ReLU and normalize to [0.0, 1.0]
        heatmap = tf.maximum(heatmap, 0.0)
        max_val = tf.math.reduce_max(heatmap)
        if max_val > 1e-10:
            heatmap = heatmap / max_val
        else:
            heatmap = tf.zeros_like(heatmap)

        return heatmap.numpy().astype(np.float32), class_idx, confidence
