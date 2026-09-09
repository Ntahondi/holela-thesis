# Smart Maintenance Management System (SMMS) - Tanzania

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Client-Flutter-blue.svg)](https://flutter.dev/)

Computational and empirical implementation of the doctoral thesis:
> **"Framework for Smart Maintenance Management System (SMMS) for Sustainability of Infrastructure Development in Tanzania"**  
> Candidate: **Paul Zablon Holela** (2019-07-09982)  
> Supervisor: **Prof. John Makunza**, Department of Structural and Construction Engineering, CoET, University of Dar es Salaam (UDSM)

---

## Quick Navigation

* **[Blueprint (`blueprint.md`)](file:///d:/Projects/holela/blueprint.md)**: Full-stack system architecture, thesis alignment, and roadmap.
* **[Doctoral Mapping Guide (`docs/thesis_mapping.md`)](file:///d:/Projects/holela/docs/thesis_mapping.md)**: Direct mapping between source code and thesis chapters, objectives, and research questions.
* **[AI Models (`ai_models/`)](file:///d:/Projects/holela/ai_models/)**: Primary focus (Phase 1) — CNN deep learning models, baselines (SVM, RF, LSTM), noise robustness simulation, and evaluation.
* **[FastAPI Backend (`backend/`)](file:///d:/Projects/holela/backend/)**: Phase 2 — REST API endpoints for telemetry ingestion, model inference, and IDSS decision engine.
* **[Flutter Client (`client/`)](file:///d:/Projects/holela/client/)**: Phase 3 — Cross-platform field technician and manager interface.

---

## Current Focus: Phase 1 (AI Models)

To install dependencies and start working on the models:
```powershell
# Activate Python 3.12 virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r ai_models/requirements.txt
```
