"""Controles de calidad de datos: lo que haría un equipo de gobierno de datos antes de publicar."""
from __future__ import annotations

import pandas as pd


def saltos_mensuales(mor: pd.DataFrame, umbral_pp: float = 1.0) -> pd.DataFrame:
    """Marca variaciones de un mes a otro mayores al umbral (en puntos porcentuales)."""
    d = mor.diff()
    filas = [
        {"fecha": f.strftime("%Y-%m"), "entidad": c, "anterior": mor[c].shift(1)[f],
         "actual": mor[c][f], "variacion_pp": d[c][f]}
        for c in mor.columns for f in d.index[d[c].abs() > umbral_pp]
    ]
    return pd.DataFrame(filas).round(2)


def completitud(df: pd.DataFrame) -> pd.Series:
    """Porcentaje de meses con dato por serie."""
    return (df.notna().mean() * 100).round(1)
