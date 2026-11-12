import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from quality import completitud, saltos_mensuales  # noqa: E402


def test_saltos_detecta_variacion_mayor_al_umbral():
    idx = pd.date_range("2026-01-01", periods=3, freq="MS")
    df = pd.DataFrame({"A": [2.0, 2.1, 3.5]}, index=idx)
    out = saltos_mensuales(df, umbral_pp=1.0)
    assert list(out["fecha"]) == ["2026-03"]
    assert out["variacion_pp"].iloc[0] == 1.4


def test_completitud():
    df = pd.DataFrame({"A": [1, None, 3, 4]})
    assert completitud(df)["A"] == 75.0
