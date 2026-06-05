# app/core/config.py
import os
from pathlib import Path

def load_secret(secret_name):
    secret_file = Path(f"/run/secrets/{secret_name}")

    if not secret_file.exists():
        return {}

    result = {}

    with open(secret_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if "=" in line:
                k, v = line.split("=", 1)
                result[k.strip()] = v.strip()

    return result

class Settings:
    secret_name = os.getenv("secret_name")
    cfg = load_secret(secret_name)

    APP_NAME = cfg.get("APP_NAME", "FastAPI")
    DB_DRIVER = cfg.get("DB_DRIVER")
    DB_SERVER = cfg.get("DB_SERVER")
    DB_NAME = cfg.get("DB_NAME")
    DB_USER = cfg.get("DB_USER")
    DB_PASSWORD = cfg.get("DB_PASSWORD")
    DB_ENCRYPT = cfg.get("DB_ENCRYPT")
    DB_TRUST_SERVER_CERTIFICATE = cfg.get("DB_TRUST_SERVER_CERTIFICATE")
    IMAGE_URL = cfg.get("IMAGE_URL")
    MESSAGE: str = ''
    ROOT_PATH = cfg.get("ROOT_PATH", "")

settings = Settings()