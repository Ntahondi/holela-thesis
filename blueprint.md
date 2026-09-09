# PROJECT BLUEPRINT: SMART MAINTENANCE MANAGEMENT SYSTEM (SMMS) FOR TANZANIA

**Author / PhD Candidate**: Paul Zablon Holela (2019-07-09982)  
**Supervisor**: Prof. John Makunza, Department of Structural and Construction Engineering, CoET, University of Dar es Salaam (UDSM)  
**Project Scope**: Full-stack implementation & research validation of the Smart Maintenance Management System (SMMS) incorporating Deep Learning Condition Monitoring, FastAPI Analytical Backend, and Cross-Platform Flutter Mobile/Web Client.

---

## 1. Executive Summary & Thesis Alignment

This project serves as the computational, empirical, and architectural realization of the doctoral thesis:
> **"Framework for Smart Maintenance Management System (SMMS) for Sustainability of Infrastructure Development in Tanzania"**

### Alignment with Thesis Objectives & Contributions
* **Objective (b)**: Establish key SMMS parameters via systematic review and Delphi validation.
* **Objective (c)**: Identify IoT sensor parameters and develop a validated **Convolutional Neural Network (CNN)** predictive maintenance model for concrete infrastructure.
* **Objective (d)**: Establish intelligent decision-making logic from sensor trigger to maintenance resource allocation.
* **Objective (e)**: Develop and validate the generic 3-Layer SMMS Framework (**Field Layer**, **Platform Layer**, **Decision Layer**).
* **Key Research Contributions (Chapter 7)**:
  * **Contribution 5**: Open-source CNN predictive maintenance model for concrete structures in tropical conditions.
  * **Contribution 6**: IoT network readiness evidence base for Tanzanian transport and civil infrastructure corridors.
  * **Contribution 1 & 4**: Validated SMMS framework combining Total Interpretive Structural Modelling (TISM) and Design Science Research (DSR).

---

## 2. Global System Architecture

The project integrates three tightly coupled tiers that map directly to the thesis three-layer framework:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           SMMS COMPLETE END-TO-END STACK                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

   ┌───────────────────────────────────────────────────────────────────────────────────┐
   │                                  CLIENT LAYER                                     │
   │                              [Flutter Mobile / Web]                               │
   │  • Field Engineer Inspection & Work Orders        • Real-Time SHM Telemetry Dash  │
   │  • GIS Infrastructure Map (TANROADS/TRC/TANESCO)  • IDSS Maintenance Approvals    │
   └───────────────────────────────────────────────────────────────────────────────────┘
                                            ▲
                                            │ HTTP / WebSocket (REST & Real-Time)
                                            ▼
   ┌───────────────────────────────────────────────────────────────────────────────────┐
   │                                 BACKEND LAYER                                     │
   │                             [FastAPI Microservice]                                │
   │  • Ingestion & IoT Data Normalization             • Anomaly Trigger & Alert System│
   │  • IDSS Decision Engine & Priority Scoring        • PostgreSQL / TimeSeries DB    │
   └───────────────────────────────────────────────────────────────────────────────────┘
                                            ▲
                                            │ Model Inference Pipeline (.keras / .onnx)
                                            ▼
   ┌───────────────────────────────────────────────────────────────────────────────────┐
   │                          AI & PREDICTIVE ANALYTICS ENGINE                         │
   │                            [Python 3.12 Deep Learning]                            │
   │  • 1D-CNN Telemetry Model (Vibration, Strain, Crack Displacement)                 │
   │  • 2D-CNN Visual Concrete Damage Classifier (Surface Cracks, Spalling)            │
   │  • Benchmark Comparison Suite: SVM, Random Forest, LSTM                           │
   │  • Tropical Noise & Packet-Loss Robustness Simulator                              │
   └───────────────────────────────────────────────────────────────────────────────────┘
                                            ▲
                                            │ Ingests Datasets & Telemetry
                                            ▼
   ┌───────────────────────────────────────────────────────────────────────────────────┐
   │                                   DATA LAYER                                      │
   │  • Public Benchmarks: SDNET2018, Mendeley Crack, Z24 Bridge, LANL SHM             │
   │  • Local Field Data: Tanzanian concrete assets (DSM, Dodoma, Arusha, Mwanza)      │
   └───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Directory Structure

```text
holela/
├── PhD_Thesis_Framework_SMMS_Tanzania_Holela.docx  # Master PhD thesis blueprint
├── blueprint.md                                     # This comprehensive project plan
├── README.md                                        # Master repository entrypoint
│
├── ai_models/                                       # [PHASE 1 FOCUS] AI & Deep Learning Core
│   ├── data/
│   │   ├── raw/
│   │   │   ├── public/                              # Public SHM datasets (SDNET2018, Z24, LANL)
│   │   │   └── local_telemetry/                     # Tanzanian sensor logs & pilot telemetry
│   │   ├── processed/                               # Scaled, windowed, harmonized arrays
│   │   └── synthetic_noise/                         # Corrupted datasets (packet loss, drift)
│   ├── notebooks/                                   # Interactive research & visualization
│   │   ├── 01_eda_and_preprocessing.ipynb
│   │   ├── 02_cnn_model_training.ipynb
│   │   ├── 03_benchmarks_svm_rf_lstm.ipynb
│   │   └── 04_noise_robustness_evaluation.ipynb
│   ├── src/
│   │   ├── __init__.py
│   │   ├── data_loader.py                           # Dataset ingestion, balancing, splits
│   │   ├── preprocessor.py                          # Butterworth filters, FFT, STFT, scaling
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── cnn_1d.py                            # 1D-CNN for sensor telemetry
│   │   │   ├── cnn_2d.py                            # 2D-CNN for visual crack classification
│   │   │   ├── lstm_baseline.py                     # Recurrent baseline model
│   │   │   └── classical_baselines.py               # SVM and Random Forest baselines
│   │   ├── train.py                                 # Standardized training with checkpointing
│   │   ├── evaluate.py                              # Accuracy, F1, AUC-ROC, Confusion Matrix
│   │   ├── noise_simulator.py                       # Section 5.9.5 field noise degradation test
│   │   └── idss_decision_logic.py                   # Section 5.10.3 decision logic rules
│   ├── weights/                                     # Exported trained models (.keras, .pth, .joblib)
│   ├── reports/
│   │   ├── figures/                                 # Accuracy curves, ROC curves, loss plots
│   │   └── tables/                                  # LaTeX/CSV performance & benchmark tables
│   ├── requirements.txt
│   └── README.md
│
├── backend/                                         # [PHASE 2] FastAPI Analytical Microservice
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints_telemetry.py           # Ingestion of live IoT sensor packets
│   │   │       ├── endpoints_prediction.py          # On-demand AI damage state inference
│   │   │       ├── endpoints_alerts.py              # Anomaly alerts & notification dispatch
│   │   │       └── endpoints_decision.py            # IDSS maintenance priority ranking
│   │   ├── core/
│   │   │   ├── config.py                            # App settings, environment variables
│   │   │   └── security.py                          # Auth & API key security
│   │   ├── models/                                  # Database ORM models (Assets, Telemetry, Alerts)
│   │   ├── schemas/                                 # Pydantic schemas (Input/Output contracts)
│   │   ├── services/
│   │   │   ├── model_runner.py                      # Loaded AI model inference runner
│   │   │   └── idss_service.py                      # Priority scoring & work-order generator
│   │   └── main.py                                  # FastAPI application entrypoint
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── client/                                          # [PHASE 3] Flutter Cross-Platform Client
│   ├── lib/                                         # Flutter application codebase
│   │   ├── src/
│   │   │   ├── features/
│   │   │   │   ├── dashboard/                       # Real-time condition overview
│   │   │   │   ├── telemetry/                       # Sensor graphs (strain, vibration, crack)
│   │   │   │   ├── inspection/                      # Camera crack capture & AI inference
│   │   │   │   ├── idss_actions/                    # Prioritized maintenance work orders
│   │   │   │   └── asset_gis/                       # Map of monitored assets in Tanzania
│   │   │   ├── shared/                              # Themes, network client, widgets
│   │   │   └── app.dart
│   ├── pubspec.yaml
│   └── README.md
│
└── docs/                                            # Academic documentation & thesis extracts
    ├── thesis_mapping.md                            # Mapping code artifacts to thesis sections
    └── thesis_extracts/                             # Raw text extracts from the thesis .docx
```

---

## 4. Phase 1: Deep Learning Models Deep Dive (Current Priority)

### 4.1 Scope of the AI Modeling Task
The AI module satisfies **Chapter 5, Part B (Sections 5.6 – 5.9)**:
1. **Target Infrastructure**: Reinforced and prestressed concrete civil structures (bridges, culverts, building frames, road slabs).
2. **Monitored Physical Parameters**:
   * **Strain**: Microstrain variations under traffic/dead loads.
   * **Vibration**: Acceleration amplitudes, dynamic natural frequency shifts.
   * **Crack Width / Growth**: Direct displacement measurements or visual crack detection.
   * **Corrosion & Moisture**: Half-cell potential, relative humidity, temperature.
3. **Target Prediction Outcomes (Condition States)**:
   * Class 0: **Normal / Healthy** (no noticeable distress)
   * Class 1: **Minor Deterioration** (early micro-cracking, normal seasonal strain)
   * Class 2: **Moderate Distress** (accelerated crack expansion, stiffness reduction)
   * Class 3: **Critical / Severe Damage** (active failure risk, immediate intervention required)

### 4.2 Model Specifications

#### 1. 1D-CNN Telemetry Model (`src/models/cnn_1d.py`)
* **Input**: Multi-channel time series $[B, T, C]$ where $T = 256$ to $1024$ time steps, $C = 3$ to $6$ sensor channels.
* **Architecture**:
  * Conv1D(filters=32, kernel=7, padding='same') + BatchNorm + ReLU + MaxPool1D(2)
  * Conv1D(filters=64, kernel=5, padding='same') + BatchNorm + ReLU + MaxPool1D(2)
  * Conv1D(filters=128, kernel=3, padding='same') + BatchNorm + ReLU + GlobalAvgPool1D
  * Dense(64, ReLU) + Dropout(0.3)
  * Dense(4, Softmax) for multi-class condition state.

#### 2. 2D-CNN Visual Inspection Model (`src/models/cnn_2d.py`)
* **Input**: $[B, 224, 224, 3]$ RGB images of concrete surfaces.
* **Architecture**: Custom lightweight CNN / MobileNetV3 backbone fine-tuned for edge inference, outputting crack presence and severity rating.

#### 3. Benchmark Baseline Models (`src/models/classical_baselines.py` & `lstm_baseline.py`)
* **SVM Baseline**: RBF kernel operating on statistical feature vectors (Mean, Variance, Skewness, Kurtosis, RMS, Peak-to-Peak, Peak Frequency).
* **Random Forest Baseline**: 100 estimators, providing Gini feature importance rankings to validate which physical parameters contribute most to damage detection.
* **LSTM Baseline**: 2-layer Bidirectional LSTM (units=64) with Dropout(0.3) for sequential condition tracking.

### 4.3 Data Sourcing & Integration Strategy
* **Data Provenance & Citations**: Fully documented in [`docs/dataset_citations.md`](file:///d:/Projects/holela/docs/dataset_citations.md) with APA 7th and BibTeX entries for:
  1. **Sarmadi & Daneshvar (2022)**: Cable-Stayed Bridge Modal Analysis Telemetry (`2xnn95rpb5-1.zip`).
  2. **Sjölander et al. (2023)**: Cracked Reinforced Concrete DIC & BIM Models (`Monitoring of structural performance...zip`).
  3. **Bridge Digital Twin Telemetry**: 43,200 continuous multi-sensor timestamps (`archive.zip`).
  4. **Benz & Rodehorst (2022)**: S2DS Concrete Structural Defects (743 pairs, 7 classes) (`s2ds.zip`).
  5. **Multi-Feature Background Concrete Damage**: 2,750 annotated concrete images (`Damage Detection...zip`).
* **Step 1 (Harmonization)**: Standardize sampling rates, apply Butterworth bandpass filters, scale to zero-mean unit-variance.
* **Step 2 (Multi-Modal Architecture)**:
  - 1D-CNN + LSTM + SVM + RF on continuous bridge sensor telemetry.
  - 2D-CNN on visual concrete surface damage images.
* **Step 3 (Field Robustness / Tropical Noise Simulation - Section 5.9.5)**:
  - Inject white Gaussian noise at decreasing Signal-to-Noise Ratios (SNR: 30 dB down to 5 dB).
  - Simulate transmission dropouts: 5%, 10%, 20% random packet drop to mimic Tanzanian 2G/3G/4G rural corridor limitations.
  - Inject simulated thermal drift based on East African diurnal temperature shifts ($20^\circ\text{C} \to 38^\circ\text{C}$).
  - Plot accuracy degradation curves across all models.

---

## 5. Phase 2: FastAPI Microservice (Roadmap)

Once the models are trained, evaluated, and saved to `ai_models/weights/`, the backend wraps them into high-performance REST APIs:
* `POST /api/v1/telemetry/ingest`: Accepts sensor streams, stores them in database, and passes them to the 1D-CNN.
* `POST /api/v1/inspection/analyze-image`: Accepts camera photos from field engineers and returns crack classification & severity index.
* `GET /api/v1/alerts/active`: Returns anomalies exceeding structural safety thresholds.
* `POST /api/v1/decision/rank-actions`: Evaluates sensor triggers against TISM decision parameters and outputs prioritized maintenance work orders.

---

## 6. Phase 3: Flutter Cross-Platform Client (Roadmap)

The mobile and web client delivers the human-in-the-loop interface:
* **Field Engineer View**:
  * Bluetooth/Wi-Fi connection to IoT gateways.
  * Mobile camera crack scanning with real-time bounding box / severity alert.
  * Offline-first local SQLite cache for remote sites with no cellular connectivity.
* **Maintenance Manager / TANROADS Dashboard**:
  * GIS map displaying bridge and asset condition states across Tanzania.
  * Alert triage center and automated work order dispatch.
  * Cost-benefit priority list generated by the IDSS module.

---

## 7. Immediate Action Plan (Phase 1 Execution)

1. **AI Environment Initialization**:
   * Generate `ai_models/requirements.txt` with exact compatible versions.
   * Provide data download scripts for public SHM benchmarks.
2. **Implement Core Preprocessing & Models**:
   * Implement `data_loader.py` and `preprocessor.py`.
   * Implement `cnn_1d.py`, `cnn_2d.py`, `lstm_baseline.py`, and `classical_baselines.py`.
3. **Training & Benchmark Evaluation**:
   * Implement `train.py` and `evaluate.py`.
   * Produce thesis-ready outputs: training curves, confusion matrices, ROC curves, and benchmark comparison tables for Chapter 5.
4. **Noise Robustness Pipeline**:
   * Implement `noise_simulator.py` to satisfy Section 5.9.5.
