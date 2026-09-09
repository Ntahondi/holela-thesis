"""
Intelligent Decision Support System (IDSS) Service
Manages automated maintenance priority scoring (MPI), action recommendations,
and work order dispatch for TANROADS / TRC / Municipalities.
Fulfills SMMS Decision Layer (Chapter 6, Section 6.6).
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Ensure ai_models/src is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
AI_SRC_DIR = os.path.join(BASE_DIR, "ai_models/src")
if AI_SRC_DIR not in sys.path:
    sys.path.insert(0, AI_SRC_DIR)

from idss_decision_logic import IDSSDecisionEngine

class IDSSService:
    _instance = None
    _work_orders = []

    def __init__(self):
        # Pre-populate sample historic work order for demonstration
        self._work_orders.append({
            "order_id": "WO-TZ-2026-001",
            "asset_id": "TZ-TANROADS-BR-004",
            "asset_name": "Tanzanite Bridge - Pier 4",
            "severity_level": "Preventative Maintenance",
            "priority_index_score": 39.96,
            "recommended_action": "Schedule visual inspection during next routine patrol. Clean expansion joints, apply protective surface coating.",
            "resource_tier": "Tier 3: Annual Recurrent Routine Maintenance Allocation",
            "maximum_response_window_days": 60,
            "created_at": "2026-09-08 14:30:00",
            "status": "Scheduled"
        })

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def evaluate_and_create_work_order(
        self,
        asset_id: str,
        asset_name: str,
        predicted_class: int,
        class_probabilities: List[float],
        telemetry_summary: Dict[str, float],
        road_class: str = "Trunk",
        importance_weight: float = 1.2
    ) -> Dict[str, Any]:
        """Runs the IDSS decision chain and creates a formal maintenance work order."""
        asset_meta = {
            "asset_id": asset_id,
            "asset_name": asset_name,
            "road_class": road_class,
            "importance_weight": importance_weight
        }

        decision_output = IDSSDecisionEngine.process_telemetry_to_decision(
            predicted_class=predicted_class,
            class_probabilities=class_probabilities,
            telemetry_summary=telemetry_summary,
            asset_metadata=asset_meta
        )

        d_chain = decision_output["decision_chain"]
        work_order = {
            "order_id": f"WO-TZ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}",
            "asset_id": asset_id,
            "asset_name": asset_name,
            "severity_level": d_chain["severity_level"],
            "priority_index_score": d_chain["priority_index_score"],
            "recommended_action": d_chain["recommended_action"],
            "resource_tier": d_chain["resource_allocation"],
            "maximum_response_window_days": d_chain["maximum_response_window_days"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Pending Engineer Approval" if d_chain["priority_index_score"] >= 40 else "Auto-Logged"
        }

        self._work_orders.insert(0, work_order)
        return {
            "decision": decision_output,
            "work_order": work_order
        }

    def list_work_orders(self) -> List[Dict[str, Any]]:
        return self._work_orders

    def update_work_order_status(self, order_id: str, new_status: str) -> bool:
        for wo in self._work_orders:
            if wo["order_id"] == order_id:
                wo["status"] = new_status
                return True
        return False
