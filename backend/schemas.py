"""Modelos Pydantic del contrato de la API."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

Semaforo = Literal["verde", "amarillo", "rojo"]
NivelSargazo = Literal["bajo", "medio", "alto"]
NivelOcupacion = Literal["vacia", "normal", "llena"]


class PlayaInput(BaseModel):
    id: str
    nombre: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    popularidad: float = Field(ge=0, le=1)
    sargazo: Optional[float] = Field(default=None, ge=0, le=100)
    temp_agua: float = Field(ge=15, le=40)
    fragilidad: Optional[float] = Field(default=None, ge=0, le=100)
    transporte: str = ""
    nota: str = ""


class AlternativaOut(BaseModel):
    id: str
    nombre: str
    ocupacion: int = Field(ge=0, le=100)
    estres: int = Field(ge=0, le=100)
    transporte: str


class PlayaSemaforoOut(BaseModel):
    id: str
    nombre: str
    lat: float
    lng: float
    ocupacion: int = Field(ge=0, le=100)
    ocupacion_2h: int = Field(ge=0, le=100)
    estres: int = Field(ge=0, le=100)
    semaforo: Semaforo
    motivos: list[str]
    transporte: str
    alternativas: list[AlternativaOut]
    distancia_km: Optional[float] = None


class SaludOut(BaseModel):
    ok: bool


class Reporte(BaseModel):
    id: Optional[str] = None
    playa_id: str
    fecha_hora: datetime
    sargazo: int = Field(ge=0, le=100)
    ocupacion: int = Field(ge=0, le=100)
    origen: Optional[str] = "qr_sitio"


class ImpactoPlayaOut(BaseModel):
    id: str
    nombre: str
    semaforo: Semaforo
    estres: int
    alternativa_id: str
    alternativa_nombre: str
    estres_alternativa: int
    reduccion_estres_pct: int = Field(ge=0, le=100)


class ImpactoOut(BaseModel):
    playas_evaluadas: int
    playas_en_riesgo: int
    reduccion_promedio_pct: int
    reportes_ciudadanos_activos: int
    detalle: list[ImpactoPlayaOut]
