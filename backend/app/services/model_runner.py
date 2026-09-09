"""
Model Runner Service
Loads and manages inference for:
1. 1D-CNN Physics-Aware Telemetry Model (with Monte Carlo Dropout)
2. 2D-CNN Visual Inspection Model (with Grad-CAM Explainable AI)
Fulfills SMMS Platform Layer (Chapter 6, Section 6.5.3).
"""

import os
import sys
import io
import base64
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from torchvision import transforms
from typing import Dict, Any, List, Tuple

# Ensure ai_models/src is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
AI_SRC_DIR = os.path.join(BASE_DIR, "ai_models/src")
if AI_SRC_DIR not in sys.path:
    sys.path.insert(0, AI_SRC_DIR)

from models.cnn_1d import ConcreteSHMCNN1D
from models.cnn_2d import ConcreteDamageCNN2D
from explainability import ConcreteGradCAM
from preprocessor import SHMPreprocessor

class ModelRunnerService:
    _instance = None

    CONDITION_CLASSES = {
        0: "Normal / Healthy",
        1: "Minor Deterioration",
        2: "Moderate Distress",
        3: "Critical Damage"
    }

    DEFECT_CLASSES = {
        0: "Intact Substrate",
        1: "Structural Crack",
        2: "Concrete Spalling / Damage",
        3: "Corrosion / Efflorescence"
    }

    SEVERITY_LEVELS = {
        0: "Healthy (Routine Monitoring)",
        1: "Minor (Preventative Action)",
        2: "Moderate (Corrective Repair)",
        3: "Critical (Immediate Intervention)"
    }

    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.weights_dir = os.path.join(BASE_DIR, "ai_models/weights")
        
        self.cnn_1d = None
        self.cnn_2d = None
        self.gradcam = None
        self.preprocessor = SHMPreprocessor(sampling_rate=1.0 / 60.0)

        self._load_models()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_models(self):
        """Loads trained weights into memory."""
        # 1. Load 1D-CNN Telemetry Model
        path_1d = os.path.join(self.weights_dir, "cnn_1d_telemetry_best.pth")
        if os.path.exists(path_1d):
            self.cnn_1d = ConcreteSHMCNN1D(in_channels=8, num_classes=4, base_filters=32, dropout_rate=0.3)
            state_dict = torch.load(path_1d, map_location=self.device)
            self.cnn_1d.load_state_dict(state_dict)
            self.cnn_1d.to(self.device)
            self.cnn_1d.eval()
            print(f"[ModelRunner] Loaded 1D-CNN Telemetry Model from {path_1d}")
        else:
            print(f"[ModelRunner] WARNING: 1D-CNN weights not found at {path_1d}")

        # 2. Load 2D-CNN Visual Inspection Model
        path_2d = os.path.join(self.weights_dir, "cnn_2d_visual_best.pth")
        if os.path.exists(path_2d):
            self.cnn_2d = ConcreteDamageCNN2D(in_channels=3, num_classes=4, base_channels=32, dropout_rate=0.3)
            state_dict = torch.load(path_2d, map_location=self.device)
            self.cnn_2d.load_state_dict(state_dict)
            self.cnn_2d.to(self.device)
            self.cnn_2d.eval()
            self.gradcam = ConcreteGradCAM(self.cnn_2d)
            print(f"[ModelRunner] Loaded 2D-CNN Visual Model & Grad-CAM from {path_2d}")
        else:
            print(f"[ModelRunner] WARNING: 2D-CNN weights not found at {path_2d}")

    def run_telemetry_inference(self, readings: List[Dict[str, float]], window_size: int = 128) -> Dict[str, Any]:
        """
        Processes temporal telemetry readings:
        Applies thermal-mechanical strain decoupling and runs 1D-CNN with Monte Carlo Dropout.
        """
        if self.cnn_1d is None:
            raise RuntimeError("1D-CNN model is not initialized.")

        # Convert readings to array [N, 8]
        raw_feats = []
        for r in readings:
            raw_feats.append([
                r.get('strain_microstrain', 700.0),
                r.get('vibration_ms2', 1.0),
                r.get('crack_propagation_mm', 0.01),
                r.get('deflection_mm', 0.5),
                r.get('tilt_deg', 0.05),
                r.get('modal_frequency_hz', 1.9),
                r.get('temperature_c', 25.0),
                r.get('humidity_percent', 60.0)
            ])
        arr = np.array(raw_feats, dtype=np.float32)

        # Thermal decoupling: epsilon_mech = epsilon_tot - alpha * (T - mean_T)
        temp = arr[:, 6]
        strain_tot = arr[:, 0]
        alpha_c = 11.5
        thermal_strain = alpha_c * (temp - np.mean(temp))
        mech_strain = strain_tot - thermal_strain
        arr[:, 0] = mech_strain  # Replace with mechanical strain

        # Pad or truncate to window_size
        if len(arr) < window_size:
            pad_len = window_size - len(arr)
            pad_arr = np.tile(arr[-1:], (pad_len, 1))
            window = np.vstack([arr, pad_arr])
        else:
            window = arr[-window_size:]

        # Standardize
        norm_window = (window - np.mean(window, axis=0, keepdims=True)) / (np.std(window, axis=0, keepdims=True) + 1e-6)

        # Reshape to [1, 8, window_size]
        tensor_x = torch.tensor(norm_window, dtype=torch.float32).unsqueeze(0).permute(0, 2, 1).to(self.device)

        # Monte Carlo Dropout Uncertainty Quantification (20 samples)
        mean_probs, std_uncertainty = self.cnn_1d.predict_with_uncertainty(tensor_x, num_samples=20)
        mean_probs_np = mean_probs[0].cpu().numpy()
        std_np = std_uncertainty[0].cpu().numpy()

        pred_class = int(np.argmax(mean_probs_np))
        conf_pct = round(float(mean_probs_np[pred_class]) * 100, 2)
        ci_str = f"{conf_pct:.1f}% ± {2 * float(std_np[pred_class]) * 100:.2f}% (95% CI)"

        return {
            "class_index": pred_class,
            "condition_name": self.CONDITION_CLASSES[pred_class],
            "confidence_pct": conf_pct,
            "confidence_interval_95": ci_str,
            "probabilities": [round(float(p), 4) for p in mean_probs_np],
            "anomaly_detected": bool(pred_class > 0),
            "mechanical_strain_isolated": round(float(np.mean(mech_strain)), 2),
            "thermal_expansion_offset": round(float(np.mean(thermal_strain)), 2)
        }

    def run_visual_inference(self, image_bytes: bytes, img_size: int = 224) -> Dict[str, Any]:
        """
        Runs visual concrete defect inspection on uploaded image.
        Returns defect classification, severity, and base64 Grad-CAM heatmap.
        """
        if self.cnn_2d is None:
            raise RuntimeError("2D-CNN visual model is not initialized.")

        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        raw_resized = img.resize((img_size, img_size))
        raw_np = np.array(raw_resized).astype(np.float32) / 255.0

        eval_transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        tensor_x = eval_transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.cnn_2d(tensor_x)
            probs = F.softmax(logits, dim=-1).cpu().numpy()[0]

        pred_class = int(np.argmax(probs))
        conf_pct = round(float(probs[pred_class]) * 100, 2)

        # Epistemic Uncertainty & Out-of-Distribution (OOD) Gating
        # Concrete structures exhibit distinct feature activations; arbitrary/non-concrete images
        # produce flat softmax distributions or high entropy across defect classes.
        entropy = float(-np.sum(probs * np.log(probs + 1e-9)))
        max_entropy = float(np.log(len(probs))) # ln(4) ≈ 1.386
        norm_entropy = float(entropy / max_entropy) if max_entropy > 0 else 0.0

        is_ood = bool(conf_pct < 52.0 or norm_entropy > 0.88)
        defect_name = self.DEFECT_CLASSES[pred_class]
        severity_level = self.SEVERITY_LEVELS[pred_class]
        ood_warning = None

        if is_ood:
            defect_name = "Unrecognized Surface (OOD Rejection)"
            severity_level = "Out-of-Distribution"
            ood_warning = (
                f"Epistemic uncertainty safety gate triggered: Normalized Entropy = {norm_entropy:.2f} "
                f"(threshold: 0.88), Max Softmax = {conf_pct}%. The model detected that this specimen "
                f"does not exhibit structural concrete surface characteristics."
            )

        # Generate Grad-CAM Heatmap
        cam_map = self.gradcam.generate_heatmap(tensor_x, target_class=pred_class)
        overlay_np = self.gradcam.overlay_heatmap_on_image(raw_np, cam_map)

        # Estimate defect area ratio (pixels with activation > 0.45)
        defect_ratio = round(float(np.mean(cam_map > 0.45) * 100), 2)

        # Convert overlay image to Base64 PNG for Flutter client rendering
        overlay_pil = Image.fromarray(overlay_np)
        buffer = io.BytesIO()
        overlay_pil.save(buffer, format="PNG")
        overlay_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "defect_class_index": pred_class,
            "defect_name": defect_name,
            "confidence_pct": conf_pct,
            "probabilities": [round(float(p), 4) for p in probs],
            "severity_level": severity_level,
            "estimated_surface_defect_ratio_pct": defect_ratio,
            "gradcam_heatmap_base64": overlay_b64,
            "is_out_of_distribution": is_ood,
            "ood_warning": ood_warning
        }
