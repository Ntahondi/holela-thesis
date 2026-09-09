"""
SMMS Preprocessor Module
Responsible for signal filtering, windowing, standardization, and feature extraction
for Concrete Infrastructure Structural Health Monitoring (SHM).
Aligned with PhD Chapter 5, Section 5.8.1 & 5.8.2.
"""

import numpy as np
from scipy import signal
from typing import Tuple, Dict, Any, Optional

class SHMPreprocessor:
    """
    Signal processing and feature engineering pipeline for structural health monitoring.
    Handles vibration, dynamic strain, crack displacement, and environmental telemetry.
    """
    def __init__(self, sampling_rate: float = 100.0, filter_low: float = 0.5, filter_high: float = 40.0):
        self.sampling_rate = sampling_rate
        self.filter_low = filter_low
        self.filter_high = filter_high
        self.mean_ = None
        self.std_ = None

    def butter_bandpass_filter(self, data: np.ndarray, order: int = 4) -> np.ndarray:
        """
        Applies a zero-phase Butterworth bandpass filter to remove sensor DC offset
        and high-frequency electronic noise.
        """
        nyq = 0.5 * self.sampling_rate
        low = self.filter_low / nyq
        high = min(self.filter_high / nyq, 0.99)
        b, a = signal.butter(order, [low, high], btype='band')
        
        # If multi-channel [samples, channels]
        if data.ndim == 1:
            return signal.filtfilt(b, a, data)
        elif data.ndim == 2:
            filtered = np.zeros_like(data)
            for ch in range(data.shape[1]):
                filtered[:, ch] = signal.filtfilt(b, a, data[:, ch])
            return filtered
        elif data.ndim == 3: # [batch, time, channels]
            filtered = np.zeros_like(data)
            for b_idx in range(data.shape[0]):
                for ch in range(data.shape[2]):
                    filtered[b_idx, :, ch] = signal.filtfilt(b, a, data[b_idx, :, ch])
            return filtered
        return data

    def fit_normalizer(self, X: np.ndarray):
        """Calculates mean and standard deviation for Z-score normalization."""
        self.mean_ = np.mean(X, axis=(0, 1), keepdims=True)
        self.std_ = np.std(X, axis=(0, 1), keepdims=True)
        self.std_[self.std_ == 0] = 1.0  # Prevent division by zero

    def transform_normalizer(self, X: np.ndarray) -> np.ndarray:
        """Applies Z-score normalization using fitted statistics."""
        if self.mean_ is None or self.std_ is None:
            raise ValueError("Normalizer must be fitted before transforming.")
        return (X - self.mean_) / self.std_

    def fit_transform_normalizer(self, X: np.ndarray) -> np.ndarray:
        self.fit_normalizer(X)
        return self.transform_normalizer(X)

    @staticmethod
    def create_sliding_windows(
        data: np.ndarray, 
        labels: Optional[np.ndarray] = None, 
        window_size: int = 256, 
        stride: int = 128
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Segments continuous sensor telemetry into overlapping time-series windows [N, window_size, channels].
        """
        num_samples = data.shape[0]
        num_channels = data.shape[1] if data.ndim > 1 else 1
        data_2d = data.reshape(-1, num_channels)

        windows = []
        window_labels = []

        for start in range(0, num_samples - window_size + 1, stride):
            end = start + window_size
            window = data_2d[start:end, :]
            windows.append(window)

            if labels is not None:
                # Assign majority class label in window
                w_labels = labels[start:end]
                unique, counts = np.unique(w_labels, return_counts=True)
                window_labels.append(unique[np.argmax(counts)])

        X_win = np.array(windows, dtype=np.float32)
        y_win = np.array(window_labels, dtype=np.int64) if labels is not None else None
        return X_win, y_win

    @staticmethod
    def extract_statistical_features(windows: np.ndarray) -> np.ndarray:
        """
        Extracts engineered time-domain and frequency-domain statistical features
        for benchmark classical ML algorithms (SVM, Random Forest).
        Returns feature vector per window: [N, num_features].
        """
        N, T, C = windows.shape
        features_list = []

        for i in range(N):
            win_features = []
            for ch in range(C):
                sig = windows[i, :, ch]
                
                # Time domain features
                mean_val = np.mean(sig)
                std_val = np.std(sig)
                var_val = np.var(sig)
                rms_val = np.sqrt(np.mean(sig ** 2))
                peak_val = np.max(np.abs(sig))
                p2p_val = np.ptp(sig)
                crest_factor = peak_val / (rms_val + 1e-8)
                
                # Skewness and Kurtosis
                centered = sig - mean_val
                skewness = np.mean(centered ** 3) / ((std_val ** 3) + 1e-8)
                kurtosis = np.mean(centered ** 4) / ((std_val ** 4) + 1e-8)
                
                # Frequency domain features via FFT
                fft_vals = np.abs(np.fft.rfft(sig))
                spectral_energy = np.sum(fft_vals ** 2)
                dominant_freq_idx = np.argmax(fft_vals)

                win_features.extend([
                    mean_val, std_val, var_val, rms_val,
                    peak_val, p2p_val, crest_factor,
                    skewness, kurtosis, spectral_energy, dominant_freq_idx
                ])
            features_list.append(win_features)

        return np.array(features_list, dtype=np.float32)

    @staticmethod
    def compute_spectrogram(
        windows: np.ndarray, 
        fs: float = 100.0, 
        nperseg: int = 32
    ) -> np.ndarray:
        """
        Converts 1D multi-channel windows [N, T, C] to 2D time-frequency spectrograms
        [N, freq_bins, time_steps, C] for 2D-CNN visual representations.
        """
        N, T, C = windows.shape
        spectrograms = []

        for i in range(N):
            channel_specs = []
            for ch in range(C):
                _, _, Sxx = signal.spectrogram(windows[i, :, ch], fs=fs, nperseg=nperseg)
                # Convert to dB power scale
                Sxx_db = 10 * np.log10(Sxx + 1e-8)
                channel_specs.append(Sxx_db)
            # Stack channels: shape [freq_bins, time_steps, C]
            spec_stacked = np.stack(channel_specs, axis=-1)
            spectrograms.append(spec_stacked)

        return np.array(spectrograms, dtype=np.float32)
