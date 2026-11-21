import json
from datetime import date

import pytest
from fastapi.testclient import TestClient

import main
from engine import (
    MSG_REEF_SAFE, MSG_SIN_SARGAZO, MSG_TORTUGAS, estres, evaluar,
)
from schemas import PlayaInput


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "PLAYAS_PATH", tmp_path / "no_existe.json")
    monkeypatch.setattr(main, "REPORTES_PATH", tmp_path / "no_reportes.json")
    return TestClient(main.app)


def get(client, fecha, hora, festivo="false"):
    r = client.get("/api/playas", params={"fecha": fecha, "hora": hora, "festivo": festivo})
    assert r.status_code == 200
    return {p["id"]: p for p in r.json()}


def test_salud(client):
    assert client.get("/api/salud").json() == {"ok": True}


def test_sabado_13_delfines_rojo_con_alternativas_verdes(client):
    d = get(client, "2026-11-21", 13)
    delfines = d["delfines"]
    assert delfines["semaforo"] == "rojo"
    assert delfines["ocupacion"] == 100
    assert delfines["motivos"][0] == "Saturada: 100% de ocupación"
    assert delfines["alternativas"]
    for alt in delfines["alternativas"]:
        assert d[alt["id"]]["semaforo"] == "verde"
        assert set(alt) == {"id", "nombre", "ocupacion", "estres", "transporte"}
    ocups = [a["ocupacion"] for a in delfines["alternativas"]]
    assert ocups == sorted(ocups)
    assert d["langosta"]["alternativas"] == []


def test_lunes_7_todo_verde(client):
    d = get(client, "2026-11-23", 7)
    assert all(p["semaforo"] == "verde" and p["alternativas"] == [] for p in d.values())


def test_sabado_9_contraste(client):
    d9 = get(client, "2026-11-21", 9)
    d13 = get(client, "2026-11-21", 13)
    assert d9["delfines"]["semaforo"] == "amarillo"
    assert d13["delfines"]["semaforo"] == "rojo"
    assert d9["delfines"]["ocupacion"] < d13["delfines"]["ocupacion"]


def test_festivo_incrementa_ocupacion(client):
    normal = get(client, "2026-11-21", 12)
    festivo = get(client, "2026-11-21", 12, "true")
    assert festivo["langosta"]["ocupacion"] > normal["langosta"]["ocupacion"]
    assert get(client, "2026-11-21", 13, "true")["delfines"]["ocupacion"] == 100


def test_hora_20_ocupacion_2h_sin_error(client):
    d = get(client, "2026-11-21", 20)
    assert all(0 <= p["ocupacion_2h"] <= 100 for p in d.values())


def test_julio_alerta_tortugas_y_noviembre_no(client):
    julio = get(client, "2026-07-15", 10)
    assert MSG_TORTUGAS in julio["tortugas"]["motivos"]
    assert MSG_TORTUGAS not in julio["langosta"]["motivos"]
    nov = get(client, "2026-11-21", 10)
    assert MSG_TORTUGAS not in nov["tortugas"]["motivos"]


def test_hora_25_422(client):
    r = client.get("/api/playas", params={"fecha": "2026-11-21", "hora": 25})
    assert r.status_code == 422


def test_hot_reload_json(tmp_path, monkeypatch):
    f = tmp_path / "playas.json"
    f.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(main, "PLAYAS_PATH", f)
    c = TestClient(main.app)
    assert len(c.get("/api/playas", params={"fecha": "2026-11-21", "hora": 9}).json()) == 3
    f.write_text(
        '[{"id":"x","nombre":"X","lat":1,"lng":2,"popularidad":0.1,"sargazo":0,'
        '"temp_agua":28,"fragilidad":0,"transporte":"t","nota":""}]',
        encoding="utf-8",
    )
    r = c.get("/api/playas", params={"fecha": "2026-11-21", "hora": 9}).json()
    assert [p["id"] for p in r] == ["x"]


def test_fallback_sin_verdes_devuelve_2_menor_estres():
    def mk(i, estres_sarg):
        return PlayaInput(id=i, nombre=i, lat=0, lng=0, popularidad=1.0,
                          sargazo=estres_sarg, temp_agua=32, fragilidad=100,
                          transporte=f"bus-{i}", nota="")
    playas = [mk("a", 100), mk("b", 90), mk("c", 95), mk("d", 85)]
    res = {p.id: p for p in evaluar(playas, date(2026, 11, 21), 13, False)}
    assert all(p.semaforo == "rojo" for p in res.values())
    alts = res["a"].alternativas
    assert [x.id for x in alts] == ["d", "b"]
    assert all(x.transporte.endswith(" (alternativa de menor impacto)") for x in alts)
    assert "a" not in [x.id for x in res["d"].alternativas]


PLAYAS_CON_NULL = [
    {"id": "delfines", "nombre": "Playa Delfines", "lat": 21.06, "lng": -86.77,
     "popularidad": 1.0, "sargazo": None, "temp_agua": 28.87, "fragilidad": 70,
     "transporte": "", "nota": ""},
    {"id": "langosta", "nombre": "Playa Langosta", "lat": 21.14, "lng": -86.78,
     "popularidad": 0.4, "sargazo": 1, "temp_agua": 28.87, "fragilidad": None,
     "transporte": "Bus R-1 Km 5", "nota": ""},
    {"id": "langosta", "nombre": "Duplicada", "lat": 0, "lng": 0,
     "popularidad": 0.1, "sargazo": 0, "temp_agua": 28, "fragilidad": 0,
     "transporte": "x", "nota": ""},
]


@pytest.fixture()
def real(tmp_path, monkeypatch):
    f = tmp_path / "playas.json"
    f.write_text(json.dumps(PLAYAS_CON_NULL), encoding="utf-8")
    monkeypatch.setattr(main, "PLAYAS_PATH", f)
    rep_file = tmp_path / "reportes.json"
    rep_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(main, "REPORTES_PATH", rep_file)
    return TestClient(main.app), rep_file


def test_null_no_descarta_playas_ni_cuenta_como_cero(real):
    c, _ = real
    d = get(c, "2026-11-21", 13)
    assert set(d) == {"delfines", "langosta"}
    assert MSG_SIN_SARGAZO in d["delfines"]["motivos"]
    assert d["delfines"]["transporte"]
    p = PlayaInput(**PLAYAS_CON_NULL[0])
    assert estres(p, 100) > estres(p.model_copy(update={"sargazo": 0}), 100)


def test_reef_safe_en_playa_fragil(real):
    c, _ = real
    d = get(c, "2026-11-23", 7)
    assert MSG_REEF_SAFE in d["delfines"]["motivos"]
    assert MSG_REEF_SAFE not in d["langosta"]["motivos"]


def test_simulacion_reportes_json_recalibra_semaforo(real):
    c, rep_file = real
    hoy = "2026-11-23"
    antes = get(c, hoy, 10)["langosta"]
    assert antes["semaforo"] == "verde"
    
    # Simulamos que en data/reportes.json entraron 2 reportes de visitantes por QR
    simulados = [
        {"playa_id": "langosta", "fecha_hora": "2026-11-23T10:15:00", "sargazo": 80, "ocupacion": 90},
        {"playa_id": "langosta", "fecha_hora": "2026-11-23T10:20:00", "sargazo": 80, "ocupacion": 90},
    ]
    rep_file.write_text(json.dumps(simulados), encoding="utf-8")
    
    despues = get(c, hoy, 10)["langosta"]
    assert despues["semaforo"] != "verde"
    assert despues["ocupacion"] > antes["ocupacion"]
    assert any("reportes ciudadanos" in m for m in despues["motivos"])


def test_impacto_ecologico(client):
    r = client.get("/api/impacto", params={"fecha": "2026-11-21", "hora": 13})
    assert r.status_code == 200
    body = r.json()
    assert body["playas_en_riesgo"] >= 1
    det = {x["id"]: x for x in body["detalle"]}
    assert det["delfines"]["reduccion_estres_pct"] > 0
    assert det["delfines"]["estres_alternativa"] < det["delfines"]["estres"]
