"""
Long Short-Term Memory (LSTM) Baseline Model
Recurrent benchmark model for structural condition state degradation tracking.
Fulfills PhD Chapter 5, Section 5.9.4 benchmark comparison.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any

class ConcreteSHMLSTM(nn.Module):
    """
    2-Layer Bidirectional LSTM for sequential condition classification.
    Input shape: [Batch, TimeSteps, Channels]
    """
    def __init__(
        self,
        in_channels: int = 4,
        hidden_dim: int = 64,
        num_layers: int = 2,
        num_classes: int = 4,
        dropout_rate: float = 0.3,
        bidirectional: bool = True
    ):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.bidirectional = bidirectional

        self.lstm = nn.LSTM(
            input_size=in_channels,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0.0,
            bidirectional=bidirectional
        )

        num_directions = 2 if bidirectional else 1
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * num_directions, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(64, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: [B, T, C] or [B, C, T]. If [B, C, T], transpose to [B, T, C].
        """
        if x.ndim == 3 and x.shape[1] < x.shape[2]:
            x = x.permute(0, 2, 1)

        lstm_out, (hn, cn) = self.lstm(x)  # lstm_out: [B, T, hidden_dim * num_directions]
        
        # Aggregate temporal representation using attention or mean pooling
        temporal_repr = torch.mean(lstm_out, dim=1)  # [B, hidden_dim * num_directions]
        logits = self.classifier(temporal_repr)
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
            "model_name": "ConcreteSHMLSTM",
            "in_channels": self.in_channels,
            "hidden_dim": self.hidden_dim,
            "num_classes": self.num_classes,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params
        }
