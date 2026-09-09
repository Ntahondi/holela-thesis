"""
Visual Inspection & Prediction API Endpoints
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from schemas.prediction import VisualInspectionResponse
from services.model_runner import ModelRunnerService

router = APIRouter()

@router.post("/visual-inspection", response_model=VisualInspectionResponse, summary="Inspect concrete photo with 2D-CNN and Grad-CAM")
async def inspect_concrete_photo(file: UploadFile = File(...)):
    """
    Accepts field photos captured by smartphone or drone cameras.
    Runs 2D-CNN to detect cracks, spalling, and corrosion, and returns
    Grad-CAM explainability heatmaps directly in the JSON response.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image format (JPEG/PNG).")

    runner = ModelRunnerService.get_instance()
    try:
        image_bytes = await file.read()
        res = runner.run_visual_inference(image_bytes, img_size=224)
        return VisualInspectionResponse(
            defect_class_index=res["defect_class_index"],
            defect_name=res["defect_name"],
            confidence_pct=res["confidence_pct"],
            probabilities=res["probabilities"],
            severity_level=res["severity_level"],
            estimated_surface_defect_ratio_pct=res["estimated_surface_defect_ratio_pct"],
            gradcam_heatmap_base64=res["gradcam_heatmap_base64"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
