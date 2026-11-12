"""Descarga series públicas del BCRP (API de estadísticas) y guarda CSV en data/raw.

Fuente: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
No requiere API key.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pandas as pd

API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codes}/json/{start}/{end}"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

# Cartera atrasada / colocaciones (%) por banco. Desde ene-2018 la serie es comparable
# (antes de esa fecha el BCRP la publicaba neta de provisiones; ver README).
MOROSIDAD = {
    "PN07746EM": "Banca total",
    "PN07737EM": "Mibanco",
    "PN43423EM": "Compartamos",
    "PN07729EM": "BCP",
    "PN07733EM": "BBVA",
    "PN07732EM": "Scotiabank",
    "PN07730EM": "Interbank",
    "PN07739EM": "Falabella",
    "PN07741EM": "Ripley",
}

MACRO = {
    "PD04722MM": "tasa_referencia",
    "PN07807NM": "tamn",
    "PN01728AM": "pbi_var_anual",
    "PN38063GM": "desempleo_lima",
    "PN01271PM": "inflacion_mensual",
}

MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
         "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}


def _periodo(nombre: str) -> pd.Timestamp:
    mes, anio = nombre.split(".")
    return pd.Timestamp(year=int(anio), month=MESES[mes], day=1)


def _fetch_one(code: str, start: str, end: str) -> pd.Series:
    url = API.format(codes=code, start=start, end=end)
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    idx, vals = [], []
    for p in data["periods"]:
        v = p["values"][0]
        idx.append(_periodo(p["name"]))
        vals.append(None if v in ("n.d.", "") else float(v))
    return pd.Series(vals, index=pd.DatetimeIndex(idx, name="fecha"), dtype="float64")


def fetch(series: dict[str, str], start: str = "2018-1", end: str = "2026-12") -> pd.DataFrame:
    """Una llamada por serie: la API no garantiza el orden de las columnas en llamadas múltiples."""
    return pd.DataFrame({name: _fetch_one(code, start, end) for code, name in series.items()})


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    fetch(MOROSIDAD).to_csv(RAW / "morosidad_bancos.csv")
    fetch(MACRO).to_csv(RAW / "macro.csv")
    print("Datos guardados en", RAW)


if __name__ == "__main__":
    main()
