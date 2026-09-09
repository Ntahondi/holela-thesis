"""
Model Evaluation and Thesis Reporting Module
Generates comprehensive quantitative metrics, confusion matrices, ROC curves,
and LaTeX/CSV benchmark comparison tables for Chapter 5 of the PhD thesis.
Fulfills PhD Chapter 5, Section 5.9 (5.9.1, 5.9.2, 5.9.3, 5.9.4, 5.9.5).
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, roc_curve, auc, classification_report
)
from typing import Dict, Any, List, Optional, Tuple

# Set academic plotting style
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'sans-serif',
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14
})

class SHMModelEvaluator:
    """Evaluation suite providing publication-ready metrics and visualizations."""
    
    CLASS_NAMES = [
        "Normal (Healthy)",
        "Minor Deterioration",
        "Moderate Distress",
        "Critical Damage"
    ]

    def __init__(self, output_fig_dir: str = "ai_models/reports/figures", output_tab_dir: str = "ai_models/reports/tables"):
        self.fig_dir = output_fig_dir
        self.tab_dir = output_tab_dir
        os.makedirs(self.fig_dir, exist_ok=True)
        os.makedirs(self.tab_dir, exist_ok=True)

    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, y_probs: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Calculates Accuracy, Precision, Recall, F1, and AUC-ROC."""
        acc = accuracy_score(y_true, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
        macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
        
        results = {
            "accuracy": round(float(acc), 4),
            "precision_weighted": round(float(prec), 4),
            "recall_weighted": round(float(rec), 4),
            "f1_weighted": round(float(f1), 4),
            "precision_macro": round(float(macro_prec), 4),
            "recall_macro": round(float(macro_rec), 4),
            "f1_macro": round(float(macro_f1), 4),
        }

        # Multi-class AUC-ROC calculation (One-vs-Rest)
        if y_probs is not None:
            num_classes = y_probs.shape[1]
            roc_aucs = []
            for i in range(num_classes):
                y_binary = (y_true == i).astype(int)
                if len(np.unique(y_binary)) > 1:
                    fpr, tpr, _ = roc_curve(y_binary, y_probs[:, i])
                    roc_aucs.append(auc(fpr, tpr))
            results["roc_auc_macro"] = round(float(np.mean(roc_aucs)), 4) if roc_aucs else 0.0

        return results

    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "CNN_1D") -> str:
        """Plots and saves normalized confusion matrix with high DPI for thesis."""
        cm = confusion_matrix(y_true, y_pred, normalize='true')
        fig, ax = plt.subplots(figsize=(7, 6))
        
        sns.heatmap(
            cm, annot=True, fmt='.2%', cmap='Blues',
            xticklabels=self.CLASS_NAMES, yticklabels=self.CLASS_NAMES,
            cbar=True, ax=ax
        )
        ax.set_title(f'Normalized Confusion Matrix - {model_name}\n(Concrete Infrastructure Condition States)', pad=12)
        ax.set_xlabel('Predicted Condition State', labelpad=10)
        ax.set_ylabel('True Condition State', labelpad=10)
        plt.xticks(rotation=25, ha='right')
        plt.tight_layout()

        filepath = os.path.join(self.fig_dir, f'confusion_matrix_{model_name.lower()}.png')
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_roc_curves(self, y_true: np.ndarray, y_probs: np.ndarray, model_name: str = "CNN_1D") -> str:
        """Plots and saves multi-class One-vs-Rest ROC curves."""
        num_classes = y_probs.shape[1]
        fig, ax = plt.subplots(figsize=(8, 6))

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for i in range(num_classes):
            y_binary = (y_true == i).astype(int)
            if len(np.unique(y_binary)) > 1:
                fpr, tpr, _ = roc_curve(y_binary, y_probs[:, i])
                roc_auc = auc(fpr, tpr)
                ax.plot(fpr, tpr, color=colors[i % len(colors)], lw=2,
                        label=f'{self.CLASS_NAMES[i]} (AUC = {roc_auc:.3f})')

        ax.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Random Chance (AUC = 0.500)')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate (1 - Specificity)')
        ax.set_ylabel('True Positive Rate (Sensitivity)')
        ax.set_title(f'Receiver Operating Characteristic (ROC) Curves - {model_name}', pad=12)
        ax.legend(loc="lower right", frameon=True)
        ax.grid(alpha=0.3)
        plt.tight_layout()

        filepath = os.path.join(self.fig_dir, f'roc_curves_{model_name.lower()}.png')
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_training_history(self, history: Dict[str, List[float]], model_name: str = "CNN_1D") -> str:
        """Plots training & validation Loss and Accuracy curves."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

        # Loss Curve
        epochs = range(1, len(history['train_loss']) + 1)
        ax1.plot(epochs, history['train_loss'], 'b-', lw=2, label='Training Loss')
        ax1.plot(epochs, history['val_loss'], 'r--', lw=2, label='Validation Loss')
        ax1.set_title(f'Training vs. Validation Loss ({model_name})')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Cross-Entropy Loss')
        ax1.legend(frameon=True)
        ax1.grid(alpha=0.3)

        # Accuracy Curve
        ax2.plot(epochs, history['train_acc'], 'b-', lw=2, label='Training Accuracy')
        ax2.plot(epochs, history['val_acc'], 'r--', lw=2, label='Validation Accuracy')
        ax2.set_title(f'Training vs. Validation Accuracy ({model_name})')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend(frameon=True)
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.fig_dir, f'training_curves_{model_name.lower()}.png')
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def plot_noise_degradation(self, degradation_results: Dict[str, Any], model_name: str = "CNN_1D") -> str:
        """Plots Section 5.9.5 noise and packet-loss degradation curves."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

        # SNR Degradation
        snr_data = degradation_results["snr_degradation"]
        snr_vals = [d["snr_db"] for d in snr_data]
        snr_accs = [d["accuracy"] * 100 for d in snr_data]
        snr_f1s = [d["f1_score"] * 100 for d in snr_data]

        ax1.plot(snr_vals, snr_accs, 'o-', color='#1f77b4', lw=2, label='Accuracy (%)')
        ax1.plot(snr_vals, snr_f1s, 's--', color='#ff7f0e', lw=2, label='Weighted F1-Score (%)')
        ax1.set_title(f'Performance vs. Additive Noise (SNR)\n({model_name})')
        ax1.set_xlabel('Signal-to-Noise Ratio (dB) [Higher = Cleaner]')
        ax1.set_ylabel('Performance (%)')
        ax1.invert_xaxis()  # Lower SNR on right represents worse noise
        ax1.legend(frameon=True)
        ax1.grid(alpha=0.3)

        # Packet Loss Degradation
        drop_data = degradation_results["packet_drop_degradation"]
        drop_rates = [d["drop_rate"] * 100 for d in drop_data]
        drop_accs = [d["accuracy"] * 100 for d in drop_data]
        drop_f1s = [d["f1_score"] * 100 for d in drop_data]

        ax2.plot(drop_rates, drop_accs, 'o-', color='#2ca02c', lw=2, label='Accuracy (%)')
        ax2.plot(drop_rates, drop_f1s, 's--', color='#d62728', lw=2, label='Weighted F1-Score (%)')
        ax2.set_title(f'Performance vs. Packet Loss (Network Dropout)\n({model_name})')
        ax2.set_xlabel('Simulated Cellular Packet Drop Rate (%)')
        ax2.set_ylabel('Performance (%)')
        ax2.legend(frameon=True)
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.fig_dir, f'noise_degradation_{model_name.lower()}.png')
        plt.savefig(filepath, dpi=300)
        plt.close()
        return filepath

    def export_benchmark_comparison(self, benchmark_dict: Dict[str, Dict[str, float]]) -> Tuple[str, str]:
        """
        Exports comparative benchmark table to CSV and LaTeX for direct insertion
        into Chapter 5, Section 5.9.4 of the PhD thesis.
        """
        df = pd.DataFrame.from_dict(benchmark_dict, orient='index')
        df.index.name = "Model Architecture"
        
        # Reorder columns
        cols = ["accuracy", "precision_weighted", "recall_weighted", "f1_weighted", "roc_auc_macro"]
        existing_cols = [c for c in cols if c in df.columns]
        df = df[existing_cols]

        csv_path = os.path.join(self.tab_dir, 'benchmark_comparison.csv')
        tex_path = os.path.join(self.tab_dir, 'benchmark_comparison.tex')

        df.to_csv(csv_path)
        
        # LaTeX table formatting
        latex_str = df.to_latex(
            caption="Comparison of Deep Learning and Baseline Machine Learning Models for Concrete Condition Assessment (Section 5.9.4)",
            label="tab:benchmark_models",
            float_format="%.4f"
        )
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_str)

        return csv_path, tex_path
