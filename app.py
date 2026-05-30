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
        "informes": "Informes SEC",
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
        "informes": "SEC Filings",
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
    },
}

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
lang = st.session_state.language
T = TEXTS[lang]

def tr_text(text, target_lang="en"):
    if not text or not isinstance(text, str):
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception:
        return text

def maybe_translate(text):
    if st.session_state.language == "EN":
        return tr_text(text, "en")
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
        <div class="company-header fade-container">
            <div class="company-name">{company_name}</div>
            <div class="company-meta">{ticker} · {sector} · {industry} · {currency}</div>
            <div class="company-price">{price:.2f} {currency} {delta_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_champagne_table(df: pd.DataFrame, pills_cols=None, html_cols=None):
    pills_cols = pills_cols or []
    html_cols = html_cols or []

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
            if col in html_cols:
                html += f"<td>{display}</td>"
            elif col in pills_cols:
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

def format_financial_df(df):
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
    out.rename(columns={"index": "Concepto" if lang == "ES" else "Item"}, inplace=True)
    return out

# =========================
# SEC HELPERS — CORREGIDOS
# =========================

SEC_BASE = "https://data.sec.gov"
# ⚠️ PON TU NOMBRE Y EMAIL REAL — la SEC lo exige para no bloquear peticiones
SEC_HEADERS = {
    "User-Agent": "EquityTerminal/1.0 tucorreo@tudominio.com",
    "Accept-Encoding": "gzip, deflate",
}

# Sufijos de bolsas NO americanas
SUFFIXES_NO_US = {
    ".MC", ".L", ".PA", ".AS", ".MI", ".DE", ".HK",
    ".T", ".AX", ".TO", ".BR", ".LS", ".VI", ".SW",
    ".OL", ".ST", ".HE", ".CO", ".BO", ".NS", ".SA"
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_cik_from_ticker_us(ticker: str):
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        resp = requests.get(url, headers=SEC_HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        ticker_norm = ticker.upper().replace(".US", "").replace("-", "").replace(".", "")
        for entry in data.values():
            entry_norm = entry["ticker"].upper().replace("-", "").replace(".", "")
            if entry_norm == ticker_norm:
                return str(entry["cik_str"]).zfill(10)
        return None
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_sec_filings_metadata(cik: str, form_types=None, limit=30):
    if form_types is None:
        form_types = ["10-K", "10-Q", "20-F", "40-F", "8-K", "6-K"]
    try:
        url = f"{SEC_BASE}/submissions/CIK{cik}.json"
        resp = requests.get(url, headers=SEC_HEADERS, timeout=30)
        resp.raise_for_status()
        j = resp.json()

        filings      = j.get("filings", {}).get("recent", {})
        forms        = filings.get("form", [])
        dates        = filings.get("filingDate", [])
        acc_nos      = filings.get("accessionNumber", [])
        primary_docs = filings.get("primaryDocument", [])
        descriptions = filings.get("primaryDocDescription", [])
        extra_files  = j.get("filings", {}).get("files", [])
        cik_int      = str(int(cik))

        rows = []
        for f, d, a, doc, desc in zip(forms, dates, acc_nos, primary_docs, descriptions):
            if f not in form_types:
                continue
            accession_clean = a.replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_clean}/{doc}"
            rows.append({
                "Formulario": f,
                "Descripción": desc if desc else f,
                "Fecha": d,
                "Documento": doc,
                "Ver informe": f'<a href="{filing_url}" target="_blank" style="color:{ACCENT_GOLD};font-weight:600;text-decoration:none;">📄 Abrir</a>',
                "EDGAR": f'<a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={f}&dateb=&owner=include&count=40" target="_blank" style="color:{TEXT_SECONDARY};font-size:0.85rem;text-decoration:none;">🔗 EDGAR</a>',
            })
            if len(rows) >= limit:
                break

        # Paginación adicional de EDGAR si hay pocos resultados
        if len(rows) < 5 and extra_files:
            for ef in extra_files[:3]:
                ef_name = ef.get("name", "")
                if not ef_name:
                    continue
                try:
                    ef_resp = requests.get(f"{SEC_BASE}/submissions/{ef_name}", headers=SEC_HEADERS, timeout=20)
                    ef_resp.raise_for_status()
                    ef_j = ef_resp.json()
                    for f, d, a, doc, desc in zip(
                        ef_j.get("form", []),
                        ef_j.get("filingDate", []),
                        ef_j.get("accessionNumber", []),
                        ef_j.get("primaryDocument", []),
                        ef_j.get("primaryDocDescription", []),
                    ):
                        if f not in form_types:
                            continue
                        accession_clean = a.replace("-", "")
                        filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_clean}/{doc}"
                        rows.append({
                            "Formulario": f,
                            "Descripción": desc if desc else f,
                            "Fecha": d,
                            "Documento": doc,
                            "Ver informe": f'<a href="{filing_url}" target="_blank" style="color:{ACCENT_GOLD};font-weight:600;text-decoration:none;">📄 Abrir</a>',
                            "EDGAR": f'<a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={f}&dateb=&owner=include&count=40" target="_blank" style="color:{TEXT_SECONDARY};font-size:0.85rem;text-decoration:none;">🔗 EDGAR</a>',
                        })
                        if len(rows) >= limit:
                            break
                except Exception:
                    continue
                if len(rows) >= limit:
                    break

        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()

def get_cnmv_filings_for_spanish_issuer(ticker_base: str) -> pd.DataFrame:
    # Stub CNMV — implementa aquí la llamada a su API cuando quieras activarla
    return pd.DataFrame()

# =========================
# VALORACIÓN
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

    def dcf_model(fcf0, g_high, g_low, r, label, calidad, origen):
        if fcf0 is None or shares is None or shares <= 0 or r <= g_low:
            return
        pv = 0.0
        for t in range(1, 6):
            pv += fcf0 * (1 + g_high) ** t / (1 + r) ** t
        for t in range(6, 11):
            pv += fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** (t - 5) / (1 + r) ** t
        terminal   = fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** 5 * (1 + g_low) / (r - g_low)
        pv_terminal = terminal / (1 + r) ** 10
        equity      = pv + pv_terminal + cash - total_debt
        valor_accion = equity / shares

        if lang == "ES":
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

        methods.append({
            "Método": label,
            "Tipo": "DCF",
            "Calidad": calidad if lang == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}.get(calidad, calidad),
            "Valor": valor_accion,
            "Qué se usó": usado,
            "Detalle": detalle,
        })

    if fcf is not None:
        dcf_model(fcf, 0.15, 0.04, 0.11, "DCF Agresivo" if lang == "ES" else "Aggressive DCF", "Media", "flujo de caja libre" if lang == "ES" else "free cash flow")
        dcf_model(fcf, 0.10, 0.03, 0.10, "DCF Base" if lang == "ES" else "Base DCF", "Alta", "flujo de caja libre" if lang == "ES" else "free cash flow")
        dcf_model(fcf, 0.06, 0.02, 0.09, "DCF Conservador" if lang == "ES" else "Conservative DCF", "Alta", "flujo de caja libre" if lang == "ES" else "free cash flow")

    if net_income is not None and shares and shares > 0:
        dcf_model(net_income, 0.08, 0.03, 0.10, "DCF (Bº neto proxy)" if lang == "ES" else "DCF (Net income proxy)", "Media", "beneficio neto" if lang == "ES" else "net income")

    if ebitda is not None and ebitda > 0 and shares and shares > 0:
        for mult, cal in [(8, "Alta"), (10, "Alta"), (12, "Media"), (15, "Media"), (20, "Baja")]:
            ev = ebitda * mult
            valor_accion = (ev + cash - total_debt) / shares
            detalle = (
                f"Se toma el EBITDA ({fmt_large(ebitda)}) y se multiplica por {mult}× para estimar el valor empresa. "
                f"Después se suma la caja, se resta la deuda y se divide entre las acciones en circulación."
                if lang == "ES" else
                f"EBITDA ({fmt_large(ebitda)}) is multiplied by {mult}× to estimate enterprise value. "
                f"Then cash is added, debt is subtracted, and the result is divided by shares outstanding."
            )
            methods.append({
                "Método": f"EV/EBITDA {mult}×",
                "Tipo": "Múltiplo" if lang == "ES" else "Multiple",
                "Calidad": cal if lang == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}.get(cal, cal),
                "Valor": valor_accion,
                "Qué se usó": f"EBITDA × {mult}",
                "Detalle": detalle,
            })

    if ebit is not None and ebit > 0 and shares and shares > 0:
        for mult, cal in [(10, "Alta"), (14, "Media"), (18, "Baja")]:
            ev = ebit * mult
            valor_accion = (ev + cash - total_debt) / shares
            detalle = (
                f"Se toma el EBIT ({fmt_large(ebit)}) y se multiplica por {mult}× para obtener el valor empresa. "
                f"Luego se ajusta por caja y deuda, y se divide entre el número de acciones."
                if lang == "ES" else
                f"EBIT ({fmt_large(ebit)}) is multiplied by {mult}× to estimate enterprise value. "
                f"Then cash and debt adjustments are applied and divided by shares outstanding."
            )
            methods.append({
                "Método": f"EV/EBIT {mult}×",
                "Tipo": "Múltiplo" if lang == "ES" else "Multiple",
                "Calidad": cal if lang == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}.get(cal, cal),
                "Valor": valor_accion,
                "Qué se usó": f"EBIT × {mult}",
                "Detalle": detalle,
            })

    eps_use    = eps if (eps and eps > 0) else fwd_eps
    eps_origen = ("BPA histórico" if lang == "ES" else "Historical EPS") if (eps and eps > 0) else ("BPA estimado" if lang == "ES" else "Forward EPS")

    if eps_use and eps_use > 0:
        for mult, cal in [(10, "Alta"), (15, "Alta"), (20, "Media"), (25, "Media"), (30, "Baja")]:
            valor_accion = eps_use * mult
            detalle = (
                f"Se usa el {eps_origen.lower()} por acción ({eps_use:.2f}) y se multiplica por un PER objetivo de {mult}×. "
                f"Así se obtiene un precio razonable por acción según ese múltiplo."
                if lang == "ES" else
                f"The {eps_origen.lower()} ({eps_use:.2f}) is multiplied by a target P/E of {mult}×. "
                f"This gives an estimated fair value per share under that multiple."
            )
            methods.append({
                "Método": f"P/E {mult}×",
                "Tipo": "Múltiplo" if lang == "ES" else "Multiple",
                "Calidad": cal if lang == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}.get(cal, cal),
                "Valor": valor_accion,
                "Qué se usó": f"{eps_origen} × {mult}",
                "Detalle": detalle,
            })

    if revenue is not None and shares and shares > 0:
        for mult, cal in [(1, "Alta"), (2, "Alta"), (4, "Media"), (6, "Media"), (8, "Baja")]:
            valor_accion = revenue * mult / shares
            detalle = (
                f"Se toman las ventas totales ({fmt_large(revenue)}) y se multiplican por {mult}×. "
                f"El resultado se divide entre las acciones para obtener un valor aproximado por acción."
                if lang == "ES" else
                f"Total revenue ({fmt_large(revenue)}) is multiplied by {mult}×, and the result is divided by "
                f"shares outstanding to estimate a value per share."
            )
            methods.append({
                "Método": f"P/Ventas {mult}×" if lang == "ES" else f"P/Sales {mult}×",
                "Tipo": "Múltiplo" if lang == "ES" else "Multiple",
                "Calidad": cal if lang == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}.get(cal, cal),
                "Valor": valor_accion,
                "Qué se usó": f"Ventas × {mult} ÷ acciones" if lang == "ES" else f"Sales × {mult} ÷ shares",
                "Detalle": detalle,
            })

    if bvps and bvps > 0:
        for mult, cal in [(1, "Alta"), (1.5, "Alta"), (2, "Media"), (3, "Media"), (4, "Baja")]:
            valor_accion = bvps * mult
            detalle = (
                f"Se usa el valor en libros por acción ({bvps:.2f}) y se multiplica por {mult}×. "
                f"Es una forma de valorar cuánto pagar por cada unidad de patrimonio neto por acción."
                if lang == "ES" else
                f"Book value per share ({bvps:.2f}) is multiplied by {mult}×. "
                f"It estimates how much to pay for each unit of equity per share."
            )
            methods.append({
                "Método": f"P/Valor Libros {mult}×" if lang == "ES" else f"P/Book {mult}×",
                "Tipo": "Múltiplo" if lang == "ES" else "Multiple",
                "Calidad": cal if lang == "ES" else {"Alta": "High", "Media": "Medium", "Baja": "Low"}.get(cal, cal),
                "Valor": valor_accion,
                "Qué se usó": f"{'Valor en libros por acción' if lang == 'ES' else 'Book value per share'} × {mult}",
                "Detalle": detalle,
            })

    if eps_use and eps_use > 0 and bvps and bvps > 0:
        graham = math.sqrt(22.5 * eps_use * bvps)
        detalle = (
            f"Se combina el beneficio por acción ({eps_use:.2f}) con el valor en libros por acción ({bvps:.2f}). "
            f"Se multiplican ambos por 22.5 y luego se aplica una raíz cuadrada: √(22.5 × BPA × VL/acción)."
            if lang == "ES" else
            f"EPS ({eps_use:.2f}) and book value per share ({bvps:.2f}) are combined. "
            f"Both multiplied by 22.5, then square root applied: √(22.5 × EPS × BVPS)."
        )
        methods.append({
            "Método": "Graham Number",
            "Tipo": "Mixto" if lang == "ES" else "Hybrid",
            "Calidad": "Alta" if lang == "ES" else "High",
            "Valor": graham,
            "Qué se usó": "√(22.5 × BPA × VL/acción)" if lang == "ES" else "√(22.5 × EPS × BVPS)",
            "Detalle": detalle,
        })

        graham_adj = math.sqrt(15 * eps_use * bvps)
        detalle_adj = (
            f"Versión más prudente del método Graham. Se usa √(15 × BPA × VL/acción), reduciendo el factor de 22.5 a 15."
            if lang == "ES" else
            f"More conservative Graham version. Uses √(15 × EPS × BVPS), reducing the factor from 22.5 to 15."
        )
        methods.append({
            "Método": "Graham Ajustado (15×)" if lang == "ES" else "Adjusted Graham (15×)",
            "Tipo": "Mixto" if lang == "ES" else "Hybrid",
            "Calidad": "Media" if lang == "ES" else "Medium",
            "Valor": graham_adj,
            "Qué se usó": "√(15 × BPA × VL/acción)" if lang == "ES" else "√(15 × EPS × BVPS)",
            "Detalle": detalle_adj,
        })

    if div and div > 0:
        for g_div, r_div, label_div in [
            (0.02, 0.08, "DDM (g 2%, r 8%)"),
            (0.03, 0.09, "DDM (g 3%, r 9%)"),
            (0.05, 0.10, "DDM (g 5%, r 10%)"),
        ]:
            if r_div > g_div:
                val_ddm = div * (1 + g_div) / (r_div - g_div)
                detalle = (
                    f"Se toma el dividendo anual por acción ({div:.2f}), se aumenta con un crecimiento del "
                    f"{g_div*100:.0f}%, y se divide entre la diferencia entre la rentabilidad exigida ({r_div*100:.0f}%) y ese crecimiento."
                    if lang == "ES" else
                    f"Annual dividend ({div:.2f}) increased by expected growth of {g_div*100:.0f}% "
                    f"and divided by required return ({r_div*100:.0f}%) minus growth."
                )
                methods.append({
                    "Método": label_div,
                    "Tipo": "DDM",
                    "Calidad": "Media" if lang == "ES" else "Medium",
                    "Valor": val_ddm,
                    "Qué se usó": "Dividendo × (1+g) ÷ (r−g)" if lang == "ES" else "Dividend × (1+g) ÷ (r−g)",
                    "Detalle": detalle,
                })

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
        key="language"
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
        corr_tickers_input = st.text_input(
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
            <div style="font-size:1.1rem; margin-top:0.5rem;">{T["welcome_1"]}</div>
            <div style="font-size:0.85rem; margin-top:0.5rem;">{T["welcome_2"]}</div>
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
        stock        = yf.Ticker(active_ticker)
        info         = stock.info
        hist         = stock.history(period=period)
        financials   = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow     = stock.cashflow
    except Exception as e:
        st.error(f"Error al obtener datos / Error fetching data: {e}")
        st.stop()

price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
if price is None:
    st.error(T["price_error"])
    st.stop()

company_name = info.get("longName") or info.get("shortName") or active_ticker
sector       = info.get("sector", "N/A")
industry     = info.get("industry", "N/A")
currency     = info.get("currency", "USD")

prev_close = safe_float(info.get("previousClose"))
if price and prev_close:
    chg      = price - prev_close
    chg_pct  = chg / prev_close * 100
    color_chg = ACCENT_GREEN if chg >= 0 else ACCENT_RED
    delta_str = f'<span style="color:{color_chg}; font-size:1.05rem;">{chg:+.2f} ({chg_pct:+.2f}%)</span>'
else:
    delta_str = ""

render_company_header(company_name, active_ticker, sector, industry, currency, price, delta_str)

mc     = fmt_large(info.get("marketCap"))
high52 = fmt_num(info.get("fiftyTwoWeekHigh"))
low52  = fmt_num(info.get("fiftyTwoWeekLow"))
beta_v = fmt_num(info.get("beta"))

k1, k2, k3, k4 = st.columns(4)
with k1: metric_card(T["market_cap"], mc)
with k2: metric_card(T["high_52"], f"{high52} {currency}")
with k3: metric_card(T["low_52"], f"{low52} {currency}")
with k4: metric_card(T["beta"], beta_v)

returns = None

# =========================
# TABS
# =========================
tab_emp, tab_rat, tab_val, tab_bench, tab_corr, tab_price, tab_port, tab_fin, tab_filings = st.tabs([
    T["company"], T["ratios"], T["valuation"], T["benchmarks"], T["correlations"],
    T["price"], T["portfolio"], T["financials"], T["informes"]
])

# -------- TAB EMPRESA --------
with tab_emp:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(T["description"])
        desc = info.get("longBusinessSummary")
        if desc:
            st.write(maybe_translate(desc))
        else:
            st.info(T["no_data"])
    with c2:
        st.subheader(T["corp_data"])
        employees = info.get("fullTimeEmployees")
        corp_df = pd.DataFrame({
            "Campo" if lang == "ES" else "Field": [T["country"], T["city"], T["exchange"], T["employees"], T["sector"], T["industry"]],
            "Valor" if lang == "ES" else "Value": [
                info.get("country", "N/A"),
                info.get("city", "N/A"),
                info.get("exchange", "N/A"),
                f"{employees:,}" if employees else "N/A",
                sector,
                industry
            ]
        })
        render_champagne_table(corp_df)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB RATIOS --------
with tab_rat:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)

    pe             = safe_float(info.get("trailingPE"))
    fwd_pe         = safe_float(info.get("forwardPE"))
    pb             = safe_float(info.get("priceToBook"))
    ps             = safe_float(info.get("priceToSalesTrailing12Months"))
    roe            = safe_float(info.get("returnOnEquity"))
    roa            = safe_float(info.get("returnOnAssets"))
    profit_margin  = safe_float(info.get("profitMargins"))
    gross_margin   = safe_float(info.get("grossMargins"))
    debt_equity    = safe_float(info.get("debtToEquity"))
    current_ratio  = safe_float(info.get("currentRatio"))
    quick_ratio    = safe_float(info.get("quickRatio"))
    dividend_yield = safe_float(info.get("dividendYield"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**{T['market_val']}**")
        st.write(f"P/E (TTM): **{fmt_num(pe)}**")
        st.write(f"P/E (Fwd): **{fmt_num(fwd_pe)}**")
        st.write(f"P/B: **{fmt_num(pb)}**")
        st.write(f"P/S: **{fmt_num(ps)}**")
    with col2:
        st.markdown(f"**{T['profitability']}**")
        st.write(f"ROE: **{fmt_num(roe*100 if roe else None, 1, '%')}**")
        st.write(f"ROA: **{fmt_num(roa*100 if roa else None, 1, '%')}**")
        st.write(f"{'Margen bruto' if lang == 'ES' else 'Gross margin'}: **{fmt_num(gross_margin*100 if gross_margin else None, 1, '%')}**")
        st.write(f"{'Margen neto' if lang == 'ES' else 'Net margin'}: **{fmt_num(profit_margin*100 if profit_margin else None, 1, '%')}**")
    with col3:
        st.markdown(f"**{T['risk_liq']}**")
        st.write(f"{'Deuda/Equity' if lang == 'ES' else 'Debt/Equity'}: **{fmt_num(debt_equity)}**")
        st.write(f"Current ratio: **{fmt_num(current_ratio)}**")
        st.write(f"Quick ratio: **{fmt_num(quick_ratio)}**")
        st.write(f"Dividend yield: **{fmt_num(dividend_yield*100 if dividend_yield else None, 2, '%')}**")

    st.markdown("---")
    st.markdown(f"**{T['financial_profile']}**")

    def norm(v, lo, hi):
        v2 = safe_float(v, None)
        if v2 is None:
            return 0.0
        return max(0.0, min(1.0, (v2 - lo) / (hi - lo)))

    radar_labels = ["ROE", "ROA",
                    "Net Margin" if lang == "EN" else "Margen neto",
                    "Low P/E" if lang == "EN" else "P/E bajo",
                    "Low Debt" if lang == "EN" else "Deuda baja",
                    "Liquidity" if lang == "EN" else "Liquidez"]
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

    fig_radar = go.Figure(data=go.Scatterpolar(
        r=radar_values, theta=radar_labels, fill="toself",
        line_color=ACCENT_GOLD, fillcolor="rgba(182,138,82,0.25)",
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False, paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor=CARD_BG, height=350, font=dict(color=TEXT_PRIMARY),
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB VALORACIÓN --------
with tab_val:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)
    st.subheader(T["intrinsic_title"])
    methods, current_price = compute_valuations(info, currency)

    if not methods:
        st.warning(T["valuation_warn"])
    else:
        df_val = pd.DataFrame(methods)

        def rango_upside(u):
            if pd.isna(u): return "N/A"
            if lang == "ES":
                if u >= 40:  return "Muy infravalorado"
                if u >= 20:  return "Infravalorado"
                if u >= -10: return "En línea"
                if u >= -30: return "Sobrevalorado"
                return "Muy sobrevalorado"
            else:
                if u >= 40:  return "Deeply undervalued"
                if u >= 20:  return "Undervalued"
                if u >= -10: return "Fairly valued"
                if u >= -30: return "Overvalued"
                return "Deeply overvalued"

        df_val["Interpretación"] = df_val["Upside %"].apply(rango_upside)

        def score_row(row):
            u   = row["Upside %"]
            cal = row["Calidad"]
            if pd.isna(u):  base = 2
            elif u >= 40:   base = 5
            elif u >= 20:   base = 4
            elif u >= 0:    base = 3
            elif u >= -20:  base = 2
            else:           base = 1
            if cal in ["Alta", "High"]:   base = min(base + 1, 5)
            elif cal in ["Baja", "Low"]:  base = max(base - 1, 1)
            return "★" * base + "☆" * (5 - base)

        df_val["Score"] = df_val.apply(score_row, axis=1)

        df_tabla = pd.DataFrame({
            "Método" if lang == "ES" else "Method": df_val["Método"],
            T["type"]:           df_val["Tipo"],
            T["score"]:          df_val["Score"],
            "Upside (%)":        df_val["Upside %"].apply(lambda u: f"{u:+.1f}%" if pd.notna(u) else "N/A"),
            T["intrinsic_value"]: df_val["Valor"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            T["current_price"]:  df_val["Precio"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            T["quality"]:        df_val["Calidad"],
            T["interpretation"]: df_val["Interpretación"],
            T["used"]:           df_val["Qué se usó"],
        })
        df_tabla = df_tabla.reindex(df_val.sort_values("Upside %", ascending=False).index)
        render_champagne_table(df_tabla, pills_cols=[T["quality"], T["interpretation"]])

        st.markdown("---")
        upsides = df_val["Upside %"].dropna()
        m1, m2, m3, m4 = st.columns(4)
        with m1: metric_card("Métodos" if lang == "ES" else "Methods", str(len(df_val)))
        with m2: metric_card("Upside mediano" if lang == "ES" else "Median upside", f"{upsides.median():+.1f}%" if len(upsides) else "N/A")
        with m3: metric_card("Upside medio" if lang == "ES" else "Mean upside", f"{upsides.mean():+.1f}%" if len(upsides) else "N/A")
        with m4: metric_card("Rango" if lang == "ES" else "Range", f"{upsides.min():+.1f}% / {upsides.max():+.1f}%" if len(upsides) else "N/A")

        st.markdown("---")
        st.markdown(f"### {T['detail_methods']}")
        for _, row in df_val.sort_values("Upside %", ascending=False).reset_index(drop=True).iterrows():
            titulo = f"{row['Método']} · {T['intrinsic_value']}: {row['Valor']:.2f} {currency}"
            with st.expander(titulo, expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**{T['type']}:** {row['Tipo']}")
                    st.markdown(f"**{T['quality']}:** {row['Calidad']}")
                    st.markdown(f"**{T['current_price']}:** {row['Precio']:.2f} {currency}" if pd.notna(row["Precio"]) else f"**{T['current_price']}:** N/A")
                with c2:
                    st.markdown(f"**{T['intrinsic_value']}:** {row['Valor']:.2f} {currency}")
                    st.markdown(f"**{T['upside']}:** {row['Upside %']:+.1f}%" if pd.notna(row["Upside %"]) else f"**{T['upside']}:** N/A")
                    st.markdown(f"**{T['interpretation']}:** {row['Interpretación']}")
                st.markdown(f"**{T['used']}:** {row['Qué se usó']}")
                st.markdown(f"**{T['explanation']}:** {row['Detalle']}")

        fig_val = px.strip(
            df_val, x="Upside %", y="Tipo", color="Tipo",
            hover_data=["Método", "Valor", "Qué se usó"],
            title="Distribución de upside por tipo de método" if lang == "ES" else "Upside distribution by valuation type",
            color_discrete_sequence=CHART_COLORS,
        )
        fig_val.add_vline(x=0, line_dash="dash", line_color="#7A6856", opacity=0.5)
        fig_val.update_layout(
            paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor=CARD_BG,
            height=350, font=dict(color=TEXT_PRIMARY),
            xaxis_title="Upside vs precio actual (%)" if lang == "ES" else "Upside vs current price (%)",
        )
        st.plotly_chart(fig_val, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB BENCHMARKS --------
with tab_bench:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)
    st.subheader(T["bench_title"])
    peers = get_benchmark_list(info, active_ticker)

    if not peers:
        st.info(T["bench_none"])
    else:
        tickers_all = [active_ticker] + peers
        with st.spinner("Descargando benchmarks..." if lang == "ES" else "Downloading benchmarks..."):
            data_bench = {}
            for t in tickers_all:
                try:
                    tk  = yf.Ticker(t)
                    inf = tk.info
                    data_bench[t] = {
                        "Name":       inf.get("shortName", t),
                        "P/E":        safe_float(inf.get("trailingPE")),
                        "P/B":        safe_float(inf.get("priceToBook")),
                        "ROE":        safe_float(inf.get("returnOnEquity")),
                        "Net Margin": safe_float(inf.get("profitMargins")),
                        "Price":      safe_float(inf.get("currentPrice")) or safe_float(inf.get("regularMarketPrice")),
                        "Market Cap": safe_float(inf.get("marketCap")),
                    }
                except Exception:
                    continue

        if len(data_bench) <= 1:
            st.warning(T["bench_warn"])
        else:
            df_bench = pd.DataFrame.from_dict(data_bench, orient="index")
            df_bench.index.name = "Ticker"
            df_bench.reset_index(inplace=True)

            df_view = pd.DataFrame({
                "Ticker": df_bench["Ticker"],
                "Nombre" if lang == "ES" else "Name": df_bench["Name"],
                "Precio" if lang == "ES" else "Price": df_bench["Price"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"),
                "P/E": df_bench["P/E"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"),
                "P/B": df_bench["P/B"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"),
                "ROE": df_bench["ROE"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A"),
                "Margen neto" if lang == "ES" else "Net Margin": df_bench["Net Margin"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A"),
                "Market Cap": df_bench["Market Cap"].apply(fmt_large),
            })
            render_champagne_table(df_view)

            fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comp.add_trace(go.Bar(x=df_bench["Ticker"], y=df_bench["P/E"], name="P/E", marker_color=ACCENT_GOLD), secondary_y=False)
            fig_comp.add_trace(go.Scatter(x=df_bench["Ticker"], y=df_bench["ROE"]*100, name="ROE (%)", mode="lines+markers", line_color=ACCENT_GREEN), secondary_y=True)
            fig_comp.update_yaxes(title_text="P/E", secondary_y=False)
            fig_comp.update_yaxes(title_text="ROE (%)", secondary_y=True)
            fig_comp.update_layout(paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor=CARD_BG, height=400, font=dict(color=TEXT_PRIMARY))
            st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB CORRELACIONES --------
with tab_corr:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)
    st.subheader(T["corr_title"])
    corr_tickers = [t.strip().upper() for t in corr_tickers_input.replace(",", "\n").split("\n") if t.strip()]
    if active_ticker not in corr_tickers:
        corr_tickers.insert(0, active_ticker)

    with st.spinner("Descargando precios históricos..." if lang == "ES" else "Downloading historical prices..."):
        try:
            df_download = yf.download(corr_tickers, period=period, auto_adjust=True, progress=False)
            if isinstance(df_download.columns, pd.MultiIndex):
                prices = df_download.xs("Close", level=0, axis=1, drop_level=True)
            else:
                prices = df_download["Close"].to_frame(name=corr_tickers[0]) if len(corr_tickers) == 1 else df_download["Close"]
            returns = prices.pct_change().dropna()
        except Exception as e:
            st.error(f"No se pudo descargar precios / Could not download prices: {e}")
            returns = None

    if returns is not None and not returns.empty:
        corr = returns.corr()
        st.markdown(f"#### {T['corr_matrix']}")
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale=["#B85C5C", "#FFF8F0", "#5E8B6F"], zmin=-1, zmax=1)
        fig_corr.update_layout(paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor=CARD_BG, height=420, font=dict(color=TEXT_PRIMARY))
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown(f"#### {T['cum_returns']}")
        cum = (1 + returns).cumprod()
        fig_cum = px.line(cum, labels={"value": T["cum_returns"], "index": "Date"}, color_discrete_sequence=CHART_COLORS)
        fig_cum.update_layout(paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor=CARD_BG, height=400, font=dict(color=TEXT_PRIMARY))
        st.plotly_chart(fig_cum, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB PRECIO --------
with tab_price:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)
    st.subheader(T["price_hist"])
    if hist is None or hist.empty:
        st.warning(T["price_hist_warn"])
    else:
        fig_price = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig_price.add_trace(go.Candlestick(
            x=hist.index, open=hist["Open"], high=hist["High"], low=hist["Low"], close=hist["Close"],
            name="OHLC", increasing_line_color=ACCENT_GREEN, decreasing_line_color=ACCENT_RED,
        ), row=1, col=1)
        fig_price.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume", marker_color=ACCENT_GOLD), row=2, col=1)
        fig_price.update_layout(
            height=600, xaxis_rangeslider_visible=False,
            paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor=CARD_BG, font=dict(color=TEXT_PRIMARY),
        )
        st.plotly_chart(fig_price, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB PORTFOLIO --------
with tab_port:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)
    st.subheader(T["portfolio_title"])

    if returns is not None and not returns.empty:
        st.markdown(T["portfolio_cfg"])
        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            objetivo = st.selectbox(T["optimizer_goal"], [T["goal_sharpe"], T["goal_var"]], key="portfolio_goal")
        with c_opt2:
            rf_rate = st.number_input(T["rf_rate"], value=4.0, step=0.1) / 100

        num_activos        = len(corr_tickers)
        rendimientos_medios = returns.mean() * 252
        matriz_covarianza   = returns.cov() * 252

        def estadisticas_cartera(weights):
            weights    = np.array(weights)
            r_cartera  = np.sum(rendimientos_medios * weights)
            vol_cartera = np.sqrt(np.dot(weights.T, np.dot(matriz_covarianza, weights)))
            sharpe     = (r_cartera - rf_rate) / vol_cartera if vol_cartera > 0 else 0
            return r_cartera, vol_cartera, sharpe

        def funcion_a_minimizar(weights):
            if objetivo == T["goal_sharpe"]:
                return -estadisticas_cartera(weights)[2]
            return estadisticas_cartera(weights)[1]

        restricciones = ({"type": "eq", "fun": lambda x: np.sum(x) - 1})
        limites       = tuple((0, 1) for _ in range(num_activos))
        resultado_opt = minimize(funcion_a_minimizar, num_activos * [1.0/num_activos],
                                 method="SLSQP", bounds=limites, constraints=restricciones)

        if resultado_opt.success:
            pesos_optimos     = resultado_opt.x
            r_opt, vol_opt, sharpe_opt = estadisticas_cartera(pesos_optimos)

            st.markdown(f"#### {T['portfolio_metrics']}")
            m_p1, m_p2, m_p3 = st.columns(3)
            m_p1.metric(T["exp_return"], f"{r_opt*100:.2f}%")
            m_p2.metric(T["volatility"], f"{vol_opt*100:.2f}%")
            m_p3.metric(T["sharpe"],     f"{sharpe_opt:.2f}")

            df_pesos = pd.DataFrame({
                "Activo" if lang == "ES" else "Asset": corr_tickers,
                "Ponderación (%)" if lang == "ES" else "Weight (%)": [f"{w*100:.2f}%" for w in pesos_optimos],
                "Fracción" if lang == "ES" else "Decimal": np.round(pesos_optimos, 4)
            }).sort_values(by="Fracción" if lang == "ES" else "Decimal", ascending=False)
            render_champagne_table(df_pesos)

            fig_pie = px.pie(
                df_pesos[df_pesos["Fracción" if lang == "ES" else "Decimal"] > 0.001],
                values="Fracción" if lang == "ES" else "Decimal",
                names="Activo" if lang == "ES" else "Asset",
                title=("Distribución recomendada de capital" if lang == "ES" else "Recommended capital allocation") + f" ({objetivo})",
                color_discrete_sequence=CHART_COLORS
            )
            fig_pie.update_layout(paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor=CARD_BG, font=dict(color=TEXT_PRIMARY))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.error("El algoritmo no convergió / The optimizer did not converge.")
    else:
        st.warning(T["portfolio_warn"])
    st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB FINANCIALS --------
with tab_fin:
    st.subheader(T["financials_title"])
    fs1, fs2, fs3 = st.tabs([T["income_stmt"], T["balance_sheet"], T["cash_flow"]])

    with fs1:
        st.markdown('<div class="fade-container">', unsafe_allow_html=True)
        df_income = format_financial_df(financials)
        if df_income is not None: render_champagne_table(df_income)
        else: st.info(T["no_data"])
        st.markdown('</div>', unsafe_allow_html=True)

    with fs2:
        st.markdown('<div class="fade-container">', unsafe_allow_html=True)
        df_bs = format_financial_df(balance_sheet)
        if df_bs is not None: render_champagne_table(df_bs)
        else: st.info(T["no_data"])
        st.markdown('</div>', unsafe_allow_html=True)

    with fs3:
        st.markdown('<div class="fade-container">', unsafe_allow_html=True)
        df_cf = format_financial_df(cashflow)
        if df_cf is not None: render_champagne_table(df_cf)
        else: st.info(T["no_data"])
        st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB INFORMES SEC / CNMV --------
with tab_filings:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)
    st.subheader("📋 Informes regulatorios (SEC / CNMV)" if lang == "ES" else "📋 Regulatory filings (SEC / CNMV)")

    ticker_base = active_ticker.split(".")[0].upper()
    df_all      = []

    # Detectar si es ticker USA por exclusión de sufijos extranjeros conocidos
    is_us_ticker = not any(active_ticker.upper().endswith(s) for s in SUFFIXES_NO_US)

    if is_us_ticker:
        with st.spinner("🔍 Buscando CIK en EDGAR (SEC)..." if lang == "ES" else "🔍 Looking up CIK on SEC EDGAR..."):
            cik = get_cik_from_ticker_us(ticker_base)

        if cik:
            with st.spinner("📥 Descargando filings de la SEC..." if lang == "ES" else "📥 Downloading SEC filings..."):
                df_sec = get_sec_filings_metadata(cik)

            if not df_sec.empty:
                df_all.append(df_sec)
                st.success(
                    f"✅ {'Se encontraron' if lang == 'ES' else 'Found'} **{len(df_sec)}** "
                    f"{'informes' if lang == 'ES' else 'filings'} en la SEC para **{ticker_base}** "
                    f"(CIK: {int(cik)})"
                )
            else:
                st.warning(
                    f"⚠️ CIK encontrado ({int(cik)}) pero no se obtuvieron filings. Puede ser un problema temporal con la API de la SEC."
                    if lang == "ES" else
                    f"⚠️ CIK found ({int(cik)}) but no filings returned. This might be a temporary SEC API issue."
                )
        else:
            st.info(
                f"ℹ️ No se encontró CIK para **{ticker_base}** en la SEC. La empresa puede no cotizar en EE.UU. o usar un ticker diferente."
                if lang == "ES" else
                f"ℹ️ No CIK found for **{ticker_base}** in SEC. The company may not be US-listed or may use a different ticker."
            )

    # CNMV para tickers .MC
    if active_ticker.upper().endswith(".MC"):
        with st.spinner("🔍 Buscando en CNMV..."):
            df_cnmv = get_cnmv_filings_for_spanish_issuer(ticker_base)
        if df_cnmv is not None and not df_cnmv.empty:
            df_all.append(df_cnmv)

    if df_all:
        df_filings = pd.concat(df_all, ignore_index=True)

        if "Fecha" in df_filings.columns:
            try:
                df_filings["Fecha"] = pd.to_datetime(df_filings["Fecha"], errors="coerce")
                df_filings.sort_values("Fecha", ascending=False, inplace=True)
                df_filings["Fecha"] = df_filings["Fecha"].dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        form_options   = sorted(df_filings["Formulario"].unique().tolist())
        selected_forms = st.multiselect(
            "Filtrar por tipo:" if lang == "ES" else "Filter by type:",
            options=form_options, default=form_options, key="sec_form_filter"
        )
        df_show = df_filings[df_filings["Formulario"].isin(selected_forms)].copy()

        if df_show.empty:
            st.info("No hay informes para los filtros seleccionados." if lang == "ES" else "No filings match the selected filters.")
        else:
            cols_show = [c for c in ["Formulario", "Descripción", "Fecha", "Documento", "Ver informe", "EDGAR"] if c in df_show.columns]
            render_champagne_table(df_show[cols_show], html_cols=["Ver informe", "EDGAR"])
            st.caption(
                f"{'Mostrando' if lang == 'ES' else 'Showing'} {len(df_show)} "
                f"{'informes' if lang == 'ES' else 'filings'}. Fuente: SEC EDGAR"
            )

    elif not is_us_ticker and not active_ticker.upper().endswith(".MC"):
        st.info(
            "ℹ️ Los informes regulatorios (SEC/CNMV) solo están disponibles para tickers de EE.UU. y España (.MC)."
            if lang == "ES" else
            "ℹ️ Regulatory filings are only available for US tickers and Spanish tickers (.MC)."
        )

    if is_us_ticker:
        edgar_search = f"https://www.sec.gov/cgi-bin/browse-edgar?company={ticker_base}&CIK=&type=10-K&dateb=&owner=include&count=40&search_text=&action=getcompany"
        st.markdown(
            f'<a href="{edgar_search}" target="_blank" style="color:{ACCENT_GOLD}; font-size:0.88rem; text-decoration:none;">'
            f'🔗 {"Buscar directamente en EDGAR" if lang == "ES" else "Search directly on EDGAR"}</a>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
