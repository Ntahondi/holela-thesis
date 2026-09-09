"""
2D Convolutional Neural Network (CNN) for Structural Condition Monitoring
Supports both:
1. Concrete surface crack image classification (visual inspection).
2. Time-Frequency spectrogram analysis of multi-channel IoT sensor signals.
Fulfills PhD Chapter 5, Section 5.8.3 & Section 2.5.5.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any

class ResidualBlock2D(nn.Module):
    """Residual block with skip connection for stable gradient flow."""
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)
        self.act = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = self.act(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return self.act(out)


class ConcreteDamageCNN2D(nn.Module):
    """
    Lightweight 2D-CNN for concrete crack classification and spectrogram telemetry.
    Input shape: [Batch, Channels, Height, Width]
    """
    def __init__(
        self,
        in_channels: int = 3,         # 3 for RGB crack images; 1 or C for spectrograms
        num_classes: int = 4,         # Normal, Minor, Moderate, Critical
        base_channels: int = 32,
        dropout_rate: float = 0.3
    ):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes

        # Initial Feature Extractor
        self.prep = nn.Sequential(
            nn.Conv2d(in_channels, base_channels, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(base_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )

        # Stage 1
        self.stage1_conv = nn.Sequential(
            nn.Conv2d(base_channels, base_channels * 2, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(base_channels * 2),
            nn.ReLU(inplace=True)
        )
        self.stage1_res = ResidualBlock2D(base_channels * 2)

        # Stage 2
        self.stage2_conv = nn.Sequential(
            nn.Conv2d(base_channels * 2, base_channels * 4, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(base_channels * 4),
            nn.ReLU(inplace=True)
        )
        self.stage2_res = ResidualBlock2D(base_channels * 4)

        # Global Average Pooling
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        # Classification Head
        self.classifier = nn.Sequential(
            nn.Linear(base_channels * 4, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(128, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: [B, C, H, W] or [B, H, W, C].
        """
        if x.ndim == 4 and x.shape[-1] in (1, 3, 4) and x.shape[1] not in (1, 3, 4):
            x = x.permute(0, 3, 1, 2)

        out = self.prep(x)
        out = self.stage1_conv(out)
        out = self.stage1_res(out)
        out = self.stage2_conv(out)
        out = self.stage2_res(out)

        out = self.global_pool(out)
        out = torch.flatten(out, 1)
        logits = self.classifier(out)
        return logits

    def predict_probabilities(self, x: torch.Tensor) -> torch.Tensor:
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            return F.softmax(logits, dim=-1)

    def get_model_summary(self) -> Dict[str, Any]:
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {
            "model_name": "ConcreteDamageCNN2D",
            "in_channels": self.in_channels,
            "num_classes": self.num_classes,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params
        }
