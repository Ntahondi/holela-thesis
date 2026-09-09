"""
Integration Test Suite for SMMS FastAPI Backend
Tests all API endpoints end-to-end against loaded AI weights.
"""

import os
import sys
from fastapi.testclient import TestClient

# Ensure backend/app is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
APP_DIR = os.path.join(BASE_DIR, "backend/app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from main import app

client = TestClient(app)

def test_root_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Smart Maintenance Management System" in data["system"]
    print("\n[PASS] Root health-check endpoint functional.")

def test_assets_endpoint():
    response = client.get("/api/v1/assets/")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) >= 5
    asset_names = [a["name"] for a in assets]
    assert "Tanzanite Bridge" in asset_names
    assert "Kigamboni Bridge (Nyerere Bridge)" in asset_names
    print(f"[PASS] Assets endpoint returned {len(assets)} monitored Tanzanian assets.")

def test_telemetry_ingest_and_uncertainty():
    # Fetch sample stream first
    sample_res = client.get("/api/v1/telemetry/sample-stream/TZ-TANROADS-BR-004")
    assert sample_res.status_code == 200
    payload = sample_res.json()

    # Post to ingest
    ingest_res = client.post("/api/v1/telemetry/ingest", json=payload)
    assert ingest_res.status_code == 200
    result = ingest_res.json()
    
    assert "condition_state" in result
    assert result["condition_state"]["class_index"] in [0, 1, 2, 3]
    assert "confidence_interval_95" in result["condition_state"]
    assert "mechanical_strain_isolated" in result
    print(f"[PASS] 1D-CNN Telemetry Ingest: Condition={result['condition_state']['condition_name']} | Confidence={result['condition_state']['confidence_pct']}% | {result['condition_state']['confidence_interval_95']}")

def test_visual_inspection_with_gradcam():
    # Read a real concrete photo from s2ds.zip
    import zipfile
    s2ds_zip = os.path.join(BASE_DIR, "ai_models/data/raw/public/s2ds.zip")
    assert os.path.exists(s2ds_zip), "s2ds.zip must exist"

    with zipfile.ZipFile(s2ds_zip, 'r') as z:
        img_name = [n for n in z.namelist() if n.startswith('val/') and n.endswith('.png') and not n.endswith('_lab.png')][0]
        img_bytes = z.read(img_name)

    files = {'file': ('crack_test.png', img_bytes, 'image/png')}
    response = client.post("/api/v1/prediction/visual-inspection", files=files)
    assert response.status_code == 200
    data = response.json()

    assert "defect_name" in data
    assert "confidence_pct" in data
    assert "gradcam_heatmap_base64" in data
    assert len(data["gradcam_heatmap_base64"]) > 100
    print(f"[PASS] 2D-CNN Visual Inspection: Defect={data['defect_name']} | Confidence={data['confidence_pct']}% | Grad-CAM Base64 Generated ({len(data['gradcam_heatmap_base64'])} chars)")

def test_idss_decision_and_work_order():
    decision_payload = {
        "asset_id": "TZ-TANROADS-BR-004",
        "predicted_class": 1,
        "class_probabilities": [0.1, 0.75, 0.1, 0.05],
        "telemetry_summary": {
            "max_strain": 795.0,
            "max_vibration": 1.45,
            "crack_propagation_mm": 0.02
        },
        "road_class": "Trunk",
        "importance_weight": 1.4
    }
    response = client.post("/api/v1/decision/evaluate", json=decision_payload)
    assert response.status_code == 200
    result = response.json()
    
    assert "work_order" in result
    assert result["work_order"]["priority_index_score"] > 0
    assert "order_id" in result["work_order"]
    
    # Check work orders list
    wo_list_res = client.get("/api/v1/decision/work-orders")
    assert wo_list_res.status_code == 200
    orders = wo_list_res.json()
    assert len(orders) >= 1
    print(f"[PASS] IDSS Decision Chain: Work Order {result['work_order']['order_id']} created | Priority={result['work_order']['priority_index_score']}/100 | Action: {result['work_order']['recommended_action'][:50]}...")

def test_single_asset_and_instrumentation():
    res = client.get("/api/v1/assets/TZ-TANROADS-BR-004")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Tanzanite Bridge"
    
    inst_res = client.get("/api/v1/assets/TZ-TANROADS-BR-004/instrumentation")
    assert inst_res.status_code == 200
    inst_data = inst_res.json()
    assert len(inst_data["sensors_installed"]) >= 4
    print(f"[PASS] Asset Instrumentation: Tanzanite Bridge has {len(inst_data['sensors_installed'])} active SHM sensor types.")

def test_websocket_telemetry_stream():
    with client.websocket_connect("/api/v1/telemetry/ws/TZ-TANROADS-BR-004") as websocket:
        data = websocket.receive_json()
        assert data["asset_id"] == "TZ-TANROADS-BR-004"
        assert "telemetry" in data
        assert "condition_state" in data
        assert "confidence_pct" in data["condition_state"]
        print(f"[PASS] WebSocket Telemetry Stream: Seq={data['sequence']} | Live Condition={data['condition_state']['condition_name']} ({data['condition_state']['confidence_pct']}%)")

if __name__ == "__main__":
    print("\n--- RUNNING BACKEND INTEGRATION TEST SUITE ---")
    test_root_health_check()
    test_assets_endpoint()
    test_single_asset_and_instrumentation()
    test_telemetry_ingest_and_uncertainty()
    test_visual_inspection_with_gradcam()
    test_idss_decision_and_work_order()
    test_websocket_telemetry_stream()
    print("\n=========================================================================")
    print("ALL BACKEND INTEGRATION TESTS (REST + WEBSOCKET) PASSED SUCCESSFULLY!")
    print("=========================================================================")
