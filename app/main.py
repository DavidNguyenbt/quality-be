import os

import uvicorn
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.openapi.utils import get_openapi
from app.qc_dashboard.controller import qc_dashboard_router

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="Test JWT in Swagger UI",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

ROOT_PATH = os.getenv("ROOT_PATH", "")

app = FastAPI(
    title="Quality API",
    root_path=ROOT_PATH
)
origins = ["*"]
app.openapi = custom_openapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/files", StaticFiles(directory="files"), name="files")

app.include_router(qc_dashboard_router, prefix="/api/v2/qc_dashboard", tags=["qc_dashboard"])

if __name__ == "__main__":
    uvicorn.run("main:app", port=5008, reload=True)
