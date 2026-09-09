"""
Visual Inspection & Prediction Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class VisualInspectionResponse(BaseModel):
    defect_class_index: int = Field(..., description="0: Normal, 1: Crack, 2: Spalling, 3: Corrosion/Efflorescence")
    defect_name: str
    confidence_pct: float
    probabilities: List[float]
    severity_level: str
    estimated_surface_defect_ratio_pct: float
    gradcam_heatmap_base64: Optional[str] = Field(None, description="Base64 PNG of the Grad-CAM explainability overlay")
    is_out_of_distribution: bool = Field(False, description="True if specimen fails epistemic confidence gating (non-concrete or non-structural OOD)")
    ood_warning: Optional[str] = Field(None, description="Doctoral explanation for OOD safety gating")
