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
from deep_translator import GoogleTranslator  # NUEVO

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
        return "N/A"
    return f"{v:.{decimals}f}{suffix}"

def fmt_large(x):
    v = safe_float(x, None)
    if v is None:
        return "N/A"
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
    "Consumer Cíclical":      ["AMZN", "TSLA", "HD", "MCD"],
    "Energy":                 ["XOM", "CVX", "BP", "TOT"],
}

def get_benchmark_list(info, main_ticker):
    sector = info.get("sector")
    peers  = DEFAULT_BENCHMARKS.get(sector, [])
    peers  = [p for p in peers if p.upper() != main_ticker.upper()]
    return peers[:4]

# ===== TRADUCTOR =====
def traducir_a_es(texto: str) -> str:
    if not texto:
        return ""
    try:
        # auto-detecta idioma y traduce a español
        return GoogleTranslator(source="auto", target="es").translate(texto)
    except Exception:
        # si falla, devolvemos el original para no romper nada
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
                "Metodo":    f"P/E {mult}x",
                "Tipo":      "Múltiplo",
                "Calidad":   cal,
                "Valor":     eps_use * mult,
                "Supuestos": f"EPS={eps_use:.2f}, múltiplo={mult}x",
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
            "Supuestos": f"sqrt(22.5 × EPS {eps_use:.2f} × VCPS {bvps:.2f})",
        })
        methods.append({
            "Metodo":    "Graham ajustado 15x",
            "Tipo":      "Mixto",
            "Calidad":   "Media",
            "Valor":     math.sqrt(15 * eps_use * bvps),
            "Supuestos": f"sqrt(15 × EPS {eps_use:.2f} × VCPS {bvps:.2f})",
        })

    if div and div > 0:
        for g_div, r_div, label_div in [
            (0.02, 0.08, "DDM g 2%, r 8%"),
            (0.03, 0.09, "DDM g 3%, r 9%"),
            (0.05, 0.10, "DDM g 5%, r 10%"),
        ]:
            if r_div > g_div:
                methods.append({
                    "Metodo":    label_div,
                    "Tipo":      "DDM",
                    "Calidad":   "Media",
                    "Valor":     div * (1 + g_div) / (r_div - g_div),
                    "Supuestos": f"Dividendo={div:.2f}, g={g_div*100:.0f}%, r={r_div*100:.0f}%",
                })

    for m in methods:
        m["Precio"] = price
        if price and price > 0:
            m["Upside %"] = round((m["Valor"] - price) / price * 100, 1)
        else:
            m["Upside %"] = None

    return methods, price

def style_df(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    styler = df.style.set_properties(
        **{
            "background-color": CARD_BG,
            "color": TEXT_PRIMARY,
            "border-color": BORDER,
            "border-width": "1px",
            "border-style": "solid",
            "font-size": "13px",
        }
    )
    styler = styler.set_table_styles(
        [
            {
                "selector": "tbody tr:nth-child(even)",
                "props": [("background-color", CARD_BG_ALT)],
            },
            {
                "selector": "thead th",
                "props": [
                    ("background-color", BORDER),
                    ("color", TEXT_PRIMARY),
                    ("font-size", "11px"),
                    ("text-transform", "uppercase"),
                    ("letter-spacing", "0.06em"),
                ],
            },
        ]
    )
    return styler

# =========================
# HERO / BUSCADOR
# =========================
st.markdown('<div class="hero-title">Equity Terminal</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Value investing · Análisis fundamental de empresas cotizadas</div>', unsafe_allow_html=True)

col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input(
        "",
        placeholder="Busca una empresa o ticker (Apple, AAPL, TEF.MC, SAN.MC...)",
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button("Analizar", use_container_width=True, type="primary")

if query != st.session_state["current_query"]:
    st.session_state["current_query"] = query

ticker_sym = ""
if query:
    suggestions = search_ticker(query)
    if suggestions:
        choice     = st.selectbox("Sugerencias", suggestions, label_visibility="collapsed")
        ticker_sym = choice.split(" — ")[0].strip()
    else:
        ticker_sym = query.strip().upper()

with st.expander("Opciones de análisis", expanded=False):
    op1, op2 = st.columns([1, 2])
    with op1:
        period = st.selectbox("Período histórico", ["1y", "3y", "5y", "10y"], index=1)
    with op2:
        corr_tickers_input = st.text_input(
            "Tickers para correlación y cartera (separados por comas)",
            value="AAPL, MSFT, GOOGL, AMZN, META",
        )

if analyze_btn and ticker_sym:
    st.session_state["analyzed_ticker"] = ticker_sym

if not st.session_state["analyzed_ticker"]:
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center;color:{TEXT_SECONDARY};padding:3rem 0;">
            <div style="font-size:3rem;">🏦</div>
            <div style="font-size:1.1rem;margin-top:0.5rem;">
                Escribe el nombre o ticker de una empresa y pulsa <b>Analizar</b>.
            </div>
            <div style="font-size:0.85rem;margin-top:0.5rem;">
                Ejemplos: Apple · MSFT · Stellantis · TEF.MC · SAN.MC · Inditex
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

active_ticker = st.session_state["analyzed_ticker"]

# =========================
# DATOS PRINCIPALES
# =========================
with st.spinner(f"Cargando datos de {active_ticker}..."):
    try:
        stock = yf.Ticker(active_ticker)
        info  = stock.info
        hist  = stock.history(period=period)
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        st.stop()

price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
if price is None:
    st.error("No se pudo obtener el precio de mercado. Revisa el ticker.")
    st.stop()

company_name = info.get("longName") or info.get("shortName") or active_ticker
sector       = info.get("sector",   "N/A")
industry     = info.get("industry", "N/A")
currency     = info.get("currency", "USD")

prev_close = safe_float(info.get("previousClose"))
if price and prev_close:
    chg       = price - prev_close
    chg_pct   = chg / prev_close * 100
    color_chg = ACCENT_GREEN if chg >= 0 else ACCENT_RED
    delta_str = f'<span style="color:{color_chg}">{chg:+.2f} ({chg_pct:+.2f}%)</span>'
else:
    delta_str = ""

st.markdown(
    f"""
    <div style="margin:1.2rem 0 0.3rem 0;">
        <span style="font-size:1.7rem;font-weight:700;">{company_name}</span>
        <span style="color:{TEXT_SECONDARY};font-size:0.95rem;margin-left:0.8rem;">
            {active_ticker} · {sector} · {industry} · {currency}
        </span>
    </div>
    <div style="font-size:2rem;font-weight:700;margin-bottom:0.5rem;">
        {price:.2f} {currency} {delta_str}
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
for col, label, val in [
    (k1, "Capitalización bursátil", fmt_large(info.get("marketCap"))),
    (k2, "Máximo 52 semanas",       f"{fmt_num(info.get('fiftyTwoWeekHigh'))} {currency}"),
    (k3, "Mínimo 52 semanas",       f"{fmt_num(info.get('fiftyTwoWeekLow'))} {currency}"),
    (k4, "Beta",                    fmt_num(info.get("beta"))),
]:
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{val}</div></div>',
            unsafe_allow_html=True,
        )

returns = None

# =========================
# PESTAÑAS
# =========================
tab_emp, tab_rat, tab_val, tab_bench, tab_corr, tab_price, tab_port = st.tabs(
    ["Empresa", "Ratios", "Valoración", "Benchmarks", "Correlaciones", "Precio", "Optimización de cartera"]
)

# ---- EMPRESA ----
with tab_emp:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Descripción del negocio")
        desc = info.get("longBusinessSummary")
        if desc:
            st.write(traducir_a_es(desc))
        else:
            st.info("No hay descripción disponible para esta empresa.")
    with c2:
        st.subheader("Datos corporativos")
        employees = info.get("fullTimeEmployees")
        for label, val in [
            ("País",      info.get("country",  "N/D")),
            ("Ciudad",    info.get("city",     "N/D")),
            ("Bolsa",     info.get("exchange", "N/D")),
            ("Empleados", f"{employees:,}" if employees else "N/D"),
            ("Sector",    sector),
            ("Industria", industry),
        ]:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{val}</div></div>',
                unsafe_allow_html=True,
            )

# ---- RATIOS ----
with tab_rat:
    pe            = safe_float(info.get("trailingPE"))
    fwd_pe        = safe_float(info.get("forwardPE"))
    pb            = safe_float(info.get("priceToBook"))
    ps            = safe_float(info.get("priceToSalesTrailing12Months"))
    roe           = safe_float(info.get("returnOnEquity"))
    roa           = safe_float(info.get("returnOnAssets"))
    profit_margin = safe_float(info.get("profitMargins"))
    gross_margin  = safe_float(info.get("grossMargins"))
    debt_equity   = safe_float(info.get("debtToEquity"))
    current_ratio = safe_float(info.get("currentRatio"))
    quick_ratio   = safe_float(info.get("quickRatio"))
    dividend_yield = safe_float(info.get("dividendYield"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Valoración de mercado**")
        st.write(f"PER (últimos 12m): **{fmt_num(pe)}**")
        st.write(f"PER (estimado): **{fmt_num(fwd_pe)}**")
        st.write(f"P/VC (precio/valor contable): **{fmt_num(pb)}**")
        st.write(f"P/Ventas: **{fmt_num(ps)}**")
    with col2:
        st.markdown("**Rentabilidad**")
        st.write(f"ROE (rent. sobre fondos propios): **{fmt_num(roe*100 if roe else None, 1, '%')}**")
        st.write(f"ROA (rent. sobre activos): **{fmt_num(roa*100 if roa else None, 1, '%')}**")
        st.write(f"Margen bruto: **{fmt_num(gross_margin*100 if gross_margin else None, 1, '%')}**")
        st.write(f"Margen neto: **{fmt_num(profit_margin*100 if profit_margin else None, 1, '%')}**")
    with col3:
        st.markdown("**Riesgo y liquidez**")
        st.write(f"Deuda / patrimonio: **{fmt_num(debt_equity)}**")
        st.write(f"Ratio corriente: **{fmt_num(current_ratio)}**")
        st.write(f"Prueba ácida: **{fmt_num(quick_ratio)}**")
        st.write(f"Rentabilidad por dividendo: **{fmt_num(dividend_yield*100 if dividend_yield else None, 2, '%')}**")

# … (resto de pestañas igual que en el mensaje anterior:
# Valoración con Score y expanders, Benchmarks, Correlaciones, Precio, Optimización)
# Copia y pega debajo exactamente el bloque que ya tienes funcionando.
