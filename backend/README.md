# SMMS FastAPI Microservice

Backend analytical and decision-support microservice for the Smart Maintenance Management System (SMMS).

## Key Capabilities (Phase 2 Roadmap)
1. **IoT Telemetry Ingestion**: High-throughput REST & WebSocket endpoints for field sensors (strain, vibration, crack, climate).
2. **AI Inference Service**: Hosts the trained CNN models (`ai_models/weights/`) for near real-time condition classification.
3. **Intelligent Decision Support System (IDSS)**: Automated prioritization of maintenance interventions based on TISM relationship weights and budget limits.
4. **Alert & Notification Engine**: Dispatches critical threshold warnings to TANROADS / TRC / TANESCO engineers.
