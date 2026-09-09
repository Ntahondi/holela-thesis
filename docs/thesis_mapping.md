# DOCTORAL THESIS TRACEABILITY & MAPPING GUIDE

This document maps every computational component and source file in the `holela` codebase directly to the corresponding Chapter, Section, Research Objective, and Research Question in:
**"Framework for Smart Maintenance Management System (SMMS) for Sustainability of Infrastructure Development in Tanzania"**  
Candidate: Paul Zablon Holela | Supervisor: Prof. John Makunza, UDSM

---

## 1. Chapter 5: Key SMMS Parameters, Decision-Making System, and Deep Learning Model

| Thesis Section | Title in Thesis | Responsible Source Code / Artifacts | Output Delivered |
| :--- | :--- | :--- | :--- |
| **5.6** | **IoT Sensor Selection for Concrete Infrastructure Monitoring** | `ai_models/src/preprocessor.py`<br>`ai_models/reports/tables/sensor_selection_table.csv` | Justified sensor selection specification table suited to Tanzania's concrete infrastructure. |
| **5.7** | **Data Collection for Model Training** | `ai_models/src/data_loader.py`<br>`ai_models/data/raw/public`<br>`ai_models/data/raw/local_telemetry` | Public SHM datasets + local Tanzanian sensor telemetry harmonized pipeline. |
| **5.8** | **CNN Model Architecture and Development** | `ai_models/src/models/cnn_1d.py`<br>`ai_models/src/models/cnn_2d.py`<br>`ai_models/src/train.py` | Python 3.12 Deep Learning CNN architectures with full hyperparameter definitions. |
| **5.9.1** | **Training and Validation Accuracy Curves** | `ai_models/src/evaluate.py`<br>`ai_models/reports/figures/training_validation_curves.png` | Loss and Accuracy convergence curves across epochs. |
| **5.9.2** | **Confusion Matrix and Classification Report** | `ai_models/src/evaluate.py`<br>`ai_models/reports/figures/confusion_matrix.png` | Multi-class damage state classification report (Precision, Recall, F1). |
| **5.9.3** | **AUC-ROC Results** | `ai_models/src/evaluate.py`<br>`ai_models/reports/figures/roc_curves.png` | Receiver Operating Characteristic (ROC) curves per damage state. |
| **5.9.4** | **Comparison with Benchmark Models** | `ai_models/src/models/classical_baselines.py`<br>`ai_models/src/models/lstm_baseline.py`<br>`ai_models/reports/tables/benchmark_comparison.csv` | Empirical comparison against SVM, Random Forest, and LSTM baselines. |
| **5.9.5** | **Model Performance under Real-World Noise Conditions** | `ai_models/src/noise_simulator.py`<br>`ai_models/reports/figures/noise_degradation_curves.png` | Robustness evaluation under packet dropouts and tropical sensor thermal drift. |
| **5.10.3**| **Decision Logic: From Sensor Data to Maintenance Action**| `ai_models/src/idss_decision_logic.py`<br>`backend/app/services/idss_service.py` | Anomaly detection ➔ severity ➔ priority ranking ➔ resource allocation chain. |
| **5.11 & 5.12**| **ISM and TISM Structural Relationship Models** | `docs/tism_matrices.xlsx`<br>`ai_models/reports/figures/tism_digraph.png` | SSIM, Reachability Matrix, Partition Levels, and MICMAC drive-dependence plot. |

---

## 2. Chapter 6: SMMS Framework Development & Validation

| Thesis Section | Title in Thesis | Responsible Source Code / Artifacts | Output Delivered |
| :--- | :--- | :--- | :--- |
| **6.4** | **Layer 1: Field Layer (IoT Condition Monitoring)** | `client/lib/src/features/telemetry/`<br>`backend/app/api/v1/endpoints_telemetry.py` | Sensor acquisition, gateway connectivity, and local field technician interface. |
| **6.5** | **Layer 2: Platform Layer (Data Management & AI)** | `backend/app/services/model_runner.py`<br>`backend/app/api/v1/endpoints_prediction.py` | Big Data ingestion, CNN inference runtime, and anomaly alert dispatching. |
| **6.6** | **Layer 3: Decision Layer (IDSS)** | `backend/app/api/v1/endpoints_decision.py`<br>`client/lib/src/features/idss_actions/` | Maintenance Priority Scoring Model and resource allocation optimization. |
| **6.8** | **Framework Demonstration** | `client/` + `backend/` full integration | Live demonstration of end-to-end framework on a selected Tanzanian case study asset. |
| **6.9** | **Framework Validation** | `docs/validation_workshop/` | Expert validation workshop evaluation instruments and quantitative scoring data. |

---

## 3. Chapter 7: Research Contributions

| Contribution | Type | Realized by |
| :--- | :--- | :--- |
| **Contribution 1** | Theoretical | First validated 3-Layer SMMS framework for Sub-Saharan Africa (`blueprint.md` & Chapter 6). |
| **Contribution 4** | Methodological | Demonstration of combined TISM + DSR methodology (`docs/tism_matrices.xlsx`). |
| **Contribution 5** | Technical / Practical | Open-source CNN predictive maintenance model for concrete structures in tropical conditions (`ai_models/`). |
| **Contribution 6** | Empirical | IoT network readiness evidence base for Tanzania (`backend/` & Chapter 4/6). |
