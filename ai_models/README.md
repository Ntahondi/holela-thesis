# Smart Maintenance Management System (SMMS) - AI & Deep Learning Core

This sub-project implements the artificial intelligence and predictive modeling components for:
**"Framework for Smart Maintenance Management System (SMMS) for Sustainability of Infrastructure Development in Tanzania"**  
Author: Paul Zablon Holela (PhD Candidate, UDSM)

---

## Architecture & Modules

* **`data/`**: Storage for raw public benchmarks, local Tanzanian sensor logs, processed features, and noise-injected test splits.
* **`src/models/`**:
  * `cnn_1d.py`: 1D-CNN for multi-sensor time-series telemetry (strain, vibration, crack displacement).
  * `cnn_2d.py`: 2D-CNN for concrete surface crack image classification.
  * `lstm_baseline.py`: Sequential recurrent LSTM baseline.
  * `classical_baselines.py`: Support Vector Machine (SVM) and Random Forest (RF) benchmarks.
* **`src/preprocessor.py`**: Filtering (Butterworth), signal windowing, normalization, and FFT/spectrogram feature generation.
* **`src/train.py`**: Standardized training script with validation early stopping and model checkpointing.
* **`src/evaluate.py`**: Evaluation metrics generator (Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix).
* **`src/noise_simulator.py`**: Empirical robustness testing under field conditions (packet loss, sensor drift, white noise) fulfilling Section 5.9.5.
* **`src/idss_decision_logic.py`**: Rule-based & parameter-ranked decision engine mapping sensor alerts to maintenance actions (Section 5.10.3).
* **`reports/`**: Figures and LaTeX/CSV tables ready for direct insertion into Chapter 5 of the thesis.

---

## Virtual Environment & Setup

The project uses Python 3.12:
```bash
# In the root folder (d:\Projects\holela):
venv\Scripts\activate

# Install dependencies:
pip install -r ai_models/requirements.txt
```
