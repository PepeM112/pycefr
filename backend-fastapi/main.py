from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.analysis import *
from models.common import *
from api import analysis_routes
from api import catalog_routes

app = FastAPI(
    title="PyCEFR API",
    description="API para el análisis y clasificación de código.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_routes.router)
app.include_router(catalog_routes.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API is running"}