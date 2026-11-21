"""Modelos Pydantic del contrato de la API."""
from typing import Literal

from pydantic import BaseModel, Field

Semaforo = Literal["verde", "amarillo", "rojo"]


class PlayaInput(BaseModel):
    id: str
    nombre: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    popularidad: float = Field(ge=0, le=1)
    sargazo: float = Field(ge=0, le=100)
    temp_agua: float
    fragilidad: float = Field(ge=0, le=100)
    transporte: str
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


class SaludOut(BaseModel):
    ok: bool
