"""
Intelligent Decision Support System (IDSS) Decision Logic Module
Implements the operational decision chain:
Sensor Trigger ➔ Anomaly Detection ➔ Severity Classification ➔ Maintenance Recommendation ➔ Priority Ranking ➔ Resource Allocation.
Fulfills PhD Chapter 5, Section 5.10.3 & Chapter 6, Section 6.6.
"""

from typing import Dict, Any, List
import numpy as np

class IDSSDecisionEngine:
    """
    Translates deep learning condition state inferences and field telemetry
    into prioritized, actionable maintenance work orders for TANROADS / TRC / Municipalities.
    """
    
    ACTION_RECOMMENDATIONS = {
        0: {
            "level": "Routine Monitoring",
            "action": "Maintain standard automated IoT sensor telemetry. No physical intervention required.",
            "urgency_days": 180,
            "base_priority": 10
        },
        1: {
            "level": "Preventative Maintenance",
            "action": "Schedule visual inspection during next routine patrol. Clean expansion joints, check drainage channels, apply protective surface coating.",
            "urgency_days": 60,
            "base_priority": 35
        },
        2: {
            "level": "Corrective Rehabilitation",
            "action": "Dispatch specialized structural engineering team for non-destructive evaluation (NDE). Plan crack injection epoxy sealing, bearing replacement, or carbon-fiber reinforcement.",
            "urgency_days": 14,
            "base_priority": 70
        },
        3: {
            "level": "Emergency Structural Intervention",
            "action": "CRITICAL RISK: Immediate temporary load posting (axle weight restriction) or lane closure. Install propping/shoring support. Initiate urgent emergency rehabilitation.",
            "urgency_days": 1,
            "base_priority": 95
        }
    }

    @classmethod
    def process_telemetry_to_decision(
        cls,
        predicted_class: int,
        class_probabilities: List[float],
        telemetry_summary: Dict[str, float],
        asset_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes the full IDSS decision chain.
        telemetry_summary: e.g. {'max_strain': 280.0, 'max_vibration': 3.2, 'crack_width_mm': 0.8}
        asset_metadata: e.g. {'asset_name': 'Tanzanite Bridge Pier 4', 'road_class': 'Trunk', 'aadt': 25000, 'importance_weight': 1.2}
        """
        rec_info = cls.ACTION_RECOMMENDATIONS.get(predicted_class, cls.ACTION_RECOMMENDATIONS[0])
        
        # Calculate Multi-Criteria Maintenance Priority Index (MPI)
        # MPI = (Base_Priority * 0.45) + (Prob_Severity * 0.25) + (Traffic_Weight * 0.15) + (Asset_Importance * 0.15)
        severity_prob = class_probabilities[predicted_class] if class_probabilities else 1.0
        
        road_class = asset_metadata.get("road_class", "Regional")
        traffic_weight = 1.0
        if road_class in ("Trunk", "Highway"):
            traffic_weight = 1.4  # Strategic national road artery
        elif road_class in ("Hydro Dam", "Dam"):
            traffic_weight = 1.8  # Critical national energy & reservoir safety asset
        elif road_class in ("Marine Port", "Port"):
            traffic_weight = 1.5  # Strategic maritime trade infrastructure
        elif road_class in ("Heavy Rail", "Rail"):
            traffic_weight = 1.6  # Heavy axle rail transport corridor
        elif road_class in ("Building", "Commercial"):
            traffic_weight = 1.2  # High-occupancy commercial / public facility
        elif road_class == "Regional":
            traffic_weight = 1.1
        else:
            traffic_weight = 1.0

        importance = asset_metadata.get("importance_weight", 1.0)
        
        mpi_score = (
            (rec_info["base_priority"] * 0.45)
            + (severity_prob * 100 * 0.25)
            + (traffic_weight * 10 * 0.15)
            + (importance * 10 * 0.15)
        )
        mpi_score = round(min(100.0, max(0.0, mpi_score)), 2)

        # Budget / Resource Allocation Tier
        if mpi_score >= 80:
            resource_tier = "Tier 1: Emergency Contingency Fund (Immediate Release)"
        elif mpi_score >= 55:
            resource_tier = "Tier 2: Quarterly Major Periodic Maintenance Budget"
        elif mpi_score >= 30:
            resource_tier = "Tier 3: Annual Recurrent Routine Maintenance Allocation"
        else:
            resource_tier = "Tier 4: Standard Operations & Monitoring"

        return {
            "asset_id": asset_metadata.get("asset_id", "UNKNOWN"),
            "asset_name": asset_metadata.get("asset_name", "Monitored Asset"),
            "condition_state": {
                "class_index": predicted_class,
                "confidence": round(float(severity_prob) * 100, 2),
                "probabilities": [round(float(p), 4) for p in class_probabilities]
            },
            "decision_chain": {
                "anomaly_triggered": bool(predicted_class > 0),
                "severity_level": rec_info["level"],
                "recommended_action": rec_info["action"],
                "maximum_response_window_days": rec_info["urgency_days"],
                "priority_index_score": mpi_score,
                "resource_allocation": resource_tier
            }
        }
