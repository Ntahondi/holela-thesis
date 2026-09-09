"""
Telemetry Input and Output Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TelemetryReading(BaseModel):
    timestamp: Optional[str] = None
    strain_microstrain: float = Field(..., description="Dynamic bending/axial microstrain")
    vibration_ms2: float = Field(..., description="Acceleration amplitude in m/s^2")
    crack_propagation_mm: float = Field(0.0, description="Crack opening displacement in mm")
    deflection_mm: float = Field(0.0, description="Vertical deflection in mm")
    tilt_deg: float = Field(0.0, description="Inclination / tilt angle in degrees")
    modal_frequency_hz: float = Field(..., description="Resonant structural frequency in Hz")
    temperature_c: float = Field(..., description="Ambient temperature in degrees Celsius")
    humidity_percent: float = Field(..., description="Relative humidity percentage")

class TelemetryBatchInput(BaseModel):
    asset_id: str = Field(..., example="TZ-TANROADS-BR-004")
    readings: List[TelemetryReading]

class ConditionStateOutput(BaseModel):
    class_index: int = Field(..., description="0: Normal, 1: Minor, 2: Moderate, 3: Critical")
    condition_name: str
    confidence_pct: float
    confidence_interval_95: str
    probabilities: List[float]
    anomaly_detected: bool

class TelemetryInferenceResponse(BaseModel):
    asset_id: str
    num_readings_processed: int
    condition_state: ConditionStateOutput
    mechanical_strain_isolated: float
    thermal_expansion_offset: float
