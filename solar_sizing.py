import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import copy
import requests
from io import BytesIO

st.set_page_config(page_title="Solar Sizing Tool", page_icon="☀️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

  /* ── Tipografía global homologada ── */
  html, body, [class*="css"],
  .stMarkdown, .stTextInput, .stNumberInput, .stSlider,
  .stRadio, .stCheckbox, .stDataFrame, .stMetric,
  button, label, p, span, div { font-family: 'DM Sans', sans-serif !important; }

  /* Monoespaciado solo donde se necesita */
  .mono { font-family: 'DM Mono', monospace !important; }

  .main { background: #0f1117; }

  .section-header {
    font-size: 12px; font-weight: 600; color: #6b7280;
    text-transform: uppercase; letter-spacing: 0.10em;
    margin: 1.6rem 0 0.9rem; padding-bottom: 6px;
    border-bottom: 1px solid #2a2d3a;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] { background:#1a1d27; border-radius:10px; padding:4px; gap:4px; }
  .stTabs [data-baseweb="tab"]      { background:transparent; border-radius:8px; color:#9ca3af; font-weight:500; font-size:14px; }
  .stTabs [aria-selected="true"]    { background:#f59e0b !important; color:#0f1117 !important; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] { background:#13151f; border-right:1px solid #2a2d3a; }
  .stDataFrame { border-radius:10px; overflow:hidden; }

  /* ── Cabecera app ── */
  .app-title { font-size:30px; font-weight:600; color:#f9fafb; letter-spacing:-0.5px; }
  .app-sub   { font-size:14px; color:#6b7280; margin-top:-4px; margin-bottom:1.5rem; }

  /* ── Cajas informativas ── */
  .info-box { background:#1a1d27; border-left:3px solid #f59e0b; border-radius:0 8px 8px 0; padding:10px 14px; font-size:13px; color:#9ca3af; margin-bottom:1rem; }
  .nasa-box { background:#0f1f2e; border-left:3px solid #3b82f6; border-radius:0 8px 8px 0; padding:10px 14px; font-size:13px; color:#93c5fd; margin-bottom:1rem; }
  .warn-box { background:#1a1d27; border-left:3px solid #f43f5e; border-radius:0 8px 8px 0; padding:10px 14px; font-size:13px; color:#9ca3af; margin-bottom:1rem; }

  /* ── TOR Hero ── */
  .tor-hero {
    background: linear-gradient(135deg, #1a1d27 0%, #12151e 100%);
    border: 1px solid #2a2d3a; border-radius: 14px;
    padding: 20px 24px; margin-bottom: 1.4rem;
  }
  .tor-hero .th-project { font-size:11px; color:#6b7280; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px; }
  .tor-hero .th-meta    { font-size:12px; color:#6b7280; margin-bottom:16px; }
  .tor-hero .th-grid    { display:grid; grid-template-columns:repeat(4,1fr); gap:14px 20px; }
  .tor-hero .th-item    { display:flex; flex-direction:column; }
  .tor-hero .th-label   { font-size:10px; color:#6b7280; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:3px; }
  .tor-hero .th-val     { font-size:18px; font-weight:600; color:#f59e0b; font-family:'DM Mono',monospace; line-height:1.1; word-break:break-word; }
  .tor-hero .th-unit    { font-size:11px; color:#9ca3af; margin-top:3px; }

  /* ── Badges PR ── */
  .pr-badge  { display:inline-flex; align-items:center; gap:6px; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:500; }
  .pr-green  { background:#052e16; color:#4ade80; border:1px solid #166534; }
  .pr-yellow { background:#1c1a04; color:#facc15; border:1px solid #713f12; }
  .pr-red    { background:#1f0a0a; color:#f87171; border:1px solid #7f1d1d; }

  /* ── Panel card ── */
  .panel-card         { background:#1a1d27; border:1px solid #2a2d3a; border-radius:12px; padding:14px 18px; margin-bottom:1rem; }
  .panel-card .pc-title { font-size:11px; color:#6b7280; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:10px; }
  .panel-card .pc-grid  { display:grid; grid-template-columns:1fr 1fr; gap:6px 16px; }
  .panel-card .pc-item  { display:flex; flex-direction:column; }
  .panel-card .pc-label { font-size:10px; color:#6b7280; }
  .panel-card .pc-val   { font-size:13px; font-weight:500; color:#f59e0b; font-family:'DM Mono',monospace; }

  /* ── Snap cards financieras (KPIs) ──
       Solución al corte de números: altura automática, fuente adaptable */
  .snap-card {
    background:#13151f; border:1px solid #2a2d3a; border-radius:12px;
    padding:16px 12px; text-align:center;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    min-height:110px;
  }
  .snap-card .sc-label {
    font-size:10px; color:#6b7280; text-transform:uppercase;
    letter-spacing:0.07em; margin-bottom:6px; line-height:1.3;
    font-family:'DM Sans',sans-serif;
  }
  .snap-card .sc-val {
    font-size:clamp(13px, 1.4vw, 20px); font-weight:700;
    font-family:'DM Mono',monospace;
    word-break:break-word; overflow-wrap:anywhere;
    line-height:1.2; max-width:100%;
  }
  .snap-card .sc-sub {
    font-size:10px; color:#6b7280; margin-top:4px;
    line-height:1.3; font-family:'DM Sans',sans-serif;
  }

  /* ── Métricas pie de tabla (st.metric) — evitar corte ── */
  [data-testid="stMetric"] {
    background:#13151f; border:1px solid #2a2d3a; border-radius:12px;
    padding:14px 12px !important; text-align:center;
  }
  [data-testid="stMetricValue"] {
    font-family:'DM Mono',monospace !important;
    font-size:clamp(13px, 1.3vw, 20px) !important;
    font-weight:700 !important;
    word-break:break-word !important;
    overflow-wrap:anywhere !important;
    white-space:normal !important;
    line-height:1.2 !important;
  }
  [data-testid="stMetricLabel"] {
    font-family:'DM Sans',sans-serif !important;
    font-size:11px !important; color:#6b7280 !important;
    text-transform:uppercase; letter-spacing:0.06em;
  }

  /* ── Comparador ── */
  .comp-card           { background:#1a1d27; border:1px solid #2a2d3a; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
  .comp-card.active-run { border-color:#f59e0b66; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
MONTHS     = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
MONTH_DAYS = [31,28,31,30,31,30,31,31,30,31,30,31]
DEFAULT_IRR      = [4.8,5.2,5.9,6.1,5.8,5.4,5.3,5.2,4.7,4.5,4.6,4.5]
DEFAULT_CONS_REL = [1.05,1.00,0.95,0.90,0.95,1.10,1.15,1.10,1.00,0.95,0.95,1.10]
NASA_START, NASA_END = 2005, 2024

PR_DEFAULTS = {          # PR base por tipo de montaje (antes de pérdidas adicionales)
    "Techo plano":        0.76,
    "Techo inclinado":    0.80,
    "Suelo (ground)":     0.82,
    "Fachada":            0.72,
}
TENSION_OPTIONS  = ["400 V AC / 1000 V DC", "400 V AC / 1500 V DC", "600 V AC / 1000 V DC"]
TECH_OPTIONS     = ["Monocristalino PERC", "Monocristalino TOPCon", "Bifacial TOPCon",
                    "Policristalino", "Thin Film (CdTe)", "Thin Film (CIGS)"]

MEXICAN_CITIES = {
    "Ciudad de México":  (19.4326,  -99.1332),
    "Guadalajara":       (20.6767, -103.3475),
    "Monterrey":         (25.6866, -100.3161),
    "Mérida":            (20.9674,  -89.5926),
    "Hermosillo":        (29.0729, -110.9559),
    "Tijuana":           (32.5149, -117.0382),
    "Cancún":            (21.1619,  -86.8515),
    "Puebla":            (19.0414,  -98.2063),
    "León":              (21.1250, -101.6857),
    "Chihuahua":         (28.6320, -106.0691),
    "Querétaro":         (20.5888, -100.3899),
    "San Luis Potosí":   (22.1565, -100.9855),
    "Aguascalientes":    (21.8853, -102.2916),
    "Oaxaca":            (17.0732,  -96.7266),
    "Veracruz":          (19.1738,  -96.1342),
    "Personalizado":     (19.4326,  -99.1332),
}

PLOT_LAYOUT = dict(
    paper_bgcolor="#0f1117", plot_bgcolor="#13151f",
    font=dict(family="DM Sans", color="#9ca3af", size=12),
    xaxis=dict(gridcolor="#2a2d3a", linecolor="#2a2d3a", tickcolor="#2a2d3a"),
    yaxis=dict(gridcolor="#2a2d3a", linecolor="#2a2d3a", tickcolor="#2a2d3a"),
    margin=dict(l=10, r=10, t=30, b=10),
)
AMBER="#f59e0b"; TEAL="#14b8a6"; ROSE="#f43f5e"; BLUE="#3b82f6"; VIOLET="#8b5cf6"


# ── NASA POWER ────────────────────────────────────────────────────────────────
# ── NASA POWER (2005–2024) ────────────────────────────────────────────────────
@st.cache_data(ttl=7200, show_spinner=False)
def get_nasa_power_irradiance(lat: float, lon: float):
    """
    Devuelve una tupla (irr_media, irr_por_anio):
      irr_media   : list[12]  — promedio climatológico mensual (kWh/m²/día)
      irr_por_anio: dict[int, list[12]] — irradiancia mensual de cada año
                    {2005: [v_ene, v_feb, …, v_dic], 2006: …}
    Valores inválidos (< 0 o None) se sustituyen por el promedio del mes.
    """
    url = (
        "https://power.larc.nasa.gov/api/temporal/monthly/point"
        "?parameters=ALLSKY_SFC_SW_DWN&community=RE"
        f"&longitude={lon}&latitude={lat}&format=JSON"
        f"&start={NASA_START}&end={NASA_END}"
    )

    try:
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        data = r.json()

        raw = (data.get("properties", {})
                   .get("parameter", {})
                   .get("ALLSKY_SFC_SW_DWN", {}))

        if not raw:
            raise ValueError("NASA POWER no devolvió datos.")

        # ── 1. Construir serie por año ────────────────────────────────────────
        irr_por_anio: dict[int, list] = {}   # {año: [None]*12}
        monthly_sum   = [0.0] * 12
        monthly_count = [0]   * 12

        for key, value in raw.items():
            if len(key) != 6:
                continue
            try:
                year      = int(key[:4])
                month_idx = int(key[4:6]) - 1
                if not (0 <= month_idx <= 11):
                    continue
                if value is None or value < 0:
                    continue
                irr_por_anio.setdefault(year, [None] * 12)
                irr_por_anio[year][month_idx] = float(value)
                monthly_sum[month_idx]   += value
                monthly_count[month_idx] += 1
            except (ValueError, IndexError, TypeError):
                continue

        # ── 2. Promedio climatológico mensual ────────────────────────────────
        irr_media = [
            round(monthly_sum[i] / monthly_count[i], 4) if monthly_count[i] > 0
            else DEFAULT_IRR[i]
            for i in range(12)
        ]

        # ── 3. Rellenar meses faltantes en cada año con el promedio del mes ──
        for year, meses in irr_por_anio.items():
            for i in range(12):
                if meses[i] is None:
                    meses[i] = irr_media[i]

        return irr_media, irr_por_anio

    except requests.exceptions.Timeout:
        raise Exception("⏱️ Timeout: NASA POWER tardó demasiado.")
    except requests.exceptions.ConnectionError:
        raise Exception("🌐 Sin conexión a internet.")
    except Exception as e:
        raise Exception(f"❌ Error NASA POWER: {str(e)[:100]}")


# ── P90 riguroso: percentil 10 de la distribución de generaciones anuales ─────
def compute_p90(irr_por_anio: dict, kwp: float, pr: float) -> tuple:
    """
    Simula la generación anual para cada año histórico y devuelve:
      (p50_real, p90_real, gen_por_anio)
      p50_real    : mediana de las generaciones anuales (kWh)
      p90_real    : percentil 10 de las generaciones anuales (kWh)
                    — el sistema supera este valor el 90% de los años —
      gen_por_anio: dict {año: generación_kWh}
    Si no hay datos históricos, devuelve None para ambos percentiles.
    """
    if not irr_por_anio:
        return None, None, {}

    gen_por_anio = {}
    for year, meses in sorted(irr_por_anio.items()):
        gen_anual = sum(
            kwp * meses[m] * pr * MONTH_DAYS[m]
            for m in range(12)
        )
        gen_por_anio[year] = gen_anual

    valores = sorted(gen_por_anio.values())
    p50_real = float(np.percentile(valores, 50))
    p90_real = float(np.percentile(valores, 10))   # percentil 10 = excedido 90% de años
    return p50_real, p90_real, gen_por_anio



# ── Perfiles de consumo por tipo de cliente ───────────────────────────────────
# Índice mensual relativo — 1.0 = promedio anual
# Fuente: perfiles típicos México (CFE / ANES)
CLIENT_PROFILES = {
    "🏠 Residencial":   [1.05, 1.00, 0.95, 0.90, 0.95, 1.10, 1.15, 1.10, 1.00, 0.95, 0.95, 1.10],
    "🏢 Comercial":     [1.00, 1.00, 1.02, 1.03, 1.05, 1.08, 1.10, 1.08, 1.05, 1.02, 0.95, 0.90],
    "🏭 Industrial":    [1.02, 1.02, 1.02, 1.00, 1.00, 0.98, 0.95, 0.95, 1.00, 1.02, 1.02, 1.02],
    "🏪 Comercial-GD":  [0.90, 0.90, 0.95, 1.00, 1.05, 1.15, 1.20, 1.18, 1.10, 1.02, 0.95, 0.85],
    "🌡️ Clima cálido":  [0.80, 0.82, 0.90, 1.05, 1.15, 1.30, 1.38, 1.35, 1.20, 1.05, 0.90, 0.80],
}

# Tarifas CFE de referencia (MXN/kWh, bloques bimestral residencial DAC 2024)
CFE_TARIFAS_REF = {
    "1 — Residencial básica":    {"bloques": [300, 900], "precios": [0.79, 0.97, 2.85]},
    "1A — Residencial <25°C":    {"bloques": [400, 1800],"precios": [0.79, 0.97, 2.85]},
    "1B — Residencial <28°C":    {"bloques": [800, 2500],"precios": [0.79, 0.97, 2.85]},
    "1C — Residencial <30°C":    {"bloques": [1000, 3500],"precios":[0.79, 0.97, 2.85]},
    "1D — Residencial <33°C":    {"bloques": [1500, 5000],"precios":[0.79, 0.97, 2.85]},
    "1E — Residencial <34°C":    {"bloques": [2000, 7000],"precios":[0.79, 0.97, 2.85]},
    "1F — Residencial <34.5°C":  {"bloques": [2500,10000],"precios":[0.79, 0.97, 2.85]},
    "DAC — Alto consumo":        {"bloques": [],           "precios": [4.50]},
    "GDBT — Baja tensión":       {"bloques": [],           "precios": [2.20]},
    "GDMTH — Media tensión":     {"bloques": [],           "precios": [1.85]},
    "Personalizada":             {"bloques": [],           "precios": [2.80]},
}


# ── Funciones de cálculo cacheadas ───────────────────────────────────────────

@st.cache_data(show_spinner=False)
def calc_sizing_area(area_total: float, occ_factor: int,
                     panel_wp: int, panel_area: float,
                     irr_vals: tuple, effective_pr: float) -> dict:
    """Sizing por área: número de paneles, kWp y generación mensual."""
    n_panels  = int(math.floor(area_total * occ_factor / 100 / panel_area))
    kwp       = n_panels * panel_wp / 1000
    area_util = area_total * occ_factor / 100
    area_used = n_panels * panel_area
    monthly_gen = [round(kwp * irr_vals[m] * effective_pr * MONTH_DAYS[m], 1) for m in range(12)]
    return dict(n_panels=n_panels, kwp=kwp, area_util=area_util,
                area_used=area_used, monthly_gen=monthly_gen,
                annual_gen=sum(monthly_gen))


@st.cache_data(show_spinner=False)
def calc_sizing_recibo(consumo_bimestral: float, perfil: tuple,
                       solar_pct: int, sizing_strategy: str,
                       panel_wp: int, panel_area: float,
                       irr_vals: tuple, effective_pr: float,
                       occ_factor: int) -> dict:
    """Sizing por recibo CFE: kWp necesario según consumo y perfil de cliente."""
    consumo_mensual_base = consumo_bimestral / 2
    monthly_cons = [round(consumo_mensual_base * r, 1) for r in perfil]
    target_m = [c * solar_pct / 100 for c in monthly_cons]
    kwp_por_mes = [
        target_m[m] / (irr_vals[m] * effective_pr * MONTH_DAYS[m])
        if irr_vals[m] > 0 else 0 for m in range(12)
    ]
    kwp_raw  = max(kwp_por_mes) if "Peor" in sizing_strategy else sum(kwp_por_mes) / 12
    n_panels = int(math.ceil(kwp_raw * 1000 / panel_wp))
    kwp      = n_panels * panel_wp / 1000
    area_used = n_panels * panel_area
    area_util = area_used / (occ_factor / 100) if occ_factor > 0 else area_used
    monthly_gen = [round(kwp * irr_vals[m] * effective_pr * MONTH_DAYS[m], 1) for m in range(12)]
    return dict(n_panels=n_panels, kwp=kwp, area_util=area_util,
                area_used=area_used, monthly_gen=monthly_gen,
                annual_gen=sum(monthly_gen), monthly_cons=monthly_cons)


@st.cache_data(show_spinner=False)
def calc_sizing_recibo_detallado(monthly_cons: tuple, monthly_tarifas: tuple,
                                  solar_pct: int, sizing_strategy: str,
                                  panel_wp: int, panel_area: float,
                                  irr_vals: tuple, effective_pr: float,
                                  occ_factor: int) -> dict:
    """
    Sizing con consumos y tarifas mensuales reales (12 valores cada uno).
    Devuelve kWp, generación, ahorro real mes a mes y tarifa media ponderada.
    """
    target_m = [c * solar_pct / 100 for c in monthly_cons]
    kwp_por_mes = [
        target_m[m] / (irr_vals[m] * effective_pr * MONTH_DAYS[m])
        if irr_vals[m] > 0 else 0 for m in range(12)
    ]
    kwp_raw  = max(kwp_por_mes) if "Peor" in sizing_strategy else sum(kwp_por_mes) / 12
    n_panels = int(math.ceil(kwp_raw * 1000 / panel_wp))
    kwp      = n_panels * panel_wp / 1000
    area_used = n_panels * panel_area
    area_util = area_used / (occ_factor / 100) if occ_factor > 0 else area_used
    monthly_gen = [round(kwp * irr_vals[m] * effective_pr * MONTH_DAYS[m], 1) for m in range(12)]

    # Ahorro real mes a mes: energía cubierta × tarifa de ese mes
    energia_cubierta = [min(monthly_gen[m], monthly_cons[m]) for m in range(12)]
    ahorro_mensual   = [energia_cubierta[m] * monthly_tarifas[m] for m in range(12)]
    excedente        = [monthly_gen[m] - monthly_cons[m] for m in range(12)]
    cobertura_pct    = [
        min(100.0, monthly_gen[m] / monthly_cons[m] * 100) if monthly_cons[m] > 0 else 0.0
        for m in range(12)
    ]

    consumo_anual = sum(monthly_cons)
    gasto_actual  = sum(monthly_cons[m] * monthly_tarifas[m] for m in range(12))
    tarifa_media_pond = gasto_actual / consumo_anual if consumo_anual > 0 else 0

    return dict(
        n_panels=n_panels, kwp=kwp, area_util=area_util, area_used=area_used,
        monthly_gen=monthly_gen, annual_gen=sum(monthly_gen),
        monthly_cons=list(monthly_cons),
        energia_cubierta=energia_cubierta,
        ahorro_mensual=ahorro_mensual,
        ahorro_anual=sum(ahorro_mensual),
        excedente=excedente,
        cobertura_pct=cobertura_pct,
        cobertura_anual=sum(energia_cubierta) / consumo_anual * 100 if consumo_anual > 0 else 0,
        gasto_actual=gasto_actual,
        tarifa_media_pond=tarifa_media_pond,
        monthly_tarifas=list(monthly_tarifas),
    )


@st.cache_data(show_spinner=False)
def calc_financial_model(annual_gen: float, kwp: float, inversion_usd: float,
                         tarifa_efectiva: float, inflation: float,
                         discount_rate: float, panel_degradation: float,
                         vida_util: int, usd_to_mxn: float) -> dict:
    """Modelo financiero completo: VPN, TIR, payback, LCOE, flujos anuales."""
    years = list(range(1, vida_util + 1))
    r     = discount_rate / 100
    inv_mxn = inversion_usd * usd_to_mxn

    gen_proj      = [annual_gen * (1 - panel_degradation / 100) ** (y - 1) for y in years]
    tarifas_y     = [tarifa_efectiva * (1 + inflation / 100) ** (y - 1) for y in years]
    flujo_nominal = [gen_proj[i] * tarifas_y[i] for i in range(len(years))]
    om_anual      = [inv_mxn * 0.01 * (1 + inflation / 100) ** (y - 1) for y in years]
    flujo_neto    = [flujo_nominal[i] - om_anual[i] for i in range(len(years))]
    factor_desc   = [1 / (1 + r) ** y for y in years]
    flujo_desc    = [flujo_neto[i] * factor_desc[i] for i in range(len(years))]

    acum_nominal, acum = [], -inv_mxn
    for fn in flujo_neto:
        acum += fn; acum_nominal.append(acum)
    acum_desc, acum = [], -inv_mxn
    for fd in flujo_desc:
        acum += fd; acum_desc.append(acum)

    vpn = acum_desc[-1]

    # TIR — bisección
    def _irr(cf):
        def npv(rr): return sum(c / (1 + rr) ** t for t, c in enumerate(cf))
        try:
            lo, hi = -0.99, 2.0
            if npv(lo) * npv(hi) > 0: return None
            for _ in range(200):
                mid = (lo + hi) / 2
                fm = npv(mid)
                if abs(fm) < 1e-6 or (hi - lo) / 2 < 1e-6: return mid * 100
                if npv(lo) * fm < 0: hi = mid
                else: lo = mid
            return ((lo + hi) / 2) * 100
        except Exception: return None

    tir = _irr([-inv_mxn] + flujo_neto)
    pb_simple = next((years[i] for i, v in enumerate(acum_nominal) if v >= 0), None)
    pb_disc   = next((years[i] for i, v in enumerate(acum_desc)   if v >= 0), None)

    total_gen_desc  = sum(gen_proj[i] * factor_desc[i] for i in range(len(years)))
    total_cost_desc = inv_mxn + sum(om_anual[i] * factor_desc[i] for i in range(len(years)))
    lcoe = total_cost_desc / total_gen_desc if total_gen_desc > 0 else 0

    return dict(
        vpn=vpn, tir=tir, pb_simple=pb_simple, pb_disc=pb_disc, lcoe=lcoe,
        years=years, gen_proj=gen_proj, tarifas_y=tarifas_y,
        flujo_nominal=flujo_nominal, om_anual=om_anual, flujo_neto=flujo_neto,
        factor_desc=factor_desc, flujo_desc=flujo_desc,
        acum_nominal=acum_nominal, acum_desc=acum_desc, inv_mxn=inv_mxn,
    )


@st.cache_data(show_spinner=False)
def calc_ppa_result(gen1: float, inv_usd: float, precio_ppa: float,
                    plazo: int, wacc_pct: float, esc_ppa: float,
                    deg: float, om_pct: float, inf_om: float,
                    seg_pct: float, usd_mx: float, equity_pct: float,
                    tasa_deuda: float, plazo_deuda: int, con_fin: bool) -> dict:
    """Resultado financiero PPA para un plazo dado. Cacheado por todos sus parámetros."""
    inv_mxn    = inv_usd * usd_mx
    equity_mxn = inv_mxn * (equity_pct / 100)
    deuda_mxn  = inv_mxn - equity_mxn
    if con_fin and tasa_deuda > 0 and plazo_deuda > 0 and deuda_mxn > 0:
        r_d = tasa_deuda / 100
        serv_deuda = deuda_mxn * r_d / (1 - (1 + r_d) ** (-plazo_deuda))
    else:
        serv_deuda = 0.0; deuda_mxn = 0.0; equity_mxn = inv_mxn
    r      = wacc_pct / 100
    years  = list(range(1, plazo + 1))
    gen_y  = [gen1 * (1 - deg / 100) ** i for i in range(plazo)]
    prec_y = [precio_ppa * (1 + esc_ppa / 100) ** i for i in range(plazo)]
    ing_y  = [gen_y[i] * prec_y[i] for i in range(plazo)]
    om_y   = [inv_mxn * om_pct  / 100 * (1 + inf_om / 100) ** i for i in range(plazo)]
    seg_y  = [inv_mxn * seg_pct / 100 * (1 + inf_om / 100) ** i for i in range(plazo)]
    deu_y  = [serv_deuda if y <= plazo_deuda else 0.0 for y in years]
    fn_y   = [ing_y[i] - om_y[i] - seg_y[i] - deu_y[i] for i in range(plazo)]
    fd_y   = [fn_y[i] / (1 + r) ** years[i] for i in range(plazo)]
    vpn    = -equity_mxn + sum(fd_y)
    def _irr(cf):
        def npv(rr): return sum(c/(1+rr)**t for t,c in enumerate(cf))
        try:
            lo, hi = -0.99, 5.0
            if npv(lo)*npv(hi) > 0: return None
            for _ in range(200):
                mid=(lo+hi)/2
                fm=npv(mid)
                if abs(fm)<1e-6 or (hi-lo)/2<1e-6: return mid*100
                if npv(lo)*fm<0: hi=mid
                else: lo=mid
            return ((lo+hi)/2)*100
        except Exception: return None
    tir  = _irr([-equity_mxn]+fn_y)
    acum = -equity_mxn; pb = None
    for i, fn in enumerate(fn_y):
        acum += fn
        if acum >= 0: pb = years[i]; break
    return dict(vpn=vpn, tir=tir, pb=pb, ing_total=sum(ing_y),
                fn_y=fn_y, fd_y=fd_y, ing_y=ing_y, om_y=om_y,
                seg_y=seg_y, gen_y=gen_y, prec_y=prec_y, deu_y=deu_y,
                equity_mxn=equity_mxn, inv_mxn=inv_mxn, years=years)


@st.cache_data(show_spinner=False)
def calc_precio_minimo(gen1: float, inv_usd: float, plazo: int,
                       wacc_pct: float, esc_ppa: float, deg: float,
                       om_pct: float, inf_om: float, seg_pct: float,
                       usd_mx: float, equity_pct: float,
                       tasa_deuda: float, plazo_deuda: int, con_fin: bool):
    """Precio mínimo PPA (VPN=0) por bisección. Cacheado."""
    lo, hi = 0.01, 20.0
    def vpn_at(p):
        return calc_ppa_result(gen1, inv_usd, p, plazo, wacc_pct, esc_ppa,
                               deg, om_pct, inf_om, seg_pct, usd_mx,
                               equity_pct, tasa_deuda, plazo_deuda, con_fin)["vpn"]
    if vpn_at(hi) < 0: return None
    for _ in range(80):
        mid = (lo+hi)/2
        if vpn_at(mid) >= 0: hi = mid
        else: lo = mid
    return round((lo+hi)/2, 4)


    """Paneles que caben considerando pitch de filas y ancho de panel.
    
    panel_w : dimensión horizontal del panel (m) — depende de orientación
    panel_h : dimensión a lo largo de la fila   (m)
    row_gap : separación entre filas             (m)
    """
    area_util = area_total * occ_pct / 100
    pitch = panel_h + row_gap
    if pitch <= 0 or panel_w <= 0:
        return 0
    return int(math.floor(area_util / (pitch * panel_w)))


def pr_badge(pr_pct):
    if pr_pct >= 75:
        return f'<span class="pr-badge pr-green">● PR {pr_pct:.1f}% · Rango típico</span>'
    elif pr_pct >= 68:
        return f'<span class="pr-badge pr-yellow">● PR {pr_pct:.1f}% · Bajo — revisar pérdidas</span>'
    else:
        return f'<span class="pr-badge pr-red">● PR {pr_pct:.1f}% · Fuera de rango</span>'


def build_tor_text(proj_name, proj_date, proj_loc, proj_notes,
                   panel_wp, panel_eff, panel_largo_mm, panel_ancho_mm, panel_peso_kg,
                   panel_area, n_panels, kwp,
                   pr_pct, irr_vals, monthly_gen, annual_gen,
                   p50, p90, co2_saved,
                   inversion, ahorro1, payback,
                   gen_por_anio=None):
    lines = [
        "═══════════════════════════════════════════════════════════",
        f"  TÉRMINOS DE REFERENCIA — PRE-SIZING FOTOVOLTAICO",
        "═══════════════════════════════════════════════════════════",
        f"  Proyecto  : {proj_name}",
        f"  Fecha     : {proj_date}",
        f"  Ubicación : {proj_loc}",
        f"  Fuente irr: NASA POWER climatología {NASA_START}–{NASA_END}",
        "",
        "",
        "─── PARÁMETROS DEL PANEL (referencia) ──────────────────────",
        f"  Potencia pico (Pmax) : {panel_wp} Wp",
        f"  Eficiencia           : {panel_eff:.1f} %",
        f"  Dimensiones          : {panel_largo_mm} × {panel_ancho_mm} mm",
        f"  Área unitaria        : {panel_area:.4f} m²",
        f"  Peso                 : {panel_peso_kg} kg",
        "",
        "─── RESULTADOS DEL SIZING ──────────────────────────────────",
        f"  Paneles estimados    : {n_panels} unidades",
        f"  Capacidad pico       : {kwp:.2f} kWp",
        f"  PR asumido           : {pr_pct:.1f} %",
        f"  Generación P50       : {p50:,.0f} kWh/año",
        f"  Generación P90       : {f'{p90:,.0f} kWh/año  (percentil 10 · {len(gen_por_anio)} años NASA POWER {NASA_START}–{NASA_END})' if p90 else 'No disponible — cargar datos NASA POWER'}",
        f"  CO₂ evitado/año      : {co2_saved/1000:.2f} t  (factor 0.454 kg/kWh MX)",
        "",
        "─── IRRADIANCIA MENSUAL (kWh/m²/día) ──────────────────────",
    ]
    for i, m in enumerate(MONTHS):
        lines.append(f"  {m:>3} : {irr_vals[i]:.2f}   →   Gen: {monthly_gen[i]:>7,.0f} kWh")
    lines += [
        f"  {'TOTAL':>3}        →   Gen: {annual_gen:>7,.0f} kWh/año",
        "",
        "─── REFERENCIA FINANCIERA ──────────────────────────────────",
        f"  Inversión ref. (USD)  : ${inversion:,.0f}  (@ $1,000/kWp est.)",
        f"  Ahorro año 1 (MXN)    : ${ahorro1:,.0f}",
        f"  Payback simple        : {payback:.1f} años",
        "",
    ]
    if proj_notes.strip():
        lines += ["─── NOTAS / ALCANCE ────────────────────────────────────────",
                  f"  {proj_notes}", ""]
    lines += [
        "─── CONSIDERACIONES PARA COTIZACIÓN ────────────────────────",
        "  • Los valores son estimados de pre-sizing (±15%).",
        "  • El proveedor deberá realizar diseño detallado con software",
        "    (PVSyst, Helioscope, etc.) para confirmar generación.",
        "  • El P90 se calcula como percentil 10 de la generación simulada",
        f"    con {len(gen_por_anio) if gen_por_anio else 'N/A'} años de irradiancia real NASA POWER ({NASA_START}–{NASA_END}).",
        "  • Para mayor precisión solicitar simulación con PVSyst / Helioscope.",
        "  • Verificar disponibilidad de red y trámites CFE / CRE.",
        "═══════════════════════════════════════════════════════════",
    ]
    return "\n".join(lines)


# ── Session state initialization ──────────────────────────────────────────────
if "nasa_irradiance" not in st.session_state:
    st.session_state.nasa_irradiance = DEFAULT_IRR.copy()

if "nasa_irr_por_anio" not in st.session_state:
    st.session_state.nasa_irr_por_anio = {}   # vacío → P90 no disponible sin NASA

if "nasa_source_label" not in st.session_state:
    st.session_state.nasa_source_label = None

if "saved_runs" not in st.session_state:
    st.session_state.saved_runs = []


## ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("logo.png", width=275)   # Logo ocupa todo el ancho del sidebar
    st.markdown("---")
    st.markdown("### ☀️ Pre-Sizing")
    st.markdown("---")

    # ── Ubicación con Mapa (solo coordenadas en sidebar) ─────────────────────
    st.markdown("#### Ubicación")

    col_lat, col_lon = st.columns(2)
    lat = col_lat.number_input("Latitud", -90.0, 90.0, 19.4326, format="%.4f", key="lat_input")
    lon = col_lon.number_input("Longitud", -180.0, 180.0, -99.1332, format="%.4f", key="lon_input")

    st.caption(f"📍 Coordenadas actuales: **{lat:.4f}**, **{lon:.4f}**")

    # Botón único para NASA POWER
    if st.button("🌍 Obtener irradiancia NASA POWER (2005–2024)", 
                 type="primary", 
                 use_container_width=True, 
                 key="nasa_button"):
        with st.spinner("Consultando datos de NASA POWER..."):
            try:
                irr_media, irr_por_anio = get_nasa_power_irradiance(lat, lon)
                st.session_state.nasa_irradiance   = irr_media
                st.session_state.nasa_irr_por_anio = irr_por_anio
                st.session_state.nasa_source_label = f"({lat:.4f}, {lon:.4f})"
                n_anios = len(irr_por_anio)
                st.success(f"✅ Datos de NASA POWER cargados — {n_anios} años históricos ({NASA_START}–{NASA_END})")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.nasa_irradiance   = DEFAULT_IRR.copy()
                st.session_state.nasa_irr_por_anio = {}
                st.session_state.nasa_source_label = None

    lbl = st.session_state.get("nasa_source_label", None)
    st.caption(f"Fuente: NASA POWER (2005–2024) · {lbl}" if lbl else "Valores por defecto: CDMX")

    st.markdown("---")

    # ── Ficha técnica del panel ───────────────────────────────────────────────
    st.markdown("#### 📋 Panel (datos básicos)")
    panel_wp           = st.number_input("Potencia pico Pmax (Wp)", 100, 900, 650, 5)
    panel_eff_declared = st.number_input("Eficiencia (%)", 10.0, 26.0, 24.1, 0.01)
    panel_largo_mm     = st.number_input("Largo (mm)", 1000, 2500, 2382, 1)
    panel_ancho_mm     = st.number_input("Ancho (mm)", 700, 1300, 1134, 1)
    panel_peso_kg      = st.number_input("Peso (kg)", 5.0, 40.0, 32.7, .1)

    st.markdown("---")

    # ── PR del Sistema ───────────────────────────────────────────────────────
    st.markdown("#### ⚙️ Performance Ratio (PR) del sistema")

    st.markdown("""
    <div style="font-size:13px; color:#9ca3af; margin-bottom:10px;">
        PR global del sistema (incluye inversor, cableado, suciedad, mismatch, temperatura, etc.)
    </div>
    """, unsafe_allow_html=True)

    effective_pr = st.slider(
        "Performance Ratio (PR)",
        min_value=0.60,
        max_value=0.95,
        value=0.78,
        step=0.01,
        format="%.2f"
    )

    pr_pct = effective_pr * 100

    if pr_pct >= 82:
        badge_class = "pr-green"
        badge_text = "● Excelente"
    elif pr_pct >= 75:
        badge_class = "pr-yellow"
        badge_text = "● Bueno"
    else:
        badge_class = "pr-red"
        badge_text = "● Bajo — revisar diseño"

    st.markdown(f"""
    <div class="pr-badge {badge_class}" style="margin:10px 0 8px 0;">
        {badge_text} — PR {pr_pct:.1f}%
    </div>
    """, unsafe_allow_html=True)

    st.caption("Valor típico residencial en México: 0.75 – 0.82")

    # Degradación anual
    st.markdown("---")
    panel_degradation = st.slider("Degradación anual (%/año)", 0.3, 1.0, 0.5, 0.1, key="degradacion_anual")

    st.markdown("---")
    st.markdown("#### 💰 Referencia financiera")
    tarifa    = st.slider("Tarifa ref. área (MXN/kWh)", 1.0, 8.0, 2.80, 0.10, key="tarifa",
                          help="Usada en modo 'Por área'. En modo recibo CFE se usa la tarifa del recibo.")
    inflation = st.slider("Inflación tarifa anual (%)", 0.0, 8.0, 3.0, 0.5, key="inflation")
    discount_rate = st.slider("Tasa de descuento (%)", 0.0, 30.0, 15.0, 0.5, key="discount_rate",
                              help="Tasa usada para evaluación")
    usd_to_mxn    = st.slider("Tipo de Cambio (MXN por USD)", 16.0, 22.0, 17.50, 0.1, key="usd_to_mxn",
                              help="Tipo de cambio para evaluación financiera")
    vida_util = st.slider("Vida útil (años)", 10, 30, 25, 1, key="vida_util")
    costo_kwp = st.slider("Costo ref. instalación (USD/kWp)", 500, 2000, 1000, 50, key="costo_kwp")

    st.markdown("---")
    st.markdown(f"<div style='font-size:11px;color:#4b5563;'>v3.0 · NASA POWER {NASA_START}–{NASA_END} · México</div>",
                unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# Derived panel values (se calculan después del sidebar)
# ═════════════════════════════════════════════════════════════════════════════
panel_largo_m  = panel_largo_mm / 1000
panel_ancho_m  = panel_ancho_mm / 1000
panel_area     = panel_largo_m * panel_ancho_m
panel_eff_calc = (panel_wp / (panel_area * 1000)) * 100
eff_delta      = panel_eff_calc - panel_eff_declared
eff_ok         = abs(eff_delta) <= 0.5
eff_color      = "#14b8a6" if eff_ok else "#f43f5e"
eff_note       = "✓" if eff_ok else f"{'↑' if eff_delta>0 else '↓'}{abs(eff_delta):.1f}% vs declarada"


# ═════════════════════════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="app-title">☀️ Solar Sizing Tool</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="app-sub">Pre-sizing fotovoltaico · TOR para cotización · '
    f'Climatología NASA POWER {NASA_START}–{NASA_END}</div>',
    unsafe_allow_html=True)

tab1, tab3 = st.tabs(["📐  Sizing", "📄  PPA · Venta al Cliente"])
active_irr         = st.session_state.nasa_irradiance
active_irr_por_anio = st.session_state.nasa_irr_por_anio


def irr_source_banner():
    lbl = st.session_state.nasa_source_label
    if lbl:
        st.markdown(
            f'<div class="nasa-box">🌍 NASA POWER · Climatología {NASA_START}–{NASA_END} · {lbl} · Editable</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="info-box">Valores por defecto CDMX. Busca coordenada en el sidebar para modificar el sitio.</div>',
            unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — PRE-SIZING / TOR
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    col_p, col_r = st.columns([1, 1.8], gap="large")

    with col_p:
        # ── Datos del proyecto ─────────────────────────────────────────────────
        st.markdown('<div class="section-header">Datos del proyecto</div>', unsafe_allow_html=True)
        proj_loc  = st.text_input("Ubicación / dirección", value=f"{lat:.4f}, {lon:.4f}")

        # ── Mapa de ubicación ─────────────────────────────────────────────────
        st.markdown('<div class="section-header">Mapa de ubicación</div>', unsafe_allow_html=True)
        map_data = pd.DataFrame({"lat": [lat], "lon": [lon]})
        st.map(map_data, zoom=11, use_container_width=True)

        # ── Modo de dimensionamiento ───────────────────────────────────────────
        st.markdown('<div class="section-header">Modo de dimensionamiento</div>', unsafe_allow_html=True)
        sizing_mode = st.radio(
            "Método de sizing",
            ["📐 Por área disponible", "🧾 Por datos del recibo CFE"],
            horizontal=True,
            help="'Por área' calcula cuántos paneles caben. 'Por recibo' dimensiona según el consumo real del cliente."
        )
        uso_area = sizing_mode == "📐 Por área disponible"

        if uso_area:
            # ── Área disponible ────────────────────────────────────────────────
            st.markdown('<div class="section-header">Área disponible</div>', unsafe_allow_html=True)
            area_total = st.number_input("Área total disponible (m²)", 10.0, 50000.0, 200.0, 10.0)
            occ_factor = st.slider("Factor de ocupación (%)", 40, 95, 75, 5,
                help="% del área realmente aprovechable (sin obstáculos, accesos, bordes de seguridad)")
        else:
            # ── Datos del recibo CFE ───────────────────────────────────────────
            st.markdown('<div class="section-header">Datos del recibo CFE</div>', unsafe_allow_html=True)

            # ── Tipo de cliente ────────────────────────────────────────────────
            tipo_cliente = st.selectbox(
                "Tipo de cliente / perfil de consumo",
                list(CLIENT_PROFILES.keys()),
                help="Ajusta el patrón estacional cuando usas consumo único bimestral.")

            tarifa_ref_nombre = st.selectbox(
                "Tarifa CFE de referencia", list(CFE_TARIFAS_REF.keys()), key="tarifa_ref")
            tarifa_ref_data = CFE_TARIFAS_REF[tarifa_ref_nombre]

            # ── Modo de captura ────────────────────────────────────────────────
            modo_captura = st.radio(
                "Modo de captura",
                ["📋 Recibo único (promedio)", "📅 Histórico mensual (12 meses)"],
                horizontal=True,
                help="El histórico mensual da un sizing y un ahorro proyectado mucho más precisos.",
                key="modo_captura_recibo"
            )
            uso_historico = modo_captura == "📅 Histórico mensual (12 meses)"

            if not uso_historico:
                # ── MODO SIMPLE: un solo recibo bimestral ──────────────────────
                st.markdown('<div class="info-box">Captura el último recibo o el promedio de los últimos 6 meses.</div>', unsafe_allow_html=True)
                rec_consumo_bimestral = st.number_input(
                    "Consumo bimestral (kWh)", 100.0, 500000.0, 1200.0, 50.0,
                    help="kWh totales del período del recibo (2 meses)")
                rec_importe = st.number_input(
                    "Importe total del recibo (MXN)", 100.0, 5_000_000.0, 3500.0, 100.0)
                rec_demanda_kw = st.number_input(
                    "Demanda contratada / medida (kW)", 0.0, 10000.0, 0.0, 0.5,
                    help="Solo aplica tarifas industriales. Deja en 0 si no aplica.")

                st.markdown('<div class="section-header">Tarifa CFE</div>', unsafe_allow_html=True)
                rec_modo_tarifa = st.radio("Captura de tarifa",
                    ["Precio medio (simple)", "Por bloques"], horizontal=True, key="rec_modo_tar")

                if rec_modo_tarifa == "Precio medio (simple)":
                    tarifa_auto = round(rec_importe / max(rec_consumo_bimestral, 1), 3)
                    tarifa_media_recibo = st.number_input(
                        "Precio medio pagado (MXN/kWh)", 0.5, 20.0, tarifa_auto,
                        0.001, format="%.3f")
                else:
                    bloques_def = tarifa_ref_data["bloques"]
                    precios_def = tarifa_ref_data["precios"]
                    n_bloques   = len(precios_def)
                    bloques_kwh = []; bloques_pxkw = []
                    cols_b = st.columns(2)
                    for i in range(n_bloques):
                        with cols_b[0]:
                            bkwh = st.number_input(f"Bloque {i+1} kWh", 0.0, 50000.0,
                                float(bloques_def[i]) if i < len(bloques_def) else 0.0,
                                10.0, key=f"bkwh_{i}")
                            bloques_kwh.append(bkwh)
                        with cols_b[1]:
                            bpxkw = st.number_input(f"Precio {i+1} $/kWh", 0.0, 30.0,
                                float(precios_def[i]), 0.001, format="%.4f", key=f"bpxkw_{i}")
                            bloques_pxkw.append(bpxkw)
                    total_kwh_b = sum(bloques_kwh)
                    tarifa_media_recibo = (
                        sum(bloques_kwh[i]*bloques_pxkw[i] for i in range(n_bloques)) / total_kwh_b
                        if total_kwh_b > 0 else rec_importe / max(rec_consumo_bimestral, 1))
                    if total_kwh_b > 0 and len(precios_def) > 1:
                        st.markdown(f'<div class="nasa-box">💡 Tarifa media: <b>${tarifa_media_recibo:.4f}/kWh</b> · Bloque más caro: <b>${max(precios_def):.4f}/kWh</b></div>', unsafe_allow_html=True)

                # Construir arrays mensuales con perfil seleccionado
                cons_base_m = rec_consumo_bimestral / 2
                perfil_sel  = CLIENT_PROFILES[tipo_cliente]
                monthly_cons_input  = tuple(round(cons_base_m * r, 1) for r in perfil_sel)
                monthly_tar_input   = tuple(tarifa_media_recibo for _ in range(12))

            else:
                # ── MODO HISTÓRICO: captura mes a mes ──────────────────────────
                st.markdown('<div class="nasa-box">📅 Ingresa el consumo y precio medio de cada mes del último año. Puedes obtener estos datos de tus recibos bimestrales (divide entre 2) o de tu portal CFE.</div>', unsafe_allow_html=True)

                # Tarifa de referencia inicial para pre-llenar
                tarifa_ref_precio = tarifa_ref_data["precios"][0] if tarifa_ref_data["precios"] else 2.80

                # Construir defaults razonables
                cons_default = [500.0, 480.0, 460.0, 450.0, 470.0, 550.0,
                                600.0, 580.0, 510.0, 470.0, 460.0, 520.0]
                tar_default  = [round(tarifa_ref_precio * (1 + i * 0.005), 3) for i in range(12)]

                st.markdown('<div class="section-header">Consumo y tarifa mensual</div>', unsafe_allow_html=True)
                st.caption("Edita directamente en la tabla — el consumo es kWh mensuales y la tarifa el precio medio pagado ese mes.")

                df_hist = pd.DataFrame({
                    "Mes":              MONTHS,
                    "Consumo (kWh)":    cons_default,
                    "Tarifa (MXN/kWh)": tar_default,
                    "Importe (MXN)":    [round(cons_default[i]*tar_default[i], 0) for i in range(12)],
                })

                df_edit = st.data_editor(
                    df_hist,
                    column_config={
                        "Mes":              st.column_config.TextColumn(disabled=True),
                        "Consumo (kWh)":    st.column_config.NumberColumn(
                            min_value=0.0, max_value=2_000_000.0, step=10.0, format="%.0f"),
                        "Tarifa (MXN/kWh)": st.column_config.NumberColumn(
                            min_value=0.0, max_value=50.0, step=0.001, format="%.3f",
                            help="Precio medio pagado ese mes (importe ÷ kWh)"),
                        "Importe (MXN)":    st.column_config.NumberColumn(
                            min_value=0.0, step=100.0, format="%.0f",
                            help="Opcional — referencia visual. No afecta el cálculo."),
                    },
                    hide_index=True, use_container_width=True, key="hist_mensual",
                    num_rows="fixed",
                )

                monthly_cons_input = tuple(float(v) for v in df_edit["Consumo (kWh)"].tolist())
                monthly_tar_input  = tuple(float(v) for v in df_edit["Tarifa (MXN/kWh)"].tolist())

                # Resumen rápido
                consumo_anual_hist = sum(monthly_cons_input)
                gasto_anual_hist   = sum(monthly_cons_input[m] * monthly_tar_input[m] for m in range(12))
                tar_media_hist     = gasto_anual_hist / consumo_anual_hist if consumo_anual_hist > 0 else 0
                mes_max_idx        = monthly_cons_input.index(max(monthly_cons_input))
                mes_min_idx        = monthly_cons_input.index(min(monthly_cons_input))
                st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px;">
  <div class="snap-card" style="min-height:80px;">
    <div class="sc-label">Consumo anual</div>
    <div class="sc-val" style="font-size:15px;">{consumo_anual_hist:,.0f}</div>
    <div class="sc-sub">kWh/año</div>
  </div>
  <div class="snap-card" style="min-height:80px;">
    <div class="sc-label">Gasto anual CFE</div>
    <div class="sc-val" style="font-size:15px;">${gasto_anual_hist:,.0f}</div>
    <div class="sc-sub">MXN/año</div>
  </div>
  <div class="snap-card" style="min-height:80px;">
    <div class="sc-label">Tarifa media real</div>
    <div class="sc-val" style="color:#f59e0b;font-size:15px;">${tar_media_hist:.3f}</div>
    <div class="sc-sub">MXN/kWh ponderada</div>
  </div>
  <div class="snap-card" style="min-height:80px;">
    <div class="sc-label">Mes pico / valle</div>
    <div class="sc-val" style="font-size:13px;">{MONTHS[mes_max_idx]} / {MONTHS[mes_min_idx]}</div>
    <div class="sc-sub">{max(monthly_cons_input):,.0f} / {min(monthly_cons_input):,.0f} kWh</div>
  </div>
</div>
""", unsafe_allow_html=True)

                tarifa_media_recibo = tar_media_hist
                rec_demanda_kw = 0.0

            st.markdown('<div class="section-header">Objetivo de cobertura</div>', unsafe_allow_html=True)
            solar_pct = st.slider("% del consumo a cubrir con solar", 20, 100, 80, 5,
                                  help="80% es típico para evitar sobredimensionado")
            sizing_strategy = st.radio(
                "Estrategia de dimensionamiento",
                ["Peor mes (conservador)", "Promedio anual (económico)"],
                horizontal=True)
            area_total  = 0.0
            occ_factor  = 75

        # ── Irradiancia (siempre visible) ──────────────────────────────────────
        st.markdown('<div class="section-header">Irradiancia mensual (kWh/m²/día)</div>',
                    unsafe_allow_html=True)
        irr_source_banner()
        irr_df1 = pd.DataFrame({"Mes": MONTHS, "Irradiancia (kWh/m²/día)": active_irr})
        irr_ed1 = st.data_editor(irr_df1, column_config={
            "Mes": st.column_config.TextColumn(disabled=True),
            "Irradiancia (kWh/m²/día)": st.column_config.NumberColumn(
                min_value=0.0, max_value=10.0, step=0.0001, format="%.4f"),
        }, hide_index=True, use_container_width=True, key="irr1")
        irr_vals = irr_ed1["Irradiancia (kWh/m²/día)"].tolist()

    # ── Calculations — todo cacheado ───────────────────────────────────────────
    with col_r:

        irr_tuple = tuple(irr_vals)

        if uso_area:
            sz = calc_sizing_area(area_total, occ_factor, panel_wp, panel_area,
                                  irr_tuple, effective_pr)
            monthly_cons_ref = None
            monthly_tar_ref  = None
            tarifa_efectiva  = tarifa
            uso_historico_r  = False
        else:
            uso_historico_r = uso_historico
            if uso_historico:
                sz = calc_sizing_recibo_detallado(
                    monthly_cons_input, monthly_tar_input,
                    solar_pct, sizing_strategy,
                    panel_wp, panel_area,
                    irr_tuple, effective_pr, occ_factor)
                monthly_cons_ref = sz["monthly_cons"]
                monthly_tar_ref  = sz["monthly_tarifas"]
                tarifa_efectiva  = sz["tarifa_media_pond"]
            else:
                perfil_sel = tuple(CLIENT_PROFILES[tipo_cliente])
                sz = calc_sizing_recibo(rec_consumo_bimestral, perfil_sel,
                                        solar_pct, sizing_strategy,
                                        panel_wp, panel_area,
                                        irr_tuple, effective_pr, occ_factor)
                monthly_cons_ref = sz["monthly_cons"]
                monthly_tar_ref  = tuple(tarifa_media_recibo for _ in range(12))
                tarifa_efectiva  = tarifa_media_recibo

        n_panels   = sz["n_panels"]
        kwp        = sz["kwp"]
        area_util  = sz["area_util"]
        area_used  = sz["area_used"]
        monthly_gen = sz["monthly_gen"]
        annual_gen  = sz["annual_gen"]

        daily_avg   = annual_gen / 365
        co2_saved   = annual_gen * 0.454
        inversion   = kwp * costo_kwp
        # En modo histórico el ahorro real ya está calculado con tarifas mensuales reales
        if not uso_area and uso_historico_r and "ahorro_anual" in sz:
            ahorro1 = sz["ahorro_anual"]
        else:
            ahorro1 = annual_gen * tarifa_efectiva
        payback = inversion / ahorro1 if ahorro1 > 0 else 999

        # ── P50 / P90 riguroso con serie interanual NASA POWER ────────────────
        # Si el usuario no ha cargado datos NASA, no hay serie histórica y
        # se muestra un aviso en lugar de un número inventado.
        p50_real, p90_real, gen_por_anio = compute_p90(
            active_irr_por_anio, kwp, effective_pr
        )
        has_p90 = p50_real is not None
        # Para el TOR y comparador usamos P50 = generación con irr media editada
        p50 = annual_gen
        p90 = p90_real if has_p90 else None

        # ── TOR HERO — resultados en encabezado ───────────────────────────────
        area_label = f"{area_used:.0f} m² de {area_util:.0f} útiles" if uso_area else f"{area_used:.0f} m² estimados"
        st.markdown(f"""
<div class="tor-hero">
  <div class="th-project">📋 PRE-SIZING • {"ÁREA DISPONIBLE" if uso_area else "RECIBO CFE"}</div>
  <div class="th-meta">
    {proj_loc} &nbsp;·&nbsp; {pr_badge(pr_pct)}
    {"" if uso_area else f"&nbsp;·&nbsp; Tarifa media: <b>${tarifa_efectiva:.3f}/kWh</b>"}
  </div>
  <div class="th-grid">
    <div class="th-item">
      <span class="th-label">CAPACIDAD PICO</span>
      <span class="th-val">{kwp:.1f}</span>
      <span class="th-unit">kWp</span>
    </div>
    <div class="th-item">
      <span class="th-label">PANELES</span>
      <span class="th-val">{n_panels}</span>
      <span class="th-unit">unidades • {panel_wp} Wp</span>
    </div>
    <div class="th-item">
      <span class="th-label">GENERACIÓN P50</span>
      <span class="th-val">{p50/1000:.1f}</span>
      <span class="th-unit">MWh/año</span>
    </div>
    <div class="th-item">
      <span class="th-label">GENERACIÓN P90</span>
      <span class="th-val">{"—" if not has_p90 else f"{p90/1000:.1f}"}</span>
      <span class="th-unit">{"Carga NASA" if not has_p90 else "MWh/año"}</span>
    </div>
    <div class="th-item">
      <span class="th-label">{"ÁREA UTILIZADA" if uso_area else "COBERTURA SOLAR"}</span>
      <span class="th-val">{"—" if not uso_area else f"{area_used:.0f}"}</span>
      <span class="th-unit">{"m²" if uso_area else f"{round(annual_gen/max(sum(monthly_cons_ref),1)*100,1) if monthly_cons_ref else '—'}% del consumo"}</span>
    </div>
    <div class="th-item">
      <span class="th-label">INVERSIÓN REF.</span>
      <span class="th-val">${inversion:,.0f}</span>
      <span class="th-unit">USD</span>
    </div>
    <div class="th-item">
      <span class="th-label">AHORRO AÑO 1</span>
      <span class="th-val">${ahorro1:,.0f}</span>
      <span class="th-unit">MXN</span>
    </div>
    <div class="th-item">
      <span class="th-label">PAYBACK SIMPLE</span>
      <span class="th-val">{payback:.1f}</span>
      <span class="th-unit">años</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── ALERTA REGULATORIA para Generación Distribuida ─────────────────────
        if kwp > 699:
            st.error("⚠️ **Proyecto mayor a 699 kWp** — supera el límite típico de Generación Distribuida en México.")
        if uso_area:
            max_kwp_gd = 699
            area_max_gd = max_kwp_gd * 1000 / panel_wp * panel_area / (occ_factor / 100)
            st.caption(f"📏 Área máx. para GD (<700 kWp): **{area_max_gd:,.0f} m²** (con {occ_factor}% ocupación)")
        else:
            consumo_anual_ref = sum(monthly_cons_ref) if monthly_cons_ref else 0
            cobertura_pct = annual_gen / max(consumo_anual_ref, 1) * 100
            st.caption(f"📊 Consumo anual estimado: **{consumo_anual_ref:,.0f} kWh** · Cobertura: **{cobertura_pct:.1f}%** · Tarifa media: **${tarifa_efectiva:.3f}/kWh**")
        # ── Panel activo (mini card) ────────────────────────────────────────────
        st.markdown(f"""
<div class="panel-card">
  <div class="pc-title">📋 Panel de referencia</div>
  <div class="pc-grid">
    <div class="pc-item"><span class="pc-label">Potencia</span>
      <span class="pc-val">{panel_wp} Wp</span></div>
    <div class="pc-item"><span class="pc-label">Eficiencia calc.</span>
      <span class="pc-val" style="color:{eff_color}">{panel_eff_calc:.2f}%
        <span style="font-size:10px;color:{eff_color}">{eff_note}</span></span></div>
    <div class="pc-item"><span class="pc-label">Dimensiones</span>
      <span class="pc-val">{panel_largo_mm}×{panel_ancho_mm} mm</span></div>
    <div class="pc-item"><span class="pc-label">Área unitaria</span>
      <span class="pc-val">{panel_area:.4f} m²</span></div>
    <div class="pc-item"><span class="pc-label">Peso</span>
      <span class="pc-val">{panel_peso_kg} kg</span></div>
    <div class="pc-item"><span class="pc-label">Densidad potencia</span>
      <span class="pc-val">{panel_wp/panel_area:.0f} Wp/m²</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Si modo recibo: mostrar comparativa consumo vs generación ───────────
        if not uso_area and monthly_cons_ref:
            st.markdown('<div class="section-header">Generación vs Consumo mensual</div>', unsafe_allow_html=True)

            # Usar datos detallados si están disponibles
            if uso_historico_r and "ahorro_mensual" in sz:
                excedente_m = sz["excedente"]
                coverage_m  = sz["cobertura_pct"]
                ahorro_m    = sz["ahorro_mensual"]
                energy_cov  = sz["energia_cubierta"]
            else:
                excedente_m = [monthly_gen[m] - monthly_cons_ref[m] for m in range(12)]
                coverage_m  = [min(100, monthly_gen[m] / max(monthly_cons_ref[m], 1) * 100) for m in range(12)]
                tar_mes     = monthly_tar_ref if monthly_tar_ref else [tarifa_efectiva]*12
                ahorro_m    = [min(monthly_gen[m], monthly_cons_ref[m]) * tar_mes[m] for m in range(12)]
                energy_cov  = [min(monthly_gen[m], monthly_cons_ref[m]) for m in range(12)]

            fig_cv = go.Figure()
            fig_cv.add_trace(go.Bar(x=MONTHS, y=monthly_cons_ref, name="Consumo",
                marker_color="#374151",
                hovertemplate="<b>%{x}</b><br>Consumo: %{y:,.0f} kWh<extra></extra>"))
            fig_cv.add_trace(go.Bar(x=MONTHS, y=energy_cov, name="Cubierto solar",
                marker_color=AMBER,
                hovertemplate="<b>%{x}</b><br>Cubierto: %{y:,.0f} kWh<extra></extra>"))
            fig_cv.add_trace(go.Scatter(x=MONTHS, y=monthly_gen, mode="lines+markers",
                name="Generación total", line=dict(color=TEAL, width=2, dash="dot"),
                marker=dict(size=6, color=TEAL),
                hovertemplate="<b>%{x}</b><br>Generación: %{y:,.0f} kWh<extra></extra>"))
            lyt_cv = copy.deepcopy(PLOT_LAYOUT)
            lyt_cv.update({"height": 270, "barmode": "overlay",
                           "yaxis": dict(title="kWh", gridcolor="#2a2d3a"),
                           "legend": dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"),
                           "margin": dict(l=20, r=20, t=30, b=40)})
            fig_cv.update_layout(**lyt_cv)
            st.plotly_chart(fig_cv, use_container_width=True)

            # ── Gráfica de tarifas mensuales (solo modo histórico) ─────────────
            if uso_historico_r and monthly_tar_ref:
                fig_tar = go.Figure()
                fig_tar.add_trace(go.Scatter(
                    x=MONTHS, y=list(monthly_tar_ref),
                    mode="lines+markers+text",
                    line=dict(color=VIOLET, width=2.5),
                    marker=dict(size=8, color=VIOLET),
                    text=[f"${t:.3f}" for t in monthly_tar_ref],
                    textposition="top center",
                    textfont=dict(size=10, family="DM Mono"),
                    name="Tarifa CFE real",
                    hovertemplate="<b>%{x}</b><br>Tarifa: $%{y:.3f}/kWh<extra></extra>"))
                fig_tar.add_trace(go.Bar(
                    x=MONTHS, y=ahorro_m, name="Ahorro mensual (MXN)",
                    yaxis="y2", marker_color=TEAL, opacity=0.5,
                    hovertemplate="<b>%{x}</b><br>Ahorro: $%{y:,.0f} MXN<extra></extra>"))
                lyt_tar = copy.deepcopy(PLOT_LAYOUT)
                lyt_tar.update({
                    "height": 240,
                    "yaxis":  dict(title="MXN/kWh", gridcolor="#2a2d3a", tickformat=".3f"),
                    "yaxis2": dict(title="Ahorro (MXN)", overlaying="y", side="right",
                                  tickformat=",", tickfont=dict(color=TEAL)),
                    "legend": dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"),
                    "margin": dict(l=20, r=60, t=30, b=40),
                })
                fig_tar.update_layout(**lyt_tar)
                st.plotly_chart(fig_tar, use_container_width=True)

            # ── Tabla mensual ──────────────────────────────────────────────────
            st.markdown('<div class="section-header">Tabla mensual detallada</div>', unsafe_allow_html=True)
            tar_display = monthly_tar_ref if monthly_tar_ref else [tarifa_efectiva]*12
            df_tabla = pd.DataFrame({
                "Mes":               MONTHS,
                "Consumo (kWh)":    [f"{v:,.0f}" for v in monthly_cons_ref],
                "Generación (kWh)": [f"{v:,.0f}" for v in monthly_gen],
                "Cubierto (kWh)":   [f"{v:,.0f}" for v in energy_cov],
                "Cobertura (%)":    [f"{v:.1f}%" for v in coverage_m],
                "Excedente (kWh)":  [f"+{v:,.0f}" if v >= 0 else f"{v:,.0f}" for v in excedente_m],
                "Tarifa ($/kWh)":   [f"${t:.3f}" for t in tar_display],
                "Ahorro (MXN)":     [f"${v:,.0f}" for v in ahorro_m],
            })
            st.dataframe(df_tabla, use_container_width=True, hide_index=True)

            # Resumen anual
            cobertura_anual = sz.get("cobertura_anual",
                sum(energy_cov) / max(sum(monthly_cons_ref), 1) * 100)
            st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px;">
  <div class="snap-card" style="min-height:80px;">
    <div class="sc-label">Consumo anual</div>
    <div class="sc-val" style="font-size:14px;">{sum(monthly_cons_ref):,.0f}</div>
    <div class="sc-sub">kWh/año</div>
  </div>
  <div class="snap-card" style="min-height:80px;">
    <div class="sc-label">Cobertura solar</div>
    <div class="sc-val" style="color:#f59e0b;font-size:14px;">{cobertura_anual:.1f}%</div>
    <div class="sc-sub">del consumo anual</div>
  </div>
  <div class="snap-card" style="min-height:80px;">
    <div class="sc-label">Ahorro anual</div>
    <div class="sc-val" style="color:#4ade80;font-size:14px;">${sum(ahorro_m):,.0f}</div>
    <div class="sc-sub">MXN/año</div>
  </div>
  <div class="snap-card" style="min-height:80px;">
    <div class="sc-label">Tarifa media real</div>
    <div class="sc-val" style="font-size:14px;">${tarifa_efectiva:.3f}</div>
    <div class="sc-sub">MXN/kWh ponderada</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Gráfica Mensual + Variabilidad interanual ─────────────────────────
        st.markdown('<div class="section-header">Generación mensual estimada</div>',
                    unsafe_allow_html=True)

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=MONTHS, y=monthly_gen,
            name="Generación P50 (irr. media)",
            marker_color=AMBER, opacity=0.95,
            hovertemplate="<b>%{x}</b><br>P50: %{y:,.0f} kWh<extra></extra>"
        ))
        fig1.add_trace(go.Scatter(
            x=MONTHS, y=irr_vals,
            mode="lines+markers",
            name="Irradiancia NASA (2005–2024)",
            yaxis="y2",
            line=dict(color=ROSE, width=3, dash="dot"),
            marker=dict(size=7, color=ROSE, line=dict(width=1.5, color="white")),
            hovertemplate="<b>%{x}</b><br>Irradiancia: %{y:.4f} kWh/m²/día<extra></extra>"
        ))
        layout1 = copy.deepcopy(PLOT_LAYOUT)
        layout1.update({
            "height": 380, "barmode": "group",
            "title": dict(text="Generación Mensual (P50 con irradiancia media)", font=dict(size=15)),
            "yaxis":  dict(title="kWh generados", gridcolor="#2a2d3a", tickformat=",", rangemode="tozero"),
            "yaxis2": dict(title="Irradiancia (kWh/m²/día)", overlaying="y", side="right",
                           range=[0, max(irr_vals) * 1.25],
                           tickfont=dict(color=ROSE), tickformat=".2f"),
            "legend": dict(orientation="h", y=-0.22, x=0.5, xanchor="center", yanchor="top",
                           font=dict(size=13), bgcolor="rgba(0,0,0,0)",
                           bordercolor="#2a2d3a", borderwidth=1),
            "margin": dict(l=20, r=80, t=60, b=100),
            "hovermode": "x unified",
        })
        fig1.update_layout(**layout1)
        st.plotly_chart(fig1, use_container_width=True)

        # ── Distribución interanual + P90 real ────────────────────────────────
        if has_p90:
            st.markdown('<div class="section-header">Variabilidad interanual · P90 riguroso</div>',
                        unsafe_allow_html=True)
            n_anios = len(gen_por_anio)

            # Aviso metodológico
            st.markdown(
                f'<div class="nasa-box">🔬 P90 calculado como percentil 10 de la generación anual '
                f'simulada con los {n_anios} años de irradiancia real NASA POWER '
                f'({NASA_START}–{NASA_END}). '
                f'El sistema supera el P90 el 90% de los años históricos.</div>',
                unsafe_allow_html=True)

            anios  = list(gen_por_anio.keys())
            gen_v  = [gen_por_anio[y] / 1000 for y in anios]   # MWh
            p50_mwh = p50_real / 1000
            p90_mwh = p90_real / 1000

            # Colores: rojo si el año está por debajo del P90, ámbar si debajo del P50
            bar_colors = [
                ROSE  if v < p90_mwh else
                AMBER if v < p50_mwh else
                TEAL
                for v in gen_v
            ]

            fig_p90 = go.Figure()
            fig_p90.add_trace(go.Bar(
                x=anios, y=gen_v,
                name="Generación anual",
                marker_color=bar_colors,
                hovertemplate="<b>%{x}</b><br>%{y:,.1f} MWh<extra></extra>",
            ))
            fig_p90.add_hline(
                y=p50_mwh, line_color=AMBER, line_dash="dash", line_width=2,
                annotation_text=f"P50 = {p50_mwh:,.1f} MWh",
                annotation_position="top left",
                annotation_font=dict(color=AMBER, size=12),
            )
            fig_p90.add_hline(
                y=p90_mwh, line_color=ROSE, line_dash="dot", line_width=2,
                annotation_text=f"P90 = {p90_mwh:,.1f} MWh",
                annotation_position="bottom left",
                annotation_font=dict(color=ROSE, size=12),
            )
            layout_p90 = copy.deepcopy(PLOT_LAYOUT)
            layout_p90.update({
                "height": 340,
                "title": dict(text=f"Generación anual simulada {NASA_START}–{NASA_END}", font=dict(size=15)),
                "yaxis": dict(title="MWh/año", gridcolor="#2a2d3a"),
                "xaxis": dict(tickmode="linear", dtick=1, gridcolor="#2a2d3a"),
                "legend": dict(orientation="h", y=1.1, x=0.5, xanchor="center",
                               bgcolor="rgba(0,0,0,0)"),
                "margin": dict(l=20, r=20, t=60, b=40),
            })
            fig_p90.update_layout(**layout_p90)
            st.plotly_chart(fig_p90, use_container_width=True)

            # Métricas compactas P90
            mp1, mp2, mp3, mp4 = st.columns(4)
            mp1.metric("P50",        f"{p50_mwh:,.1f} MWh")
            mp2.metric("P90", f"{p90_mwh:,.1f} MWh",
                       f"{(p90_real/p50_real - 1)*100:+.1f}% vs P50")
            mp3.metric("Mejor año",  f"{max(gen_v):,.1f} MWh")
            mp4.metric("Peor año",   f"{min(gen_v):,.1f} MWh")
        else:
            st.info("ℹ️ Carga datos de NASA POWER desde el sidebar para calcular el P90 riguroso con variabilidad interanual.")

        # ── Modelo financiero — cacheado ──────────────────────────────────────
        fm = calc_financial_model(
            annual_gen, kwp, float(inversion),
            tarifa_efectiva, inflation, discount_rate,
            panel_degradation, vida_util, usd_to_mxn
        )
        years         = fm["years"]
        gen_proj      = fm["gen_proj"]
        tarifas_y     = fm["tarifas_y"]
        flujo_nominal = fm["flujo_nominal"]
        om_anual      = fm["om_anual"]
        flujo_neto    = fm["flujo_neto"]
        factor_desc   = fm["factor_desc"]
        flujo_desc    = fm["flujo_desc"]
        acum_nominal  = fm["acum_nominal"]
        acum_desc     = fm["acum_desc"]
        inversion_mxn = fm["inv_mxn"]
        vpn           = fm["vpn"]
        tir           = fm["tir"]
        tir_str       = f"{tir:.1f}%" if tir is not None else "N/A"
        pb_simple     = fm["pb_simple"]
        pb_simple_str = f"{pb_simple} años" if pb_simple else f">{vida_util} años"
        pb_disc       = fm["pb_disc"]
        pb_disc_str   = f"{pb_disc} años" if pb_disc else f">{vida_util} años"
        lcoe          = fm["lcoe"]

        # ── 2. KPIs principales ───────────────────────────────────────────────
        kc = "#4ade80" if vpn > 0 else "#f87171"

        st.markdown(f"""
<div style="margin-bottom:0.5rem">
  <div class="section-header">Modelo financiero · {vida_util} años</div>
</div>
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:12px;">

  <div class="snap-card">
    <div class="sc-label">VPN</div>
    <div class="sc-val" style="color:{kc};">${vpn:,.0f}</div>
    <div class="sc-sub">MXN</div>
  </div>

  <div class="snap-card">
    <div class="sc-label">TIR</div>
    <div class="sc-val" style="color:#22d3ee;">{tir_str}</div>
    <div class="sc-sub">vs {discount_rate}% WACC</div>
  </div>

  <div class="snap-card">
    <div class="sc-label">LCOE</div>
    <div class="sc-val" style="color:{VIOLET};">${lcoe:.2f}</div>
    <div class="sc-sub">MXN/kWh generado</div>
  </div>

  <div class="snap-card">
    <div class="sc-label">Payback simple</div>
    <div class="sc-val" style="color:#f9fafb;">{pb_simple_str}</div>
    <div class="sc-sub">flujos nominales</div>
  </div>

  <div class="snap-card">
    <div class="sc-label">Payback descontado</div>
    <div class="sc-val" style="color:#f9fafb;">{pb_disc_str}</div>
    <div class="sc-sub">flujos descontados</div>
  </div>

  <div class="snap-card">
    <div class="sc-label">O&amp;M año 1</div>
    <div class="sc-val" style="color:#6b7280;">${om_anual[0]:,.0f}</div>
    <div class="sc-sub">MXN (est. 1% inv.)</div>
  </div>

</div>
""", unsafe_allow_html=True)

        # ── 3. Gráfica 1: Flujos nominales vs descontados (barras agrupadas) ──
        st.markdown('<div class="section-header">Flujos de efectivo anuales</div>',
                    unsafe_allow_html=True)

        fig_cf = go.Figure()
        fig_cf.add_trace(go.Bar(
            x=years, y=flujo_neto,
            name="Flujo neto nominal (MXN)",
            marker_color=AMBER, opacity=0.9,
            hovertemplate="<b>Año %{x}</b><br>Flujo neto: $%{y:,.0f} MXN<extra></extra>",
        ))
        fig_cf.add_trace(go.Bar(
            x=years, y=flujo_desc,
            name="Flujo descontado (MXN)",
            marker_color=TEAL, opacity=0.85,
            hovertemplate="<b>Año %{x}</b><br>Flujo desc.: $%{y:,.0f} MXN<extra></extra>",
        ))
        fig_cf.add_trace(go.Scatter(
            x=years, y=om_anual,
            name="O&M anual (MXN)",
            mode="lines+markers",
            line=dict(color=ROSE, width=2, dash="dot"),
            marker=dict(size=5, color=ROSE),
            hovertemplate="<b>Año %{x}</b><br>O&M: $%{y:,.0f} MXN<extra></extra>",
        ))
        lay_cf = copy.deepcopy(PLOT_LAYOUT)
        lay_cf.update({
            "height": 320, "barmode": "group",
            "yaxis": dict(title="MXN", gridcolor="#2a2d3a", tickformat=","),
            "xaxis": dict(title="Año", tickmode="linear", dtick=max(1, vida_util // 10),
                          gridcolor="#2a2d3a"),
            "legend": dict(orientation="h", y=1.12, x=0.5, xanchor="center",
                           bgcolor="rgba(0,0,0,0)"),
            "margin": dict(l=20, r=20, t=50, b=40),
            "hovermode": "x unified",
        })
        fig_cf.update_layout(**lay_cf)
        st.plotly_chart(fig_cf, use_container_width=True)

        # ── 4. Gráfica 2: VPN acumulado y payback ────────────────────────────
        st.markdown('<div class="section-header">VPN acumulado y payback</div>',
                    unsafe_allow_html=True)

        fig_vpn = go.Figure()
        # Zona de inversión inicial (año 0)
        fig_vpn.add_trace(go.Scatter(
            x=[0] + years, y=[-inversion_mxn] + acum_desc,
            name="VPN acumulado (descontado)",
            mode="lines+markers",
            line=dict(color=TEAL, width=3),
            marker=dict(size=6, color=TEAL),
            fill="tozeroy",
            fillcolor="rgba(20,184,166,0.08)",
            hovertemplate="<b>Año %{x}</b><br>VPN acum.: $%{y:,.0f} MXN<extra></extra>",
        ))
        fig_vpn.add_trace(go.Scatter(
            x=[0] + years, y=[-inversion_mxn] + acum_nominal,
            name="Flujo acumulado nominal",
            mode="lines",
            line=dict(color=AMBER, width=2, dash="dash"),
            hovertemplate="<b>Año %{x}</b><br>Acum. nominal: $%{y:,.0f} MXN<extra></extra>",
        ))
        # Línea de breakeven
        fig_vpn.add_hline(y=0, line_color="#6b7280", line_dash="solid", line_width=1)
        # Anotación payback descontado
        if pb_disc:
            fig_vpn.add_vline(x=pb_disc, line_color=TEAL, line_dash="dot", line_width=1.5,
                              annotation_text=f"Payback desc. año {pb_disc}",
                              annotation_font=dict(color=TEAL, size=11))
        if pb_simple and pb_simple != pb_disc:
            fig_vpn.add_vline(x=pb_simple, line_color=AMBER, line_dash="dot", line_width=1.5,
                              annotation_text=f"Payback simple año {pb_simple}",
                              annotation_font=dict(color=AMBER, size=11),
                              annotation_position="bottom right")
        lay_vpn = copy.deepcopy(PLOT_LAYOUT)
        lay_vpn.update({
            "height": 320,
            "yaxis": dict(title="MXN acumulados", gridcolor="#2a2d3a", tickformat=","),
            "xaxis": dict(title="Año", tickmode="linear", dtick=max(1, vida_util // 10),
                          gridcolor="#2a2d3a"),
            "legend": dict(orientation="h", y=1.12, x=0.5, xanchor="center",
                           bgcolor="rgba(0,0,0,0)"),
            "margin": dict(l=20, r=20, t=50, b=40),
            "hovermode": "x unified",
        })
        fig_vpn.update_layout(**lay_vpn)
        st.plotly_chart(fig_vpn, use_container_width=True)

        # ── 5. Gráfica 3: Sensibilidad VPN vs tasa de descuento ──────────────
        st.markdown('<div class="section-header">Sensibilidad: VPN vs tasa de descuento</div>',
                    unsafe_allow_html=True)

        tasas_sens = [i * 0.5 for i in range(0, 61)]   # 0% a 30%
        vpn_sens   = []
        for t_s in tasas_sens:
            r_s = t_s / 100
            fd_s = [flujo_neto[i] / (1 + r_s) ** years[i] for i in range(len(years))]
            vpn_sens.append(-inversion_mxn + sum(fd_s))

        fig_sens = go.Figure()
        # Colorear área positiva/negativa
        fig_sens.add_trace(go.Scatter(
            x=tasas_sens, y=vpn_sens,
            mode="lines", name="VPN",
            line=dict(color=TEAL, width=3),
            fill="tozeroy",
            fillcolor="rgba(20,184,166,0.10)",
            hovertemplate="<b>WACC %{x:.1f}%</b><br>VPN: $%{y:,.0f} MXN<extra></extra>",
        ))
        # Marcar tasa actual
        fig_sens.add_vline(x=discount_rate, line_color=AMBER, line_dash="dash", line_width=2,
                           annotation_text=f"WACC actual {discount_rate}%",
                           annotation_font=dict(color=AMBER, size=11))
        # Marcar TIR (cruce por cero)
        if tir is not None:
            fig_sens.add_vline(x=tir, line_color=ROSE, line_dash="dot", line_width=2,
                               annotation_text=f"TIR {tir:.1f}%",
                               annotation_font=dict(color=ROSE, size=11),
                               annotation_position="top right")
        fig_sens.add_hline(y=0, line_color="#6b7280", line_width=1)
        lay_sens = copy.deepcopy(PLOT_LAYOUT)
        lay_sens.update({
            "height": 300,
            "yaxis": dict(title="VPN (MXN)", gridcolor="#2a2d3a", tickformat=","),
            "xaxis": dict(title="Tasa de descuento WACC (%)", gridcolor="#2a2d3a"),
            "legend": dict(orientation="h", y=1.12, x=0.5, xanchor="center",
                           bgcolor="rgba(0,0,0,0)"),
            "margin": dict(l=20, r=20, t=50, b=40),
        })
        fig_sens.update_layout(**lay_sens)
        st.plotly_chart(fig_sens, use_container_width=True)

        # ── 6. Tabla detallada año a año ──────────────────────────────────────
        st.markdown('<div class="section-header">Tabla financiera detallada</div>',
                    unsafe_allow_html=True)
        tabla_fin = pd.DataFrame({
            "Año":                  years,
            "Generación (MWh)":     [f"{g/1000:,.2f}" for g in gen_proj],
            "Tarifa (MXN/kWh)":     [f"${t:.3f}" for t in tarifas_y],
            "Ingreso bruto (MXN)":  [f"${v:,.0f}" for v in flujo_nominal],
            "O&M (MXN)":            [f"${v:,.0f}" for v in om_anual],
            "Flujo neto (MXN)":     [f"${v:,.0f}" for v in flujo_neto],
            "Factor desc.":         [f"{v:.4f}" for v in factor_desc],
            "Flujo desc. (MXN)":    [f"${v:,.0f}" for v in flujo_desc],
            "VPN acum. (MXN)":      [f"${v:,.0f}" for v in acum_desc],
        })
        st.dataframe(tabla_fin, use_container_width=True, hide_index=True)

        # Totales pie de tabla
        st.markdown(f"""
<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-top:12px;">
  <div class="snap-card">
    <div class="sc-label">Ingreso bruto total</div>
    <div class="sc-val" style="color:#f9fafb;">${sum(flujo_nominal):,.0f}</div>
    <div class="sc-sub">MXN nominales</div>
  </div>
  <div class="snap-card">
    <div class="sc-label">O&amp;M total (nominal)</div>
    <div class="sc-val" style="color:#6b7280;">${sum(om_anual):,.0f}</div>
    <div class="sc-sub">MXN nominales</div>
  </div>
  <div class="snap-card">
    <div class="sc-label">Flujo neto total</div>
    <div class="sc-val" style="color:#f9fafb;">${sum(flujo_neto):,.0f}</div>
    <div class="sc-sub">MXN nominales</div>
  </div>
  <div class="snap-card">
    <div class="sc-label">VPN final</div>
    <div class="sc-val" style="color:{'#4ade80' if vpn>0 else '#f87171'};">${vpn:,.0f}</div>
    <div class="sc-sub">MXN</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Criterio de decisión
        if tir is None:
            st.warning("⚠️ No se pudo calcular la TIR (flujo sin solución en el rango analizado).")
        elif vpn > 0 and tir > discount_rate + 3:
            st.success("🟢 **Proyecto muy atractivo** — VPN positivo y TIR supera significativamente el costo de capital.")
        elif vpn > 0 and tir > discount_rate:
            st.success("🟡 **Proyecto atractivo** — VPN positivo y TIR supera el costo de capital.")
        else:
            st.error("🔴 **Proyecto poco atractivo** — VPN negativo o TIR por debajo del costo de capital.")

                # ── Exportar TOR ───────────────────────────────────────────────────────
        st.markdown('<div class="section-header">Exportar TOR</div>', unsafe_allow_html=True)

        # Llamada corregida y simplificada a build_tor_text
        tor_text = build_tor_text(
            "Proyecto Solar",
            "—",
            proj_loc,
            "",
            panel_wp,
            panel_eff_declared,
            panel_largo_mm,
            panel_ancho_mm,
            panel_peso_kg,
            panel_area,
            n_panels,
            kwp,
            pr_pct,
            irr_vals,
            monthly_gen,
            annual_gen,
            p50,
            p90,
            co2_saved,
            inversion,
            ahorro1,
            payback,
            gen_por_anio,
        )

        ex1, ex2 = st.columns(2)
        with ex1:
            st.download_button(
                "⬇️ Descargar TOR (.txt)",
                data=tor_text.encode("utf-8"),
                file_name=f"TOR_Solar_{proj_loc[:20].replace(' ','_')}.txt",
                mime="text/plain",
                use_container_width=True)
        with ex2:
            alias = st.text_input("Alias para el comparador", value=proj_loc[:30], key="run_alias")
            if st.button("💾 Guardar corrida en comparador", use_container_width=True):
                run = {
                    "alias":     alias or proj_loc[:30],
                    "modo":      "Área" if uso_area else "Recibo CFE",
                    "kwp":       round(kwp, 2),
                    "n_panels":  n_panels,
                    "panel_wp":  panel_wp,
                    "p50_mwh":   round(p50 / 1000, 2),
                    "p90_mwh":   round(p90 / 1000, 2) if p90 else None,
                    "pr_pct":    round(pr_pct, 1),
                    "tarifa":    round(tarifa_efectiva, 3),
                    "inversion_usd": round(inversion, 0),
                    "inversion_mxn": round(inversion * usd_to_mxn, 0),
                    "ahorro1":   round(ahorro1, 0),
                    "payback":   round(payback, 1),
                    "vpn":       round(vpn, 0),
                    "tir":       round(tir, 1) if tir else None,
                    "lcoe":      round(lcoe, 3),
                    "co2_t":     round(co2_saved / 1000, 2),
                    "irr_media": round(sum(irr_vals) / 12, 3),
                }
                st.session_state.saved_runs.append(run)
                st.success(f"✅ '{alias}' guardado — ve al Comparador ↓")

        # ── COMPARADOR ─────────────────────────────────────────────────────────
        if st.session_state.saved_runs:
            st.markdown('<div class="section-header">📊 Comparador de corridas</div>',
                        unsafe_allow_html=True)

            runs = st.session_state.saved_runs
            n_runs = len(runs)

            # Botón para limpiar
            ccol1, ccol2 = st.columns([4, 1])
            with ccol2:
                if st.button("🗑️ Limpiar", use_container_width=True, key="clear_runs"):
                    st.session_state.saved_runs = []
                    st.rerun()

            # Tabla comparativa
            tabla_comp = pd.DataFrame([{
                "Alias":         r["alias"],
                "Modo":          r["modo"],
                "kWp":           f"{r['kwp']:.1f}",
                "Paneles":       r["n_panels"],
                "P50 (MWh/a)":   f"{r['p50_mwh']:.1f}",
                "P90 (MWh/a)":   f"{r['p90_mwh']:.1f}" if r.get("p90_mwh") else "—",
                "PR (%)":        f"{r['pr_pct']:.1f}",
                "Tarifa $/kWh":  f"${r['tarifa']:.3f}",
                "Inv. USD":      f"${r['inversion_usd']:,.0f}",
                "Ahorro año 1":  f"${r['ahorro1']:,.0f}",
                "Payback (a)":   f"{r['payback']:.1f}",
                "VPN (MXN)":     f"${r['vpn']:,.0f}",
                "TIR (%)":       f"{r['tir']:.1f}%" if r.get("tir") else "N/A",
                "LCOE $/kWh":    f"${r['lcoe']:.3f}",
                "CO₂ (t/a)":     f"{r['co2_t']:.2f}",
            } for r in runs])
            st.dataframe(tabla_comp, use_container_width=True, hide_index=True)

            # Gráficas comparativas — solo si hay 2+ corridas
            if n_runs >= 2:
                aliases = [r["alias"] for r in runs]
                cg1, cg2 = st.columns(2)

                with cg1:
                    st.markdown('<div class="section-header">kWp por corrida</div>',
                                unsafe_allow_html=True)
                    fig_ck = go.Figure(go.Bar(
                        x=aliases, y=[r["kwp"] for r in runs],
                        marker_color=AMBER, text=[f"{r['kwp']:.1f}" for r in runs],
                        textposition="outside", textfont=dict(family="DM Mono", size=11),
                        hovertemplate="<b>%{x}</b><br>%{y:.1f} kWp<extra></extra>"))
                    lc = copy.deepcopy(PLOT_LAYOUT)
                    lc.update({"height": 260, "yaxis": dict(title="kWp", gridcolor="#2a2d3a"),
                               "margin": dict(l=20, r=20, t=20, b=60),
                               "xaxis": dict(tickangle=-30)})
                    fig_ck.update_layout(**lc)
                    st.plotly_chart(fig_ck, use_container_width=True)

                with cg2:
                    st.markdown('<div class="section-header">VPN vs Payback</div>',
                                unsafe_allow_html=True)
                    vpn_vals_c  = [r["vpn"] for r in runs]
                    pb_vals_c   = [r["payback"] for r in runs]
                    kwp_vals_c  = [r["kwp"] for r in runs]
                    fig_sc = go.Figure(go.Scatter(
                        x=pb_vals_c, y=vpn_vals_c,
                        mode="markers+text",
                        marker=dict(
                            size=[max(14, min(50, k * 0.8)) for k in kwp_vals_c],
                            color=[TEAL if v > 0 else ROSE for v in vpn_vals_c],
                            opacity=0.85, line=dict(width=1.5, color="#2a2d3a")),
                        text=aliases, textposition="top center",
                        textfont=dict(size=10, family="DM Sans"),
                        hovertemplate="<b>%{text}</b><br>Payback: %{x:.1f}a<br>VPN: $%{y:,.0f} MXN<extra></extra>"))
                    fig_sc.add_hline(y=0, line_color="#6b7280", line_width=1)
                    ls = copy.deepcopy(PLOT_LAYOUT)
                    ls.update({"height": 260,
                               "xaxis": dict(title="Payback simple (años)", gridcolor="#2a2d3a"),
                               "yaxis": dict(title="VPN (MXN)", gridcolor="#2a2d3a", tickformat=","),
                               "margin": dict(l=20, r=20, t=20, b=40)})
                    fig_sc.update_layout(**ls)
                    st.plotly_chart(fig_sc, use_container_width=True)

                # Radar de métricas normalizadas
                st.markdown('<div class="section-header">Radar comparativo (normalizado)</div>',
                            unsafe_allow_html=True)
                radar_cats = ["kWp", "P50 MWh", "Ahorro año 1", "VPN", "CO₂ (t)"]

                def _norm(vals):
                    mx = max(vals) if max(vals) > 0 else 1
                    return [v / mx * 100 for v in vals]

                kwp_n    = _norm([r["kwp"]          for r in runs])
                p50_n    = _norm([r["p50_mwh"]       for r in runs])
                aho_n    = _norm([r["ahorro1"]        for r in runs])
                vpn_n    = _norm([max(0, r["vpn"])    for r in runs])
                co2_n    = _norm([r["co2_t"]          for r in runs])

                fig_rad = go.Figure()
                colors_rad = [AMBER, TEAL, ROSE, VIOLET, BLUE]
                for i, r in enumerate(runs):
                    vals = [kwp_n[i], p50_n[i], aho_n[i], vpn_n[i], co2_n[i]]
                    vals_closed = vals + [vals[0]]
                    cats_closed = radar_cats + [radar_cats[0]]
                    fig_rad.add_trace(go.Scatterpolar(
                        r=vals_closed, theta=cats_closed,
                        name=r["alias"], fill="toself", opacity=0.5,
                        line=dict(color=colors_rad[i % len(colors_rad)], width=2)))
                fig_rad.update_layout(
                    polar=dict(
                        bgcolor="#13151f",
                        radialaxis=dict(visible=True, range=[0, 100],
                                        gridcolor="#2a2d3a", tickcolor="#2a2d3a",
                                        tickfont=dict(size=9, color="#6b7280")),
                        angularaxis=dict(gridcolor="#2a2d3a", tickfont=dict(size=11))),
                    paper_bgcolor="#0f1117",
                    font=dict(family="DM Sans", color="#9ca3af"),
                    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                                bgcolor="rgba(0,0,0,0)"),
                    height=380, margin=dict(l=40, r=40, t=20, b=60))
                st.plotly_chart(fig_rad, use_container_width=True)

                # Exportar comparador como CSV
                csv_comp = tabla_comp.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Exportar comparador CSV", data=csv_comp,
                                   file_name="comparador_solar.csv", mime="text/csv",
                                   use_container_width=True)
        else:
            st.markdown('<div class="info-box">💡 Guarda una corrida arriba para activar el comparador. Puedes guardar múltiples escenarios (distintas áreas, tecnologías o tarifas) y compararlos aquí.</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — PPA · VENTA AL CLIENTE
# ═════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown("""
    <div class="info-box">
    💡 <b>Power Purchase Agreement (PPA)</b> — El cliente paga por la energía generada a una
    tarifa fija acordada ($/kWh), en lugar de comprar la instalación. Tú (o el financiador)
    eres dueño del sistema durante el plazo del contrato. Evalúa distintos plazos y
    encuentra el precio PPA que hace viable el proyecto.
    </div>
    """, unsafe_allow_html=True)

    ppa_col1, ppa_col2, ppa_col3 = st.columns([1.1, 1.1, 1.8], gap="large")

    with ppa_col1:
        st.markdown('<div class="section-header">Sistema base</div>', unsafe_allow_html=True)
        ppa_kwp = st.number_input("Capacidad (kWp)", 1.0, 50000.0,
                                   max(1.0, round(float(kwp), 1)),
                                   1.0, key="ppa_kwp")
        ppa_gen_anual = st.number_input("Generación año 1 (kWh/año)", 100.0, 50_000_000.0,
                                         max(100.0, round(float(annual_gen), 0)), 100.0, key="ppa_gen")
        ppa_inversion_usd = st.number_input("Inversión total (USD)", 1000.0, 50_000_000.0,
                                             max(1000.0, round(ppa_kwp * float(costo_kwp), 0)),
                                             100.0, key="ppa_inv")
        st.caption(f"≈ ${ppa_inversion_usd * usd_to_mxn:,.0f} MXN al tipo de cambio configurado")

        st.markdown('<div class="section-header">Parámetros técnicos</div>', unsafe_allow_html=True)
        ppa_degradacion  = st.slider("Degradación anual (%)", 0.0, 1.5, 0.5, 0.05, key="ppa_deg")
        ppa_om_pct       = st.slider("O&M anual (% inv. MXN)", 0.3, 2.5, 1.0, 0.1, key="ppa_om")
        ppa_seguros_pct  = st.slider("Seguros / otros (% inv. MXN)", 0.0, 1.0, 0.3, 0.05, key="ppa_seg")

    with ppa_col2:
        st.markdown('<div class="section-header">Condiciones financieras</div>', unsafe_allow_html=True)
        ppa_wacc             = st.slider("WACC (%)", 5.0, 30.0, 15.0, 0.5, key="ppa_wacc")
        ppa_inflacion_tarifa = st.slider("Escalador PPA anual (%)", 0.0, 8.0, 3.5, 0.5, key="ppa_esc",
                                          help="Incremento anual pactado en el precio PPA")
        ppa_inflacion_om     = st.slider("Inflación O&M anual (%)", 0.0, 8.0, 4.0, 0.5, key="ppa_inf_om")

        ppa_financiamiento = st.checkbox("¿Incluir financiamiento?", value=False, key="ppa_fin_chk")
        if ppa_financiamiento:
            ppa_equity_pct  = st.slider("Capital propio (%)", 10, 100, 30, 5, key="ppa_eq")
            ppa_tasa_deuda  = st.slider("Tasa deuda anual (%)", 5.0, 25.0, 12.0, 0.5, key="ppa_debt_r")
            ppa_plazo_deuda = st.slider("Plazo deuda (años)", 3, 20, 10, 1, key="ppa_debt_p")
        else:
            ppa_equity_pct  = 100
            ppa_tasa_deuda  = 0.0
            ppa_plazo_deuda = 0

        st.markdown('<div class="section-header">Tarifa CFE del cliente</div>', unsafe_allow_html=True)
        ppa_tarifa_cliente = st.number_input("Tarifa actual (MXN/kWh)", 0.5, 15.0,
                                              max(0.5, round(float(tarifa_efectiva), 2)),
                                              0.05, key="ppa_tar")
        ppa_inflacion_cfe  = st.slider("Inflación CFE anual (%)", 0.0, 12.0, 6.0, 0.5, key="ppa_inf_cfe")

    with ppa_col3:
        st.markdown('<div class="section-header">Precio PPA a evaluar</div>', unsafe_allow_html=True)
        ppa_precio_manual = st.number_input(
            "Precio PPA año 1 (MXN/kWh)", 0.50, 10.0, 1.80, 0.05, key="ppa_price",
            help="Ajusta este valor hasta encontrar el precio óptimo para tu cliente")

        ppa_plazos = st.multiselect(
            "Plazos a comparar (años)",
            options=[3, 5, 10, 15, 20, 25],
            default=[10, 15, 20, 25],
            key="ppa_plazos")
        if not ppa_plazos:
            ppa_plazos = [10, 15, 20, 25]
        ppa_plazos = sorted(ppa_plazos)

        st.markdown('<div class="section-header">Plazo objetivo</div>', unsafe_allow_html=True)
        ppa_plazo_minimo = st.selectbox("Plazo para análisis detallado", ppa_plazos, key="ppa_pmin_plazo")

    # ── Calcular todos los plazos — usando funciones cacheadas globales ──────
    ppa_cache_kwargs = dict(
        gen1=ppa_gen_anual, inv_usd=ppa_inversion_usd,
        wacc_pct=ppa_wacc, esc_ppa=ppa_inflacion_tarifa,
        deg=ppa_degradacion, om_pct=ppa_om_pct,
        inf_om=ppa_inflacion_om, seg_pct=ppa_seguros_pct,
        usd_mx=usd_to_mxn, equity_pct=ppa_equity_pct,
        tasa_deuda=ppa_tasa_deuda, plazo_deuda=ppa_plazo_deuda,
        con_fin=ppa_financiamiento)

    resultados = {}
    for pl in ppa_plazos:
        res = dict(calc_ppa_result(precio_ppa=ppa_precio_manual, plazo=pl, **ppa_cache_kwargs))
        res["pm"] = calc_precio_minimo(plazo=pl, **ppa_cache_kwargs)
        resultados[pl] = res

    descuento_vs_cfe = ((ppa_precio_manual / ppa_tarifa_cliente) - 1) * 100
    pm_obj = resultados[ppa_plazo_minimo]["pm"]
    viable = pm_obj is not None and ppa_precio_manual >= pm_obj
    color_viable = "#4ade80" if viable else "#f87171"
    pm_str = f"${pm_obj:.4f}/kWh" if pm_obj else "No viable en este plazo"

    # ── Hero PPA ─────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="tor-hero" style="margin-top:1rem;">
  <div class="th-project">📄 ANÁLISIS PPA · Plazo objetivo {ppa_plazo_minimo} años</div>
  <div class="th-meta">
    Precio evaluado: <b style="color:#f59e0b">${ppa_precio_manual:.4f}/kWh</b>
    &nbsp;·&nbsp; Ahorro cliente vs CFE hoy: <b style="color:#14b8a6">{descuento_vs_cfe:+.1f}%</b>
    &nbsp;·&nbsp; <b style="color:{color_viable}">{'✅ Precio viable' if viable else '⚠️ Por debajo del mínimo'}</b>
  </div>
  <div class="th-grid" style="grid-template-columns:repeat(4,1fr);">
    <div class="th-item">
      <span class="th-label">Precio mínimo viable</span>
      <span class="th-val" style="color:{color_viable};font-size:15px;">{pm_str}</span>
      <span class="th-unit">a {ppa_plazo_minimo} años · VPN = 0</span>
    </div>
    <div class="th-item">
      <span class="th-label">Precio PPA evaluado</span>
      <span class="th-val">${ppa_precio_manual:.4f}</span>
      <span class="th-unit">MXN/kWh año 1</span>
    </div>
    <div class="th-item">
      <span class="th-label">Tarifa CFE cliente</span>
      <span class="th-val">${ppa_tarifa_cliente:.2f}</span>
      <span class="th-unit">MXN/kWh actual</span>
    </div>
    <div class="th-item">
      <span class="th-label">Inversión total</span>
      <span class="th-val">${ppa_inversion_usd:,.0f}</span>
      <span class="th-unit">USD · ${ppa_inversion_usd*usd_to_mxn:,.0f} MXN</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Tarjetas comparativas por plazo ───────────────────────────────────────
    st.markdown('<div class="section-header">Comparativo de plazos</div>', unsafe_allow_html=True)
    cols_pl = st.columns(len(ppa_plazos))
    for idx, pl in enumerate(ppa_plazos):
        r   = resultados[pl]
        vc  = "#4ade80" if r["vpn"]>0 else "#f87171"
        tis = f"{r['tir']:.1f}%" if r["tir"] is not None else "N/A"
        pbs = f"{r['pb']} años" if r["pb"] else f">{pl}a"
        pmc = "#4ade80" if r["pm"] and ppa_precio_manual>=r["pm"] else "#f87171"
        pms = f"${r['pm']:.4f}" if r["pm"] else "No viable"
        with cols_pl[idx]:
            st.markdown(f"""
<div class="snap-card" style="min-height:215px;padding:18px 12px;">
  <div class="sc-label" style="font-size:14px;font-weight:700;color:#f59e0b;margin-bottom:12px;">{pl} AÑOS</div>
  <div style="width:100%;text-align:left;display:flex;flex-direction:column;gap:8px;">
    <div><div class="sc-label">VPN</div>
         <div class="sc-val" style="color:{vc};font-size:13px;">${r['vpn']:,.0f}</div></div>
    <div><div class="sc-label">TIR equity</div>
         <div class="sc-val" style="color:#22d3ee;font-size:13px;">{tis}</div></div>
    <div><div class="sc-label">Payback</div>
         <div class="sc-val" style="color:#f9fafb;font-size:13px;">{pbs}</div></div>
    <div><div class="sc-label">Precio mínimo viable</div>
         <div class="sc-val" style="color:{pmc};font-size:13px;">{pms}/kWh</div></div>
  </div>
</div>""", unsafe_allow_html=True)

    # Tabla resumen
    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)
    tabla_ppa = []
    for pl in ppa_plazos:
        r = resultados[pl]
        tabla_ppa.append({
            "Plazo":          f"{pl} años",
            "Precio evaluado":f"${ppa_precio_manual:.4f}/kWh",
            "Precio mínimo":  f"${r['pm']:.4f}/kWh" if r["pm"] else "No viable",
            "VPN (MXN)":      f"${r['vpn']:,.0f}",
            "TIR equity":     f"{r['tir']:.1f}%" if r["tir"] else "N/A",
            "Payback":        f"{r['pb']} años" if r["pb"] else f">{pl}a",
            "Ingreso total":  f"${r['ing_total']:,.0f}",
        })
    st.dataframe(pd.DataFrame(tabla_ppa), use_container_width=True, hide_index=True)

    # ── Gráficas ──────────────────────────────────────────────────────────────
    gc1, gc2 = st.columns(2, gap="large")

    with gc1:
        st.markdown('<div class="section-header">VPN por plazo</div>', unsafe_allow_html=True)
        vpn_vals = [resultados[pl]["vpn"] for pl in ppa_plazos]
        fig_vp = go.Figure(go.Bar(
            x=[f"{pl}a" for pl in ppa_plazos], y=vpn_vals,
            marker_color=[TEAL if v>=0 else ROSE for v in vpn_vals],
            text=[f"${v/1e6:.2f}M" for v in vpn_vals],
            textposition="outside", textfont=dict(size=12, family="DM Mono"),
            hovertemplate="<b>%{x}</b><br>VPN: $%{y:,.0f} MXN<extra></extra>"))
        fig_vp.add_hline(y=0, line_color="#6b7280", line_width=1.5)
        lyt_vp = copy.deepcopy(PLOT_LAYOUT)
        lyt_vp.update({"height":300,
                       "yaxis": dict(title="VPN (MXN)", gridcolor="#2a2d3a", tickformat=","),
                       "xaxis": dict(title="Plazo"),
                       "margin": dict(l=20,r=20,t=30,b=40)})
        fig_vp.update_layout(**lyt_vp)
        st.plotly_chart(fig_vp, use_container_width=True)

    with gc2:
        st.markdown('<div class="section-header">Precio mínimo viable por plazo</div>', unsafe_allow_html=True)
        pm_vals = [resultados[pl]["pm"] for pl in ppa_plazos]
        fig_pm = go.Figure()
        fig_pm.add_trace(go.Scatter(
            x=[f"{pl}a" for pl in ppa_plazos],
            y=[v if v else None for v in pm_vals],
            mode="lines+markers+text",
            line=dict(color=AMBER, width=3),
            marker=dict(size=10, color=AMBER),
            text=[f"${v:.4f}" if v else "N/V" for v in pm_vals],
            textposition="top center", textfont=dict(size=11, family="DM Mono"),
            name="Precio mínimo",
            hovertemplate="<b>%{x}</b><br>Precio mín: $%{y:.4f}/kWh<extra></extra>"))
        fig_pm.add_hline(y=ppa_precio_manual, line_color=TEAL, line_dash="dash", line_width=2,
                         annotation_text=f"Precio evaluado ${ppa_precio_manual:.4f}",
                         annotation_font=dict(color=TEAL, size=11))
        fig_pm.add_hline(y=ppa_tarifa_cliente, line_color=ROSE, line_dash="dot", line_width=1.5,
                         annotation_text=f"CFE hoy ${ppa_tarifa_cliente:.2f}",
                         annotation_font=dict(color=ROSE, size=11), annotation_position="bottom right")
        lyt_pm = copy.deepcopy(PLOT_LAYOUT)
        lyt_pm.update({"height":300,
                       "yaxis": dict(title="MXN/kWh", gridcolor="#2a2d3a", tickformat=".4f"),
                       "xaxis": dict(title="Plazo"),
                       "margin": dict(l=20,r=20,t=30,b=40),
                       "legend": dict(orientation="h",y=1.1,x=0.5,xanchor="center",bgcolor="rgba(0,0,0,0)")})
        fig_pm.update_layout(**lyt_pm)
        st.plotly_chart(fig_pm, use_container_width=True)

    # ── Flujos anuales plazo objetivo ─────────────────────────────────────────
    st.markdown(f'<div class="section-header">Flujos anuales — {ppa_plazo_minimo} años</div>',
                unsafe_allow_html=True)
    ro = resultados[ppa_plazo_minimo]
    fig_fl = go.Figure()
    fig_fl.add_trace(go.Bar(x=ro["years"], y=ro["ing_y"], name="Ingreso PPA",
        marker_color=AMBER, opacity=0.9,
        hovertemplate="<b>Año %{x}</b><br>Ingreso: $%{y:,.0f} MXN<extra></extra>"))
    costos_y = [ro["om_y"][i]+ro["seg_y"][i] for i in range(ppa_plazo_minimo)]
    fig_fl.add_trace(go.Bar(x=ro["years"], y=costos_y, name="O&M + Seguros",
        marker_color="#374151",
        hovertemplate="<b>Año %{x}</b><br>Costos: $%{y:,.0f} MXN<extra></extra>"))
    if any(d>0 for d in ro["deu_y"]):
        fig_fl.add_trace(go.Bar(x=ro["years"], y=ro["deu_y"], name="Servicio deuda",
            marker_color=ROSE, opacity=0.8,
            hovertemplate="<b>Año %{x}</b><br>Deuda: $%{y:,.0f} MXN<extra></extra>"))
    fig_fl.add_trace(go.Scatter(x=ro["years"], y=ro["fn_y"], name="Flujo neto",
        mode="lines+markers", line=dict(color=TEAL,width=2.5), marker=dict(size=6,color=TEAL),
        hovertemplate="<b>Año %{x}</b><br>Flujo neto: $%{y:,.0f} MXN<extra></extra>"))
    lyt_fl = copy.deepcopy(PLOT_LAYOUT)
    lyt_fl.update({"height":330,"barmode":"stack",
                   "yaxis": dict(title="MXN",gridcolor="#2a2d3a",tickformat=","),
                   "xaxis": dict(title="Año",tickmode="linear",dtick=max(1,ppa_plazo_minimo//10)),
                   "legend": dict(orientation="h",y=1.12,x=0.5,xanchor="center",bgcolor="rgba(0,0,0,0)"),
                   "margin": dict(l=20,r=20,t=50,b=40),"hovermode":"x unified"})
    fig_fl.update_layout(**lyt_fl)
    st.plotly_chart(fig_fl, use_container_width=True)

    # ── Perspectiva del cliente ───────────────────────────────────────────────
    st.markdown('<div class="section-header">Perspectiva del cliente · Ahorro vs CFE</div>',
                unsafe_allow_html=True)
    gen_cl   = ro["gen_y"]
    prec_cl  = ro["prec_y"]
    cfe_y    = [ppa_tarifa_cliente*(1+ppa_inflacion_cfe/100)**i for i in range(ppa_plazo_minimo)]
    pago_ppa = [gen_cl[i]*prec_cl[i] for i in range(ppa_plazo_minimo)]
    pago_cfe = [gen_cl[i]*cfe_y[i]   for i in range(ppa_plazo_minimo)]
    ahorro_y = [pago_cfe[i]-pago_ppa[i] for i in range(ppa_plazo_minimo)]

    fig_cl = go.Figure()
    fig_cl.add_trace(go.Bar(x=ro["years"], y=pago_cfe, name="Lo que pagaría a CFE",
        marker_color="#374151",
        hovertemplate="<b>Año %{x}</b><br>CFE: $%{y:,.0f} MXN<extra></extra>"))
    fig_cl.add_trace(go.Bar(x=ro["years"], y=pago_ppa, name="Pago PPA",
        marker_color=AMBER, opacity=0.9,
        hovertemplate="<b>Año %{x}</b><br>PPA: $%{y:,.0f} MXN<extra></extra>"))
    fig_cl.add_trace(go.Scatter(x=ro["years"], y=ahorro_y, name="Ahorro anual",
        mode="lines+markers", line=dict(color=TEAL,width=2.5), marker=dict(size=6,color=TEAL),
        hovertemplate="<b>Año %{x}</b><br>Ahorro: $%{y:,.0f} MXN<extra></extra>"))
    lyt_cl = copy.deepcopy(PLOT_LAYOUT)
    lyt_cl.update({"height":310,"barmode":"overlay",
                   "yaxis": dict(title="MXN/año",gridcolor="#2a2d3a",tickformat=","),
                   "xaxis": dict(title="Año",tickmode="linear",dtick=max(1,ppa_plazo_minimo//10)),
                   "legend": dict(orientation="h",y=1.12,x=0.5,xanchor="center",bgcolor="rgba(0,0,0,0)"),
                   "margin": dict(l=20,r=20,t=50,b=40),"hovermode":"x unified"})
    fig_cl.update_layout(**lyt_cl)
    st.plotly_chart(fig_cl, use_container_width=True)

    # KPIs cliente
    ahorro_total = sum(ahorro_y)
    cfe_final    = cfe_y[-1]
    ppa_final    = prec_cl[-1]
    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:8px;">
  <div class="snap-card">
    <div class="sc-label">Ahorro total cliente</div>
    <div class="sc-val" style="color:#4ade80;">${ahorro_total:,.0f}</div>
    <div class="sc-sub">MXN en {ppa_plazo_minimo} años</div>
  </div>
  <div class="snap-card">
    <div class="sc-label">Ahorro año 1</div>
    <div class="sc-val" style="color:#4ade80;">${ahorro_y[0]:,.0f}</div>
    <div class="sc-sub">MXN</div>
  </div>
  <div class="snap-card">
    <div class="sc-label">Descuento vs CFE hoy</div>
    <div class="sc-val" style="color:#f59e0b;">{descuento_vs_cfe:+.1f}%</div>
    <div class="sc-sub">precio PPA vs tarifa actual</div>
  </div>
  <div class="snap-card">
    <div class="sc-label">CFE año {ppa_plazo_minimo} (proyectada)</div>
    <div class="sc-val" style="color:#f87171;">${cfe_final:.4f}</div>
    <div class="sc-sub">vs ${ppa_final:.4f} PPA ese año</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Tabla anual detallada ─────────────────────────────────────────────────
    st.markdown(f'<div class="section-header">Tabla año a año · {ppa_plazo_minimo} años</div>',
                unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Año":                ro["years"],
        "Generación (MWh)":  [f"{g/1000:.2f}" for g in gen_cl],
        "Precio PPA ($/kWh)":[f"${p:.4f}" for p in prec_cl],
        "Ingreso PPA (MXN)": [f"${v:,.0f}" for v in pago_ppa],
        "CFE equiv. ($/kWh)":[f"${c:.4f}" for c in cfe_y],
        "Si pagara CFE":     [f"${v:,.0f}" for v in pago_cfe],
        "Ahorro cliente":    [f"${v:,.0f}" for v in ahorro_y],
        "Flujo neto":        [f"${v:,.0f}" for v in ro["fn_y"]],
    }), use_container_width=True, hide_index=True)
