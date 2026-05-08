# app/core/config.py
import os

class Settings:
    APP_NAME = os.getenv("APP_NAME", "FastAPI")
    DB_DRIVER =  os.getenv("DB_DRIVER")
    DB_SERVER = os.getenv("DB_SERVER")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_ENCRYPT = os.getenv("DB_ENCRYPT")
    DB_TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE")
    IMAGE_URL = os.getenv("IMAGE_URL")
    MESSAGE: str = ''

settings = Settings()