"""
SMMS Analytical & Decision Support Microservice
Master FastAPI Application Entrypoint
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure backend/app is in sys.path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from core.config import settings
from services.model_runner import ModelRunnerService
from api.v1 import (
    endpoints_telemetry,
    endpoints_prediction,
    endpoints_decision,
    endpoints_assets
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Preload PyTorch deep learning models into memory
    print("[SMMS Backend] Preloading AI Models into memory...")
    ModelRunnerService.get_instance()
    print("[SMMS Backend] All AI Models loaded and ready for inference!")
    yield
    # Shutdown
    print("[SMMS Backend] Shutting down SMMS Microservice.")

app = FastAPI(
    title="Smart Maintenance Management System (SMMS) API",
    description="Doctoral AI analytics and intelligent decision support microservice for Tanzania civil infrastructure.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Flutter Client and external dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Routers
app.include_router(endpoints_telemetry.router, prefix=f"{settings.API_V1_STR}/telemetry", tags=["IoT Telemetry"])
app.include_router(endpoints_prediction.router, prefix=f"{settings.API_V1_STR}/prediction", tags=["Visual Inspection & AI"])
app.include_router(endpoints_decision.router, prefix=f"{settings.API_V1_STR}/decision", tags=["IDSS Decision Logic"])
app.include_router(endpoints_assets.router, prefix=f"{settings.API_V1_STR}/assets", tags=["Infrastructure Assets"])

# Mount reports directory for serving generated figures to frontend/browser
if os.path.exists(settings.REPORTS_DIR):
    app.mount("/reports", StaticFiles(directory=settings.REPORTS_DIR), name="reports")

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "system": "Smart Maintenance Management System (SMMS) - Tanzania",
        "framework_layer": "Layer 2 (Platform Layer) & Layer 3 (Decision Layer)",
        "docs_url": "/docs",
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
