"""
1D Convolutional Neural Network (CNN) for Structural Health Monitoring (SHM)
Specifically designed for multi-sensor IoT telemetry (vibration, strain, crack displacement)
in concrete civil infrastructure under tropical conditions.
Fulfills PhD Chapter 5, Section 5.8.3.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple

class ConvBlock1D(nn.Module):
    """Convolutional Block with 1D Conv, BatchNorm, LeakyReLU, and MaxPool."""
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 5, stride: int = 1, pool_size: int = 2):
        super().__init__()
        self.conv = nn.Conv1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=kernel_size // 2,
            bias=False
        )
        self.bn = nn.BatchNorm1d(out_channels)
        self.act = nn.LeakyReLU(negative_slope=0.1, inplace=True)
        self.pool = nn.MaxPool1d(kernel_size=pool_size) if pool_size > 1 else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.pool(self.act(self.bn(self.conv(x))))


class ConcreteSHMCNN1D(nn.Module):
    """
    Multi-Scale 1D-CNN for concrete structure condition state classification.
    Input shape: [Batch, Channels, TimeSteps]
    Output: Logits for condition states (e.g. 4 classes: Healthy, Minor, Moderate, Severe).
    """
    def __init__(
        self,
        in_channels: int = 4,         # e.g., Vibration_X, Vibration_Z, Strain, Crack_Displacement
        num_classes: int = 4,         # Normal, Minor, Moderate, Critical
        base_filters: int = 32,
        dropout_rate: float = 0.3
    ):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes

        # Feature Extraction Layers
        # Layer 1: Captures broad low-frequency structural dynamic shifts (kernel 7)
        self.block1 = ConvBlock1D(in_channels, base_filters, kernel_size=7, pool_size=2)
        
        # Layer 2: Captures intermediate transient vibrations and load variations (kernel 5)
        self.block2 = ConvBlock1D(base_filters, base_filters * 2, kernel_size=5, pool_size=2)
        
        # Layer 3: Captures localized micro-strain fluctuations and crack acoustic emission bursts (kernel 3)
        self.block3 = ConvBlock1D(base_filters * 2, base_filters * 4, kernel_size=3, pool_size=2)

        # Layer 4: Deep contextual representation
        self.block4 = ConvBlock1D(base_filters * 4, base_filters * 4, kernel_size=3, pool_size=2)

        # Global Pooling prevents overfitting and accommodates variable window sizes
        self.global_pool = nn.AdaptiveAvgPool1d(1)

        # Classifier Head with Dropout for Regularization (vital for field robustness)
        self.classifier = nn.Sequential(
            nn.Linear(base_filters * 4, 64),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(negative_slope=0.1, inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(64, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: [B, C, T] or [B, T, C]. If [B, T, C], transpose to [B, C, T].
        """
        if x.ndim == 3 and x.shape[1] > x.shape[2]:
            x = x.permute(0, 2, 1)

        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        
        x = self.global_pool(x)       # [B, C_out, 1]
        x = torch.flatten(x, 1)      # [B, C_out]
        logits = self.classifier(x)  # [B, num_classes]
        return logits

    def predict_probabilities(self, x: torch.Tensor) -> torch.Tensor:
        """Returns softmax class probabilities [B, num_classes]."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            return F.softmax(logits, dim=-1)

    def predict_with_uncertainty(self, x: torch.Tensor, num_samples: int = 25) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Monte Carlo Dropout (Uncertainty Quantification) for safety-critical civil SHM.
        Keeps stochastic dropout active across multiple forward passes to estimate
        epistemic model uncertainty.
        Returns:
            mean_probabilities: [B, num_classes]
            uncertainty_std: [B, num_classes]
        """
        self.eval()  # Set model to eval mode
        # Enable ONLY Dropout modules so BatchNorm layers use running statistics
        for m in self.modules():
            if isinstance(m, torch.nn.Dropout):
                m.train()
        predictions = []
        with torch.no_grad():
            for _ in range(num_samples):
                logits = self.forward(x)
                probs = F.softmax(logits, dim=-1)
                predictions.append(probs)
        stacked = torch.stack(predictions, dim=0)  # [num_samples, B, num_classes]
        mean_probs = torch.mean(stacked, dim=0)
        std_uncertainty = torch.std(stacked, dim=0)
        self.eval()  # Reset back to eval mode
        return mean_probs, std_uncertainty

    def get_model_summary(self) -> Dict[str, Any]:
        """Returns parameter count and layer summary for thesis transparency note (Section 5.8)."""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {
            "model_name": "ConcreteSHMCNN1D",
            "in_channels": self.in_channels,
            "num_classes": self.num_classes,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params
        }
