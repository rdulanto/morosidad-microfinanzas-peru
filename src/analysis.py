"""Métricas del análisis de morosidad. Las usan el dashboard y el README."""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

MICRO = ["Mibanco", "Compartamos"]
TRADICIONAL = ["BCP", "BBVA", "Scotiabank", "Interbank"]
CONSUMO = ["Falabella", "Ripley"]


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    mor = pd.read_csv(RAW / "morosidad_bancos.csv", parse_dates=["fecha"], index_col="fecha").asfreq("MS")
    mac = pd.read_csv(RAW / "macro.csv", parse_dates=["fecha"], index_col="fecha").asfreq("MS")
    return mor, mac


def resumen(mor: pd.DataFrame) -> pd.DataFrame:
    """Pregunta 1: ¿la morosidad volvió a su nivel prepandemia?"""
    base = mor.loc["2019"].mean()
    post = mor.loc["2020":]
    ultimo = mor.ffill().iloc[-1]
    df = pd.DataFrame({
        "prom_2019": base,
        "pico": post.max(),
        "fecha_pico": post.idxmax().dt.strftime("%Y-%m"),
        "ultimo": ultimo,
        "vs_2019_pp": ultimo - base,
    })
    return df.round(2)


def brecha(mor: pd.DataFrame, entidad: str = "Mibanco", ref: str = "Banca total") -> pd.Series:
    """Pregunta 2: diferencia en puntos porcentuales frente a la banca total."""
    return (mor[entidad] - mor[ref]).rename(f"brecha_{entidad}")


def correlacion_rezagos(mor: pd.DataFrame, mac: pd.DataFrame, entidad: str = "Mibanco",
                        variable: str = "desempleo_lima", rezagos=(0, 3, 6, 9, 12)) -> pd.DataFrame:
    """Pregunta 3: ¿el desempleo anticipa la morosidad? Variaciones a 12 meses, con y sin pandemia."""
    y = mor[entidad].diff(12)
    filas = []
    for r in rezagos:
        x = mac[variable].diff(12).shift(r)
        d = pd.concat([y, x], axis=1).dropna()
        sin_covid = d[(d.index < "2020-03-01") | (d.index > "2022-12-31")]
        filas.append({"rezago_meses": r,
                      "corr_todo": d.corr().iloc[0, 1],
                      "corr_sin_pandemia": sin_covid.corr().iloc[0, 1],
                      "n_sin_pandemia": len(sin_covid)})
    return pd.DataFrame(filas).round(2)


def backtest(serie: pd.Series, horizonte: int = 6, desde: str = "2023-01-01") -> pd.DataFrame:
    """Pregunta 4: ¿se puede pronosticar a 6 meses mejor que 'repetir el último dato'?"""
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    s = serie.dropna()
    err = {"Ingenuo (último dato)": [], "Suavizado exponencial": [], "ARIMA(1,1,0)": []}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for corte in pd.date_range(desde, s.index[-1] - pd.DateOffset(months=horizonte), freq="MS"):
            tr = s[:corte]
            te = s[corte + pd.offsets.MonthBegin(1): corte + pd.offsets.MonthBegin(horizonte)]
            err["Ingenuo (último dato)"].append(np.abs(te.values - tr.iloc[-1]).mean())
            f = ExponentialSmoothing(tr, trend="add", damped_trend=True).fit().forecast(horizonte)
            err["Suavizado exponencial"].append(np.abs(te.values - f.values).mean())
            a = ARIMA(tr, order=(1, 1, 0)).fit().forecast(horizonte)
            err["ARIMA(1,1,0)"].append(np.abs(te.values - a.values).mean())
    out = pd.DataFrame({"modelo": list(err), "mae_pp": [np.mean(v) for v in err.values()],
                        "n_cortes": [len(v) for v in err.values()]})
    return out.round(3)
