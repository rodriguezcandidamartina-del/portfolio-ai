"""
╔══════════════════════════════════════════════════════════════════╗
║   PortfolioAI — Dashboard de Análisis de Portafolio por Perfil  ║
║   Seminario de Finanzas e Inteligencia Artificial                ║
╚══════════════════════════════════════════════════════════════════╝

Ejecutar con:  streamlit run app.py
Dependencias:  pip install streamlit yfinance plotly pandas numpy
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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
# ESTILOS PERSONALIZADOS (CSS inyectado)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Fuentes ── */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    /* ── Fondo oscuro premium ── */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1321 50%, #0a1628 100%);
        color: #e2e8f0;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1629 0%, #111827 100%);
        border-right: 1px solid rgba(99,179,237,0.15);
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] p {
        color: #94a3b8 !important;
        font-size: 0.85rem;
    }

    /* ── Tarjetas de métricas ── */
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

    /* ── Títulos ── */
    h1 { color: #e2e8f0 !important; font-weight: 700 !important; }
    h2 { color: #cbd5e1 !important; font-weight: 600 !important; }
    h3 { color: #94a3b8 !important; font-weight: 500 !important; }

    /* ── Tablas ── */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(99,179,237,0.15) !important;
        border-radius: 10px !important;
    }

    /* ── Botones ── */
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

    /* ── Divisores ── */
    hr {
        border-color: rgba(99,179,237,0.15) !important;
    }

    /* ── Badge de perfil ── */
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

    /* ── Info box ── */
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

    /* ── Ocultar footer de Streamlit ── */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTES Y CONFIGURACIÓN DE PERFILES
# ─────────────────────────────────────────────

PERFILES = {
    "🛡️ Conservador": {
        "tickers": [
            # USA — Defensivas
            "KO", "PEP", "PG", "JNJ", "MCD", "WMT", "MMM",
            # Europa
            "NESN.SW", "NOVN.SW", "OR.PA", "SAN.PA", "ULVR.L", "REP.MC",
            # América Latina
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
            # USA — Tecnología madura
            "AAPL", "MSFT", "GOOGL", "V", "JPM", "AMZN", "META", "BRK-B",
            # Europa
            "SAP", "ASML", "BMW.DE", "MC.PA", "SIE.DE",
            # Asia
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
            # USA — Alto crecimiento
            "TSLA", "NVDA", "AMD", "COIN", "MSTR", "PLTR", "SOFI", "RKLB",
            # Asia — Emergentes
            "NIO", "XPEV", "SE", "GRAB",
            # América Latina
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
    "📅 Último año": 365,
    "📅 Últimos 3 años": 365 * 3,
    "📅 Últimos 5 años": 365 * 5,
}

TASA_LIBRE_RIESGO = 0.0  # Simplificación para el seminario
DIAS_TRADING_ANUALES = 252


# ─────────────────────────────────────────────
# FUNCIONES DE DATOS Y MÉTRICAS
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def descargar_datos(tickers: list[str], fecha_inicio: str, fecha_fin: str) -> pd.DataFrame:
    """
    Descarga precios de cierre ajustado para una lista de tickers.
    Retorna un DataFrame con columnas = tickers, index = fecha.
    Los tickers que fallen se excluyen con un warning.
    """
    datos_validos = {}
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

            # Manejo robusto: columna Close o Adj Close
            # yfinance puede devolver MultiIndex; aplanamos
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if "Close" in df.columns:
                serie = df["Close"].squeeze()
                if isinstance(serie, pd.DataFrame):
                    serie = serie.iloc[:, 0]
                datos_validos[ticker] = serie
            elif "Adj Close" in df.columns:
                serie = df["Adj Close"].squeeze()
                if isinstance(serie, pd.DataFrame):
                    serie = serie.iloc[:, 0]
                datos_validos[ticker] = serie
            else:
                tickers_fallidos.append(ticker)
        except Exception as e:
            tickers_fallidos.append(ticker)

    if tickers_fallidos:
        st.warning(
            f"⚠️ No se pudieron cargar datos para: **{', '.join(tickers_fallidos)}**. "
            "Puede deberse a problemas de conectividad o que el ticker no esté disponible.",
            icon="⚠️",
        )

    if not datos_validos:
        return pd.DataFrame()

    df_combined = pd.concat(datos_validos, axis=1).dropna(how="all")
    df_combined.columns = list(datos_validos.keys())
    return df_combined


def calcular_metricas(precios: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas financieras clave por acción:
    - Rendimiento total (%)
    - Rendimiento anualizado (CAGR %)
    - Volatilidad anualizada (%)
    - Ratio de Sharpe anualizado
    - Precio inicial y final
    """
    if precios.empty:
        return pd.DataFrame()

    retornos_diarios = precios.pct_change().dropna()
    n_dias = len(precios)
    n_anios = n_dias / DIAS_TRADING_ANUALES

    metricas = {}
    for ticker in precios.columns:
        precio_inicio = precios[ticker].iloc[0]
        precio_fin = precios[ticker].iloc[-1]

        # Rendimiento total
        rend_total = (precio_fin / precio_inicio - 1) * 100

        # CAGR (Compound Annual Growth Rate)
        if n_anios > 0:
            cagr = ((precio_fin / precio_inicio) ** (1 / n_anios) - 1) * 100
        else:
            cagr = 0.0

        # Volatilidad anualizada
        vol = retornos_diarios[ticker].std() * np.sqrt(DIAS_TRADING_ANUALES) * 100

        # Ratio de Sharpe (con tasa libre de riesgo = 0)
        rend_medio_diario = retornos_diarios[ticker].mean()
        vol_diaria = retornos_diarios[ticker].std()
        sharpe = (rend_medio_diario / vol_diaria * np.sqrt(DIAS_TRADING_ANUALES)
                  if vol_diaria > 0 else 0.0)

        # Máximo drawdown
        curva = (1 + retornos_diarios[ticker]).cumprod()
        rolling_max = curva.cummax()
        drawdown = (curva - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100

        metricas[ticker] = {
            "Ticker": ticker,
            "Precio Inicial ($)": round(precio_inicio, 2),
            "Precio Final ($)": round(precio_fin, 2),
            "Rend. Total (%)": round(rend_total, 2),
            "CAGR (%)": round(cagr, 2),
            "Volatilidad Anual (%)": round(vol, 2),
            "Ratio Sharpe": round(sharpe, 3),
            "Max Drawdown (%)": round(max_drawdown, 2),
        }

    return pd.DataFrame(metricas).T.reset_index(drop=True)


def rendimiento_acumulado(precios: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el rendimiento porcentual acumulado normalizado
    (base 100) desde el primer día del período.
    """
    if precios.empty:
        return pd.DataFrame()
    return (precios / precios.iloc[0] * 100)


# ─────────────────────────────────────────────
# COMPONENTES DE VISUALIZACIÓN
# ─────────────────────────────────────────────

def grafico_evolucion(rend_acum: pd.DataFrame, perfil_nombre: str, color_accent: str) -> go.Figure:
    """Gráfico de líneas interactivo con rendimiento acumulado."""
    COLORES = [
        "#60a5fa", "#34d399", "#f87171", "#a78bfa", "#fbbf24",
        "#38bdf8", "#fb923c", "#e879f9", "#4ade80", "#facc15",
    ]

    fig = go.Figure()

    for i, ticker in enumerate(rend_acum.columns):
        color = COLORES[i % len(COLORES)]
        fig.add_trace(go.Scatter(
            x=rend_acum.index,
            y=rend_acum[ticker],
            name=ticker,
            mode="lines",
            line=dict(width=2.5, color=color),
            hovertemplate=(
                f"<b>{ticker}</b><br>"
                "Fecha: %{x|%d %b %Y}<br>"
                "Valor base 100: <b>%{y:.1f}</b><extra></extra>"
            ),
        ))

    # Línea de referencia en 100
    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color="rgba(148,163,184,0.4)",
        annotation_text="Base (inicio del período)",
        annotation_font_color="rgba(148,163,184,0.6)",
        annotation_font_size=11,
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Evolución del Rendimiento Acumulado</b>  ·  {perfil_nombre}",
            font=dict(size=16, color="#e2e8f0", family="Space Grotesk"),
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
            ticksuffix=" ",
            tickfont=dict(family="DM Mono", size=11),
            title="Valor (Base 100)",
        ),
        hovermode="x unified",
        height=440,
        margin=dict(l=0, r=10, t=50, b=10),
    )
    return fig


def grafico_barras_metricas(df_metricas: pd.DataFrame, metrica: str, color_accent: str) -> go.Figure:
    """Gráfico de barras horizontales para comparar una métrica."""
    df_sorted = df_metricas.sort_values(metrica, ascending=True)
    valores = df_sorted[metrica].astype(float)

    # Color condicional: verde positivo, rojo negativo
    colores = ["#34d399" if v >= 0 else "#f87171" for v in valores]

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
        xaxis=dict(
            gridcolor="rgba(99,179,237,0.08)",
            tickfont=dict(family="DM Mono", size=11),
        ),
        yaxis=dict(
            tickfont=dict(size=13, color="#e2e8f0"),
            gridcolor="rgba(99,179,237,0.05)",
        ),
        height=280,
        margin=dict(l=0, r=60, t=45, b=10),
    )
    return fig


def grafico_scatter_riesgo_retorno(df_metricas: pd.DataFrame, color_accent: str) -> go.Figure:
    """Scatter plot Riesgo vs. Retorno con tamaño proporcional al Sharpe."""
    df = df_metricas.copy()
    df["Ratio Sharpe"] = pd.to_numeric(df["Ratio Sharpe"], errors="coerce").fillna(0)
    df["CAGR (%)"] = pd.to_numeric(df["CAGR (%)"], errors="coerce").fillna(0)
    df["Volatilidad Anual (%)"] = pd.to_numeric(df["Volatilidad Anual (%)"], errors="coerce").fillna(0)

    # Tamaño de punto proporcional al Sharpe absoluto
    tamanios = (df["Ratio Sharpe"].abs() * 30 + 12).clip(upper=60)

    COLORES_SCATTER = ["#60a5fa", "#34d399", "#f87171", "#a78bfa", "#fbbf24"]

    fig = go.Figure()
    for i, row in df.iterrows():
        idx = int(i) if isinstance(i, int) else list(df.index).index(i)
        fig.add_trace(go.Scatter(
            x=[row["Volatilidad Anual (%)"]],
            y=[row["CAGR (%)"]],
            mode="markers+text",
            marker=dict(
                size=tamanios.iloc[idx] if hasattr(tamanios, 'iloc') else 20,
                color=COLORES_SCATTER[idx % len(COLORES_SCATTER)],
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
        xaxis=dict(
            title="Volatilidad Anual (%)",
            gridcolor="rgba(99,179,237,0.08)",
            tickfont=dict(family="DM Mono", size=11),
        ),
        yaxis=dict(
            title="CAGR (%)",
            gridcolor="rgba(99,179,237,0.08)",
            tickfont=dict(family="DM Mono", size=11),
        ),
        showlegend=False,
        height=380,
        margin=dict(l=0, r=10, t=45, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR — CONTROLES DEL USUARIO
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

    # Selector de perfil
    st.markdown("**🎯 Perfil de riesgo**")
    perfil_seleccionado = st.selectbox(
        label="Perfil",
        options=list(PERFILES.keys()),
        index=1,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Selector de período
    st.markdown("**⏱ Horizonte de análisis**")
    periodo_seleccionado = st.selectbox(
        label="Período",
        options=list(PERIODOS.keys()),
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tickers personalizados (avanzado)
    with st.expander("⚙️ Personalizar tickers (avanzado)"):
        tickers_default = ", ".join(PERFILES[perfil_seleccionado]["tickers"])
        tickers_input = st.text_input(
            "Tickers (separados por coma):",
            value=tickers_default,
            help="Ingresá tickers de Yahoo Finance separados por coma. Ej: AAPL, MSFT, GOOG",
        )
        usar_custom = st.checkbox("Usar mis propios tickers", value=False)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#334155; line-height:1.5; text-align:center;'>
        Datos provistos por Yahoo Finance.<br>
        Solo con fines educativos · No constituye asesoramiento financiero.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RESOLUCIÓN DE PARÁMETROS FINALES
# ─────────────────────────────────────────────

perfil_info = PERFILES[perfil_seleccionado]
dias_atras = PERIODOS[periodo_seleccionado]
fecha_fin = datetime.today()
fecha_inicio = fecha_fin - timedelta(days=dias_atras)
fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d")
fecha_fin_str = fecha_fin.strftime("%Y-%m-%d")

# Determinar tickers a usar
if usar_custom and tickers_input.strip():
    tickers_finales = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
else:
    tickers_finales = perfil_info["tickers"]

# Nombre limpio del perfil
perfil_nombre_limpio = perfil_seleccionado.split(" ", 1)[-1]  # sin emoji
badge_class = perfil_info["badge_class"]
color_accent = perfil_info["color_accent"]


# ─────────────────────────────────────────────
# ENCABEZADO PRINCIPAL
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

# Descripción del perfil
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

# Guard: sin datos
if df_precios.empty:
    st.error(
        "❌ No se pudieron obtener datos para los tickers seleccionados. "
        "Verificá tu conexión a internet o intentá con otros tickers.",
        icon="🚨",
    )
    st.stop()

# Calcular métricas y rendimiento acumulado
df_metricas = calcular_metricas(df_precios)
df_rend_acum = rendimiento_acumulado(df_precios)

# Columnas numéricas a float para cálculos
cols_num = ["Precio Inicial ($)", "Precio Final ($)", "Rend. Total (%)",
            "CAGR (%)", "Volatilidad Anual (%)", "Ratio Sharpe", "Max Drawdown (%)"]
for col in cols_num:
    if col in df_metricas.columns:
        df_metricas[col] = pd.to_numeric(df_metricas[col], errors="coerce")


# ─────────────────────────────────────────────
# SECCIÓN 1: MÉTRICAS DESTACADAS (KPIs)
# ─────────────────────────────────────────────

st.markdown("### 📊 Métricas del Portafolio")

# Acción principal = mayor CAGR del grupo
ticker_estrella = df_metricas.loc[df_metricas["CAGR (%)"].idxmax(), "Ticker"] \
    if not df_metricas.empty else tickers_finales[0]

# Métricas del portafolio igualmente ponderado
rend_prom = df_metricas["Rend. Total (%)"].mean()
cagr_prom = df_metricas["CAGR (%)"].mean()
vol_prom = df_metricas["Volatilidad Anual (%)"].mean()
sharpe_prom = df_metricas["Ratio Sharpe"].mean()
dd_max = df_metricas["Max Drawdown (%)"].min()  # el peor drawdown del grupo

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="🏆 Mejor Acción",
        value=ticker_estrella,
        delta=f"CAGR: {df_metricas.loc[df_metricas['Ticker']==ticker_estrella, 'CAGR (%)'].values[0]:+.1f}%",
    )
with col2:
    st.metric(
        label="📈 Rend. Promedio",
        value=f"{rend_prom:+.1f}%",
        delta=f"CAGR: {cagr_prom:+.1f}%",
    )
with col3:
    st.metric(
        label="📉 Volatilidad Prom.",
        value=f"{vol_prom:.1f}%",
        delta="anualizada",
        delta_color="off",
    )
with col4:
    st.metric(
        label="⚡ Sharpe Promedio",
        value=f"{sharpe_prom:.2f}",
        delta="rf = 0%",
        delta_color="off",
    )
with col5:
    st.metric(
        label="⚠️ Max Drawdown",
        value=f"{dd_max:.1f}%",
        delta="peor caída del grupo",
        delta_color="inverse",
    )

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECCIÓN 2: GRÁFICO DE EVOLUCIÓN
# ─────────────────────────────────────────────

st.markdown("### 📉 Evolución Acumulada")
fig_evolucion = grafico_evolucion(df_rend_acum, perfil_nombre_limpio, color_accent)
st.plotly_chart(fig_evolucion, use_container_width=True)


# ─────────────────────────────────────────────
# SECCIÓN 3: TABLA COMPARATIVA
# ─────────────────────────────────────────────

st.markdown("### 🗂 Tabla Comparativa de Métricas")

# Formateo visual con gradiente de color para columnas numéricas
def colorear_tabla(df):
    """Aplica colores semafóricos a columnas clave."""
    styled = df.style

    def color_rend(val):
        try:
            v = float(val)
            return "color: #34d399" if v >= 0 else "color: #f87171"
        except Exception:
            return ""

    def color_sharpe(val):
        try:
            v = float(val)
            if v >= 1.0:
                return "color: #34d399; font-weight: 600"
            elif v >= 0:
                return "color: #fbbf24"
            else:
                return "color: #f87171"
        except Exception:
            return ""

    for col in ["Rend. Total (%)", "CAGR (%)", "Max Drawdown (%)"]:
        if col in df.columns:
            styled = styled.map(color_rend, subset=[col])
    if "Ratio Sharpe" in df.columns:
        styled = styled.map(color_sharpe, subset=["Ratio Sharpe"])

    styled = styled.format({
        "Precio Inicial ($)": "${:.2f}",
        "Precio Final ($)": "${:.2f}",
        "Rend. Total (%)": "{:+.2f}%",
        "CAGR (%)": "{:+.2f}%",
        "Volatilidad Anual (%)": "{:.2f}%",
        "Ratio Sharpe": "{:.3f}",
        "Max Drawdown (%)": "{:.2f}%",
    })

    styled = styled.set_properties(**{
        "font-family": "DM Mono, monospace",
        "font-size": "13px",
        "text-align": "right",
    })

    return styled


st.dataframe(
    colorear_tabla(df_metricas),
    use_container_width=True,
    hide_index=True,
    height=230,
)

st.markdown("""
<div style='font-size:0.75rem; color:#334155; margin-top:4px;'>
    ℹ️ CAGR = Tasa de crecimiento anual compuesto · Sharpe calculado con Rf = 0% · Drawdown medido sobre retornos ajustados.
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SECCIÓN 4: ANÁLISIS VISUAL COMPARATIVO
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

    retornos = df_precios.pct_change().dropna()
    corr_matrix = retornos.corr()

    fig_corr = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale=[
            [0.0, "#f87171"],
            [0.5, "#1e293b"],
            [1.0, "#34d399"],
        ],
        zmin=-1, zmax=1,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont=dict(family="DM Mono", size=14, color="#e2e8f0"),
        hoverongaps=False,
        hovertemplate="<b>%{y} – %{x}</b><br>Correlación: <b>%{z:.2f}</b><extra></extra>",
    ))
    fig_corr.update_layout(
        paper_bgcolor="rgba(10,14,26,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(family="Space Grotesk", color="#94a3b8"),
        height=320,
        margin=dict(l=0, r=0, t=20, b=10),
        xaxis=dict(tickfont=dict(size=13, color="#e2e8f0")),
        yaxis=dict(tickfont=dict(size=13, color="#e2e8f0")),
        coloraxis_colorbar=dict(
            tickfont=dict(family="DM Mono", size=10, color="#94a3b8"),
            title=dict(text="ρ", font=dict(size=12, color="#94a3b8")),
        ),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("""
    <div style='font-size:0.78rem; color:#334155; margin-top:4px;'>
        ℹ️ Correlaciones próximas a <b style='color:#34d399;'>+1</b> implican movimientos conjuntos.
        Valores cercanos a <b style='color:#f87171;'>-1</b> indican movimientos opuestos (diversificación efectiva).
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
