"""
Explainable AI (XAI) Module for Concrete Infrastructure Inspection
Implements Grad-CAM (Gradient-Weighted Class Activation Mapping) for the 2D-CNN visual model.
Generates publication-quality visual heatmaps overlaying concrete surface cracks, spalling, and corrosion.
Fulfills PhD Chapter 5, Section 5.8 & Chapter 6, Section 6.4.6 (Field technician trust & interpretability).
"""

import os
import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.ndimage import zoom
from typing import Tuple, Optional

class ConcreteGradCAM:
    """
    Grad-CAM implementation for concrete damage localization.
    Hooks into the final convolutional feature layer to compute spatial activation weights.
    """
    def __init__(self, model: torch.nn.Module, target_layer: Optional[torch.nn.Module] = None):
        self.model = model
        self.model.eval()

        # If no target layer specified, default to the last residual/convolutional block
        if target_layer is None:
            if hasattr(model, 'stage2_res'):
                self.target_layer = model.stage2_res.conv2
            elif hasattr(model, 'block4'):
                self.target_layer = model.block4.conv
            else:
                raise ValueError("Target convolutional layer could not be automatically identified.")
        else:
            self.target_layer = target_layer

        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_heatmap(self, input_tensor: torch.Tensor, target_class: Optional[int] = None) -> np.ndarray:
        """
        Generates 2D normalized Grad-CAM heatmap [0, 1] for input_tensor [1, C, H, W].
        """
        self.model.zero_grad()
        logits = self.model(input_tensor)

        if target_class is None:
            target_class = torch.argmax(logits, dim=-1).item()

        score = logits[0, target_class]
        score.backward()

        # Global average pooling of gradients: alpha_k
        alpha_k = torch.mean(self.gradients, dim=(2, 3), keepdim=True)  # [1, C, 1, 1]

        # Weighted combination of forward activation maps
        cam = torch.sum(alpha_k * self.activations, dim=1, keepdim=True)  # [1, 1, H, W]
        cam = F.relu(cam)  # Only features with positive influence

        cam = cam.squeeze().cpu().numpy()
        # Normalize between 0 and 1
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max - cam_min > 1e-8:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        return cam

    def overlay_heatmap_on_image(
        self,
        original_img: np.ndarray,
        heatmap: np.ndarray,
        alpha: float = 0.45
    ) -> np.ndarray:
        """
        Overlays the Grad-CAM heatmap onto the RGB concrete inspection photograph.
        original_img: [H, W, 3] in range [0, 255] or [0, 1]
        """
        if original_img.max() > 1.0:
            norm_img = original_img.astype(np.float32) / 255.0
        else:
            norm_img = original_img.astype(np.float32)

        H, W = norm_img.shape[:2]
        zoom_factors = (H / heatmap.shape[0], W / heatmap.shape[1])
        heatmap_resized = zoom(heatmap, zoom_factors, order=1)
        heatmap_resized = np.clip(heatmap_resized, 0.0, 1.0)

        # Apply Jet colormap from matplotlib
        colored_heatmap = cm.jet(heatmap_resized)[:, :, :3]

        overlay = alpha * colored_heatmap + (1.0 - alpha) * norm_img
        overlay = np.clip(overlay * 255.0, 0, 255).astype(np.uint8)
        return overlay

    def save_gradcam_figure(
        self,
        original_img: np.ndarray,
        heatmap: np.ndarray,
        overlay: np.ndarray,
        predicted_class_name: str,
        confidence_pct: float,
        output_path: str
    ):
        """Generates a side-by-side 3-panel figure for thesis Chapter 5."""
        fig, axes = plt.subplots(1, 3, figsize=(14, 5))

        axes[0].imshow(original_img)
        axes[0].set_title("Original Field Inspection Photo", fontsize=12)
        axes[0].axis('off')

        axes[1].imshow(heatmap, cmap='jet')
        axes[1].set_title("Grad-CAM Class Activation Heatmap", fontsize=12)
        axes[1].axis('off')

        axes[2].imshow(overlay)
        axes[2].set_title(f"Damage Localization Overlay\n[{predicted_class_name}: {confidence_pct:.1f}% Confidence]", fontsize=12)
        axes[2].axis('off')

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()
