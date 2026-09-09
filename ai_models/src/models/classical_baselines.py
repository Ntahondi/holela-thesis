"""
Classical Machine Learning Baselines (SVM and Random Forest)
Evaluates statistical feature representations of concrete SHM telemetry.
Fulfills PhD Chapter 5, Section 5.9.4 benchmark comparison.
"""

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Any
import numpy as np
import joblib

class SVMBaseline:
    """
    Support Vector Machine (SVM) Classifier baseline with Radial Basis Function (RBF) kernel.
    Trained on statistical features (time & frequency domain).
    """
    def __init__(self, C: float = 1.0, kernel: str = 'rbf', probability: bool = True):
        self.model = SVC(C=C, kernel=kernel, probability=probability, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def save(self, filepath: str):
        joblib.dump(self.model, filepath)

    def load(self, filepath: str):
        self.model = joblib.load(filepath)


class RandomForestBaseline:
    """
    Random Forest Classifier baseline.
    Provides Gini importance rankings for SHM physical feature validation.
    """
    def __init__(self, n_estimators: int = 100, max_depth: int = 15):
        self.model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)

    def get_feature_importances(self) -> np.ndarray:
        return self.model.feature_importances_

    def save(self, filepath: str):
        joblib.dump(self.model, filepath)

    def load(self, filepath: str):
        self.model = joblib.load(filepath)
