"""API FastAPI del Semáforo Playero Inteligente."""
import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from engine import evaluar
from schemas import PlayaInput, PlayaSemaforoOut, SaludOut

BASE_DIR = Path(__file__).resolve().parent.parent
PLAYAS_PATH = BASE_DIR / "data" / "playas.json"

FALLBACK_PLAYAS: list[dict] = [
    {"id": "delfines", "nombre": "Playa Delfines", "lat": 21.05, "lng": -86.77,
     "popularidad": 1.0, "sargazo": 50, "temp_agua": 29.0, "fragilidad": 71,
     "transporte": "Bus R-1 Km 18",
     "nota": "Zona de dunas y arrecife frágil: evita pisar la vegetación"},
    {"id": "langosta", "nombre": "Playa Langosta", "lat": 21.15, "lng": -86.77,
     "popularidad": 0.44, "sargazo": 20, "temp_agua": 28.5, "fragilidad": 10,
     "transporte": "Bus R-1 Km 5", "nota": "Playa urbana de aguas tranquilas"},
    {"id": "tortugas", "nombre": "Playa Tortugas", "lat": 21.16, "lng": -86.80,
     "popularidad": 0.30, "sargazo": 10, "temp_agua": 28.0, "fragilidad": 85,
     "transporte": "Bus R-1 Km 6",
     "nota": "Zona de anidación de tortugas: no uses luz ni te acerques de noche"},
]


def cargar_playas() -> list[PlayaInput]:
    """Lee data/playas.json en cada petición; usa fallback si falta o es inválido."""
    try:
        datos = json.loads(PLAYAS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        datos = None
    playas: list[PlayaInput] = []
    if isinstance(datos, list):
        for item in datos:
            try:
                playas.append(PlayaInput.model_validate(item))
            except ValidationError:
                continue
    if not playas:
        playas = [PlayaInput.model_validate(p) for p in FALLBACK_PLAYAS]
    return playas


app = FastAPI(title="Semáforo Playero Inteligente")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/salud", response_model=SaludOut)
def salud() -> SaludOut:
    return SaludOut(ok=True)


@app.get("/api/playas", response_model=list[PlayaSemaforoOut])
def playas(
    fecha: date,
    hora: int = Query(..., ge=6, le=20),
    festivo: bool = False,
) -> list[PlayaSemaforoOut]:
    return evaluar(cargar_playas(), fecha, hora, festivo)


# Debe ir al final, después de todas las rutas /api.
app.mount(
    "/",
    StaticFiles(directory=BASE_DIR / "frontend", html=True, check_dir=False),
    name="frontend",
)
