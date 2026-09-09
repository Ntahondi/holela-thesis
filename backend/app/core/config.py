"""
Application Configuration and Environment Settings
"""

import os

class Settings:
    PROJECT_NAME: str = "SMMS Smart Infrastructure Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base workspace directory
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    
    # Model weights paths
    WEIGHTS_DIR: str = os.path.join(BASE_DIR, "ai_models/weights")
    CNN_1D_PATH: str = os.path.join(WEIGHTS_DIR, "cnn_1d_telemetry_best.pth")
    CNN_2D_PATH: str = os.path.join(WEIGHTS_DIR, "cnn_2d_visual_best.pth")
    LSTM_PATH: str = os.path.join(WEIGHTS_DIR, "lstm_telemetry_best.pth")
    
    # Reports and figures directory
    REPORTS_DIR: str = os.path.join(BASE_DIR, "ai_models/reports")
    
    # CORS Origins (allow Flutter web, mobile emulator, localhost)
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "*"
    ]

settings = Settings()
