import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.logging import DefaultFormatter

from backend.api import analysis_routes, common, labels, stats_routes
from backend.config.settings import settings
from backend.db import db_utils

# --- LOGGING CONFIGURATION ---
formatter = DefaultFormatter(fmt="%(levelprefix)-10s %(message)s", use_colors=True)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    db_utils.mark_orphaned_analyses_as_failed()
    yield


app = FastAPI(
    title="PyCEFR API",
    description="API for Python code complexity analysis and CEFR classification.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTING ---
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(analysis_routes.router)
api_v1_router.include_router(common.router)
api_v1_router.include_router(labels.router)
api_v1_router.include_router(stats_routes.router)

app.include_router(api_v1_router)


@app.get("/", tags=["Health"])
def read_root() -> dict[str, str]:
    """
    Health check endpoint.

    Provides a simple confirmation that the API service is reachable
    and running correctly.

    Returns:
        dict[str, str]: A dictionary containing the status and a welcome message.
    """
    return {"status": "ok", "message": "API is running"}
