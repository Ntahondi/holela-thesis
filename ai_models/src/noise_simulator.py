"""
Real-World Noise and Telemetry Corruption Simulator
Simulates field operating conditions in Tanzania:
1. Signal-to-Noise Ratio (SNR) degradation (ambient & electronic noise).
2. Packet loss and data dropouts (intermittent rural cellular 2G/3G/4G connectivity).
3. Tropical thermal sensor drift (high humidity & diurnal temperature fluctuations).
Directly satisfies PhD Chapter 5, Section 5.9.5.
"""

import numpy as np
import torch
from typing import Dict, Any, List, Tuple

class FieldNoiseSimulator:
    """
    Applies controlled corruptions to SHM telemetry to assess model robustness.
    """
    @staticmethod
    def add_gaussian_noise_snr(X: np.ndarray, snr_db: float) -> np.ndarray:
        """
        Adds Additive White Gaussian Noise (AWGN) to achieve a target SNR in dB.
        SNR_dB = 10 * log10(P_signal / P_noise)
        """
        X_noisy = np.zeros_like(X)
        N, T, C = X.shape

        for i in range(N):
            for ch in range(C):
                signal = X[i, :, ch]
                signal_power = np.mean(signal ** 2)
                if signal_power == 0:
                    X_noisy[i, :, ch] = signal
                    continue
                snr_linear = 10 ** (snr_db / 10.0)
                noise_power = signal_power / snr_linear
                noise = np.random.normal(0, np.sqrt(noise_power), size=T)
                X_noisy[i, :, ch] = signal + noise

        return X_noisy.astype(np.float32)

    @staticmethod
    def simulate_packet_loss(X: np.ndarray, drop_rate: float = 0.10, max_burst_len: int = 16) -> np.ndarray:
        """
        Simulates telecommunications packet dropouts common in developing country corridors.
        Random consecutive time steps are zeroed or held constant.
        drop_rate: fraction of data dropped (e.g. 0.05 to 0.25).
        """
        X_corrupt = X.copy()
        N, T, C = X.shape
        num_drops = int(T * drop_rate)

        for i in range(N):
            dropped = 0
            while dropped < num_drops:
                burst = min(np.random.randint(1, max_burst_len), num_drops - dropped)
                start = np.random.randint(0, max(1, T - burst))
                # Dropout across all channels in that packet time slot
                X_corrupt[i, start:start+burst, :] = 0.0
                dropped += burst

        return X_corrupt.astype(np.float32)

    @staticmethod
    def simulate_tropical_thermal_drift(X: np.ndarray, drift_magnitude: float = 0.15) -> np.ndarray:
        """
        Simulates nonlinear thermal sensor drift caused by tropical heat/humidity cycles.
        Adds low-frequency polynomial/sinusoidal baseline wandering.
        """
        X_drift = X.copy()
        N, T, C = X.shape
        t = np.linspace(0, 1, T)

        for i in range(N):
            drift = drift_magnitude * (np.sin(2 * np.pi * t) + 0.5 * (t ** 2))
            for ch in range(C):
                # Apply baseline drift (most prominent on strain and crack displacement)
                if ch in [2, 3]:
                    X_drift[i, :, ch] += drift * np.std(X[i, :, ch])

        return X_drift.astype(np.float32)

    @classmethod
    def evaluate_model_under_noise_sweep(
        cls,
        model: torch.nn.Module,
        X_test: np.ndarray,
        y_test: np.ndarray,
        snr_levels: List[float] = [30.0, 20.0, 15.0, 10.0, 5.0],
        packet_drop_rates: List[float] = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25],
        device: str = 'cpu'
    ) -> Dict[str, Any]:
        """
        Runs comprehensive noise sensitivity testing across SNR and packet dropout sweeps.
        Returns accuracy and F1 degradation matrices.
        """
        from sklearn.metrics import accuracy_score, f1_score

        model.eval()
        model.to(device)

        snr_results = []
        for snr in snr_levels:
            X_noisy = cls.add_gaussian_noise_snr(X_test, snr_db=snr)
            with torch.no_grad():
                tensor_x = torch.tensor(X_noisy).to(device)
                logits = model(tensor_x)
                preds = torch.argmax(logits, dim=-1).cpu().numpy()
            
            acc = accuracy_score(y_test, preds)
            f1 = f1_score(y_test, preds, average='weighted')
            snr_results.append({"snr_db": snr, "accuracy": acc, "f1_score": f1})

        drop_results = []
        for rate in packet_drop_rates:
            X_dropped = cls.simulate_packet_loss(X_test, drop_rate=rate)
            with torch.no_grad():
                tensor_x = torch.tensor(X_dropped).to(device)
                logits = model(tensor_x)
                preds = torch.argmax(logits, dim=-1).cpu().numpy()

            acc = accuracy_score(y_test, preds)
            f1 = f1_score(y_test, preds, average='weighted')
            drop_results.append({"drop_rate": rate, "accuracy": acc, "f1_score": f1})

        return {
            "snr_degradation": snr_results,
            "packet_drop_degradation": drop_results
        }
