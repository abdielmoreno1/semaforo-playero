from datetime import date

import pytest
from fastapi.testclient import TestClient

import main
from engine import MSG_TORTUGAS, evaluar
from schemas import PlayaInput


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Archivo inexistente -> fallback en memoria (datos deterministas).
    monkeypatch.setattr(main, "PLAYAS_PATH", tmp_path / "no_existe.json")
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
