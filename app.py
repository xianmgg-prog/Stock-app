import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import math
import io
import base64
from scipy.optimize import minimize

try:
    from deep_translator import GoogleTranslator
except Exception:
    GoogleTranslator = None

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="Equity Terminal — Value Investing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# SESSION STATE
# =========================
if "analyzed_ticker" not in st.session_state:
    st.session_state.analyzed_ticker = None
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "language" not in st.session_state:
    st.session_state.language = "ES"

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

CHART_COLORS = ["#B68A52", "#8C6A43", "#5E8B6F", "#A47E5B", "#C2A27B"]

# =========================
# TEXTOS MULTIIDIOMA
# =========================
TEXTS = {
    "ES": {
        "hero_title": "Equity Terminal",
        "hero_sub": "Value Investing · Análisis fundamental de empresas cotizadas",
        "search_placeholder": "🔎 Busca una empresa o ticker (ej: Apple, AAPL, Stellantis, TEF.MC...)",
        "analyze": "Analizar →",
        "suggestions": "Sugerencias",
        "options": "⚙️ Opciones de análisis",
        "period": "Período histórico",
        "corr_input": "Tickers para correlación y cartera (separados por comas)",
        "welcome_1": "Introduce el nombre o ticker de una empresa y pulsa Analizar →",
        "welcome_2": "Ejemplos: Apple · MSFT · Stellantis · TEF.MC · SAN.MC · Inditex",
        "loading": "Cargando datos de",
        "price_error": "No se pudo obtener el precio de mercado. Verifica el ticker.",
        "company": "Empresa",
        "ratios": "Ratios",
        "valuation": "Valoración",
        "benchmarks": "Benchmarks",
        "correlations": "Correlaciones",
        "price": "Precio",
        "portfolio": "Optimización de Cartera",
        "financials": "Estados financieros",
        "description": "Descripción",
        "corp_data": "Datos corporativos",
        "country": "País",
        "city": "Ciudad",
        "exchange": "Exchange",
        "employees": "Empleados",
        "sector": "Sector",
        "industry": "Industria",
        "market_cap": "Market Cap",
        "high_52": "52W Máx",
        "low_52": "52W Mín",
        "beta": "Beta",
        "market_val": "Valoración de mercado",
        "profitability": "Rentabilidad",
        "risk_liq": "Riesgo y liquidez",
        "financial_profile": "Perfil financiero (radar)",
        "intrinsic_title": "Valoración intrínseca — todos los métodos",
        "valuation_warn": "No se pudieron calcular valoraciones por falta de datos.",
        "bench_title": "Comparación con benchmarks del sector",
        "bench_warn": "No se pudieron cargar datos de benchmarks.",
        "bench_none": "No hay benchmarks definidos para este sector.",
        "corr_title": "Correlación de rentabilidades",
        "corr_matrix": "Matriz de correlación",
        "cum_returns": "Retornos acumulados",
        "price_hist": "Histórico de precio y volumen",
        "price_hist_warn": "No hay datos históricos disponibles.",
        "portfolio_title": "Optimización de Cartera de Markowitz",
        "portfolio_warn": "Datos históricos insuficientes. Asegúrate de configurar los tickers correctamente en las opciones superiores.",
        "portfolio_cfg": "Configura las variables para optimizar tu selección actual de activos:",
        "optimizer_goal": "Objetivo del Optimizador",
        "goal_sharpe": "Maximizar Ratio Sharpe (Eficiencia)",
        "goal_var": "Minimizar Varianza (Mínimo Riesgo)",
        "rf_rate": "Tasa libre de riesgo anualizada (%)",
        "portfolio_metrics": "Métricas de la Cartera Óptima",
        "exp_return": "Retorno Esperado Anual",
        "volatility": "Volatilidad de la Cartera",
        "sharpe": "Ratio Sharpe Resultante",
        "financials_title": "Estados financieros",
        "income_stmt": "Cuenta de resultados",
        "balance_sheet": "Balance",
        "cash_flow": "Flujo de caja",
        "no_data": "No hay datos disponibles.",
        "detail_methods": "Detalle de cada método",
        "used": "Qué se usó",
        "explanation": "Explicación",
        "type": "Tipo",
        "quality": "Calidad",
        "current_price": "Precio actual",
        "intrinsic_value": "Valor intrínseco",
        "upside": "Upside",
        "interpretation": "Interpretación",
        "language": "Idioma",
        "score": "Score",
        "filings": "Informes",
        "regulatory_reports": "Informes Regulatorios",
        "select_report": "Selecciona un informe:",
        "open_original": "Abrir documento original en el navegador",
        "generate_pdf": "⚙️ Generar PDF",
        "download_pdf": "⬇️ Descargar PDF",
        "preview": "Vista previa del documento",
        "downloading_bench": "Descargando benchmarks...",
        "downloading_prices": "Descargando precios históricos...",
        "optimizer_error": "El algoritmo no convergió.",
        "filings_none": "No se han encontrado informes regulatorios para este ticker. Nota: la búsqueda SEC solo funciona con tickers de EE.UU. sin sufijo (ej: AAPL, MSFT).",
    },
    "EN": {
        "hero_title": "Equity Terminal",
        "hero_sub": "Value Investing · Fundamental analysis of listed companies",
        "search_placeholder": "🔎 Search a company or ticker (e.g. Apple, AAPL, Stellantis, TEF.MC...)",
        "analyze": "Analyze →",
        "suggestions": "Suggestions",
        "options": "⚙️ Analysis options",
        "period": "Historical period",
        "corr_input": "Tickers for correlation and portfolio (comma separated)",
        "welcome_1": "Enter a company name or ticker and press Analyze →",
        "welcome_2": "Examples: Apple · MSFT · Stellantis · TEF.MC · SAN.MC · Inditex",
        "loading": "Loading data for",
        "price_error": "Could not retrieve market price. Check the ticker.",
        "company": "Company",
        "ratios": "Ratios",
        "valuation": "Valuation",
        "benchmarks": "Benchmarks",
        "correlations": "Correlations",
        "price": "Price",
        "portfolio": "Portfolio Optimization",
        "financials": "Financial Statements",
        "description": "Description",
        "corp_data": "Corporate data",
        "country": "Country",
        "city": "City",
        "exchange": "Exchange",
        "employees": "Employees",
        "sector": "Sector",
        "industry": "Industry",
        "market_cap": "Market Cap",
        "high_52": "52W High",
        "low_52": "52W Low",
        "beta": "Beta",
        "market_val": "Market valuation",
        "profitability": "Profitability",
        "risk_liq": "Risk and liquidity",
        "financial_profile": "Financial profile (radar)",
        "intrinsic_title": "Intrinsic valuation — all methods",
        "valuation_warn": "Valuation methods could not be calculated due to missing data.",
        "bench_title": "Sector benchmark comparison",
        "bench_warn": "Benchmark data could not be loaded.",
        "bench_none": "No benchmarks defined for this sector.",
        "corr_title": "Return correlation",
        "corr_matrix": "Correlation matrix",
        "cum_returns": "Cumulative returns",
        "price_hist": "Price and volume history",
        "price_hist_warn": "No historical data available.",
        "portfolio_title": "Markowitz Portfolio Optimization",
        "portfolio_warn": "Insufficient historical data. Make sure tickers are configured correctly in the options above.",
        "portfolio_cfg": "Set the variables to optimize your current asset selection:",
        "optimizer_goal": "Optimizer goal",
        "goal_sharpe": "Maximize Sharpe Ratio (Efficiency)",
        "goal_var": "Minimize Variance (Minimum Risk)",
        "rf_rate": "Annualized risk-free rate (%)",
        "portfolio_metrics": "Optimal Portfolio Metrics",
        "exp_return": "Expected Annual Return",
        "volatility": "Portfolio Volatility",
        "sharpe": "Resulting Sharpe Ratio",
        "financials_title": "Financial statements",
        "income_stmt": "Income statement",
        "balance_sheet": "Balance sheet",
        "cash_flow": "Cash flow",
        "no_data": "No data available.",
        "detail_methods": "Detail for each method",
        "used": "What was used",
        "explanation": "Explanation",
        "type": "Type",
        "quality": "Quality",
        "current_price": "Current price",
        "intrinsic_value": "Intrinsic value",
        "upside": "Upside",
        "interpretation": "Interpretation",
        "language": "Language",
        "score": "Score",
        "filings": "Filings",
        "regulatory_reports": "Regulatory Reports",
        "select_report": "Select a report:",
        "open_original": "Open original document in browser",
        "generate_pdf": "⚙️ Generate PDF",
        "download_pdf": "⬇️ Download PDF",
        "preview": "Document preview",
        "downloading_bench": "Downloading benchmarks...",
        "downloading_prices": "Downloading historical prices...",
        "optimizer_error": "The optimizer did not converge.",
        "filings_none": "No regulatory reports were found for this ticker. Note: SEC search only works for U.S. tickers without suffix (e.g. AAPL, MSFT).",
    },
}

lang = st.session_state.language
T = TEXTS[lang]

# =========================
# CSS
# =========================
st.markdown(
    f"""
    <style>
    [data-testid="collapsedControl"] {{ display: none; }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }}

    .stApp {{
        background:
            radial-gradient(circle at top left, {BG_GRAD_1} 0%, {BG_MAIN} 45%, {BG_GRAD_2} 100%);
        color: {TEXT_PRIMARY};
        font-family: "Inter", "Segoe UI", sans-serif;
    }}

    .hero-wrap {{
        padding: 1.2rem 0 1.8rem 0;
        text-align: center;
    }}

    .hero-title {{
        font-size: 2.9rem;
        font-weight: 800;
        letter-spacing: 0.02em;
        color: {TEXT_PRIMARY};
        margin-bottom: 0.35rem;
    }}

    .hero-sub {{
        color: {TEXT_SECONDARY};
        font-size: 0.95rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }}

    .soft-divider {{
        height: 1px;
        width: 100%;
        background: linear-gradient(90deg, transparent, {BORDER}, transparent);
        margin: 1.25rem 0 1.75rem 0;
    }}

    .fade-container {{
        opacity: 0;
        animation: fadeInUp 0.45s ease-out forwards;
    }}

    @keyframes fadeInUp {{
        0%   {{ opacity: 0; transform: translateY(10px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}

    .metric-card {{
        background: linear-gradient(180deg, {CARD_BG} 0%, {CARD_BG_2} 100%);
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 1rem 1rem 0.95rem 1rem;
        box-shadow: 0 8px 24px rgba(120, 93, 61, 0.06);
        margin-bottom: 0.5rem;
    }}

    .metric-label {{
        color: {TEXT_SECONDARY};
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        margin-bottom: 0.25rem;
    }}

    .metric-value {{
        color: {TEXT_PRIMARY};
        font-size: 1.15rem;
        font-weight: 700;
        line-height: 1.2;
    }}

    .metric-sub {{
        color: {TEXT_SECONDARY};
        font-size: 0.75rem;
        margin-top: 0.18rem;
    }}

    .company-header {{
        background: linear-gradient(180deg, rgba(255,253,249,0.92) 0%, rgba(249,244,236,0.92) 100%);
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 1.2rem 1.25rem;
        margin: 0.7rem 0 1rem 0;
        box-shadow: 0 10px 30px rgba(120, 93, 61, 0.05);
    }}

    .company-name {{
        font-size: 1.7rem;
        font-weight: 800;
        color: {TEXT_PRIMARY};
    }}

    .company-meta {{
        color: {TEXT_SECONDARY};
        font-size: 0.95rem;
        margin-top: 0.15rem;
    }}

    .company-price {{
        font-size: 2rem;
        font-weight: 800;
        color: {ACCENT_GOLD};
        margin-top: 0.55rem;
    }}

    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        background: rgba(255, 253, 249, 0.96) !important;
        color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 14px !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        background: rgba(255, 253, 249, 0.96) !important;
        color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 14px !important;
    }}

    .stButton > button {{
        background: linear-gradient(180deg, {ACCENT_GOLD_SOFT} 0%, {ACCENT_GOLD} 100%);
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.72rem 1rem !important;
        box-shadow: 0 8px 22px rgba(182, 138, 82, 0.22);
    }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 0.35rem; }}

    .stTabs [data-baseweb="tab"] {{
        background: rgba(255, 251, 245, 0.95);
        border: 1px solid {BORDER};
        border-radius: 12px 12px 0 0;
        color: {TEXT_SECONDARY};
        padding: 0.75rem 1.1rem;
        font-size: 0.92rem;
    }}

    .stTabs [aria-selected="true"] {{
        background: {CARD_BG} !important;
        color: {TEXT_PRIMARY} !important;
        border-bottom-color: {CARD_BG} !important;
        font-weight: 700 !important;
    }}

    .stExpander {{
        border: 1px solid {BORDER} !important;
        border-radius: 16px !important;
        background: rgba(255,253,249,0.7) !important;
    }}

    .champ-table-wrap {{
        background: {CARD_BG};
        border: 1px solid {TABLE_BORDER};
        border-radius: 18px;
        overflow-x: auto;
        box-shadow: 0 10px 28px rgba(120, 93, 61, 0.05);
        margin-top: 0.5rem;
    }}

    .champ-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.93rem;
    }}

    .champ-table thead th {{
        background: {TABLE_HEADER_BG};
        color: {TEXT_SECONDARY};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.73rem;
        text-align: left;
        padding: 0.95rem 0.9rem;
        border-bottom: 1px solid {TABLE_BORDER};
        white-space: nowrap;
    }}

    .champ-table tbody td {{
        padding: 0.88rem 0.9rem;
        border-bottom: 1px solid rgba(216, 199, 178, 0.55);
        color: {TEXT_PRIMARY};
        background: {TABLE_ROW_BG};
        vertical-align: top;
    }}

    .champ-table tbody tr:nth-child(even) td {{
        background: {TABLE_ALT_BG};
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
        white-space: nowrap;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================
def tr_text(text, target_lang="en"):
    if not text or not isinstance(text, str):
        return text
    if GoogleTranslator is None:
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception:
        return text


@st.cache_data(show_spinner=False, ttl=3600)
def cached_translate(text, target_lang="en"):
    return tr_text(text, target_lang)


def maybe_translate(text):
    if st.session_state.language == "EN":
        return cached_translate(text, "en")
    return text


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
    if v >= 1e9:
        return f"{sign*v/1e9:.2f}B"
    if v >= 1e6:
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
        <div class="company-header fade-container">
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
        if any(x in v for x in ["alta", "high", "infraval", "underval", "buy", "+"]):
            return "pill pill-green"
        if any(x in v for x in ["baja", "low", "sobreval", "overval", "sell"]):
            return "pill pill-red"
        return "pill pill-gold"

    html = '<div class="champ-table-wrap fade-container"><table class="champ-table"><thead><tr>'
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


@st.cache_data(show_spinner=False, ttl=3600)
def search_ticker(query: str):
    if not query:
        return []
    try:
        url = (
            "https://query2.finance.yahoo.com/v1/finance/search"
            f"?q={query}&lang=en-US&region=US&quotesCount=8&newsCount=0"
        )
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
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
    "Healthcare": ["JNJ", "PFE", "MRK", "ABBV"],
    "Industrials": ["GE", "CAT", "HON", "BA"],
}


def get_benchmark_list(info, main_ticker):
    sector = info.get("sector")
    peers = DEFAULT_BENCHMARKS.get(sector, [])
    peers = [p for p in peers if p.upper() != main_ticker.upper()]
    return peers[:4]


def format_financial_df(df, lang_):
    if df is None or df.empty:
        return None
    out = df.copy()
    try:
        out = out.iloc[:, :6]
    except Exception:
        pass
    out.columns = [str(c.date()) if hasattr(c, "date") else str(c)[:10] for c in out.columns]
    out = out.fillna(np.nan)
    out = out.map(lambda x: fmt_large(x) if pd.notna(x) else "N/A")
    out.reset_index(inplace=True)
    out.rename(columns={"index": "Concepto" if lang_ == "ES" else "Item"}, inplace=True)
    return out


# =========================
# DATA HELPERS
# =========================
@st.cache_data(show_spinner=False, ttl=1800)
def get_ticker_bundle(ticker: str, period: str):
    stock = yf.Ticker(ticker)

    info = {}
    try:
        info = stock.info or {}
    except Exception:
        info = {}

    hist = pd.DataFrame()
    try:
        hist = stock.history(period=period, auto_adjust=False)
    except Exception:
        hist = pd.DataFrame()

    financials = pd.DataFrame()
    balance_sheet = pd.DataFrame()
    cashflow = pd.DataFrame()

    try:
        financials = stock.financials
    except Exception:
        pass
    try:
        balance_sheet = stock.balance_sheet
    except Exception:
        pass
    try:
        cashflow = stock.cashflow
    except Exception:
        pass

    return info, hist, financials, balance_sheet, cashflow


@st.cache_data(show_spinner=False, ttl=1800)
def get_prices_download(tickers, period):
    df_download = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    if isinstance(df_download.columns, pd.MultiIndex):
        try:
            prices = df_download.xs("Close", level=0, axis=1, drop_level=True)
        except Exception:
            prices = pd.DataFrame()
    else:
        if len(tickers) == 1 and "Close" in df_download.columns:
            prices = df_download["Close"].to_frame(name=tickers[0])
        elif "Close" in df_download.columns:
            prices = df_download["Close"]
        else:
            prices = pd.DataFrame()
    return prices


@st.cache_data(show_spinner=False, ttl=1800)
def get_peer_info(tickers):
    data = {}
    for t in tickers:
        try:
            tk = yf.Ticker(t)
            inf = tk.info or {}
            data[t] = {
                "Name": inf.get("shortName", t),
                "P/E": safe_float(inf.get("trailingPE")),
                "P/B": safe_float(inf.get("priceToBook")),
                "ROE": safe_float(inf.get("returnOnEquity")),
                "Net Margin": safe_float(inf.get("profitMargins")),
                "Price": safe_float(inf.get("currentPrice")) or safe_float(inf.get("regularMarketPrice")),
                "Market Cap": safe_float(inf.get("marketCap")),
            }
        except Exception:
            continue
    return data


# =========================
# SEC / CNMV HELPERS
# =========================
SEC_BASE = "https://data.sec.gov"
SEC_HEADERS = {
    "User-Agent": "EquityTerminal/1.0 contacto@equityterminal.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}
SEC_HEADERS_WWW = {
    "User-Agent": "EquityTerminal/1.0 contacto@equityterminal.com",
    "Accept-Encoding": "gzip, deflate",
}


@st.cache_data(show_spinner=False, ttl=86400)
def get_cik_from_ticker_us(ticker: str):
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        resp = requests.get(url, headers=SEC_HEADERS_WWW, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        ticker_up = ticker.upper().replace(".", "")
        for entry in data.values():
            if entry["ticker"].upper() == ticker_up:
                return str(entry["cik_str"]).zfill(10)
        return None
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=3600)
def get_sec_filings_metadata(cik: str, form_types=("10-K", "10-Q", "20-F", "40-F"), limit=25):
    try:
        url = f"{SEC_BASE}/submissions/CIK{cik}.json"
        resp = requests.get(url, headers=SEC_HEADERS, timeout=30)
        resp.raise_for_status()
        j = resp.json()
        filings = j.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        acc_no = filings.get("accessionNumber", [])
        primary_docs = filings.get("primaryDocument", [])

        rows = []
        for f, d, a, doc in zip(forms, dates, acc_no, primary_docs):
            if f not in form_types:
                continue
            accession_clean = a.replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{doc}"
            rows.append(
                {
                    "Regulador": "SEC",
                    "CIK": cik,
                    "Formulario": f,
                    "Fecha": d,
                    "Documento": doc,
                    "URL": filing_url,
                }
            )
            if len(rows) >= limit:
                break
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def get_cnmv_filings_for_spanish_issuer(ticker_base: str):
    return pd.DataFrame()


def html_to_pdf_bytes(html_content: str, base_url: str):
    try:
        from weasyprint import HTML as WeasyHTML
        pdf_buffer = io.BytesIO()
        WeasyHTML(string=html_content, base_url=base_url).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer.read()
    except Exception:
        return None


# =========================
# VALORACIÓN
# =========================
def compute_valuations(info, lang_):
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

    def add_method(label, tipo, calidad, valor, usado, detalle):
        if valor is None or not np.isfinite(valor):
            return
        methods.append(
            {
                "Método": label,
                "Tipo": tipo,
                "Calidad": calidad,
                "Valor": valor,
                "Qué se usó": usado,
                "Detalle": detalle,
            }
        )

    def dcf_model(fcf0, g_high, g_low, r, label, calidad, origen):
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
        valor_accion = equity / shares

        if lang_ == "ES":
            detalle = (
                f"Se parte de {origen} actual ({fmt_large(fcf0)}), se proyecta con crecimiento del "
                f"{g_high*100:.0f}% durante 5 años, después del {g_low*100:.0f}% durante otros 5 años, "
                f"y todo se descuenta a una tasa del {r*100:.0f}%. Luego se añade la caja, se resta la deuda "
                f"y se divide entre el número de acciones."
            )
            usado = f"{origen} · crecimiento {g_high*100:.0f}% → {g_low*100:.0f}% · descuento {r*100:.0f}%"
        else:
            detalle = (
                f"It starts from current {origen} ({fmt_large(fcf0)}), projects growth at "
                f"{g_high*100:.0f}% for 5 years, then {g_low*100:.0f}% for another 5 years, "
                f"and discounts everything at {r*100:.0f}%. Then cash is added, debt is subtracted, "
                f"and the result is divided by shares outstanding."
            )
            usado = f"{origen} · growth {g_high*100:.0f}% → {g_low*100:.0f}% · discount {r*100:.0f}%"

        add_method(label, "DCF", calidad, valor_accion, usado, detalle)

    if fcf is not None:
        dcf_model(fcf, 0.15, 0.04, 0.11, "DCF Agresivo" if lang_ == "ES" else "Aggressive DCF", "Media" if lang_ == "ES" else "Medium", "flujo de caja libre" if lang_ == "ES" else "free cash flow")
        dcf_model(fcf, 0.10, 0.03, 0.10, "DCF Base" if lang_ == "ES" else "Base DCF", "Alta" if lang_ == "ES" else "High", "flujo de caja libre" if lang_ == "ES" else "free cash flow")
        dcf_model(fcf, 0.06, 0.02, 0.09, "DCF Conservador" if lang_ == "ES" else "Conservative DCF", "Alta" if lang_ == "ES" else "High", "flujo de caja libre" if lang_ == "ES" else "free cash flow")

    if net_income is not None and shares and shares > 0:
        dcf_model(net_income, 0.08, 0.03, 0.10, "DCF (Bº neto proxy)" if lang_ == "ES" else "DCF (Net income proxy)", "Media" if lang_ == "ES" else "Medium", "beneficio neto" if lang_ == "ES" else "net income")

    if ebitda is not None and ebitda > 0 and shares and shares > 0:
        for mult, cal in [(8, "Alta"), (10, "Alta"), (12, "Media"), (15, "Media")]:
            ev = ebitda * mult
            valor_accion = (ev + cash - total_debt) / shares
            detalle = (
                f"Se toma el EBITDA ({fmt_large(ebitda)}) y se multiplica por {mult}× para estimar el valor empresa. Después se suma la caja, se resta la deuda y se divide entre las acciones en circulación."
                if lang_ == "ES"
                else f"EBITDA ({fmt_large(ebitda)}) is multiplied by {mult}× to estimate enterprise value. Then cash is added, debt is subtracted, and the result is divided by shares outstanding."
            )
            add_method(
                f"EV/EBITDA {mult}×",
                "Múltiplo" if lang_ == "ES" else "Multiple",
                cal if lang_ == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}[cal],
                valor_accion,
                f"EBITDA × {mult}",
                detalle,
            )

    if ebit is not None and ebit > 0 and shares and shares > 0:
        for mult, cal in [(10, "Alta"), (14, "Media"), (18, "Baja")]:
            ev = ebit * mult
            valor_accion = (ev + cash - total_debt) / shares
            detalle = (
                f"Se toma el EBIT ({fmt_large(ebit)}) y se multiplica por {mult}× para obtener el valor empresa. Luego se ajusta por caja y deuda, y se divide entre el número de acciones."
                if lang_ == "ES"
                else f"EBIT ({fmt_large(ebit)}) is multiplied by {mult}× to estimate enterprise value. Then cash and debt adjustments are applied and divided by shares outstanding."
            )
            add_method(
                f"EV/EBIT {mult}×",
                "Múltiplo" if lang_ == "ES" else "Multiple",
                cal if lang_ == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}[cal],
                valor_accion,
                f"EBIT × {mult}",
                detalle,
            )

    eps_use = eps if (eps and eps > 0) else fwd_eps
    eps_origen = ("BPA histórico" if lang_ == "ES" else "Historical EPS") if (eps and eps > 0) else ("BPA estimado" if lang_ == "ES" else "Forward EPS")

    if eps_use and eps_use > 0:
        for mult, cal in [(10, "Alta"), (15, "Alta"), (20, "Media"), (25, "Media")]:
            valor_accion = eps_use * mult
            detalle = (
                f"Se usa el {eps_origen.lower()} por acción ({eps_use:.2f}) y se multiplica por un PER objetivo de {mult}×. Así se obtiene un precio razonable por acción según ese múltiplo."
                if lang_ == "ES"
                else f"The {eps_origen.lower()} ({eps_use:.2f}) is multiplied by a target P/E of {mult}×. This gives an estimated fair value per share under that multiple."
            )
            add_method(
                f"P/E {mult}×",
                "Múltiplo" if lang_ == "ES" else "Multiple",
                cal if lang_ == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}[cal],
                valor_accion,
                f"{eps_origen} × {mult}",
                detalle,
            )

    if revenue is not None and shares and shares > 0:
        for mult, cal in [(1, "Alta"), (2, "Alta"), (4, "Media"), (6, "Baja")]:
            valor_accion = revenue * mult / shares
            detalle = (
                f"Se toman las ventas totales ({fmt_large(revenue)}) y se multiplican por {mult}×. El resultado se divide entre las acciones para obtener un valor aproximado por acción."
                if lang_ == "ES"
                else f"Total revenue ({fmt_large(revenue)}) is multiplied by {mult}×, and the result is divided by shares outstanding to estimate a value per share."
            )
            add_method(
                f"P/Ventas {mult}×" if lang_ == "ES" else f"P/Sales {mult}×",
                "Múltiplo" if lang_ == "ES" else "Multiple",
                cal if lang_ == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}[cal],
                valor_accion,
                f"Ventas × {mult} ÷ acciones" if lang_ == "ES" else f"Sales × {mult} ÷ shares",
                detalle,
            )

    if bvps and bvps > 0:
        for mult, cal in [(1, "Alta"), (1.5, "Alta"), (2, "Media"), (3, "Baja")]:
            valor_accion = bvps * mult
            detalle = (
                f"Se usa el valor en libros por acción ({bvps:.2f}) y se multiplica por {mult}×. Es una forma de valorar cuánto pagar por cada unidad de patrimonio neto por acción."
                if lang_ == "ES"
                else f"Book value per share ({bvps:.2f}) is multiplied by {mult}×. It estimates how much to pay for each unit of equity per share."
            )
            add_method(
                f"P/Valor Libros {mult}×" if lang_ == "ES" else f"P/Book {mult}×",
                "Múltiplo" if lang_ == "ES" else "Multiple",
                cal if lang_ == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}[cal],
                valor_accion,
                f"{'Valor en libros por acción' if lang_ == 'ES' else 'Book value per share'} × {mult}",
                detalle,
            )

    if eps_use and eps_use > 0 and bvps and bvps > 0:
        graham = math.sqrt(22.5 * eps_use * bvps)
        add_method(
            "Graham Number",
            "Mixto" if lang_ == "ES" else "Hybrid",
            "Alta" if lang_ == "ES" else "High",
            graham,
            "√(22.5 × BPA × valor en libros por acción)" if lang_ == "ES" else "√(22.5 × EPS × book value per share)",
            (
                f"Se combina el beneficio por acción ({eps_use:.2f}) con el valor en libros por acción ({bvps:.2f}). Se multiplican ambos por 22.5 y luego se aplica una raíz cuadrada: √(22.5 × BPA × valor en libros por acción)."
                if lang_ == "ES"
                else f"Earnings per share ({eps_use:.2f}) and book value per share ({bvps:.2f}) are combined. Both are multiplied by 22.5 and then a square root is applied: √(22.5 × EPS × book value per share)."
            ),
        )

    if div and div > 0:
        for g_div, r_div, label_div in [
            (0.02, 0.08, "DDM (g 2%, r 8%)"),
            (0.03, 0.09, "DDM (g 3%, r 9%)"),
        ]:
            if r_div > g_div:
                val_ddm = div * (1 + g_div) / (r_div - g_div)
                detalle = (
                    f"Se toma el dividendo anual por acción ({div:.2f}), se aumenta con un crecimiento esperado del {g_div*100:.0f}%, y se divide entre la diferencia entre la rentabilidad exigida ({r_div*100:.0f}%) y ese crecimiento."
                    if lang_ == "ES"
                    else f"Annual dividend per share ({div:.2f}) is increased by expected growth of {g_div*100:.0f}% and divided by the difference between required return ({r_div*100:.0f}%) and growth."
                )
                add_method(
                    label_div,
                    "DDM",
                    "Media" if lang_ == "ES" else "Medium",
                    val_ddm,
                    "Dividendo × (1 + crecimiento) ÷ (rentabilidad exigida − crecimiento)" if lang_ == "ES" else "Dividend × (1 + growth) ÷ (required return − growth)",
                    detalle,
                )

    for m in methods:
        m["Precio"] = price
        if price and price > 0:
            m["Upside %"] = round((m["Valor"] - price) / price * 100, 1)
        else:
            m["Upside %"] = None

    return methods, price


# =========================
# HEADER + LANGUAGE
# =========================
top1, top2 = st.columns([5, 1])
with top2:
    st.selectbox(
        TEXTS[st.session_state.language]["language"],
        options=["ES", "EN"],
        key="language",
    )

lang = st.session_state.language
T = TEXTS[lang]

st.markdown(
    f"""
    <div class="hero-wrap fade-container">
        <div class="hero-title">{T["hero_title"]}</div>
        <div class="hero-sub">{T["hero_sub"]}</div>
    </div>
    <div class="soft-divider"></div>
    """,
    unsafe_allow_html=True,
)

# =========================
# BÚSQUEDA
# =========================
col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input(
        "",
        placeholder=T["search_placeholder"],
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button(T["analyze"], use_container_width=True, type="primary")

if query != st.session_state.current_query:
    st.session_state.current_query = query

ticker_sym = ""
if query:
    suggestions = search_ticker(query)
    if suggestions:
        choice = st.selectbox(T["suggestions"], suggestions, label_visibility="collapsed", key="ticker_suggestion")
        ticker_sym = choice.split(" — ")[0].strip()
    else:
        ticker_sym = query.strip().upper()

if analyze_btn and ticker_sym:
    st.session_state.analyzed_ticker = ticker_sym

with st.expander(T["options"], expanded=False):
    op1, op2 = st.columns([1, 2])
    with op1:
        period = st.selectbox(T["period"], ["1y", "3y", "5y", "10y"], index=1, key="period_select")
    with op2:
        st.text_input(
            T["corr_input"],
            value="AAPL, MSFT, GOOGL, AMZN, META",
            key="corr_input_box"
        )

if "period_select" not in st.session_state:
    st.session_state.period_select = "3y"

period = st.session_state.period_select
corr_tickers_input = st.session_state.get("corr_input_box", "AAPL, MSFT, GOOGL, AMZN, META")

# =========================
# WELCOME
# =========================
if not st.session_state.analyzed_ticker:
    st.markdown("---")
    st.markdown(
        f"""
        <div class="fade-container" style="text-align:center; color:{TEXT_SECONDARY}; padding: 3rem 0;">
            <div style="font-size:3rem;">🏦</div>
            <div style="font-size:1.1rem; margin-top:0.5rem;">
                {T["welcome_1"]}
            </div>
            <div style="font-size:0.85rem; margin-top:0.5rem;">
                {T["welcome_2"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

active_ticker = st.session_state.analyzed_ticker

# =========================
# DATA
# =========================
with st.spinner(f'{T["loading"]} {active_ticker}...'):
    try:
        info, hist, financials, balance_sheet, cashflow = get_ticker_bundle(active_ticker, period)
    except Exception 
