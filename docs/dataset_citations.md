# DATASET CITATIONS & DATA PROVENANCE RECORD

**PhD Thesis**: Framework for Smart Maintenance Management System (SMMS) for Sustainability of Infrastructure Development in Tanzania  
**Candidate**: Paul Zablon Holela (2019-07-09982)  
**Supervisor**: Prof. John Makunza, CoET, University of Dar es Salaam (UDSM)  
**Thesis Chapter**: Chapter 5, Section 5.7.1 (*Public Structural Health Monitoring Datasets Used*) & Chapter 2, Section 2.5

---

## 1. Time-Series Structural Health Monitoring Datasets

### Dataset 1: Structural Health Monitoring of a Cable-Stayed Bridge
* **Local Path**: `ai_models/data/raw/public/2xnn95rpb5-1.zip`
* **Content**: Dynamic modal vibration acceleration telemetry from a real cable-stayed bridge.
* **Role in Thesis**: Chapter 5, Section 5.7.1 & Section 5.8 (1D-CNN dynamic vibration and modal shift model).
* **APA 7th Citation**:
  > Sarmadi, H., & Daneshvar, M. H. (2022). *Structural health monitoring of a cable-stayed bridge* [Data set]. Mendeley Data, V1. https://doi.org/10.17632/2xnn95rpb5.1
* **BibTeX Entry**:
  ```bibtex
  @misc{sarmadi2022shm,
    author    = {Sarmadi, Hassan and Daneshvar, Mohammad Hassan},
    title     = {Structural Health Monitoring of A Cable-Stayed Bridge},
    year      = {2022},
    publisher = {Mendeley Data},
    version   = {V1},
    doi       = {10.17632/2xnn95rpb5.1}
  }
  ```

---

### Dataset 2: Structural Performance of Cracked Reinforced Concrete using DIC and CMfM
* **Local Path**: `ai_models/data/raw/public/Monitoring of structural performance of cracked reinforced concrete using DIC and CMfM.zip`
* **Content**: 3.06 GB of experimental load testing on full-scale reinforced concrete beams, high-precision Digital Image Correlation (DIC), continuous crack displacement measurements, load-deflection series, and Autodesk Revit (.rvt) BIM models.
* **Role in Thesis**: Chapter 5, Section 5.7.1, Section 5.8.2 (Crack propagation and strain response) & Chapter 6, Section 6.4.4 (BIM integration).
* **APA 7th Citation**:
  > Sjölander, A., Belloni, V., Peterson, V., & Ledin, J. (2023). *Monitoring of structural performance of cracked reinforced concrete using DIC and CMfM* [Data set]. Mendeley Data, V4. https://doi.org/10.17632/z3yc9z84tk.4
* **BibTeX Entry**:
  ```bibtex
  @misc{sjolander2023cracked,
    author    = {Sj{\"o}lander, Andreas and Belloni, Valeria and Peterson, Viktor and Ledin, Jonatan},
    title     = {Monitoring of structural performance of cracked reinforced concrete using DIC and CMfM},
    year      = {2023},
    publisher = {Mendeley Data},
    version   = {V4},
    doi       = {10.17632/z3yc9z84tk.4}
  }
  ```

---

### Dataset 3: Bridge Digital Twin Sensor Telemetry Dataset
* **Local Path**: `ai_models/data/raw/public/archive.zip` (`bridge_digital_twin_dataset.csv`)
* **Content**: 43,200 continuous minute-by-minute sensor readings measuring multi-axis dynamic strain ($\mu\epsilon$), vibration ($m/s^2$), crack propagation ($mm$), temperature ($^\circ C$), relative humidity ($\%$), structural health index (SHI), and maintenance alert classifications.
* **Role in Thesis**: Chapter 5, Part B (Sections 5.7, 5.8, 5.9) training 1D-CNN, LSTM, SVM, and Random Forest baselines; Section 5.10.3 sensor-to-action decision logic.

---

## 2. Visual Concrete Defect & Image Datasets

### Dataset 4: Structural Defects Dataset (S2DS)
* **Local Path**: `ai_models/data/raw/public/s2ds.zip`
* **Content**: 743 high-resolution (1024×1024) concrete surface image pairs with pixel-level segmentation masks covering 7 defect classes: crack, spalling, corrosion, efflorescence, vegetation, control point, and intact background.
* **Role in Thesis**: Chapter 5, Section 5.8 (2D-CNN visual condition assessment) and Chapter 6, Section 6.4.6 (Field technician camera crack classification).
* **APA 7th Citation**:
  > Benz, C., & Rodehorst, V. (2022). Image-based detection of structural defects using hierarchical multi-scale attention. In *DAGM German Conference on Pattern Recognition* (pp. 402–417). Springer, Cham. https://doi.org/10.1007/978-3-031-16788-1_25
* **BibTeX Entry**:
  ```bibtex
  @inproceedings{benz2022defects,
    author    = {Benz, Christian and Rodehorst, Volker},
    title     = {Image-based Detection of Structural Defects using Hierarchical Multi-Scale Attention},
    booktitle = {DAGM German Conference on Pattern Recognition},
    year      = {2022},
    pages     = {402--417},
    publisher = {Springer, Cham},
    doi       = {10.1007/978-3-031-16788-1_25}
  }
  ```

---

### Dataset 5: Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds
* **Local Path**: `ai_models/data/raw/public/Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds.zip`
* **Content**: 2,750 concrete surface images (416×416) with 2,750 Pascal VOC XML bounding-box annotations representing concrete cracks and structural damages captured in challenging environmental lighting, shadow occlusion, and background textures.
* **Role in Thesis**: Chapter 5, Section 5.8 & Section 5.9.5 (Real-world noise, uneven lighting, and shadow robustness testing).
