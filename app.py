"""
╔══════════════════════════════════════════════════════════════════╗
║   PortfolioAI — Dashboard de Análisis de Portafolio por Perfil  ║
║   Seminario de Finanzas e Inteligencia Artificial                ║
╚══════════════════════════════════════════════════════════════════╝

Ejecutar con:  streamlit run app.py
Dependencias:  pip install streamlit yfinance plotly pandas numpy google-generativeai
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import google.generativeai as genai
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL DE LA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PortfolioAI · Análisis por Perfil",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS PERSONALIZADOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1321 50%, #0a1628 100%);
        color: #e2e8f0;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1629 0%, #111827 100%);
        border-right: 1px solid rgba(99,179,237,0.15);
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] p { color: #94a3b8 !important; font-size: 0.85rem; }

    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(99,179,237,0.2);
        border-radius: 12px;
        padding: 16px 20px;
        backdrop-filter: blur(10px);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.78rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-size: 1.6rem !important;
        font-weight: 700;
        font-family: 'DM Mono', monospace !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.85rem !important;
    }

    h1 { color: #e2e8f0 !important; font-weight: 700 !important; }
    h2 { color: #cbd5e1 !important; font-weight: 600 !important; }
    h3 { color: #94a3b8 !important; font-weight: 500 !important; }

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(99,179,237,0.15) !important;
        border-radius: 10px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #1e40af);
    }

    hr { border-color: rgba(99,179,237,0.15) !important; }

    .profile-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .badge-conservador { background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
    .badge-moderado    { background: rgba(59,130,246,0.2); color: #60a5fa; border: 1px solid rgba(96,165,250,0.3); }
    .badge-agresivo    { background: rgba(239,68,68,0.2);  color: #f87171; border: 1px solid rgba(248,113,113,0.3); }

    .info-card {
        background: rgba(15,23,42,0.7);
        border-left: 3px solid #3b82f6;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin: 12px 0;
        font-size: 0.9rem;
        color: #94a3b8;
        line-height: 1.6;
    }

    .conclusion-card {
        background: rgba(15,23,42,0.85);
        border: 1px solid rgba(99,179,237,0.25);
        border-radius: 14px;
        padding: 28px 32px;
        margin-top: 16px;
        line-height: 1.9;
        color: #e2e8f0;
        font-size: 0.95rem;
    }

    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTES Y PERFILES
# ─────────────────────────────────────────────

PERFILES = {
    "🛡️ Conservador": {
        "tickers": [
            "KO", "PEP", "PG", "JNJ", "MCD", "WMT", "MMM",
            "NESN.SW", "NOVN.SW", "OR.PA", "SAN.PA", "ULVR.L", "REP.MC",
            "MELI", "ABEV", "PBR",
        ],
        "color_accent": "#34d399",
        "badge_class": "badge-conservador",
        "descripcion": (
            "Empresas de gran capitalización con flujos de caja predecibles, "
            "dividendos estables y baja sensibilidad al ciclo económico. "
            "Incluye líderes defensivos de USA, Europa y América Latina. "
            "Ideal para preservar capital con rendimiento moderado."
        ),
        "palette": px.colors.sequential.Teal,
    },
    "⚖️ Moderado": {
        "tickers": [
            "AAPL", "MSFT", "GOOGL", "V", "JPM", "AMZN", "META", "BRK-B",
            "SAP", "ASML", "BMW.DE", "MC.PA", "SIE.DE",
            "TM", "SONY", "BABA",
        ],
        "color_accent": "#60a5fa",
        "badge_class": "badge-moderado",
        "descripcion": (
            "Tecnología madura y líderes de sector con sólidos fundamentos globales. "
            "Incluye gigantes de USA, campeones europeos industriales y tecnológicos, "
            "y grandes corporaciones asiáticas. Balance entre crecimiento y estabilidad."
        ),
        "palette": px.colors.sequential.Blues,
    },
    "🚀 Agresivo": {
        "tickers": [
            "TSLA", "NVDA", "AMD", "COIN", "MSTR", "PLTR", "SOFI", "RKLB",
            "NIO", "XPEV", "SE", "GRAB",
            "NU", "VTEX", "DESP", "GLOB",
        ],
        "color_accent": "#f87171",
        "badge_class": "badge-agresivo",
        "descripcion": (
            "Activos de alta beta con potencial de retorno extraordinario. "
            "Exposición a inteligencia artificial, vehículos eléctricos, fintech, "
            "criptoactivos y empresas emergentes de Asia y América Latina. "
            "Alta volatilidad; requiere horizonte de largo plazo y tolerancia al riesgo."
        ),
        "palette": px.colors.sequential.Reds,
    },
}

PERIODOS = {
    "📅 Último año":    365,
    "📅 Últimos 3 años": 365 * 3,
    "📅 Últimos 5 años": 365 * 5,
}

TASA_LIBRE_RIESGO    = 0.0
DIAS_TRADING_ANUALES = 252


# ─────────────────────────────────────────────
# FUNCIONES DE DATOS
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def descargar_datos(tickers: list, fecha_inicio: str, fecha_fin: str) -> pd.DataFrame:
    """Descarga precios de cierre ajustado. Excluye tickers que fallen."""
    datos_validos   = {}
    tickers_fallidos = []

    for ticker in tickers:
        try:
            df = yf.download(
                ticker,
                start=fecha_inicio,
                end=fecha_fin,
                auto_adjust=True,
                progress=False,
                timeout=15,
            )
            if df.empty:
                tickers_fallidos.append(ticker)
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            col = "Close" if "Close" in df.columns else ("Adj Close" if "Adj Close" in df.columns else None)
            if col is None:
                tickers_fallidos.append(ticker)
                continue

            serie = df[col].squeeze()
            if isinstance(serie, pd.DataFrame):
                serie = serie.iloc[:, 0]
            datos_validos[ticker] = serie

        except Exception:
            tickers_fallidos.append(ticker)

    if tickers_fallidos:
        st.warning(
            f"⚠️ Sin datos para: **{', '.join(tickers_fallidos)}**. "
            "Puede deberse a conectividad o ticker no disponible.",
            icon="⚠️",
        )

    if not datos_validos:
        return pd.DataFrame()

    df_combined = pd.concat(datos_validos, axis=1).dropna(how="all")
    df_combined.columns = list(datos_validos.keys())
    return df_combined


def calcular_metricas(precios: pd.DataFrame) -> pd.DataFrame:
    """Calcula CAGR, volatilidad, Sharpe y Max Drawdown por acción."""
    if precios.empty:
        return pd.DataFrame()

    retornos_diarios = precios.pct_change().dropna()
    n_dias  = len(precios)
    n_anios = n_dias / DIAS_TRADING_ANUALES

    metricas = {}
    for ticker in precios.columns:
        precio_inicio = precios[ticker].iloc[0]
        precio_fin    = precios[ticker].iloc[-1]

        rend_total = (precio_fin / precio_inicio - 1) * 100
        cagr = ((precio_fin / precio_inicio) ** (1 / n_anios) - 1) * 100 if n_anios > 0 else 0.0

        vol    = retornos_diarios[ticker].std() * np.sqrt(DIAS_TRADING_ANUALES) * 100
        r_med  = retornos_diarios[ticker].mean()
        v_dia  = retornos_diarios[ticker].std()
        sharpe = (r_med / v_dia * np.sqrt(DIAS_TRADING_ANUALES)) if v_dia > 0 else 0.0

        curva       = (1 + retornos_diarios[ticker]).cumprod()
        rolling_max = curva.cummax()
        max_dd      = ((curva - rolling_max) / rolling_max).min() * 100

        metricas[ticker] = {
            "Ticker":               ticker,
            "Precio Inicial ($)":   round(float(precio_inicio), 2),
            "Precio Final ($)":     round(float(precio_fin), 2),
            "Rend. Total (%)":      round(float(rend_total), 2),
            "CAGR (%)":             round(float(cagr), 2),
            "Volatilidad Anual (%)": round(float(vol), 2),
            "Ratio Sharpe":         round(float(sharpe), 3),
            "Max Drawdown (%)":     round(float(max_dd), 2),
        }

    return pd.DataFrame(metricas).T.reset_index(drop=True)


def rendimiento_acumulado(precios: pd.DataFrame) -> pd.DataFrame:
    """Normaliza precios a base 100 desde el primer día."""
    if precios.empty:
        return pd.DataFrame()
    return precios / precios.iloc[0] * 100


def top5_por_cagr(df_metricas: pd.DataFrame, df_precios: pd.DataFrame) -> pd.DataFrame:
    """Retorna el DataFrame de precios filtrado a las 5 acciones con mayor CAGR."""
    df_sorted    = df_metricas.sort_values("CAGR (%)", ascending=False)
    top5_tickers = df_sorted["Ticker"].head(5).tolist()
    columnas_ok  = [t for t in top5_tickers if t in df_precios.columns]
    return df_precios[columnas_ok]


# ─────────────────────────────────────────────
# FUNCIÓN DE IA — CONCLUSIÓN CON GEMINI
# ─────────────────────────────────────────────

def generar_conclusion(
    perfil_nombre: str,
    df_metricas: pd.DataFrame,
    top5_tickers: list,
    periodo_seleccionado: str,
    api_key: str,
) -> str:
    """
    Llama a Gemini Flash (gratis) para generar una conclusión en lenguaje
    simple interpretando todas las métricas del dashboard.
    """
    resumen_metricas = []
    for _, row in df_metricas.iterrows():
        try:
            resumen_metricas.append(
                f"- {row['Ticker']}: "
                f"CAGR {float(row['CAGR (%)']):+.1f}%, "
                f"Volatilidad {float(row['Volatilidad Anual (%)'])::.1f}%, "
                f"Sharpe {float(row['Ratio Sharpe']):.2f}, "
                f"Max Drawdown {float(row['Max Drawdown (%)'])::.1f}%"
            )
        except Exception:
            resumen_metricas.append(f"- {row['Ticker']}: datos incompletos")

    metricas_texto = "\n".join(resumen_metricas)
    top5_texto     = ", ".join(top5_tickers)

    prompt = f"""Sos un asesor financiero educativo que explica inversiones
en lenguaje muy simple para alguien que nunca invirtió en su vida.

Perfil de riesgo analizado: {perfil_nombre}
Período: {periodo_seleccionado}
Las 5 mejores acciones del perfil (por CAGR): {top5_texto}

Métricas completas del perfil:
{metricas_texto}

Escribí una conclusión clara que incluya estas 5 secciones con sus títulos en negrita:

**1. ¿Qué significa este perfil?**
Explicá en 2 oraciones simples qué tipo de inversor elige este perfil.

**2. ¿Qué nos dicen los números?**
Interpretá CAGR, volatilidad y Sharpe como si hablaras con alguien de 15 años.
Usá los números reales del análisis con ejemplos concretos tipo "si hubieras invertido $1000..."

**3. Las 3 mejores opciones para invertir hoy**
Para cada una explicá por qué en base a los datos. Sé específico con los números.

**4. ⚠️ Qué tener en cuenta antes de invertir**
2 advertencias importantes en lenguaje simple y directo.

**5. Conclusión final**
Una sola oración, como si le dijeras a un amigo dónde poner su plata hoy.

Escribí en español argentino, tono amigable y directo. Sin tecnicismos innecesarios.
Máximo 450 palabras. Usá emojis con moderación."""

    try:
        genai.configure(api_key=api_key)
        modelo    = genai.GenerativeModel("gemini-1.5-flash")
        respuesta = modelo.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"⚠️ No se pudo generar el análisis: {e}"


# ─────────────────────────────────────────────
# VISUALIZACIONES
# ─────────────────────────────────────────────

def grafico_evolucion(rend_acum: pd.DataFrame, subtitulo: str, color_accent: str) -> go.Figure:
    """Gráfico de líneas: top 5 acciones vs S&P 500."""
    COLORES = [
        "#60a5fa", "#34d399", "#f87171", "#a78bfa", "#fbbf24",
        "#38bdf8", "#fb923c", "#e879f9", "#4ade80", "#facc15",
    ]

    fig = go.Figure()

    for i, ticker in enumerate(rend_acum.columns):
        es_benchmark = ticker == "S&P 500"
        color = "rgba(148,163,184,0.7)" if es_benchmark else COLORES[i % len(COLORES)]
        dash  = "dot"    if es_benchmark else "solid"
        width = 1.5      if es_benchmark else 2.5

        fig.add_trace(go.Scatter(
            x=rend_acum.index,
            y=rend_acum[ticker],
            name=ticker,
            mode="lines",
            line=dict(width=width, color=color, dash=dash),
            hovertemplate=(
                f"<b>{ticker}</b><br>"
                "Fecha: %{x|%d %b %Y}<br>"
                "Valor base 100: <b>%{y:.1f}</b><extra></extra>"
            ),
        ))

    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color="rgba(148,163,184,0.3)",
        annotation_text="Base (inicio del período)",
        annotation_font_color="rgba(148,163,184,0.5)",
        annotation_font_size=11,
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Evolución del Rendimiento Acumulado</b>  ·  {subtitulo}",
            font=dict(size=15, color="#e2e8f0", family="Space Grotesk"),
            x=0.01,
        ),
        paper_bgcolor="rgba(10,14,26,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        legend=dict(
            bgcolor="rgba(10,14,26,0.7)",
            bordercolor="rgba(99,179,237,0.2)",
            borderwidth=1,
            font=dict(size=13, color="#e2e8f0"),
        ),
        xaxis=dict(
            gridcolor="rgba(99,179,237,0.08)",
            showline=True,
            linecolor="rgba(99,179,237,0.15)",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(99,179,237,0.08)",
            showline=True,
            linecolor="rgba(99,179,237,0.15)",
            tickfont=dict(family="DM Mono", size=11),
            title="Valor (Base 100)",
        ),
        hovermode="x unified",
        height=460,
        margin=dict(l=0, r=10, t=55, b=10),
    )
    return fig


def grafico_barras_metricas(df_metricas: pd.DataFrame, metrica: str, color_accent: str) -> go.Figure:
    """Barras horizontales para comparar una métrica entre acciones."""
    df_sorted = df_metricas.sort_values(metrica, ascending=True)
    valores   = df_sorted[metrica].astype(float)
    colores   = ["#34d399" if v >= 0 else "#f87171" for v in valores]

    fig = go.Figure(go.Bar(
        x=valores,
        y=df_sorted["Ticker"],
        orientation="h",
        marker_color=colores,
        marker_line_width=0,
        text=[f"{v:+.2f}" for v in valores],
        textposition="outside",
        textfont=dict(family="DM Mono", size=12, color="#e2e8f0"),
        hovertemplate=f"<b>%{{y}}</b><br>{metrica}: <b>%{{x:.2f}}</b><extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{metrica}</b>  por Acción",
            font=dict(size=14, color="#e2e8f0", family="Space Grotesk"),
            x=0.01,
        ),
        paper_bgcolor="rgba(10,14,26,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        xaxis=dict(gridcolor="rgba(99,179,237,0.08)", tickfont=dict(family="DM Mono", size=11)),
        yaxis=dict(tickfont=dict(size=13, color="#e2e8f0"), gridcolor="rgba(99,179,237,0.05)"),
        height=300,
        margin=dict(l=0, r=60, t=45, b=10),
    )
    return fig


def grafico_scatter_riesgo_retorno(df_metricas: pd.DataFrame, color_accent: str) -> go.Figure:
    """Scatter Riesgo vs. Retorno con tamaño proporcional al Sharpe."""
    df = df_metricas.copy()
    for col in ["Ratio Sharpe", "CAGR (%)", "Volatilidad Anual (%)"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    tamanios = (df["Ratio Sharpe"].abs() * 30 + 12).clip(upper=60)
    COLORES_SCATTER = ["#60a5fa", "#34d399", "#f87171", "#a78bfa", "#fbbf24"]

    fig = go.Figure()
    for i, (_, row) in enumerate(df.iterrows()):
        fig.add_trace(go.Scatter(
            x=[row["Volatilidad Anual (%)"]],
            y=[row["CAGR (%)"]],
            mode="markers+text",
            marker=dict(
                size=float(tamanios.iloc[i]),
                color=COLORES_SCATTER[i % len(COLORES_SCATTER)],
                opacity=0.85,
                line=dict(width=1.5, color="rgba(255,255,255,0.3)"),
            ),
            text=[row["Ticker"]],
            textposition="top center",
            textfont=dict(size=12, color="#e2e8f0", family="Space Grotesk"),
            name=row["Ticker"],
            hovertemplate=(
                f"<b>{row['Ticker']}</b><br>"
                f"Volatilidad: <b>{row['Volatilidad Anual (%)']:.1f}%</b><br>"
                f"CAGR: <b>{row['CAGR (%)']:.1f}%</b><br>"
                f"Sharpe: <b>{row['Ratio Sharpe']:.2f}</b>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(
            text="<b>Mapa Riesgo–Retorno</b>  (tamaño = |Sharpe|)",
            font=dict(size=14, color="#e2e8f0", family="Space Grotesk"),
            x=0.01,
        ),
        paper_bgcolor="rgba(10,14,26,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        xaxis=dict(title="Volatilidad Anual (%)", gridcolor="rgba(99,179,237,0.08)",
                   tickfont=dict(family="DM Mono", size=11)),
        yaxis=dict(title="CAGR (%)", gridcolor="rgba(99,179,237,0.08)",
                   tickfont=dict(family="DM Mono", size=11)),
        showlegend=False,
        height=380,
        margin=dict(l=0, r=10, t=45, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <div style='font-size:2.4rem; margin-bottom:4px;'>📈</div>
        <div style='font-size:1.1rem; font-weight:700; color:#e2e8f0; letter-spacing:0.05em;'>PortfolioAI</div>
        <div style='font-size:0.75rem; color:#4b6080; letter-spacing:0.12em; text-transform:uppercase;'>
            Análisis cuantitativo
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("**🎯 Perfil de riesgo**")
    perfil_seleccionado = st.selectbox(
        label="Perfil",
        options=list(PERFILES.keys()),
        index=1,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**⏱ Horizonte de análisis**")
    periodo_seleccionado = st.selectbox(
        label="Período",
        options=list(PERIODOS.keys()),
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("⚙️ Personalizar tickers (avanzado)"):
        tickers_default = ", ".join(PERFILES[perfil_seleccionado]["tickers"])
        tickers_input = st.text_input(
            "Tickers (separados por coma):",
            value=tickers_default,
            help="Ingresá tickers de Yahoo Finance separados por coma.",
        )
        usar_custom = st.checkbox("Usar mis propios tickers", value=False)

    st.markdown("---")

    # ── API Key de Gemini ──
    st.markdown("**🤖 Análisis con IA**")
    gemini_api_key = st.text_input(
        "API Key de Gemini (gratis):",
        type="password",
        placeholder="Pegá tu key acá",
        help="Obtenela gratis en aistudio.google.com sin tarjeta de crédito.",
        label_visibility="collapsed",
    )
    st.markdown("""
    <div style='font-size:0.72rem; color:#334155; line-height:1.5;'>
        🔑 Conseguí tu key gratis en<br>
        <a href='https://aistudio.google.com' target='_blank'
           style='color:#60a5fa;'>aistudio.google.com</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#334155; line-height:1.5; text-align:center;'>
        Datos provistos por Yahoo Finance.<br>
        Solo con fines educativos · No constituye asesoramiento financiero.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PARÁMETROS FINALES
# ─────────────────────────────────────────────

perfil_info        = PERFILES[perfil_seleccionado]
dias_atras         = PERIODOS[periodo_seleccionado]
fecha_fin          = datetime.today()
fecha_inicio       = fecha_fin - timedelta(days=dias_atras)
fecha_inicio_str   = fecha_inicio.strftime("%Y-%m-%d")
fecha_fin_str      = fecha_fin.strftime("%Y-%m-%d")

tickers_finales = (
    [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    if usar_custom and tickers_input.strip()
    else perfil_info["tickers"]
)

perfil_nombre_limpio = perfil_seleccionado.split(" ", 1)[-1]
badge_class          = perfil_info["badge_class"]
color_accent         = perfil_info["color_accent"]


# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────

st.markdown(f"""
<div style='padding: 28px 0 8px 0;'>
    <span class='profile-badge {badge_class}'>{perfil_nombre_limpio}</span>
    <h1 style='margin: 4px 0 0 0; font-size: 2.1rem; letter-spacing: -0.02em; line-height:1.2;'>
        Análisis de Portafolio
    </h1>
    <p style='color:#64748b; font-size:0.9rem; margin-top:6px;'>
        Período analizado: <b style='color:#94a3b8;'>{fecha_inicio.strftime("%d %b %Y")}</b>
        → <b style='color:#94a3b8;'>{fecha_fin.strftime("%d %b %Y")}</b>
        &nbsp;·&nbsp;
        Activos: <b style='color:#94a3b8;'>{", ".join(tickers_finales)}</b>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='info-card'>
    <b style='color:#e2e8f0;'>Estrategia {perfil_nombre_limpio}:</b><br>
    {perfil_info['descripcion']}
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────

with st.spinner("⏳ Descargando datos de mercado desde Yahoo Finance..."):
    df_precios = descargar_datos(tickers_finales, fecha_inicio_str, fecha_fin_str)

if df_precios.empty:
    st.error(
        "❌ No se pudieron obtener datos. Verificá tu conexión o intentá con otros tickers.",
        icon="🚨",
    )
    st.stop()

df_metricas = calcular_metricas(df_precios)

# Columnas numéricas
cols_num = ["Precio Inicial ($)", "Precio Final ($)", "Rend. Total (%)",
            "CAGR (%)", "Volatilidad Anual (%)", "Ratio Sharpe", "Max Drawdown (%)"]
for col in cols_num:
    if col in df_metricas.columns:
        df_metricas[col] = pd.to_numeric(df_metricas[col], errors="coerce")

# Top 5 por CAGR
df_top5    = top5_por_cagr(df_metricas, df_precios)
top5_lista = list(df_top5.columns)

# S&P 500 como benchmark
with st.spinner("⏳ Descargando S&P 500 como benchmark..."):
    df_spy = descargar_datos(["^GSPC"], fecha_inicio_str, fecha_fin_str)
    if not df_spy.empty:
        df_spy = df_spy.rename(columns={"^GSPC": "S&P 500"})

# Combinamos top 5 + S&P 500 para el gráfico
df_para_grafico = (
    pd.concat([df_top5, df_spy], axis=1).dropna(how="all")
    if not df_spy.empty else df_top5
)
df_rend_acum = rendimiento_acumulado(df_para_grafico)


# ─────────────────────────────────────────────
# SECCIÓN 1: KPIs
# ─────────────────────────────────────────────

st.markdown("### 📊 Métricas del Portafolio")

ticker_estrella = df_metricas.loc[df_metricas["CAGR (%)"].idxmax(), "Ticker"]
rend_prom  = df_metricas["Rend. Total (%)"].mean()
cagr_prom  = df_metricas["CAGR (%)"].mean()
vol_prom   = df_metricas["Volatilidad Anual (%)"].mean()
sharpe_prom = df_metricas["Ratio Sharpe"].mean()
dd_max     = df_metricas["Max Drawdown (%)"].min()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🏆 Mejor Acción", ticker_estrella,
              delta=f"CAGR: {df_metricas.loc[df_metricas['Ticker']==ticker_estrella, 'CAGR (%)'].values[0]:+.1f}%")
with col2:
    st.metric("📈 Rend. Promedio", f"{rend_prom:+.1f}%", delta=f"CAGR: {cagr_prom:+.1f}%")
with col3:
    st.metric("📉 Volatilidad Prom.", f"{vol_prom:.1f}%", delta="anualizada", delta_color="off")
with col4:
    st.metric("⚡ Sharpe Promedio", f"{sharpe_prom:.2f}", delta="rf = 0%", delta_color="off")
with col5:
    st.metric("⚠️ Max Drawdown", f"{dd_max:.1f}%", delta="peor caída del grupo", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECCIÓN 2: GRÁFICO DE EVOLUCIÓN — TOP 5 vs S&P 500
# ─────────────────────────────────────────────

st.markdown("### 📉 Evolución Acumulada — Top 5 vs S&P 500")

st.markdown(f"""
<div class='info-card'>
    El gráfico muestra las <b style='color:#e2e8f0;'>5 acciones con mayor crecimiento anual (CAGR)</b>
    del perfil <b style='color:#e2e8f0;'>{perfil_nombre_limpio}</b>
    comparadas contra el <b style='color:#e2e8f0;'>S&P 500</b> (línea punteada gris) como referencia de mercado.
    Una acción que supera la línea del S&P 500 le ganó al mercado en ese período.
</div>
""", unsafe_allow_html=True)

subtitulo    = f"Top 5: {', '.join(top5_lista)} vs S&P 500"
fig_evolucion = grafico_evolucion(df_rend_acum, subtitulo, color_accent)
st.plotly_chart(fig_evolucion, use_container_width=True)


# ─────────────────────────────────────────────
# SECCIÓN 3: TABLA COMPARATIVA
# ─────────────────────────────────────────────

st.markdown("### 🗂 Tabla Comparativa de Métricas")

def colorear_tabla(df):
    styled = df.style

    def color_rend(val):
        try:
            return "color: #34d399" if float(val) >= 0 else "color: #f87171"
        except Exception:
            return ""

    def color_sharpe(val):
        try:
            v = float(val)
            if v >= 1.0:   return "color: #34d399; font-weight: 600"
            elif v >= 0:   return "color: #fbbf24"
            else:          return "color: #f87171"
        except Exception:
            return ""

    for col in ["Rend. Total (%)", "CAGR (%)", "Max Drawdown (%)"]:
        if col in df.columns:
            styled = styled.map(color_rend, subset=[col])
    if "Ratio Sharpe" in df.columns:
        styled = styled.map(color_sharpe, subset=["Ratio Sharpe"])

    styled = styled.format({
        "Precio Inicial ($)":    "${:.2f}",
        "Precio Final ($)":      "${:.2f}",
        "Rend. Total (%)":       "{:+.2f}%",
        "CAGR (%)":              "{:+.2f}%",
        "Volatilidad Anual (%)": "{:.2f}%",
        "Ratio Sharpe":          "{:.3f}",
        "Max Drawdown (%)":      "{:.2f}%",
    })
    styled = styled.set_properties(**{
        "font-family": "DM Mono, monospace",
        "font-size":   "13px",
        "text-align":  "right",
    })
    return styled

st.dataframe(colorear_tabla(df_metricas), use_container_width=True, hide_index=True, height=230)

st.markdown("""
<div style='font-size:0.75rem; color:#334155; margin-top:4px;'>
    ℹ️ CAGR = Tasa de crecimiento anual compuesto · Sharpe calculado con Rf = 0% · 
    Drawdown medido sobre retornos ajustados.
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECCIÓN 4: ANÁLISIS COMPARATIVO
# ─────────────────────────────────────────────

st.markdown("### 🔬 Análisis Comparativo Avanzado")

col_a, col_b = st.columns([1, 1])

with col_a:
    metrica_barra = st.selectbox(
        "Métrica para comparar:",
        options=["CAGR (%)", "Rend. Total (%)", "Volatilidad Anual (%)", "Ratio Sharpe", "Max Drawdown (%)"],
        index=0,
    )
    fig_barras = grafico_barras_metricas(df_metricas, metrica_barra, color_accent)
    st.plotly_chart(fig_barras, use_container_width=True)

with col_b:
    st.markdown(
        "<p style='font-size:0.85rem;color:#64748b; padding-top:38px;'>"
        "Mapa Riesgo–Retorno: cada burbuja representa una acción. "
        "El tamaño indica el Ratio de Sharpe absoluto.</p>",
        unsafe_allow_html=True,
    )
    fig_scatter = grafico_scatter_riesgo_retorno(df_metricas, color_accent)
    st.plotly_chart(fig_scatter, use_container_width=True)


# ─────────────────────────────────────────────
# SECCIÓN 5: CORRELACIONES
# ─────────────────────────────────────────────

if len(df_precios.columns) > 1:
    st.markdown("### 🔗 Matriz de Correlación de Retornos")

    retornos    = df_precios.pct_change().dropna()
    corr_matrix = retornos.corr()

    fig_corr = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale=[[0.0, "#f87171"], [0.5, "#1e293b"], [1.0, "#34d399"]],
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont=dict(family="DM Mono", size=13, color="#e2e8f0"),
        hoverongaps=False,
        hovertemplate="<b>%{y} – %{x}</b><br>Correlación: <b>%{z:.2f}</b><extra></extra>",
    ))
    fig_corr.update_layout(
        paper_bgcolor="rgba(10,14,26,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        height=340,
        margin=dict(l=0, r=0, t=20, b=10),
        xaxis=dict(tickfont=dict(size=12, color="#e2e8f0")),
        yaxis=dict(tickfont=dict(size=12, color="#e2e8f0")),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("""
    <div style='font-size:0.78rem; color:#334155; margin-top:4px;'>
        ℹ️ Correlaciones próximas a <b style='color:#34d399;'>+1</b> implican movimientos conjuntos.
        Valores cercanos a <b style='color:#f87171;'>-1</b> indican movimientos opuestos (diversificación efectiva).
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECCIÓN 6: CONCLUSIÓN CON IA (GEMINI)
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("### 🤖 Conclusión e Interpretación con IA")

st.markdown("""
<div class='info-card'>
    Esta sección usa <b style='color:#e2e8f0;'>Inteligencia Artificial (Gemini)</b> para leer
    todos los gráficos y métricas del dashboard y explicarte en lenguaje simple
    <b style='color:#e2e8f0;'>dónde conviene invertir según tu perfil de riesgo</b>,
    con ejemplos concretos y sin tecnicismos.
</div>
""", unsafe_allow_html=True)

if st.button("✨ Generar análisis con IA", use_container_width=False):
    if not gemini_api_key or not gemini_api_key.strip():
        st.warning(
            "⚠️ Ingresá tu API Key de Gemini en el panel izquierdo. "
            "Es gratis y la conseguís en aistudio.google.com",
            icon="🔑",
        )
    else:
        with st.spinner("🧠 La IA está analizando todos los datos del portafolio..."):
            conclusion = generar_conclusion(
                perfil_nombre=perfil_nombre_limpio,
                df_metricas=df_metricas,
                top5_tickers=top5_lista,
                periodo_seleccionado=periodo_seleccionado,
                api_key=gemini_api_key.strip(),
            )

        # Convertimos el markdown de Gemini a HTML básico para mostrarlo bien
        conclusion_html = (
            conclusion
            .replace("**", "<b>", 1)
        )
        # Renderizamos con st.markdown para que interprete el formato de Gemini
        st.markdown(f"""
        <div class='conclusion-card'>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(conclusion)

        st.markdown("""
        <div style='font-size:0.72rem; color:#334155; margin-top:8px; text-align:right;'>
            Análisis generado por Gemini AI (Google) · Solo con fines educativos ·
            No constituye asesoramiento financiero profesional.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='
    border-top: 1px solid rgba(99,179,237,0.1);
    padding-top: 20px;
    text-align: center;
    color: #1e293b;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
'>
    PortfolioAI · Seminario de Finanzas e Inteligencia Artificial ·
    Datos: Yahoo Finance · Solo con fines educativos
</div>
""", unsafe_allow_html=True)
