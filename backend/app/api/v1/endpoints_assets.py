"""
Civil Infrastructure Asset Directory Endpoints
"""

from fastapi import APIRouter
from typing import List
from schemas.asset import CivilAsset

router = APIRouter()

# Pre-populated representative Tanzanian civil infrastructure assets
TANZANIAN_ASSETS = [
    {
        "asset_id": "TZ-TANROADS-BR-004",
        "name": "Tanzanite Bridge",
        "structure_type": "Extradosed Cable-Stayed Concrete Bridge",
        "location_region": "Dar es Salaam",
        "gps_latitude": -6.8041,
        "gps_longitude": 39.2906,
        "road_class": "Trunk",
        "year_constructed": 2022,
        "current_health_index": 0.82,
        "condition_state": "Minor Deterioration",
        "importance_factor": 1.5
    },
    {
        "asset_id": "TZ-TANESCO-DAM-001",
        "name": "Julius Nyerere Hydropower Project (JNHPP Rufiji Dam)",
        "structure_type": "Roller-Compacted Concrete (RCC) Gravity Dam & Spillway",
        "location_region": "Rufiji Gorge / Pwani",
        "gps_latitude": -7.8000,
        "gps_longitude": 37.8500,
        "road_class": "Hydro Dam",
        "year_constructed": 2024,
        "current_health_index": 0.96,
        "condition_state": "Normal / Healthy",
        "importance_factor": 1.9
    },
    {
        "asset_id": "TZ-TPA-PRT-003",
        "name": "Dar es Salaam Port Berth 1-7 Deep-Water Quay Wall",
        "structure_type": "Marine Reinforced Concrete Quay Wall & Wharf",
        "location_region": "Dar es Salaam Port",
        "gps_latitude": -6.8286,
        "gps_longitude": 39.2974,
        "road_class": "Marine Port",
        "year_constructed": 2020,
        "current_health_index": 0.77,
        "condition_state": "Minor Deterioration",
        "importance_factor": 1.6
    },
    {
        "asset_id": "TZ-TBA-BLD-005",
        "name": "PSPF Commercial Twin Towers Complex",
        "structure_type": "35-Story Reinforced Concrete Core & Shear Wall Frame",
        "location_region": "Dar es Salaam CBD",
        "gps_latitude": -6.8152,
        "gps_longitude": 39.2889,
        "road_class": "Building",
        "year_constructed": 2015,
        "current_health_index": 0.85,
        "condition_state": "Normal / Healthy",
        "importance_factor": 1.3
    },
    {
        "asset_id": "TZ-TANROADS-BR-002",
        "name": "Kigamboni Bridge (Nyerere Bridge)",
        "structure_type": "Prestressed Concrete Cable-Stayed Bridge",
        "location_region": "Dar es Salaam",
        "gps_latitude": -6.8398,
        "gps_longitude": 39.3094,
        "road_class": "Trunk",
        "year_constructed": 2016,
        "current_health_index": 0.88,
        "condition_state": "Normal / Healthy",
        "importance_factor": 1.4
    },
    {
        "asset_id": "TZ-UDSM-COET-001",
        "name": "UDSM CoET Civil Engineering Structural Testing Lab",
        "structure_type": "Reinforced Concrete Frame & Portal Testing Rig",
        "location_region": "Dar es Salaam",
        "gps_latitude": -6.7788,
        "gps_longitude": 39.2081,
        "road_class": "Institutional",
        "year_constructed": 2010,
        "current_health_index": 0.74,
        "condition_state": "Moderate Distress",
        "importance_factor": 1.0
    },
    {
        "asset_id": "TZ-TRC-SGR-012",
        "name": "TRC SGR Viaduct 3 - Morogoro Segment",
        "structure_type": "Continuous Prestressed Concrete Box Girder",
        "location_region": "Morogoro / Dodoma Corridor",
        "gps_latitude": -6.8222,
        "gps_longitude": 37.6611,
        "road_class": "Heavy Rail",
        "year_constructed": 2023,
        "current_health_index": 0.94,
        "condition_state": "Normal / Healthy",
        "importance_factor": 1.6
    }
]

@router.get("/", response_model=List[CivilAsset], summary="List all monitored Tanzanian civil infrastructure assets")
def get_assets():
    return [CivilAsset(**a) for a in TANZANIAN_ASSETS]

@router.get("/{asset_id}", response_model=CivilAsset, summary="Get details for a specific asset by ID")
def get_asset_by_id(asset_id: str):
    match = next((a for a in TANZANIAN_ASSETS if a["asset_id"] == asset_id), None)
    if not match:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found in national registry.")
    return CivilAsset(**match)

@router.get("/{asset_id}/instrumentation", summary="Get physical sensor telemetry configuration and layout")
def get_asset_instrumentation(asset_id: str):
    """Returns the physical sensor instrumentation layout as defined in PhD Section 5.6.4."""
    match = next((a for a in TANZANIAN_ASSETS if a["asset_id"] == asset_id), None)
    if not match:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found.")
    
    # Custom sensor profiles based on structural type
    if "DAM" in asset_id:
        sensors = [
            {
                "sensor_id": f"{asset_id}-ACC-01",
                "type": "Low-Frequency Seismic Accelerometer",
                "parameter": "Crest Vibration Acceleration (m/s²)",
                "location": "Dam crest & spillway gallery",
                "sampling_frequency": "50 Hz",
                "nominal_range": "±1g",
                "critical_threshold": "> 0.8 m/s²"
            },
            {
                "sensor_id": f"{asset_id}-SG-01",
                "type": "Embedded Vibrating Wire Strain Gauge",
                "parameter": "RCC Mass Concrete Strain (με)",
                "location": "Dam heel & foundation interface",
                "sampling_frequency": "0.1 Hz",
                "nominal_range": "±1500 με",
                "critical_threshold": "> 450 με"
            },
            {
                "sensor_id": f"{asset_id}-LVDT-01",
                "type": "Linear Variable Differential Transformer (LVDT)",
                "parameter": "Monolith Joint Opening (mm)",
                "location": "Spillway radial gate & contraction joint",
                "sampling_frequency": "0.05 Hz",
                "nominal_range": "0 - 25 mm",
                "critical_threshold": "> 1.50 mm"
            },
            {
                "sensor_id": f"{asset_id}-TH-01",
                "type": "Multi-Depth Resistance Thermometer Array",
                "parameter": "Internal Mass Hydration Temp (°C)",
                "location": "Dam core section at 5m depth intervals",
                "sampling_frequency": "1/300 Hz"
            }
        ]
    elif "PRT" in asset_id:
        sensors = [
            {
                "sensor_id": f"{asset_id}-CORR-01",
                "type": "Embedded Solid-State Ag/AgCl Half-Cell",
                "parameter": "Chloride Corrosion Potential (mV)",
                "location": "Tidal splash zone on reinforced concrete quay wall",
                "sampling_frequency": "1/3600 Hz",
                "nominal_range": "-1000 mV to +200 mV",
                "critical_threshold": "< -350 mV (Active Depassivation)"
            },
            {
                "sensor_id": f"{asset_id}-SG-01",
                "type": "Fiber-Optic FBG Strain Gauge",
                "parameter": "Bollard Pull Bending Strain (με)",
                "location": "Mooring dolphin & capping beam",
                "sampling_frequency": "10 Hz",
                "nominal_range": "±2500 με",
                "critical_threshold": "> 850 με"
            },
            {
                "sensor_id": f"{asset_id}-LVDT-01",
                "type": "Linear Variable Differential Transformer (LVDT)",
                "parameter": "Quay Deck Expansion Gap (mm)",
                "location": "Berth interface joint",
                "sampling_frequency": "0.1 Hz",
                "nominal_range": "0 - 15 mm",
                "critical_threshold": "> 0.45 mm"
            }
        ]
    elif "BLD" in asset_id:
        sensors = [
            {
                "sensor_id": f"{asset_id}-INC-01",
                "type": "Biaxial High-Precision Inclinometer",
                "parameter": "Inter-Story Drift Tilt (deg)",
                "location": "Level 35 rooftop core shear wall",
                "sampling_frequency": "1 Hz",
                "nominal_range": "±2.0 deg",
                "critical_threshold": "> 0.25 deg"
            },
            {
                "sensor_id": f"{asset_id}-ACC-01",
                "type": "Tri-Axial MEMS Accelerometer",
                "parameter": "Wind/Seismic Dynamic Vibration (m/s²)",
                "location": "Mid-height mechanical floor & top floor",
                "sampling_frequency": "100 Hz",
                "nominal_range": "±2g",
                "critical_threshold": "> 1.2 m/s²"
            },
            {
                "sensor_id": f"{asset_id}-LVDT-01",
                "type": "Linear Variable Differential Transformer (LVDT)",
                "parameter": "Basement Shear Crack Opening (mm)",
                "location": "Foundation transfer slab",
                "sampling_frequency": "0.1 Hz",
                "nominal_range": "0 - 10 mm",
                "critical_threshold": "> 0.25 mm"
            }
        ]
    else:
        # Standard Bridge Instrumentation
        sensors = [
            {
                "sensor_id": f"{asset_id}-SG-01",
                "type": "Fiber-Optic FBG Strain Gauge",
                "parameter": "Microstrain (με)",
                "location": "Mid-span tension flange",
                "sampling_frequency": "1 Hz (aggregated to 1/60 Hz)",
                "nominal_range": "±3000 με",
                "critical_threshold": "> 950 με"
            },
            {
                "sensor_id": f"{asset_id}-ACC-01",
                "type": "Tri-Axial MEMS Accelerometer",
                "parameter": "Vibration Acceleration (m/s²)",
                "location": "Pylon top & deck center",
                "sampling_frequency": "100 Hz (modal decomposition)",
                "nominal_range": "±2g",
                "critical_threshold": "> 2.5 m/s²"
            },
            {
                "sensor_id": f"{asset_id}-LVDT-01",
                "type": "Linear Variable Differential Transformer (LVDT)",
                "parameter": "Crack Displacement (mm)",
                "location": "Expansion joint & pier base",
                "sampling_frequency": "0.1 Hz",
                "nominal_range": "0 - 10 mm",
                "critical_threshold": "> 0.20 mm"
            },
            {
                "sensor_id": f"{asset_id}-TH-01",
                "type": "PT100 Resistance Thermometer",
                "parameter": "Surface Temperature (°C)",
                "location": "Girder top & bottom surfaces",
                "purpose": "Thermal-mechanical strain decoupling (α=11.5 με/°C)",
                "sampling_frequency": "1/60 Hz"
            }
        ]

    return {
        "asset_id": asset_id,
        "asset_name": match["name"],
        "structure_type": match["structure_type"],
        "sensors_installed": sensors,
        "edge_gateway": "Ruggedized ARM Cortex IoT Gateway (Solar-backed, 4G LTE uplink to SMMS Cloud)"
    }
