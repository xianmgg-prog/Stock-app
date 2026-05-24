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

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Equity Terminal — Champagne Edition",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "analyzed_ticker" not in st.session_state:
    st.session_state.analyzed_ticker = None
if "current_query" not in st.session_state:
    st.session_state.current_query = ""

# =========================
# PALETA CHAMPAGNE
# =========================
ACCENT_GOLD = "#B68A52"
ACCENT_GOLD_SOFT = "#D6B98C"
ACCENT_GREEN = "#5E8B6F"
ACCENT_RED = "#B85C5C"

BG_MAIN = "#F7F1E8"
BG_GRAD_1 = "#F3E7D7"
BG_GRAD_2 = "#EADBC8"

CARD_BG = "#FFFDF9"
CARD_BG_2 = "#F9F4EC"
BORDER = "#D9C8B4"

TEXT_PRIMARY = "#2F241B"
TEXT_SECONDARY = "#7A6856"
TEXT_FAINT = "#A08F7C"

TABLE_HEADER_BG = "#EFE2D2"
TABLE_ROW_BG = "#FFFDF9"
TABLE_ALT_BG = "#FAF5EE"
TABLE_BORDER = "#D8C7B2"

CHART_COLORS = [
    "#B68A52",
    "#8C6A43",
    "#5E8B6F",
    "#A47E5B",
    "#C2A27B",
]

# =========================
# CSS GLOBAL
# =========================
st.markdown(
    f"""
    <style>
    :root {{
        --accent-gold: {ACCENT_GOLD};
        --accent-gold-soft: {ACCENT_GOLD_SOFT};
        --accent-green: {ACCENT_GREEN};
        --accent-red: {ACCENT_RED};

        --bg-main: {BG_MAIN};
        --bg-grad-1: {BG_GRAD_1};
        --bg-grad-2: {BG_GRAD_2};

        --card-bg: {CARD_BG};
        --card-bg-2: {CARD_BG_2};
        --border: {BORDER};

        --text-primary: {TEXT_PRIMARY};
        --text-secondary: {TEXT_SECONDARY};
        --text-faint: {TEXT_FAINT};

        --table-header-bg: {TABLE_HEADER_BG};
        --table-row-bg: {TABLE_ROW_BG};
        --table-alt-bg: {TABLE_ALT_BG};
        --table-border: {TABLE_BORDER};
    }}

    [data-testid="collapsedControl"] {{
        display: none;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }}

    .stApp {{
        background: radial-gradient(circle at top left, var(--bg-grad-1) 0%, var(--bg-main) 45%, var(--bg-grad-2) 100%);
        color: var(--text-primary);
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: var(--text-primary);
    }}

    .hero-wrap {{
        padding: 1.2rem 0 1.8rem 0;
        text-align: center;
    }}

    .hero-title {{
        font-size: 2.9rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        color: var(--text-primary);
        margin-bottom: 0.35rem;
    }}

    .hero-sub {{
        color: var(--text-secondary);
        font-size: 0.95rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }}

    .soft-divider {{
        height: 1px;
        width: 100%;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 1.25rem 0 1.75rem 0;
    }}

    .metric-card {{
        background: linear-gradient(180deg, var(--card-bg) 0%, var(--card-bg-2) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1rem 0.95rem 1rem;
        box-shadow: 0 8px 24px rgba(120, 93, 61, 0.06);
        margin-bottom: 0.5rem;
    }}

    .metric-label {{
        color: var(--text-secondary);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        margin-bottom: 0.25rem;
    }}

    .metric-value {{
        color: var(--text-primary);
        font-size: 1.15rem;
        font-weight: 700;
        line-height: 1.2;
    }}

    .metric-sub {{
        color: var(--text-secondary);
        font-size: 0.75rem;
        margin-top: 0.18rem;
    }}

    .company-header {{
        background: linear-gradient(180deg, rgba(255,253,249,0.92) 0%, rgba(249,244,236,0.92) 100%);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.2rem 1.25rem;
        margin: 0.7rem 0 1rem 0;
        box-shadow: 0 10px 30px rgba(120, 93, 61, 0.05);
    }}

    .company-name {{
        font-size: 1.7rem;
        font-weight: 800;
        color: var(--text-primary);
    }}

    .company-meta {{
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-top: 0.15rem;
    }}

    .company-price {{
        font-size: 2rem;
        font-weight: 800;
        color: var(--accent-gold);
        margin-top: 0.55rem;
    }}

    .stTextInput input, .stNumberInput input {{
        background: rgba(255, 253, 249, 0.96) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        background: rgba(255, 253, 249, 0.96) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
    }}

    .stButton > button {{
        background: linear-gradient(180deg, var(--accent-gold-soft) 0%, var(--accent-gold) 100%);
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.72rem 1rem !important;
        box-shadow: 0 8px 22px rgba(182, 138, 82, 0.22);
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.35rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: rgba(255, 251, 245, 0.95);
        border: 1px solid var(--border);
        border-radius: 12px 12px 0 0;
        color: var(--text-secondary);
        padding: 0.75rem 1.1rem;
        font-size: 0.92rem;
    }}

    .stTabs [aria-selected="true"] {{
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
        border-bottom-color: var(--card-bg) !important;
        font-weight: 700 !important;
    }}

    .stExpander {{
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        background: rgba(255,253,249,0.7) !important;
    }}

    .champ-table-wrap {{
        background: var(--card-bg);
        border: 1px solid var(--table-border);
        border-radius: 18px;
        overflow-x: auto;
        box-shadow: 0 10px 28px rgba(120, 93, 61, 0.05);
        margin-top: 0.5rem;
    }}

    .champ-table {{
        width: 100%;
        min-width: 900px;
        border-collapse: collapse;
        font-size: 0.93rem;
    }}

    .champ-table thead th {{
        background: var(--table-header-bg);
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.73rem;
        text-align: left;
        padding: 0.95rem 0.9rem;
        border-bottom: 1px solid var(--table-border);
        white-space: nowrap;
    }}

    .champ-table tbody td {{
        padding: 0.88rem 0.9rem;
        border-bottom: 1px solid rgba(216, 199, 178, 0.55);
        color: var(--text-primary);
        background: var(--table-row-bg);
        white-space: nowrap;
    }}

    .champ-table tbody tr:nth-child(even) td {{
        background: var(--table-alt-bg);
    }}

    .champ-table tbody tr:hover td {{
        background: #F4EBDD;
    }}

    .pill {{
        display: inline-block;
        padding: 0.28rem 0.55rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }}

    .pill-gold {{
        background: rgba(182, 138, 82, 0.14);
        color: #8B6738;
    }}

    .pill-green {{
        background: rgba(94, 139, 111, 0.14);
        color: #41614E;
    }}

    .pill-red {{
        background: rgba(184, 92, 92, 0.14);
        color: #8A4444;
    }}

    .section-title {{
        font-size: 1.08rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 0.7rem;
    }}

    .section-sub {{
        color: var(--text-secondary);
        font-size: 0.92rem;
        margin-bottom: 0.8rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

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
        return f"{sign*v/1e12:.2f}T"
    elif v >= 1e9:
        return f"{sign*v/1e9:.2f}B"
    elif v >= 1e6:
        return f"{sign*v/1e6:.2f}M"
    return f"{sign*v:.0f}"

def metric_card(label, value, sub=None):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_company_header(company_name, ticker, sector, industry, currency, price, delta_html=""):
    st.markdown(
        f"""
        <div class="company-header">
            <div class="company-name">{company_name}</div>
            <div class="company-meta">{ticker} · {sector} · {industry} · {currency}</div>
            <div class="company-price">{price:.2f} {currency} {delta_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_champagne_table(df: pd.DataFrame, pills_cols=None):
    pills_cols = pills_cols or []

    def pill_class(val):
        v = str(val).lower()
        if any(x in v for x in ["alta", "muy infravalorado", "infravalorado", "buy", "+"]):
            return "pill pill-green"
        if any(x in v for x in ["baja", "muy sobrevalorado", "sobrevalorado", "sell"]):
            return "pill pill-red"
        return "pill pill-gold"

    html = '<div class="champ-table-wrap"><table class="champ-table"><thead><tr>'
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = row[col]
            display = "N/A" if pd.isna(val) else str(val)
            if col in pills_cols:
                html += f'<td><span class="{pill_class(display)}">{display}</span></td>'
            else:
                html += f"<td>{display}</td>"
        html += "</tr>"

    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)

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
            name = q.get("longname") or q.get("shortname", "")
            exch = q.get("exchDisp", "")
            results.append(f"{symbol} — {name} ({exch})")
        return results
    except Exception:
        return []

DEFAULT_BENCHMARKS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "AMZN"],
    "Communication Services": ["GOOGL", "META", "NFLX", "DIS"],
    "Financial Services": ["JPM", "BAC", "C", "GS"],
    "Consumer Cyclical": ["AMZN", "TSLA", "HD", "MCD"],
    "Energy": ["XOM", "CVX", "BP", "TTE"],
}

def get_benchmark_list(info, main_ticker):
    sector = info.get("sector")
    peers = DEFAULT_BENCHMARKS.get(sector, [])
    peers = [p for p in peers if p.upper() != main_ticker.upper()]
    return peers[:4]

def get_statement_df(stock, statement_type, statement_period):
    if statement_type == "Income Statement":
        raw = stock.income_stmt if statement_period == "Annual" else stock.quarterly_income_stmt
    elif statement_type == "Balance Sheet":
        raw = stock.balance_sheet if statement_period == "Annual" else stock.quarterly_balance_sheet
    else:
        raw = stock.cashflow if statement_period == "Annual" else stock.quarterly_cashflow

    if raw is None or raw.empty:
        return pd.DataFrame()

    df = raw.copy()
    df.columns = [pd.to_datetime(c).strftime("%Y-%m-%d") if not isinstance(c, str) else c for c in df.columns]
    df = df.reset_index()
    df = df.rename(columns={df.columns[0]: "Concepto"})
    return df

# =========================
# MÉTODOS DE VALORACIÓN
# =========================
def compute_valuations(info, currency):
    methods = []

    price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
    shares = safe_float(info.get("sharesOutstanding"))
    fcf = safe_float(info.get("freeCashflow"))
    revenue = safe_float(info.get("totalRevenue"))
    ebitda = safe_float(info.get("ebitda"))
    ebit = safe_float(info.get("ebit"))
    bvps = safe_float(info.get("bookValue"))
    eps = safe_float(info.get("trailingEps"))
    fwd_eps = safe_float(info.get("forwardEps"))
    div = safe_float(info.get("dividendRate"))
    total_debt = safe_float(info.get("totalDebt"), 0.0)
    cash = safe_float(info.get("totalCash"), 0.0)
    net_income = safe_float(info.get("netIncomeToCommon"))

    def dcf_model(fcf0, g_high, g_low, r, label, calidad):
        if fcf0 is None or shares is None or shares <= 0 or r <= g_low:
            return
        pv = 0.0
        for t in range(1, 6):
            pv += fcf0 * (1 + g_high) ** t / (1 + r) ** t
        for t in range(6, 11):
            pv += fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** (t - 5) / (1 + r) ** t
        terminal = fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** 5 * (1 + g_low) / (r - g_low)
        pv_terminal = terminal / (1 + r) ** 10
        equity = pv + pv_terminal + cash - total_debt
        methods.append({
            "Método": label,
            "Tipo": "DCF",
            "Calidad": calidad,
            "Valor": equity / shares,
            "Supuestos": f"g {g_high*100:.0f}%→{g_low*100:.0f}%, r {r*100:.0f}%",
        })

    if fcf is not None:
        dcf_model(fcf, 0.15, 0.04, 0.11, "DCF Agresivo", "Media")
        dcf_model(fcf, 0.10, 0.03, 0.10, "DCF Base", "Alta")
        dcf_model(fcf, 0.06, 0.02, 0.09, "DCF Conservador", "Alta")

    if net_income is not None and shares and shares > 0:
        dcf_model(net_income, 0.08, 0.03, 0.10, "DCF (Bº neto proxy)", "Media")

    if ebitda is not None and ebitda > 0 and shares and shares > 0:
        for mult, cal in [(8, "Alta"), (10, "Alta"), (12, "Media"), (15, "Media"), (20, "Baja")]:
            ev = ebitda * mult
            methods.append({
                "Método": f"EV/EBITDA {mult}×",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": (ev + cash - total_debt) / shares,
                "Supuestos": f"EBITDA={fmt_large(ebitda)}, mult={mult}×",
            })

    if ebit is not None and ebit > 0 and shares and shares > 0:
        for mult, cal in [(10, "Alta"), (14, "Media"), (18, "Baja")]:
            ev = ebit * mult
            methods.append({
                "Método": f"EV/EBIT {mult}×",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": (ev + cash - total_debt) / shares,
                "Supuestos": f"EBIT={fmt_large(ebit)}, mult={mult}×",
            })

    eps_use = eps if (eps and eps > 0) else fwd_eps
    if eps_use and eps_use > 0:
        for mult, cal in [(10, "Alta"), (15, "Alta"), (20, "Media"), (25, "Media"), (30, "Baja")]:
            methods.append({
                "Método": f"P/E {mult}×",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": eps_use * mult,
                "Supuestos": f"EPS={eps_use:.2f}, mult={mult}×",
            })

    if revenue is not None and shares and shares > 0:
        for mult, cal in [(1, "Alta"), (2, "Alta"), (4, "Media"), (6, "Media"), (8, "Baja")]:
            methods.append({
                "Método": f"P/Ventas {mult}×",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": revenue * mult / shares,
                "Supuestos": f"Ventas={fmt_large(revenue)}, mult={mult}×",
            })

    if bvps and bvps > 0:
        for mult, cal in [(1, "Alta"), (1.5, "Alta"), (2, "Media"), (3, "Media"), (4, "Baja")]:
            methods.append({
                "Método": f"P/Valor Libros {mult}×",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": bvps * mult,
                "Supuestos": f"BVPS={bvps:.2f}, mult={mult}×",
            })

    if eps_use and eps_use > 0 and bvps and bvps > 0:
        graham = math.sqrt(22.5 * eps_use * bvps)
        methods.append({
            "Método": "Graham Number",
            "Tipo": "Mixto",
            "Calidad": "Alta",
            "Valor": graham,
            "Supuestos": f"√(22.5 × EPS {eps_use:.2f} × BVPS {bvps:.2f})",
        })
        graham_adj = math.sqrt(15 * eps_use * bvps)
        methods.append({
            "Método": "Graham Ajustado (15×)",
            "Tipo": "Mixto",
            "Calidad": "Media",
            "Valor": graham_adj,
            "Supuestos": f"√(15 × EPS {eps_use:.2f} × BVPS {bvps:.2f})",
        })

    if div and div > 0:
        for g_div, r_div, label_div in [
            (0.02, 0.08, "DDM (g 2%, r 8%)"),
            (0.03, 0.09, "DDM (g 3%, r 9%)"),
            (0.05, 0.10, "DDM (g 5%, r 10%)"),
        ]:
            if r_div > g_div:
                val_ddm = div * (1 + g_div) / (r_div - g_div)
                methods.append({
                    "Método": label_div,
                    "Tipo": "DDM",
                    "Calidad": "Media",
                    "Valor": val_ddm,
                    "Supuestos": f"Div={div:.2f}, g={g_div*100:.0f}%, r={r_div*100:.0f}%",
                })

    for m in methods:
        m["Precio"] = price
        if price and price > 0:
            upside = (m["Valor"] - price) / price * 100
            m["Upside %"] = round(upside, 1)
        else:
            m["Upside %"] = None

    return methods, price

def style_plotly(fig):
    fig.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#FFFDF9",
        font=dict(color=TEXT_PRIMARY),
        title_font=dict(color=TEXT_PRIMARY),
        legend=dict(bgcolor="rgba(255,255,255,0)", bordercolor=BORDER),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=BORDER,
        tickfont=dict(color=TEXT_SECONDARY),
    )
    fig.update_yaxes(
        gridcolor="rgba(217,200,180,0.45)",
        linecolor=BORDER,
        tickfont=dict(color=TEXT_SECONDARY),
    )
    return fig

# =========================
# HERO
# =========================
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-title">Equity Terminal</div>
        <div class="hero-sub">Value Investing · Análisis fundamental de empresas cotizadas</div>
    </div>
    <div class="soft-divider"></div>
    """,
    unsafe_allow_html=True,
)

col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input(
        "",
        placeholder="🔎 Busca una empresa o ticker (ej: Apple, AAPL, Stellantis, TEF.MC...)",
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button("Analizar →", use_container_width=True, type="primary")

if query != st.session_state.current_query:
    st.session_state.current_query = query

ticker_sym = ""
if query:
    suggestions = search_ticker(query)
    if suggestions:
        choice = st.selectbox("Sugerencias", suggestions, label_visibility="collapsed")
        ticker_sym = choice.split(" — ")[0].strip()
    else:
        ticker_sym = query.strip().upper()

if analyze_btn and ticker_sym:
    st.session_state.analyzed_ticker = ticker_sym

with st.expander("⚙️ Opciones de análisis", expanded=False):
    op1, op2 = st.columns([1, 2])
    with op1:
        period = st.selectbox("Período histórico", ["1y", "3y", "5y", "10y"], index=1)
    with op2:
        corr_tickers_input = st.text_input(
            "Tickers para correlación y cartera (separados por comas)",
            value="AAPL, MSFT, GOOGL, AMZN, META",
        )

if not st.session_state.analyzed_ticker:
    st.markdown(
        f"""
        <div style="text-align:center; color:{TEXT_SECONDARY}; padding: 3rem 0;">
            <div style="font-size:3rem;">🏦</div>
            <div style="font-size:1.1rem; margin-top:0.5rem;">
                Introduce el nombre o ticker de una empresa y pulsa <b>Analizar →</b>
            </div>
            <div style="font-size:0.85rem; margin-top:0.5rem;">
                Ejemplos: Apple · MSFT · Stellantis · TEF.MC · SAN.MC · Inditex
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

active_ticker = st.session_state.analyzed_ticker

# =========================
# DATOS
# =========================
with st.spinner(f"Cargando datos de {active_ticker}..."):
    try:
        stock = yf.Ticker(active_ticker)
        info = stock.info
        hist = stock.history(period=period)
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        st.stop()

price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
if price is None:
    st.error("No se pudo obtener el precio de mercado. Verifica el ticker.")
    st.stop()

company_name = info.get("longName") or info.get("shortName") or active_ticker
sector = info.get("sector", "N/A")
industry = info.get("industry", "N/A")
currency = info.get("currency", "USD")

prev_close = safe_float(info.get("previousClose"))
if price and prev_close:
    chg = price - prev_close
    chg_pct = chg / prev_close * 100
    color_chg = ACCENT_GREEN if chg >= 0 else ACCENT_RED
    delta_str = f'<span style="color:{color_chg}; font-size:1rem;">{chg:+.2f} ({chg_pct:+.2f}%)</span>'
else:
    delta_str = ""

render_company_header(company_name, active_ticker, sector, industry, currency, price, delta_str)

mc = fmt_large(info.get("marketCap"))
high52 = fmt_num(info.get("fiftyTwoWeekHigh"))
low52 = fmt_num(info.get("fiftyTwoWeekLow"))
beta_v = fmt_num(info.get("beta"))

k1, k2, k3, k4 = st.columns(4)
with k1:
    metric_card("Market Cap", mc)
with k2:
    metric_card("52W Máx", f"{high52} {currency}")
with k3:
    metric_card("52W Mín", f"{low52} {currency}")
with k4:
    metric_card("Beta", beta_v)

returns = None

# =========================
# TABS
# =========================
tab_emp, tab_rat, tab_fin, tab_val, tab_bench, tab_corr, tab_price, tab_port = st.tabs(
    [
        "Empresa",
        "Ratios",
        "Estados financieros",
        "Valoración",
        "Benchmarks",
        "Correlaciones",
        "Precio",
        "Optimización de Cartera",
    ]
)

# =========================
# TAB EMPRESA
# =========================
with tab_emp:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="section-title">Descripción</div>', unsafe_allow_html=True)
        desc = info.get("longBusinessSummary")
        if desc:
            st.write(desc)
        else:
            st.info("No hay descripción disponible.")
    with c2:
        st.markdown('<div class="section-title">Datos corporativos</div>', unsafe_allow_html=True)
        employees = info.get("fullTimeEmployees")
        for label, val in [
            ("País", info.get("country", "N/A")),
            ("Ciudad", info.get("city", "N/A")),
            ("Exchange", info.get("exchange", "N/A")),
            ("Empleados", f"{employees:,}" if employees else "N/A"),
            ("Sector", sector),
            ("Industria", industry),
        ]:
            metric_card(label, val)

# =========================
# TAB RATIOS
# =========================
with tab_rat:
    pe = safe_float(info.get("trailingPE"))
    fwd_pe = safe_float(info.get("forwardPE"))
    pb = safe_float(info.get("priceToBook"))
    ps = safe_float(info.get("priceToSalesTrailing12Months"))
    roe = safe_float(info.get("returnOnEquity"))
    roa = safe_float(info.get("returnOnAssets"))
    profit_margin = safe_float(info.get("profitMargins"))
    gross_margin = safe_float(info.get("grossMargins"))
    debt_equity = safe_float(info.get("debtToEquity"))
    current_ratio = safe_float(info.get("currentRatio"))
    quick_ratio = safe_float(info.get("quickRatio"))
    dividend_yield = safe_float(info.get("dividendYield"))

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("P/E (TTM)", fmt_num(pe))
        metric_card("P/E (Fwd)", fmt_num(fwd_pe))
        metric_card("P/B", fmt_num(pb))
        metric_card("P/S", fmt_num(ps))
    with col2:
        metric_card("ROE", fmt_num(roe*100 if roe else None, 1, "%"))
        metric_card("ROA", fmt_num(roa*100 if roa else None, 1, "%"))
        metric_card("Margen bruto", fmt_num(gross_margin*100 if gross_margin else None, 1, "%"))
        metric_card("Margen neto", fmt_num(profit_margin*100 if profit_margin else None, 1, "%"))
    with col3:
        metric_card("Deuda/Equity", fmt_num(debt_equity))
        metric_card("Current ratio", fmt_num(current_ratio))
        metric_card("Quick ratio", fmt_num(quick_ratio))
        metric_card("Dividend yield", fmt_num(dividend_yield*100 if dividend_yield else None, 2, "%"))

    def norm(v, lo, hi):
        v2 = safe_float(v, None)
        if v2 is None:
            return 0.0
        return max(0.0, min(1.0, (v2 - lo) / (hi - lo)))

    radar_labels = ["ROE", "ROA", "Margen neto", "P/E bajo", "Deuda baja", "Liquidez"]
    radar_values = [
        norm(roe*100 if roe else None, 0, 40),
        norm(roa*100 if roa else None, 0, 20),
        norm(profit_margin*100 if profit_margin else None, 0, 30),
        1 - norm(pe, 0, 40),
        1 - norm(debt_equity, 0, 200),
        norm(current_ratio, 0, 3),
    ]
    radar_values += [radar_values[0]]
    radar_labels += [radar_labels[0]]

    fig_radar = go.Figure(
        data=go.Scatterpolar(
            r=radar_values,
            theta=radar_labels,
            fill="toself",
            line_color=ACCENT_GOLD,
            fillcolor="rgba(182,138,82,0.25)",
        )
    )
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(217,200,180,0.45)")
        ),
        showlegend=False,
        height=350,
    )
    style_plotly(fig_radar)
    st.plotly_chart(fig_radar, use_container_width=True)

# =========================
# TAB ESTADOS FINANCIEROS
# =========================
with tab_fin:
    st.markdown('<div class="section-title">Estados financieros</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Consulta históricos anuales o trimestrales de resultados, balance y flujo de caja.</div>',
        unsafe_allow_html=True,
    )

    f1, f2 = st.columns([1, 1])
    with f1:
        statement_type = st.selectbox(
            "Tipo de estado",
            ["Income Statement", "Balance Sheet", "Cash Flow"]
        )
    with f2:
        statement_period = st.selectbox(
            "Periodicidad",
            ["Annual", "Quarterly"]
        )

    df_fin = get_statement_df(stock, statement_type, statement_period)

    if df_fin.empty:
        st.warning("No hay datos disponibles para este estado financiero.")
    else:
        cols_periods = [c for c in df_fin.columns if c != "Concepto"]

        st.markdown('<div class="section-title">Tabla histórica</div>', unsafe_allow_html=True)
        render_champagne_table(df_fin)

        st.markdown('<div class="section-title" style="margin-top:1.2rem;">Comparativa visual</div>', unsafe_allow_html=True)

        default_candidates = [
            "Total Revenue",
            "Net Income",
            "Operating Income",
            "EBITDA",
            "Gross Profit",
            "Free Cash Flow",
            "Operating Cash Flow",
            "Cash And Cash Equivalents",
            "Total Assets",
            "Total Debt",
            "Stockholders Equity",
        ]
        available_concepts = df_fin["Concepto"].astype(str).tolist()
        default_selected = [x for x in default_candidates if x in available_concepts][:4]
        if not default_selected and len(available_concepts) > 0:
            default_selected = available_concepts[:3]

        selected_metrics = st.multiselect(
            "Selecciona partidas para graficar",
            options=available_concepts,
            default=default_selected
        )

        if selected_metrics:
            df_plot = df_fin[df_fin["Concepto"].isin(selected_metrics)].copy()
            df_plot_long = df_plot.melt(
                id_vars="Concepto",
                value_vars=cols_periods,
                var_name="Fecha",
                value_name="Valor"
            )
            df_plot_long["Valor"] = pd.to_numeric(df_plot_long["Valor"], errors="coerce")
            df_plot_long = df_plot_long.dropna(subset=["Valor"])

            fig_fin = px.line(
                df_plot_long,
                x="Fecha",
                y="Valor",
                color="Concepto",
                markers=True,
                color_discrete_sequence=CHART_COLORS,
            )
            fig_fin.update_layout(height=430, yaxis_title="Valor reportado")
            style_plotly(fig_fin)
            st.plotly_chart(fig_fin, use_container_width=True)

            with st.expander("Ver tabla interactiva adicional"):
                st.dataframe(df_fin, use_container_width=True, hide_index=True)
        else:
            st.info("Selecciona al menos una partida para mostrar la comparativa.")

# =========================
# TAB VALORACIÓN
# =========================
with tab_val:
    st.markdown('<div class="section-title">Valoración intrínseca</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Resumen de métodos, calidad, valor intrínseco y rango de upside.</div>', unsafe_allow_html=True)

    methods, current_price = compute_valuations(info, currency)

    if not methods:
        st.warning("No se pudieron calcular valoraciones por falta de datos.")
    else:
        df_val = pd.DataFrame(methods)
        df_val = df_val[["Método", "Tipo", "Calidad", "Valor", "Precio", "Upside %", "Supuestos"]]

        def rango_upside(u):
            if pd.isna(u):
                return "N/A"
            if u >= 40:
                return "Muy infravalorado"
            if u >= 20:
                return "Infravalorado"
            if u >= -10:
                return "En línea"
            if u >= -30:
                return "Sobrevalorado"
            return "Muy sobrevalorado"

        df_val["Interpretación"] = df_val["Upside %"].apply(rango_upside)

        def score_row(row):
            u = row["Upside %"]
            cal = row["Calidad"]
            if pd.isna(u):
                base = 2
            elif u >= 40:
                base = 5
            elif u >= 20:
                base = 4
            elif u >= 0:
                base = 3
            elif u >= -20:
                base = 2
            else:
                base = 1

            if cal == "Alta":
                base = min(base + 1, 5)
            elif cal == "Baja":
                base = max(base - 1, 1)

            return "★" * base + "☆" * (5 - base)

        df_val["Score"] = df_val.apply(score_row, axis=1)

        def fmt_val(v):
            return f"{v:.2f}" if pd.notna(v) else "N/A"

        def fmt_up(u):
            return f"{u:+.1f}%" if pd.notna(u) else "N/A"

        df_tabla = pd.DataFrame({
            "Método": df_val["Método"],
            "Tipo": df_val["Tipo"],
            "Score": df_val["Score"],
            "Upside (%)": df_val["Upside %"].apply(fmt_up),
            "Valor intrínseco": df_val["Valor"].apply(fmt_val),
            "Precio actual": df_val["Precio"].apply(fmt_val),
            "Calidad": df_val["Calidad"],
            "Interpretación": df_val["Interpretación"],
            "Supuestos": df_val["Supuestos"],
        })

        df_tabla = df_tabla.reindex(df_val.sort_values("Upside %", ascending=False).index)
        render_champagne_table(df_tabla, pills_cols=["Calidad", "Interpretación"])

        upsides = df_val["Upside %"].dropna()
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_card("Métodos calculados", str(len(df_val)))
        with m2:
            metric_card("Upside mediano", f"{upsides.median():+.1f}%" if len(upsides) else "N/A")
        with m3:
            metric_card("Upside medio", f"{upsides.mean():+.1f}%" if len(upsides) else "N/A")
        with m4:
            metric_card("Rango upside", f"{upsides.min():+.1f}% / {upsides.max():+.1f}%" if len(upsides) else "N/A")

        fig_val = px.strip(
            df_val,
            x="Upside %",
            y="Tipo",
            color="Tipo",
            hover_data=["Método", "Valor", "Supuestos"],
            color_discrete_map={
                "DCF": CHART_COLORS[0],
                "Múltiplo": CHART_COLORS[1],
                "Mixto": CHART_COLORS[2],
                "DDM": CHART_COLORS[4],
            },
        )
        fig_val.add_vline(x=0, line_dash="dash", line_color="#8B7355", opacity=0.6)
        fig_val.add_vline(x=30, line_dash="dot", line_color=ACCENT_GREEN, opacity=0.6)
        fig_val.update_layout(height=350, xaxis_title="Upside vs precio actual (%)")
        style_plotly(fig_val)
        st.plotly_chart(fig_val, use_container_width=True)

        fig_bar = px.bar(
            df_val.sort_values("Valor"),
            x="Valor",
            y="Método",
            color="Tipo",
            orientation="h",
            color_discrete_map={
                "DCF": CHART_COLORS[0],
                "Múltiplo": CHART_COLORS[1],
                "Mixto": CHART_COLORS[2],
                "DDM": CHART_COLORS[4],
            },
            title=f"Valor intrínseco por método vs precio actual ({current_price:.2f} {currency})",
        )
        fig_bar.add_vline(x=current_price, line_dash="dash", line_color=ACCENT_RED)
        fig_bar.update_layout(height=max(400, len(df_val) * 22))
        style_plotly(fig_bar)
        st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# TAB BENCHMARKS
# =========================
with tab_bench:
    st.markdown('<div class="section-title">Comparables del sector</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Múltiplos y rentabilidad frente a empresas de referencia.</div>', unsafe_allow_html=True)

    peers = get_benchmark_list(info, active_ticker)
    if not peers:
        st.info("No hay benchmarks definidos para este sector.")
    else:
        tickers_all = [active_ticker] + peers
        with st.spinner("Descargando datos de benchmarks..."):
            data = {}
            for t in tickers_all:
                try:
                    tk = yf.Ticker(t)
                    inf = tk.info
                    data[t] = {
                        "Nombre": inf.get("shortName", t),
                        "P/E": safe_float(inf.get("trailingPE")),
                        "P/B": safe_float(inf.get("priceToBook")),
                        "ROE": safe_float(inf.get("returnOnEquity")),
                        "Margen neto": safe_float(inf.get("profitMargins")),
                        "Precio": safe_float(inf.get("currentPrice")) or safe_float(inf.get("regularMarketPrice")),
                        "Market Cap": safe_float(inf.get("marketCap")),
                    }
                except Exception:
                    continue

        if len(data) <= 1:
            st.warning("No se pudieron cargar datos de benchmarks.")
        else:
            df_bench = pd.DataFrame.from_dict(data, orient="index")
            df_bench.index.name = "Ticker"
            df_bench.reset_index(inplace=True)

            def fmt_pe(x):
                return f"{x:.1f}" if pd.notna(x) else "N/A"

            def fmt_ratio(x):
                return f"{x*100:.1f}%" if pd.notna(x) else "N/A"

            def fmt_price(x):
                return f"{x:.2f}" if pd.notna(x) else "N/A"

            def fmt_mc(x):
                return fmt_large(x)

            df_view = pd.DataFrame({
                "Ticker": df_bench["Ticker"],
                "Nombre": df_bench["Nombre"],
                "Precio": df_bench["Precio"].apply(fmt_price),
                "P/E": df_bench["P/E"].apply(fmt_pe),
                "P/B": df_bench["P/B"].apply(fmt_pe),
                "ROE": df_bench["ROE"].apply(fmt_ratio),
                "Margen neto": df_bench["Margen neto"].apply(fmt_ratio),
                "Market Cap": df_bench["Market Cap"].apply(fmt_mc),
            })

            df_view = df_view.reindex(df_bench.sort_values("Market Cap", ascending=False).index)
            render_champagne_table(df_view)

            fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comp.add_trace(
                go.Bar(
                    x=df_bench["Ticker"],
                    y=df_bench["P/E"],
                    name="P/E",
                    marker_color=ACCENT_GOLD,
                ),
                secondary_y=False,
            )
            fig_comp.add_trace(
                go.Scatter(
                    x=df_bench["Ticker"],
                    y=df_bench["ROE"] * 100,
                    name="ROE (%)",
                    mode="lines+markers",
                    line_color=ACCENT_GREEN,
                ),
                secondary_y=True,
            )
            fig_comp.update_yaxes(title_text="P/E", secondary_y=False)
            fig_comp.update_yaxes(title_text="ROE (%)", secondary_y=True)
            fig_comp.update_layout(height=400)
            style_plotly(fig_comp)
            st.plotly_chart(fig_comp, use_container_width=True)

# =========================
# TAB CORRELACIONES
# =========================
with tab_corr:
    st.markdown('<div class="section-title">Correlación de rentabilidades</div>', unsafe_allow_html=True)

    corr_tickers = [t.strip().upper() for t in corr_tickers_input.replace(",", "\n").split("\n") if t.strip()]
    if active_ticker not in corr_tickers:
        corr_tickers.insert(0, active_ticker)

    with st.spinner("Descargando precios históricos..."):
        try:
            df_download = yf.download(corr_tickers, period=period, auto_adjust=True, progress=False)

            if isinstance(df_download.columns, pd.MultiIndex):
                prices = df_download.xs("Close", level=0, axis=1, drop_level=True)
            else:
                prices = df_download["Close"].to_frame(name=corr_tickers[0]) if len(corr_tickers) == 1 else df_download["Close"]

            returns = prices.pct_change().dropna()
        except Exception as e:
            st.error(f"No se pudo descargar precios: {e}")
            returns = None

    if returns is not None and not returns.empty:
        corr = returns.corr()
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="BrBG", zmin=-1, zmax=1)
        fig_corr.update_layout(height=420)
        style_plotly(fig_corr)
        st.plotly_chart(fig_corr, use_container_width=True)

        cum = (1 + returns).cumprod()
        fig_cum = px.line(cum, labels={"value": "Retorno acumulado", "index": "Fecha"}, color_discrete_sequence=CHART_COLORS)
        fig_cum.update_layout(height=400)
        style_plotly(fig_cum)
        st.plotly_chart(fig_cum, use_container_width=True)

# =========================
# TAB PRECIO
# =========================
with tab_price:
    st.markdown('<div class="section-title">Histórico de precio y volumen</div>', unsafe_allow_html=True)
    if hist is None or hist.empty:
        st.warning("No hay datos históricos disponibles.")
    else:
        fig_price = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3]
        )
        fig_price.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name="OHLC",
                increasing_line_color=ACCENT_GREEN,
                decreasing_line_color=ACCENT_RED,
            ),
            row=1, col=1,
        )
        fig_price.add_trace(
            go.Bar(
                x=hist.index,
                y=hist["Volume"],
                name="Volumen",
                marker_color=ACCENT_GOLD_SOFT,
            ),
            row=2, col=1,
        )
        fig_price.update_layout(height=600, xaxis_rangeslider_visible=False)
        style_plotly(fig_price)
        st.plotly_chart(fig_price, use_container_width=True)

# =========================
# TAB CARTERA
# =========================
with tab_port:
    st.markdown('<div class="section-title">Optimización de Cartera de Markowitz</div>', unsafe_allow_html=True)

    if returns is not None and not returns.empty:
        st.markdown('<div class="section-sub">Configura las variables para optimizar tu selección actual de activos.</div>', unsafe_allow_html=True)

        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            objetivo = st.selectbox(
                "Objetivo del Optimizador",
                ["Maximizar Ratio Sharpe (Eficiencia)", "Minimizar Varianza (Mínimo Riesgo)"]
            )
        with c_opt2:
            rf_rate = st.number_input("Tasa libre de riesgo anualizada (%)", value=4.0, step=0.1) / 100

        num_activos = len(corr_tickers)
        rendimientos_medios = returns.mean() * 252
        matriz_covarianza = returns.cov() * 252

        def estadisticas_cartera(weights):
            weights = np.array(weights)
            r_cartera = np.sum(rendimientos_medios * weights)
            vol_cartera = np.sqrt(np.dot(weights.T, np.dot(matriz_covarianza, weights)))
            sharpe = (r_cartera - rf_rate) / vol_cartera if vol_cartera > 0 else 0
            return r_cartera, vol_cartera, sharpe

        def funcion_a_minimizar(weights):
            if objetivo == "Maximizar Ratio Sharpe (Eficiencia)":
                return -estadisticas_cartera(weights)[2]
            return estadisticas_cartera(weights)[1]

        restricciones = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        limites = tuple((0, 1) for _ in range(num_activos))
        pesos_iniciales = num_activos * [1.0 / num_activos]

        resultado_opt = minimize(
            funcion_a_minimizar,
            pesos_iniciales,
            method='SLSQP',
            bounds=limites,
            constraints=restricciones
        )

        if resultado_opt.success:
            pesos_optimos = resultado_opt.x
            r_opt, vol_opt, sharpe_opt = estadisticas_cartera(pesos_optimos)

            c1, c2, c3 = st.columns(3)
            with c1:
                metric_card("Retorno Esperado Anual", f"{r_opt*100:.2f}%")
            with c2:
                metric_card("Volatilidad de la Cartera", f"{vol_opt*100:.2f}%")
            with c3:
                metric_card("Ratio Sharpe Resultante", f"{sharpe_opt:.2f}")

            df_pesos = pd.DataFrame({
                "Activo": corr_tickers,
                "Ponderación Óptima (%)": [f"{w*100:.2f}%" for w in pesos_optimos],
                "Fracción Decimal": np.round(pesos_optimos, 4),
            }).sort_values(by="Fracción Decimal", ascending=False)

            render_champagne_table(df_pesos)

            fig_pie = px.pie(
                df_pesos[df_pesos["Fracción Decimal"] > 0.001],
                values="Fracción Decimal",
                names="Activo",
                title=f"Distribución recomendada de capital ({objetivo})",
                color_discrete_sequence=CHART_COLORS,
            )
            style_plotly(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.error("El algoritmo matemático de optimización no pudo converger en una solución válida.")
    else:
        st.warning("Datos históricos insuficientes. Asegúrate de configurar los tickers correctamente en las opciones superiores.")
