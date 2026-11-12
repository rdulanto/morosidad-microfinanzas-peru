"""Dashboard: morosidad de la banca de microfinanzas en el Perú (2018–2026)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import analysis as A  # noqa: E402
import quality as Q  # noqa: E402

ACCENT, INK, MUTED, SAND, WARN = "#0F5E6E", "#1F2933", "#5B6770", "#E9E4D8", "#B4532A"
COLORS = {"Mibanco": ACCENT, "Compartamos": WARN, "Banca total": INK}

T = {
    "es": {
        "title": "¿La morosidad de las microfinanzas ya volvió a su nivel prepandemia?",
        "sub": "Cartera atrasada / colocaciones (%) por banco, enero 2018 a {last}. Fuente: BCRP.",
        "k1": "Mibanco hoy", "k2": "Banca total hoy", "k3": "Compartamos hoy",
        "vs19": "vs. 2019", "vs7": "en 7 meses",
        "h1": "1. Evolución de la morosidad",
        "pick": "Bancos a comparar",
        "covid": "Pandemia",
        "h2": "2. Brecha de Mibanco frente a la banca total",
        "pp": "puntos porcentuales",
        "h3": "3. ¿El desempleo anticipa la morosidad?",
        "h3d": "Correlación entre las variaciones a 12 meses del desempleo en Lima y de la morosidad de Mibanco, según cuántos meses se adelanta el desempleo.",
        "all": "Todo el periodo", "nocovid": "Sin pandemia (2020-03 a 2022-12)",
        "lag": "Meses de adelanto del desempleo",
        "h4": "4. ¿Se puede pronosticar a 6 meses?",
        "h4d": "Error medio absoluto en 39 pronósticos sucesivos (2023–2026). Menor es mejor.",
        "h5": "5. Controles de calidad de datos",
        "h5d": "Saltos de más de 1 punto en un mes. Antes de sacar conclusiones, hay que confirmarlos con la fuente.",
        "f1": "**Hallazgo:** sí, y por debajo. Mibanco está en {mib:.2f}%, 1.6 puntos menos que en 2019, tras un pico de 9.2% en marzo de 2021 y un segundo repunte en 2024, después de la recesión de 2023 (PBI −0.3%).",
        "f2": "**Hallazgo:** la prima de riesgo de las microfinanzas sobre la banca total cayó de 2.3 puntos (2019) a 1.0 punto en promedio en 2026. Solo estuvo más baja brevemente a inicios de 2023.",
        "f3": "**Hallazgo:** la relación existe, pero es más débil de lo que parece. Con la pandemia incluida, la correlación a 6 meses es 0.76; sin ella baja a 0.31. El desempleo sirve como alerta temprana, no como predictor por sí solo.",
        "f4": "**Hallazgo:** ningún modelo univariado supera claramente a \"repetir el último dato\" (ARIMA mejora apenas 0.02 puntos). El valor está en monitorear y explicar, no en pronosticar.",
        "f5": "**Hallazgo:** el salto de BCP de 2.67% a 4.04% en septiembre de 2026 es atípico frente a su historia y debe validarse antes de usarlo en decisiones.",
        "alert": "Compartamos es la excepción: su morosidad sube desde enero de 2026 mientras el resto del sistema mejora.",
        "foot": "Datos: API pública del BCRP. Código y metodología en GitHub. Autor: Ricardo Dulanto.",
    },
    "en": {
        "title": "Has microfinance delinquency returned to pre-pandemic levels?",
        "sub": "Past-due loans / total loans (%) by bank, January 2018 to {last}. Source: Central Reserve Bank of Peru (BCRP).",
        "k1": "Mibanco today", "k2": "Banking system today", "k3": "Compartamos today",
        "vs19": "vs. 2019", "vs7": "in 7 months",
        "h1": "1. Delinquency over time",
        "pick": "Banks to compare",
        "covid": "Pandemic",
        "h2": "2. Mibanco's gap vs. the banking system",
        "pp": "percentage points",
        "h3": "3. Does unemployment lead delinquency?",
        "h3d": "Correlation between 12-month changes in Lima unemployment and Mibanco delinquency, by how many months unemployment leads.",
        "all": "Full period", "nocovid": "Excluding pandemic (2020-03 to 2022-12)",
        "lag": "Months unemployment leads",
        "h4": "4. Can we forecast 6 months ahead?",
        "h4d": "Mean absolute error across 39 rolling forecasts (2023–2026). Lower is better.",
        "h5": "5. Data quality checks",
        "h5d": "Jumps above 1 point in a single month. They should be confirmed with the source before drawing conclusions.",
        "f1": "**Finding:** yes, and lower. Mibanco stands at {mib:.2f}%, 1.6 points below 2019, after a 9.2% peak in March 2021 and a second rise in 2024 following the 2023 recession (GDP −0.3%).",
        "f2": "**Finding:** the microfinance risk premium over the banking system fell from 2.3 points (2019) to a 1.0-point average in 2026. It was lower only briefly in early 2023.",
        "f3": "**Finding:** the link is real but weaker than it looks. Including the pandemic, the 6-month correlation is 0.76; excluding it, 0.31. Unemployment works as an early warning, not a standalone predictor.",
        "f4": "**Finding:** no univariate model clearly beats \"repeat the last value\" (ARIMA improves by just 0.02 points). The value lies in monitoring and explaining, not forecasting.",
        "f5": "**Finding:** BCP's jump from 2.67% to 4.04% in September 2026 is unusual against its history and should be validated before it informs decisions.",
        "alert": "Compartamos is the exception: its delinquency has been rising since January 2026 while the rest of the system improves.",
        "foot": "Data: BCRP public API. Code and methodology on GitHub. Author: Ricardo Dulanto.",
    },
}

st.set_page_config(page_title="Morosidad microfinanzas Perú", page_icon="📉", layout="wide")
st.markdown(
    """<style>
    .block-container{max-width:1100px;padding-top:2rem}
    h1{font-size:2rem!important;letter-spacing:-.02em}
    h3{margin-top:2.2rem!important}
    [data-testid=stMetricValue]{color:#0F5E6E}
    </style>""",
    unsafe_allow_html=True,
)

lang = st.radio("Idioma / Language", ["es", "en"], horizontal=True, label_visibility="collapsed",
                format_func=lambda x: "Español" if x == "es" else "English")
t = T[lang]


@st.cache_data
def data():
    mor, mac = A.load()
    return mor, mac, A.resumen(mor), A.correlacion_rezagos(mor, mac), A.backtest(mor["Mibanco"]), Q.saltos_mensuales(mor)


mor, mac, res, corr, bt, saltos = data()
last = mor["Mibanco"].dropna().index[-1].strftime("%Y-%m")


def layout(fig: go.Figure, h: int = 380, ytitle: str = "%") -> go.Figure:
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter, sans-serif", color=INK), legend=dict(orientation="h", y=1.08, x=0),
                      hovermode="x unified")
    fig.update_yaxes(title=ytitle, gridcolor=SAND, zeroline=False)
    fig.update_xaxes(gridcolor="white")
    return fig


st.title(t["title"])
st.caption(t["sub"].format(last=last))

c1, c2, c3 = st.columns(3)
c1.metric(t["k1"], f"{res.loc['Mibanco','ultimo']:.2f}%", f"{res.loc['Mibanco','vs_2019_pp']:+.2f} pp {t['vs19']}", delta_color="inverse")
c2.metric(t["k2"], f"{res.loc['Banca total','ultimo']:.2f}%", f"{res.loc['Banca total','vs_2019_pp']:+.2f} pp {t['vs19']}", delta_color="inverse")
cmp = mor["Compartamos"].dropna()
c3.metric(t["k3"], f"{cmp.iloc[-1]:.2f}%", f"{cmp.iloc[-1]-cmp.iloc[-8]:+.2f} pp {t['vs7']}", delta_color="inverse")

st.warning(t["alert"])

st.subheader(t["h1"])
st.markdown(t["f1"].format(mib=res.loc["Mibanco", "ultimo"]))
sel = st.multiselect(t["pick"], list(mor.columns), default=["Mibanco", "Compartamos", "Banca total"])
fig = go.Figure()
fig.add_vrect(x0="2020-03-01", x1="2022-12-31", fillcolor=SAND, opacity=.6, line_width=0, layer="below",
              annotation_text=t["covid"], annotation_position="top left", annotation_font_color=MUTED)
for c in sel:
    fig.add_scatter(x=mor.index, y=mor[c], name=c, mode="lines",
                    line=dict(color=COLORS.get(c, "#9AA5AE"), width=3 if c in COLORS else 1.5))
st.plotly_chart(layout(fig), use_container_width=True)

st.subheader(t["h2"])
st.markdown(t["f2"])
b = A.brecha(mor)
fig = go.Figure(go.Bar(x=b.index, y=b, marker_color=ACCENT, name="Mibanco − Banca total"))
st.plotly_chart(layout(fig, 300, t["pp"]), use_container_width=True)

st.subheader(t["h3"])
st.markdown(t["f3"])
st.caption(t["h3d"])
fig = go.Figure()
fig.add_bar(x=corr["rezago_meses"], y=corr["corr_todo"], name=t["all"], marker_color="#9AA5AE")
fig.add_bar(x=corr["rezago_meses"], y=corr["corr_sin_pandemia"], name=t["nocovid"], marker_color=ACCENT)
fig.update_xaxes(title=t["lag"], tickvals=corr["rezago_meses"])
st.plotly_chart(layout(fig, 320, "r"), use_container_width=True)

st.subheader(t["h4"])
st.markdown(t["f4"])
st.caption(t["h4d"])
st.dataframe(bt.rename(columns={"modelo": "Modelo" if lang == "es" else "Model", "mae_pp": "MAE (pp)", "n_cortes": "n"}),
             hide_index=True, use_container_width=True)

st.subheader(t["h5"])
st.markdown(t["f5"])
st.caption(t["h5d"])
st.dataframe(saltos.sort_values("fecha", ascending=False), hide_index=True, use_container_width=True)

st.divider()
st.caption(t["foot"])
