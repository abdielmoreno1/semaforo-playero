"""Lógica pura de negocio (sin dependencias de FastAPI)."""
import math
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable, Optional

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from schemas import (
    AlternativaOut, ImpactoOut, ImpactoPlayaOut, PlayaInput, PlayaSemaforoOut,
    Reporte,
)

CURVA: dict[int, float] = {
    6: 0.05, 7: 0.08, 8: 0.15, 9: 0.30, 10: 0.50, 11: 0.75, 12: 0.95,
    13: 1.0, 14: 0.95, 15: 0.85, 16: 0.65, 17: 0.40, 18: 0.20, 19: 0.08,
    20: 0.05,
}
PESOS = {"sargazo": 0.45, "calor": 0.20, "fragilidad": 0.20, "ocupacion": 0.15}
UMBRAL_ESTRES_TERMICO = 29.5  # °C: inicio de riesgo de blanqueamiento coralino (NOAA / UNAM)

MSG_TORTUGAS = "Temporada activa de anidación de tortugas (may-oct): evita zonas de dunas"
MSG_REEF_SAFE = (
    "Protege el arrecife: agua cálida o zona frágil. Prohibido bloqueador químico "
    "(oxibenzona/octinoxato); usa protector 100% biodegradable o playera UV"
)
MSG_SIN_SARGAZO = "Sin observación reciente de sargazo: repórtalo con el QR de la playa"
SUFIJO_MENOR_IMPACTO = " (alternativa de menor impacto)"
TRANSPORTE_DEFAULT = "Ruta por confirmar (R-1/R-2 recorren la Zona Hotelera)"

VENTANA_ANTES = timedelta(hours=3)
VENTANA_DESPUES = timedelta(hours=1)


def calcular_distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Fórmula de Haversine para distancia en kilómetros."""
    r_tierra = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r_tierra * c, 1)


def ocupacion(playa: PlayaInput, fecha: date, hora: int, festivo: bool) -> int:
    factor_hora = CURVA.get(hora, 0.05)
    factor_dia = 1.0 if fecha.weekday() >= 5 else 0.7
    factor_festivo = 1.15 if festivo else 1.0
    valor = 100 * factor_hora * playa.popularidad * factor_dia * factor_festivo
    return max(0, min(100, round(valor)))


def estres(playa: PlayaInput, ocup: int) -> int:
    calor = max(0.0, min(100.0, (playa.temp_agua - 28.0) / 4.0 * 100.0))
    componentes = {
        "sargazo": playa.sargazo,
        "calor": calor,
        "fragilidad": playa.fragilidad,
        "ocupacion": float(ocup),
    }
    conocidos = {k: v for k, v in componentes.items() if v is not None}
    peso_total = sum(PESOS[k] for k in conocidos)
    valor = sum(PESOS[k] * v for k, v in conocidos.items()) / peso_total
    return max(0, min(100, round(valor)))


def semaforo(o: int, o2: int, e: int) -> str:
    if o >= 85 or e >= 65 or (o >= 70 and e >= 50):
        return "rojo"
    if o >= 60 or o2 >= 75 or e >= 45:
        return "amarillo"
    return "verde"


def motivos(
    playa: PlayaInput, o: int, o2: int, e: int, fecha: date, n_reportes: int = 0
) -> list[str]:
    out: list[str] = []
    frag = playa.fragilidad if playa.fragilidad is not None else 0
    if o >= 85:
        out.append(f"Saturada: {o}% de ocupación")
    elif o2 >= 75 and o < 75:
        out.append(f"Se va a llenar: {o}% ahora, {o2}% en 2 horas")
    elif o >= 60:
        out.append(f"Ocupación alta: {o}%")
    
    if playa.sargazo is None:
        out.append(MSG_SIN_SARGAZO)
    elif playa.sargazo >= 50:
        out.append("Mucho sargazo: riesgo de marea marrón y anoxia en pastos marinos")
    elif playa.sargazo >= 30:
        out.append("Sargazo moderado")
    
    if playa.temp_agua >= UMBRAL_ESTRES_TERMICO:
        out.append(f"Agua cálida ({playa.temp_agua}°C): mayor estrés para el arrecife")
    if e >= 45 and frag >= 60 and playa.nota:
        out.append(playa.nota)
    if 5 <= fecha.month <= 10 and frag >= 60:
        out.append(MSG_TORTUGAS)
    if playa.temp_agua >= UMBRAL_ESTRES_TERMICO or frag >= 60:
        out.append(MSG_REEF_SAFE)
    if n_reportes:
        s = "s" if n_reportes > 1 else ""
        out.append(f"Validado por {n_reportes} reporte{s} ciudadano{s} (QR) en las últimas 3 h")
    return out or ["Poca gente y ecosistema en buen estado"]


def reportes_vigentes(
    reportes: Iterable[Reporte], fecha: date, hora: int
) -> dict[str, list[Reporte]]:
    """Agrupa por playa los reportes de las últimas 3 horas hasta el cierre de la hora consultada."""
    fin_ventana = datetime.combine(fecha, time(hora, 59, 59))
    inicio_ventana = datetime.combine(fecha, time(hora, 0, 0)) - VENTANA_ANTES
    out: dict[str, list[Reporte]] = {}
    for r in reportes:
        ts = r.fecha_hora.replace(tzinfo=None)
        if inicio_ventana <= ts <= fin_ventana:
            out.setdefault(r.playa_id, []).append(r)
    return out


def evaluar(
    playas: list[PlayaInput], fecha: date, hora: int, festivo: bool,
    reportes: Iterable[Reporte] = (),
    origen_lat: Optional[float] = None, origen_lng: Optional[float] = None,
) -> list[PlayaSemaforoOut]:
    vigentes = reportes_vigentes(reportes, fecha, hora)
    base = []
    for p in playas:
        o = ocupacion(p, fecha, hora, festivo)
        o2 = ocupacion(p, fecha, hora + 2, festivo)
        rs = vigentes.get(p.id, [])
        if rs:
            p = p.model_copy(update={"sargazo": sum(r.sargazo for r in rs) / len(rs)})
            o = round((o + sum(r.ocupacion for r in rs) / len(rs)) / 2)
        e = estres(p, o)
        dist = None
        if origen_lat is not None and origen_lng is not None:
            dist = calcular_distancia_km(origen_lat, origen_lng, p.lat, p.lng)
        base.append((p, o, o2, e, semaforo(o, o2, e), len(rs), dist))

    def transporte(pl: PlayaInput) -> str:
        return pl.transporte or TRANSPORTE_DEFAULT

    resultado: list[PlayaSemaforoOut] = []
    for p, o, o2, e, sem, n_rep, dist in base:
        alternativas: list[AlternativaOut] = []
        if sem != "verde":
            otras = [b for b in base if b[0].id != p.id]
            verdes = sorted(
                (b for b in otras if b[4] == "verde"), key=lambda b: (b[1], b[3])
            )[:3]
            if verdes:
                alternativas = [
                    AlternativaOut(
                        id=b[0].id, nombre=b[0].nombre, ocupacion=b[1],
                        estres=b[3], transporte=transporte(b[0]),
                    )
                    for b in verdes
                ]
            else:
                menores = sorted(otras, key=lambda b: (b[3], b[1]))[:2]
                alternativas = [
                    AlternativaOut(
                        id=b[0].id, nombre=b[0].nombre, ocupacion=b[1],
                        estres=b[3],
                        transporte=transporte(b[0]) + SUFIJO_MENOR_IMPACTO,
                    )
                    for b in menores
                ]
        resultado.append(
            PlayaSemaforoOut(
                id=p.id, nombre=p.nombre, lat=p.lat, lng=p.lng,
                ocupacion=o, ocupacion_2h=o2, estres=e, semaforo=sem,
                motivos=motivos(p, o, o2, e, fecha, n_rep),
                transporte=transporte(p), alternativas=alternativas,
                distancia_km=dist,
            )
        )
    return resultado


def impacto(resultados: list[PlayaSemaforoOut], n_reportes: int = 0) -> ImpactoOut:
    detalle: list[ImpactoPlayaOut] = []
    for r in resultados:
        if r.semaforo == "verde" or not r.alternativas or r.estres == 0:
            continue
        mejor = min(r.alternativas, key=lambda a: a.estres)
        reduccion = max(0, round((r.estres - mejor.estres) / r.estres * 100))
        detalle.append(
            ImpactoPlayaOut(
                id=r.id, nombre=r.nombre, semaforo=r.semaforo, estres=r.estres,
                alternativa_id=mejor.id, alternativa_nombre=mejor.nombre,
                estres_alternativa=mejor.estres, reduccion_estres_pct=reduccion,
            )
        )
    promedio = round(sum(d.reduccion_estres_pct for d in detalle) / len(detalle)) if detalle else 0
    return ImpactoOut(
        playas_evaluadas=len(resultados), playas_en_riesgo=len(detalle),
        reduccion_promedio_pct=promedio, reportes_ciudadanos_activos=n_reportes,
        detalle=detalle,
    )
