import logging
import sys

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.logging import DefaultFormatter

from backend.api import analysis_routes, common, labels

# --- LOGGING CONFIGURATION ---
formatter = DefaultFormatter(fmt="%(levelprefix)-10s %(message)s", use_colors=True)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

app = FastAPI(title="PyCEFR API", description="API para el análisis y clasificación de código.", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(analysis_routes.router)
api_v1_router.include_router(common.router)
api_v1_router.include_router(labels.router)

app.include_router(api_v1_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok", "message": "API is running"}
