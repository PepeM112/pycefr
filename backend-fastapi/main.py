from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import analysis_routes

app = FastAPI(title="PyCEFR API", description="API para el análisis y clasificación de código.", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_routes.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok", "message": "API is running"}
