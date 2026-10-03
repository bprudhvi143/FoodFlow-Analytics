"""
Configuration module for FoodFlow Analytics Backend.
"""

import os

class Settings:
    PROJECT_NAME: str = "FoodFlow Analytics API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Path to dataset (prefers data/processed/food_delivery_10k.csv, falls back to Datasets/)
    DATASET_PATH: str = os.getenv(
        "DATASET_PATH",
        "data/processed/food_delivery_10k.csv" if os.path.exists("data/processed/food_delivery_10k.csv") else "Datasets/food_delivery_10k.csv"
    )
    
    # CORS Origins for React Frontend
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

settings = Settings()
