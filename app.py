import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import math
from scipy.optimize import minimize
from deep_translator import GoogleTranslator

# =========================
# ESTADO INICIAL
# =========================
if "analyzed_ticker" not in st.session_state:
    st.session_state["analyzed_ticker"] = ""
if "current_query" not in st.session_state:
    st.session_state["current_query"] = ""

# =========================
# COLORES / CSS GLOBAL
# =========================
ACCENT_BLUE    = "#268BD2"
ACCENT_GREEN   = "#2AA198"
ACCENT_RED     = "#D30102"
ACCENT_OCHRE   = "#B58900"
TEXT_PRIMARY   = "#433F38"
TEXT_SECONDARY = "#7A756B"
CARD_BG        = "#F4EFCF"
CARD_BG_ALT    = "#F7F1CF"
BORDER         = "#EAE4CD"
BG_MAIN        = "#FDF6E3"

css = f"""
<style>
[data-testid="collapsedControl"] {{ display:none; }}
.block-container {{
    padding-top:2rem;
    padding-bottom:2rem;
    max-width:1300px;
}}
.stApp {{
    background-color:{BG_MAIN};
    color:{TEXT_PRIMARY};
    font-family:system-ui,-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif;
}}
.hero-title {{
    font-size:2.8rem;
    font-weight:800;
    letter-spacing:0.03em;
    text-align:center;
    background:linear-gradient(90deg,{ACCENT_BLUE},{ACCENT_OCHRE});
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:0.2rem;
}}
.hero-sub {{
    text-align:center;
    color:{TEXT_SECONDARY};
    font-size:1rem;
    letter-spacing:0.06em;
    text-transform:uppercase;
    margin-bottom:2rem;
}}
.metric-card {{
    background:{CARD_BG};
    border-radius:8px;
    padding:0.8rem 1rem;
    border:1px solid {BORDER};
    margin-bottom:0.4rem;
    box-shadow:0 1px 3px rgba(0,0,0,0.05);
}}
.metric-label {{
    color:{TEXT_SECONDARY};
    font-size:0.75rem;
    text-transform:uppercase;
    letter-spacing:0.08em;
    margin-bottom:0.2rem;
}}
.metric-value {{
    font-size:1.1rem;
    font-weight:600;
    color:{TEXT_PRIMARY};
}}
.stTabs [data-baseweb="tab"] {{
    font-size:0.9rem;
    padding:0.75rem 1.25rem;
    color:{TEXT_SECONDARY};
}}
.stTabs [aria-selected="true"] {{
    color:{TEXT_PRIMARY} !important;
    border-bottom-color:{ACCENT_BLUE} !important;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def safe_float(x, default=None):
    if x is None:
        return default
    try:
        if isinstance(x, str) and x.strip() == "":
            return default
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except Exception:
        return default

def fmt_num(x, decimals=2, suffix=""):
    v = safe_float(x, None)
    if v is None:
        return "N/D"
    return f"{v:.{decimals}f}{suffix}"

def fmt_large(x):
    v = safe_float(x, None)
    if v is None:
        return "N/D"
    sign = -1 if v < 0 else 1
    v = abs(v)
    if v >= 1e12:
        return f"{sign*v/1e12:.2f}B"
    if v >= 1e9:
        return f"{sign*v/1e9:.2f}B"
    if v >= 1e6:
        return f"{sign*v/1e6:.2f}M"
    return f"{sign*v:.0f}"

def search_ticker(query: str):
    if not query:
        return []
    try:
        url = (
            "https://query2.finance.yahoo.com/v1/finance/search"
            f"?q={query}&lang=en-US&region=US&quotesCount=8&newsCount=0"
        )
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        data = r.json()
        results = []
        for q in data.get("quotes", []):
            if q.get("quoteType") not in ("EQUITY", "ETF"):
                continue
            symbol = q.get("symbol", "")
            name   = q.get("longname") or q.get("shortname", "")
            exch   = q.get("exchDisp", "")
            results.append(f"{symbol} — {name} ({exch})")
        return results
    except Exception:
        return []

DEFAULT_BENCHMARKS = {
    "Technology":             ["AAPL", "MSFT", "GOOGL", "META", "AMZN"],
    "Communication Services": ["GOOGL", "META", "NFLX", "DIS"],
    "Financial Services":     ["JPM", "BAC", "C", "GS"],
    "Consumer Cyclical":      ["AMZN", "TSLA", "HD", "MCD"],
    "Energy":                 ["XOM", "CVX", "BP", "TOT"],
}

def get_benchmark_list(info, main_ticker):
    sector = info.get("sector")
    peers  = DEFAULT_BENCHMARKS.get(sector, [])
    peers  = [p for p in peers if p.upper() != main_ticker.upper()]
    return peers[:4]

def traducir_a_es(texto: str) -> str:
    if not texto:
        return ""
    try:
        return GoogleTranslator(source="auto", target="es").translate(texto)
    except Exception:
        return texto

# =========================
# VALORACIONES
# =========================
def compute_valuations(info, currency):
    methods = []

    price      = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
    shares     = safe_float(info.get("sharesOutstanding"))
    fcf        = safe_float(info.get("freeCashflow"))
    revenue    = safe_float(info.get("totalRevenue"))
    ebitda     = safe_float(info.get("ebitda"))
    ebit       = safe_float(info.get("ebit"))
    bvps       = safe_float(info.get("bookValue"))
    eps        = safe_float(info.get("trailingEps"))
    fwd_eps    = safe_float(info.get("forwardEps"))
    div        = safe_float(info.get("dividendRate"))
    total_debt = safe_float(info.get("totalDebt"), 0.0)
    cash       = safe_float(info.get("totalCash"), 0.0)
    net_income = safe_float(info.get("netIncomeToCommon"))

    def dcf_model(fcf0, g_high, g_low, r, label, calidad):
        if fcf0 is None or shares is None or shares <= 0 or r <= g_low:
            return
        pv = 0.0
        for t in range(1, 6):
            pv += fcf0 * (1 + g_high) ** t / (1 + r) ** t
        for t in range(6, 11):
            pv += fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** (t - 5) / (1 + r) ** t
        terminal    = fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** 5 * (1 + g_low) / (r - g_low)
        pv_terminal = terminal / (1 + r) ** 10
        equity = pv + pv_terminal + cash - total_debt
        methods.append({
            "Metodo":    label,
            "Tipo":      "DCF",
            "Calidad":   calidad,
            "Valor":     equity / shares,
            "Supuestos": f"g {g_high*100:.0f}%→{g_low*100:.0f}%, r {r*100:.0f}%",
        })

    if fcf is not None:
        dcf_model(fcf, 0.15, 0.04, 0.11, "DCF agresivo",    "Media")
        dcf_model(fcf, 0.10, 0.03, 0.10, "DCF base",        "Alta")
        dcf_model(fcf, 0.06, 0.02, 0.09, "DCF conservador", "Alta")

    if net_income is not None and shares and shares > 0:
        dcf_model(net_income, 0.08, 0.03, 0.10, "DCF beneficio neto", "Media")

    if ebitda is not None and ebitda > 0 and shares and shares > 0:
        for mult, cal in [(8, "Alta"), (10, "Alta"), (12, "Media"), (15, "Media"), (20, "Baja")]:
            ev = ebitda * mult
            methods.append({
                "Metodo":    f"EV/EBITDA {mult}x",
                "Tipo":      "Múltiplo",
                "Calidad":   cal,
                "Valor":     (ev + cash - total_debt) / shares,
                "Supuestos": f"EBITDA={fmt_large(ebitda)}, múltiplo={mult}x",
            })

    if ebit is not None and ebit > 0 and shares and shares > 0:
        for mult, cal in [(10, "Alta"), (14, "Media"), (18, "Baja")]:
            ev = ebit * mult
            methods.append({
                "Metodo":    f"EV/EBIT {mult}x",
                "Tipo":      "Múltiplo",
                "Calidad":   cal,
                "Valor":     (ev + cash - total_debt) / shares,
                "Supuestos": f"EBIT={fmt_large(ebit)}, múltiplo={mult}x",
            })

    eps_use = eps if (eps and eps > 0) else fwd_eps
    if eps_use and eps_use > 0:
        for mult, cal in [(10, "Alta"), (15, "Alta"), (20, "Media"), (25, "Media"), (30, "Baja")]:
            methods.append({
                "Metodo":    f"PER objetivo {mult}x",
                "Tipo":      "Múltiplo",
                "Calidad":   cal,
                "Valor":     eps_use * mult,
                "Supuestos": f"EPS={eps_use:.2f}, PER={mult}x",
            })

    if revenue is not None and shares and shares > 0:
        for mult, cal in [(1, "Alta"), (2, "Alta"), (4, "Media"), (6, "Media"), (8, "Baja")]:
            methods.append({
                "Metodo":    f"P/Ventas {mult}x",
                "Tipo":      "Múltiplo",
                "Calidad":   cal,
                "Valor":     revenue * mult / shares,
                "Supuestos": f"Ventas={fmt_large(revenue)}, múltiplo={mult}x",
            })

    if bvps and bvps > 0:
        for mult, cal in [(1, "Alta"), (1.5, "Alta"), (2, "Media"), (3, "Media"), (4, "Baja")]:
            methods.append({
                "Metodo":    f"P/Valor contable {mult}x",
                "Tipo":      "Múltiplo",
                "Calidad":   cal,
                "Valor":     bvps * mult,
                "Supuestos": f"VCPS={bvps:.2f}, múltiplo={mult}x",
            })

    if eps_use and eps_use > 0 and bvps and bvps > 0:
        methods.append({
            "Metodo":    "Número de Graham",
            "Tipo":      "Mixto",
            "Calidad":   "Alta",
            "Valor":     math.sqrt(22.5 * eps_use * bvps),
            "Supuestos": f"√(22.5 × EPS {eps_use:.2f} × VCPS {bvps:.2f})",
        })
   
