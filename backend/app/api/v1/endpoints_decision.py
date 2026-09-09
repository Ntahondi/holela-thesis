"""
Intelligent Decision Support System (IDSS) Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List
from schemas.decision import IDSSDecisionRequest, WorkOrder
from services.idss_service import IDSSService

router = APIRouter()

@router.post("/evaluate", summary="Run IDSS decision logic and dispatch work order")
def evaluate_maintenance_decision(payload: IDSSDecisionRequest):
    """
    Evaluates condition state and telemetry summary against multi-criteria decision parameters.
    Returns priority index (MPI) and generated work order.
    """
    idss = IDSSService.get_instance()
    try:
        result = idss.evaluate_and_create_work_order(
            asset_id=payload.asset_id,
            asset_name=f"Asset {payload.asset_id}",
            predicted_class=payload.predicted_class,
            class_probabilities=payload.class_probabilities,
            telemetry_summary=payload.telemetry_summary,
            road_class=payload.road_class or "Trunk",
            importance_weight=payload.importance_weight or 1.2
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/work-orders", response_model=List[WorkOrder], summary="List all active work orders")
def list_work_orders():
    """Returns priority-sorted list of maintenance work orders."""
    idss = IDSSService.get_instance()
    orders = idss.list_work_orders()
    return [WorkOrder(**wo) for wo in orders]

@router.patch("/work-orders/{order_id}/approve", summary="Approve maintenance work order")
def approve_work_order(order_id: str):
    idss = IDSSService.get_instance()
    success = idss.update_order_status(order_id, "Approved - Dispatched to Maintenance Team")
    if not success:
        raise HTTPException(status_code=404, detail="Work order not found")
    return {"status": "success", "order_id": order_id, "new_state": "Approved"}
