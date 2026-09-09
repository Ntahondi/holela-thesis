"""
Decision Support System (IDSS) Schemas
Fulfills PhD Chapter 5, Section 5.10.3 & Chapter 6, Section 6.6.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class IDSSDecisionRequest(BaseModel):
    asset_id: str
    predicted_class: int
    class_probabilities: List[float]
    telemetry_summary: Dict[str, float]
    road_class: Optional[str] = "Trunk"
    importance_weight: Optional[float] = 1.2

class WorkOrder(BaseModel):
    order_id: str
    asset_id: str
    asset_name: str
    severity_level: str
    priority_index_score: float = Field(..., description="Multi-Criteria Priority Index (0-100)")
    recommended_action: str
    resource_tier: str
    maximum_response_window_days: int
    created_at: str
    status: str = "Pending Approval"
