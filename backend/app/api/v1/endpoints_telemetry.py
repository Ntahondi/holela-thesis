"""
Telemetry Ingestion & Inference API Endpoints
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from schemas.telemetry import TelemetryBatchInput, TelemetryInferenceResponse, ConditionStateOutput
from services.model_runner import ModelRunnerService

router = APIRouter()

@router.post("/ingest", response_model=TelemetryInferenceResponse, summary="Ingest IoT sensor stream and predict structural condition")
def ingest_telemetry(payload: TelemetryBatchInput):
    """
    Ingests live or batch IoT sensor telemetry from a monitored civil asset.
    Applies physics-based thermal-mechanical decoupling and evaluates
    condition state via 1D-CNN with Monte Carlo Dropout uncertainty estimation.
    """
    runner = ModelRunnerService.get_instance()
    readings_dict = [r.dict() for r in payload.readings]
    
    try:
        inference = runner.run_telemetry_inference(readings_dict, window_size=128)
        cond = ConditionStateOutput(
            class_index=inference["class_index"],
            condition_name=inference["condition_name"],
            confidence_pct=inference["confidence_pct"],
            confidence_interval_95=inference["confidence_interval_95"],
            probabilities=inference["probabilities"],
            anomaly_detected=inference["anomaly_detected"]
        )
        return TelemetryInferenceResponse(
            asset_id=payload.asset_id,
            num_readings_processed=len(payload.readings),
            condition_state=cond,
            mechanical_strain_isolated=inference["mechanical_strain_isolated"],
            thermal_expansion_offset=inference["thermal_expansion_offset"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sample-stream/{asset_id}", summary="Simulate sample live sensor telemetry packet")
def get_sample_telemetry(asset_id: str):
    """Generates a representative 16-timestep sensor packet for frontend testing."""
    return {
        "asset_id": asset_id,
        "readings": [
            {
                "timestamp": f"2026-09-09T23:{i:02d}:00",
                "strain_microstrain": 780.0 + (i * 12.5),
                "vibration_ms2": 1.25 + (0.15 * (i % 3)),
                "crack_propagation_mm": 0.015,
                "deflection_mm": 0.45,
                "tilt_deg": 0.03,
                "modal_frequency_hz": 1.88,
                "temperature_c": 28.5 + (0.2 * i),
                "humidity_percent": 65.0
            }
            for i in range(16)
        ]
    }

@router.websocket("/ws/{asset_id}")
async def websocket_telemetry_stream(websocket: WebSocket, asset_id: str):
    """
    WebSocket endpoint providing real-time sensor streams and live condition inference
    to connected clients (Flutter dashboard, monitoring command center).
    """
    await websocket.accept()
    runner = ModelRunnerService.get_instance()
    step = 0
    try:
        import asyncio
        import random
        while True:
            # Generate continuous simulated IoT reading for the asset
            step += 1
            now_iso = f"2026-09-09T23:{min(step, 59):02d}:00"
            reading = {
                "timestamp": now_iso,
                "strain_microstrain": 750.0 + random.uniform(-15.0, 25.0) + (step * 0.5),
                "vibration_ms2": 1.10 + random.uniform(-0.1, 0.3),
                "crack_propagation_mm": 0.012 + (step * 0.0005),
                "deflection_mm": 0.42 + random.uniform(-0.02, 0.05),
                "tilt_deg": 0.025,
                "modal_frequency_hz": max(1.5, 1.92 - (step * 0.002)),
                "temperature_c": 27.5 + random.uniform(-0.3, 0.6),
                "humidity_percent": 68.0
            }
            
            # Quick 1D-CNN condition inference on recent window
            sim_batch = [reading for _ in range(16)]
            inference = runner.run_telemetry_inference(sim_batch, window_size=128)
            
            packet = {
                "asset_id": asset_id,
                "sequence": step,
                "telemetry": reading,
                "condition_state": {
                    "class_index": inference["class_index"],
                    "condition_name": inference["condition_name"],
                    "confidence_pct": inference["confidence_pct"],
                    "confidence_interval_95": inference["confidence_interval_95"],
                    "anomaly_detected": inference["anomaly_detected"]
                },
                "isolated_mechanical_strain": inference["mechanical_strain_isolated"],
                "thermal_strain_offset": inference["thermal_expansion_offset"]
            }
            await websocket.send_json(packet)
            await asyncio.sleep(1.5)  # 1.5-second telemetry sampling interval
    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected from asset stream {asset_id}")
    except Exception as e:
        print(f"[WebSocket] Stream error for asset {asset_id}: {e}")

