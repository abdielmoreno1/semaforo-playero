"""Lógica pura de negocio (sin dependencias de FastAPI)."""
from datetime import date

from schemas import AlternativaOut, PlayaInput, PlayaSemaforoOut

CURVA: dict[int, float] = {
    6: 0.05, 7: 0.08, 8: 0.15, 9: 0.30, 10: 0.50, 11: 0.75, 12: 0.95,
    13: 1.0, 14: 0.95, 15: 0.85, 16: 0.65, 17: 0.40, 18: 0.20, 19: 0.08,
    20: 0.05,
}
MSG_TORTUGAS = "Temporada activa de anidación de tortugas (may-oct): evita zonas de dunas"
SUFIJO_MENOR_IMPACTO = " (alternativa de menor impacto)"


def ocupacion(playa: PlayaInput, fecha: date, hora: int, festivo: bool) -> int:
    factor_hora = CURVA.get(hora, 0.05)  # hora + 2 > 20 cae al valor base
    factor_dia = 1.0 if fecha.weekday() >= 5 else 0.7
    factor_festivo = 1.15 if festivo else 1.0
    valor = 100 * factor_hora * playa.popularidad * factor_dia * factor_festivo
    return max(0, min(100, round(valor)))


def estres(playa: PlayaInput, ocup: int) -> int:
    calor = max(0.0, min(100.0, (playa.temp_agua - 28.0) / 4.0 * 100.0))
    valor = (
        0.45 * playa.sargazo
        + 0.20 * calor
        + 0.20 * playa.fragilidad
        + 0.15 * ocup
    )
    return max(0, min(100, round(valor)))


def semaforo(o: int, o2: int, e: int) -> str:
    if o >= 85 or e >= 65 or (o >= 70 and e >= 50):
        return "rojo"
    if o >= 60 or o2 >= 75 or e >= 45:
        return "amarillo"
    return "verde"


def motivos(playa: PlayaInput, o: int, o2: int, e: int, fecha: date) -> list[str]:
    out: list[str] = []
    if o >= 85:
        out.append(f"Saturada: {o}% de ocupación")
    elif o2 >= 75 and o < 75:
        out.append(f"Se va a llenar: {o}% ahora, {o2}% en 2 horas")
    elif o >= 60:
        out.append(f"Ocupación alta: {o}%")
    if playa.sargazo >= 50:
        out.append("Mucho sargazo")
    elif playa.sargazo >= 30:
        out.append("Sargazo moderado")
    if playa.temp_agua >= 29.5:
        out.append(f"Agua cálida ({playa.temp_agua}°C): mayor estrés para el arrecife")
    if e >= 45 and playa.fragilidad >= 60 and playa.nota:
        out.append(playa.nota)
    if 5 <= fecha.month <= 10 and playa.fragilidad >= 60:
        out.append(MSG_TORTUGAS)
    return out or ["Poca gente y ecosistema en buen estado"]


def evaluar(
    playas: list[PlayaInput], fecha: date, hora: int, festivo: bool
) -> list[PlayaSemaforoOut]:
    base = []
    for p in playas:
        o = ocupacion(p, fecha, hora, festivo)
        o2 = ocupacion(p, fecha, hora + 2, festivo)
        e = estres(p, o)
        base.append((p, o, o2, e, semaforo(o, o2, e)))

    resultado: list[PlayaSemaforoOut] = []
    for p, o, o2, e, sem in base:
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
                        estres=b[3], transporte=b[0].transporte,
                    )
                    for b in verdes
                ]
            else:
                menores = sorted(otras, key=lambda b: (b[3], b[1]))[:2]
                alternativas = [
                    AlternativaOut(
                        id=b[0].id, nombre=b[0].nombre, ocupacion=b[1],
                        estres=b[3],
                        transporte=b[0].transporte + SUFIJO_MENOR_IMPACTO,
                    )
                    for b in menores
                ]
        resultado.append(
            PlayaSemaforoOut(
                id=p.id, nombre=p.nombre, lat=p.lat, lng=p.lng,
                ocupacion=o, ocupacion_2h=o2, estres=e, semaforo=sem,
                motivos=motivos(p, o, o2, e, fecha), transporte=p.transporte,
                alternativas=alternativas,
            )
        )
    return resultado
