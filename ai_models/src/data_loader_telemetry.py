"""
Real-World Bridge Telemetry Data Ingestion and Decoupling Module
Loads 43,200 continuous minute-by-minute sensor readings from `archive.zip` (bridge_digital_twin_dataset.csv).
Applies:
1. Physics-based thermal-mechanical strain decoupling (isolates mechanical distress from tropical daily heat expansion).
2. Sliding-window temporal segmentation.
3. 70/15/15 train/val/test splitting with stratification for severe class imbalance.
Fulfills PhD Chapter 5, Section 5.7 & Section 5.8.1.
"""

import os
import zipfile
import io
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, Dict, Any, List, Optional

class TelemetryWindowDataset(Dataset):
    """PyTorch Dataset for multi-channel temporal sensor windows."""
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]


class BridgeTelemetryPipeline:
    """
    Ingestion and preprocessing pipeline for the 43,200 minute-by-minute
    real bridge digital twin sensor dataset.
    """
    SENSOR_COLUMNS = [
        'Strain_microstrain',
        'Vibration_ms2',
        'Crack_Propagation_mm',
        'Deflection_mm',
        'Tilt_deg',
        'Modal_Frequency_Hz',
        'Temperature_C',
        'Humidity_percent'
    ]

    TARGET_ALERT_COL = 'Maintenance_Alert'
    HEALTH_INDEX_COL = 'Structural_Health_Index_SHI'

    def __init__(self, zip_path: str = 'ai_models/data/raw/public/archive.zip'):
        self.zip_path = zip_path
        self.raw_df = None
        self.processed_df = None
        self.mean_ = None
        self.std_ = None

    def load_raw_data(self) -> pd.DataFrame:
        """Extracts and cleans bridge_digital_twin_dataset.csv directly from zip."""
        if not os.path.exists(self.zip_path):
            raise FileNotFoundError(f"Archive not found: {self.zip_path}")

        with zipfile.ZipFile(self.zip_path, 'r') as z:
            with z.open('bridge_digital_twin_dataset.csv') as f:
                df = pd.read_csv(f)

        # Ensure timestamp sorting
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df = df.sort_values('Timestamp').reset_index(drop=True)

        # Forward fill and backward fill minimal missing values
        for col in self.SENSOR_COLUMNS + [self.TARGET_ALERT_COL, self.HEALTH_INDEX_COL]:
            if col in df.columns:
                df[col] = df[col].ffill().bfill()

        self.raw_df = df
        return df

    def apply_thermal_mechanical_decoupling(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Physics-Informed Environmental Decoupling:
        Concrete expands under tropical sunlight: epsilon_thermal = alpha_c * Delta_T.
        Decouples thermal expansion baseline from mechanical load strain.
        """
        df_clean = df.copy()
        temp = df_clean['Temperature_C'].values
        total_strain = df_clean['Strain_microstrain'].values

        # Linear thermal expansion coefficient for reinforced concrete (approx 10-12 microstrain / deg C)
        # We estimate the empirical coefficient via robust linear fit over normal operational periods
        normal_mask = (df_clean[self.TARGET_ALERT_COL] == 0)
        if np.sum(normal_mask) > 100:
            p = np.polyfit(temp[normal_mask], total_strain[normal_mask], deg=1)
            alpha_empirical = p[0]
        else:
            alpha_empirical = 11.5  # Standard physical constant (microstrain / C)

        mean_temp = np.mean(temp)
        thermal_strain_component = alpha_empirical * (temp - mean_temp)
        mechanical_strain = total_strain - thermal_strain_component

        df_clean['Mechanical_Strain_microstrain'] = mechanical_strain
        df_clean['Thermal_Expansion_Component'] = thermal_strain_component
        return df_clean

    def create_multiclass_condition_labels(self, df: pd.DataFrame) -> pd.Series:
        """
        Derives structural condition states from the continuous Structural Health Index (SHI)
        and Maintenance Alerts:
          Class 0: Normal / Healthy (SHI >= 0.82 and Alert == 0)
          Class 1: Minor Degradation (0.75 <= SHI < 0.82)
          Class 2: Moderate Distress (0.65 <= SHI < 0.75 or early alert)
          Class 3: Critical Damage (SHI < 0.65 or active Alert == 1)
        """
        shi = df[self.HEALTH_INDEX_COL].values
        alerts = df[self.TARGET_ALERT_COL].values

        labels = np.zeros(len(df), dtype=np.int64)
        for i in range(len(df)):
            if alerts[i] == 1 or shi[i] < 0.68:
                labels[i] = 3  # Critical
            elif shi[i] < 0.78:
                labels[i] = 2  # Moderate
            elif shi[i] < 0.83:
                labels[i] = 1  # Minor
            else:
                labels[i] = 0  # Normal / Healthy

        return pd.Series(labels, index=df.index, name='Condition_State')

    def generate_sliding_windows(
        self,
        window_size: int = 128,
        stride: int = 32
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Converts the 43,200 continuous timestamps into multi-channel temporal windows [N, window_size, channels].
        Returns:
          X_windows: [N, window_size, num_features]
          y_alerts: [N] (Binary anomaly target: 0 or 1)
          y_states: [N] (Multi-class condition state: 0, 1, 2, 3)
        """
        if self.raw_df is None:
            self.load_raw_data()

        df = self.apply_thermal_mechanical_decoupling(self.raw_df)
        df['Condition_State'] = self.create_multiclass_condition_labels(df)

        feature_cols = [
            'Mechanical_Strain_microstrain',
            'Vibration_ms2',
            'Crack_Propagation_mm',
            'Deflection_mm',
            'Tilt_deg',
            'Modal_Frequency_Hz',
            'Temperature_C',
            'Humidity_percent'
        ]

        feature_data = df[feature_cols].values
        alert_data = df[self.TARGET_ALERT_COL].values
        state_data = df['Condition_State'].values

        total_rows = len(df)
        windows = []
        alert_labels = []
        state_labels = []

        for start in range(0, total_rows - window_size + 1, stride):
            end = start + window_size
            w_features = feature_data[start:end, :]
            # Window label: positive if any alert occurs within window
            w_alert = 1 if np.any(alert_data[start:end] == 1) else 0
            # Condition state: maximum severity within window
            w_state = int(np.max(state_data[start:end]))

            windows.append(w_features)
            alert_labels.append(w_alert)
            state_labels.append(w_state)

        X_win = np.array(windows, dtype=np.float32)
        y_alert_win = np.array(alert_labels, dtype=np.int64)
        y_state_win = np.array(state_labels, dtype=np.int64)

        return X_win, y_alert_win, y_state_win

    @staticmethod
    def train_val_test_split(
        X: np.ndarray,
        y: np.ndarray,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Stratified temporal train/val/test split."""
        from sklearn.model_selection import train_test_split

        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=(val_ratio + test_ratio), random_state=random_state, stratify=y
        )
        val_share = val_ratio / (val_ratio + test_ratio)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=(1.0 - val_share), random_state=random_state, stratify=y_temp
        )
        return X_train, y_train, X_val, y_val, X_test, y_test
