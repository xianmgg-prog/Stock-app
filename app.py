import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import math
import re
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
ACCENT_GOLD      = "#B68A52"
ACCENT_GOLD_SOFT = "#D6B98C"
ACCENT_GREEN     = "#5E8B6F"
ACCENT_RED       = "#B85C5C"

BG_MAIN   = "#F7F1E8"
BG_GRAD_1 = "#F3E7D7"
BG_GRAD_2 = "#EADBC8"

CARD_BG   = "#FFFDF9"
CARD_BG_2 = "#F9F4EC"
BORDER    = "#D9C8B4"

TEXT_PRIMARY   = "#2F241B"
TEXT_SECONDARY = "#7A6856"
TEXT_FAINT     = "#A08F7C"

TABLE_HEADER_BG = "#EFE2D2"
TABLE_ROW_BG    = "#FFFDF9"
TABLE_ALT_BG    = "#FAF5EE"
TABLE_BORDER    = "#D8C7B2"

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
        "informes": "Informes",
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
        "portfolio_warn": "Datos históricos insuficientes. Configura los tickers en las opciones superiores.",
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
        "informes": "Filings",
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
        "portfolio_warn": "Insufficient historical data. Make sure tickers are configured correctly.",
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
    .block-container {{ padding-top: 2rem; padding-bottom: 2rem; max-width: 1320px; }}
    .stApp {{
        background: radial-gradient(circle at top left, {BG_GRAD_1} 0%, {BG_MAIN} 45%, {BG_GRAD_2} 100%);
        color: {TEXT_PRIMARY};
        font-family: "Inter", "Segoe UI", sans-serif;
    }}
    .hero-wrap {{ padding: 1.2rem 0 1.8rem 0; text-align: center; }}
    .hero-title {{ font-size: 2.9rem; font-weight: 800; letter-spacing: 0.02em; color: {TEXT_PRIMARY}; margin-bottom: 0.35rem; }}
    .hero-sub {{ color: {TEXT_SECONDARY}; font-size: 0.95rem; letter-spacing: 0.14em; text-transform: uppercase; }}
    .soft-divider {{
        height: 1px; width: 100%;
        background: linear-gradient(90deg, transparent, {BORDER}, transparent);
        margin: 1.25rem 0 1.75rem 0;
    }}
    .fade-container {{ opacity: 0; animation: fadeInUp 0.45s ease-out forwards; }}
    @keyframes fadeInUp {{
        0%   {{ opacity: 0; transform: translateY(10px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .metric-card {{
        background: linear-gradient(180deg, {CARD_BG} 0%, {CARD_BG_2} 100%);
        border: 1px solid {BORDER}; border-radius: 16px;
        padding: 1rem 1rem 0.95rem 1rem;
        box-shadow: 0 8px 24px rgba(120,93,61,0.06);
        margin-bottom: 0.5rem;
    }}
    .metric-label {{ color: {TEXT_SECONDARY}; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.11em; margin-bottom: 0.25rem; }}
    .metric-value {{ color: {TEXT_PRIMARY}; font-size: 1.15rem; font-weight: 700; line-height: 1.2; }}
    .metric-sub   {{ color: {TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 0.18rem; }}
    .company-header {{
        background: linear-gradient(180deg, rgba(255,253,249,0.92) 0%, rgba(249,244,236,0.92) 100%);
        border: 1px solid {BORDER}; border-radius: 18px;
        padding: 1.2rem 1.25rem; margin: 0.7rem 0 1rem 0;
        box-shadow: 0 10px 30px rgba(120,93,61,0.05);
    }}
    .company-name  {{ font-size: 1.7rem; font-weight: 800; color: {TEXT_PRIMARY}; }}
    .company-meta  {{ color: {TEXT_SECONDARY}; font-size: 0.95rem; margin-top: 0.15rem; }}
    .company-price {{ font-size: 2rem; font-weight: 800; color: {ACCENT_GOLD}; margin-top: 0.55rem; }}
    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        background: rgba(255,253,249,0.96) !important; color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER} !important; border-radius: 14px !important;
    }}
    .stSelectbox div[data-baseweb="select"] > div {{
        background: rgba(255,253,249,0.96) !important; color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER} !important; border-radius: 14px !important;
    }}
    .stButton > button {{
        background: linear-gradient(180deg, {ACCENT_GOLD_SOFT} 0%, {ACCENT_GOLD} 100%);
        color: white !important; border: none !important; border-radius: 14px !important;
        font-weight: 700 !important; padding: 0.72rem 1rem !important;
        box-shadow: 0 8px 22px rgba(182,138,82,0.22);
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 0.35rem; }}
    .stTabs [data-baseweb="tab"] {{
        background: rgba(255,251,245,0.95); border: 1px solid {BORDER};
        border-radius: 12px 12px 0 0; color: {TEXT_SECONDARY};
        padding: 0.75rem 1.1rem; font-size: 0.92rem;
    }}
    .stTabs [aria-selected="true"] {{
        background: {CARD_BG} !important; color: {TEXT_PRIMARY} !important;
        border-bottom-color: {CARD_BG} !important; font-weight: 700 !important;
    }}
    .stExpander {{
        border: 1px solid {BORDER} !important; border-radius: 16px !important;
        background: rgba(255,253,249,0.7) !important;
    }}
    .champ-table-wrap {{
        background: {CARD_BG}; border: 1px solid {TABLE_BORDER};
        border-radius: 18px; overflow-x: auto;
        box-shadow: 0 10px 28px rgba(120,93,61,0.05); margin-top: 0.5rem;
    }}
    .champ-table {{ width: 100%; border-collapse: collapse; font-size: 0.93rem; }}
    .champ-table thead th {{
        background: {TABLE_HEADER_BG}; color: {TEXT_SECONDARY};
        text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.73rem;
        text-align: left; padding: 0.95rem 0.9rem;
        border-bottom: 1px solid {TABLE_BORDER}; white-space: nowrap;
    }}
    .champ-table tbody td {{
        padding: 0.88rem 0.9rem; border-bottom: 1px solid rgba(216,199,178,0.55);
        color: {TEXT_PRIMARY}; background: {TABLE_ROW_BG}; vertical-align: top;
    }}
    .champ-table tbody tr:nth-child(even) td {{ background: {TABLE_ALT_BG}; }}
    .champ-table tbody tr:hover td {{ background: #F4EBDD; }}
    .pill {{ display: inline-block; padding: 0.28rem 0.55rem; border-radius: 999px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.03em; white-space: nowrap; }}
    .pill-gold  {{ background: rgba(182,138,82,0.14); color: #8B6738; }}
    .pill-green {{ background: rgba(94,139,111,0.14);  color: #41614E; }}
    .pill-red   {{ background: rgba(184,92,92,0.14);   color: #8A4444; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS GENERALES
# =========================
lang = st.session_state.language
T    = TEXTS[lang]

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
    if v >= 1e12:  return f"{sign*v/1e12:.2f}T"
    elif v >= 1e9: return f"{sign*v/1e9:.2f}B"
    elif v >= 1e6: return f"{sign*v/1e6:.2f}M"
    return f"{sign*v:.0f}"

def metric_card(label, value, sub=None):
    sub_html = '<div class="metric-sub">' + str(sub) + '</div>' if sub else ""
    html = (
        '<div class="metric-card">'
        '<div class="metric-label">' + str(label) + '</div>'
        '<div class="metric-value">' + str(value) + '</div>'
        + sub_html +
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_company_header(company_name, ticker, sector, industry, currency, price, delta_html=""):
    html = (
        '<div class="company-header fade-container">'
        '<div class="company-name">' + company_name + '</div>'
        '<div class="company-meta">' + ticker + ' · ' + sector + ' · ' + industry + ' · ' + currency + '</div>'
        '<div class="company-price">' + f"{price:.2f}" + ' ' + currency + ' ' + delta_html + '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_champagne_table(df: pd.DataFrame, pills_cols=None, html_cols=None):
    pills_cols = pills_cols or []
    html_cols  = html_cols  or []

    def pill_class(val):
        v = str(val).lower()
        if any(x in v for x in ["alta", "high", "infraval", "underval", "buy", "+"]):
            return "pill pill-green"
        if any(x in v for x in ["baja", "low", "sobreval", "overval", "sell"]):
            return "pill pill-red"
        return "pill pill-gold"

    html = '<div class="champ-table-wrap fade-container"><table class="champ-table"><thead><tr>'
    for col in df.columns:
        html += "<th>" + str(col) + "</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val     = row[col]
            display = "N/A" if pd.isna(val) else str(val)
            if col in html_cols:
                html += "<td>" + display + "</td>"
            elif col in pills_cols:
                html += '<td><span class="' + pill_class(display) + '">' + display + '</span></td>'
            else:
                html += "<td>" + display + "</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)

def search_ticker(query: str):
    if not query:
        return []
    try:
        url  = "https://query2.finance.yahoo.com/v1/finance/search?q=" + query + "&lang=en-US&region=US&quotesCount=8&newsCount=0"
        r    = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
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
    "Energy":                 ["XOM", "CVX", "BP", "TTE"],
}

def get_benchmark_list(info, main_ticker):
    sector = info.get("sector")
    peers  = DEFAULT_BENCHMARKS.get(sector, [])
    peers  = [p for p in peers if p.upper() != main_ticker.upper()]
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
# SEC HELPERS
# =========================
SEC_BASE    = "https://data.sec.gov"
# ⚠️ CAMBIA por tu nombre y email real
SEC_HEADERS = {
    "User-Agent":      "EquityTerminal/1.0 tucorreo@tudominio.com",
    "Accept-Encoding": "gzip, deflate",
}

SUFFIXES_NO_US = {
    ".MC", ".L", ".PA", ".AS", ".MI", ".DE", ".HK",
    ".T",  ".AX", ".TO", ".BR", ".LS", ".VI", ".SW",
    ".OL", ".ST", ".HE", ".CO", ".BO", ".NS", ".SA"
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_cik_from_ticker_us(ticker: str):
    try:
        resp = requests.get("https://www.sec.gov/files/company_tickers.json", headers=SEC_HEADERS, timeout=30)
        resp.raise_for_status()
        ticker_norm = ticker.upper().replace(".US","").replace("-","").replace(".","")
        for entry in resp.json().values():
            entry_norm = entry["ticker"].upper().replace("-","").replace(".","")
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
        resp = requests.get(f"{SEC_BASE}/submissions/CIK{cik}.json", headers=SEC_HEADERS, timeout=30)
        resp.raise_for_status()
        j            = resp.json()
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
            ac  = a.replace("-", "")
            url = "https://www.sec.gov/Archives/edgar/data/" + cik_int + "/" + ac + "/" + doc
            rows.append({
                "Formulario":  f,
                "Descripción": desc if desc else f,
                "Fecha":       d,
                "Documento":   doc,
                "Ver informe": '<a href="' + url + '" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">📄 Abrir</a>',
                "EDGAR":       '<a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + cik + '&type=' + f + '&dateb=&owner=include&count=40" target="_blank" style="color:' + TEXT_SECONDARY + ';font-size:0.85rem;text-decoration:none;">🔗 EDGAR</a>',
            })
            if len(rows) >= limit:
                break
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
                        ef_j.get("form",[]), ef_j.get("filingDate",[]),
                        ef_j.get("accessionNumber",[]), ef_j.get("primaryDocument",[]),
                        ef_j.get("primaryDocDescription",[]),
                    ):
                        if f not in form_types:
                            continue
                        ac  = a.replace("-","")
                        url = "https://www.sec.gov/Archives/edgar/data/" + cik_int + "/" + ac + "/" + doc
                        rows.append({
                            "Formulario":  f,
                            "Descripción": desc if desc else f,
                            "Fecha":       d,
                            "Documento":   doc,
                            "Ver informe": '<a href="' + url + '" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">📄 Abrir</a>',
                            "EDGAR":       '<a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + cik + '&type=' + f + '&dateb=&owner=include&count=40" target="_blank" style="color:' + TEXT_SECONDARY + ';font-size:0.85rem;text-decoration:none;">🔗 EDGAR</a>',
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

# =========================
# CNMV & BOLSAS EUROPEAS
# =========================
REGULATORY_SOURCES = {
    ".MC": "CNMV",
    ".L":  "FCA",
    ".PA": "AMF",
    ".AS": "AFM",
    ".MI": "CONSOB",
    ".BR": "FSMA",
    ".LS": "CMVM",
    ".DE": "BaFin",
    ".VI": "FMA",
    ".SW": "FINMA",
    ".ST": "FI",
    ".HE": "FIN-FSA",
    ".CO": "DFSA",
    ".OL": "Finanstilsynet",
}

REGULATORY_SEARCH_LINKS = {
    ".MC": "https://www.cnmv.es/portal/hr/busquedahr?nombre={ticker}&lang=es",
    ".L":  "https://www.londonstockexchange.com/live-markets/company-news-and-events/",
    ".PA": "https://live.euronext.com/en/product/equities/{ticker}-XPAR",
    ".AS": "https://live.euronext.com/en/product/equities/{ticker}-XAMS",
    ".MI": "https://www.borsaitaliana.it/borsa/azioni/scheda/{ticker}.html",
    ".BR": "https://live.euronext.com/en/product/equities/{ticker}-XBRU",
    ".LS": "https://live.euronext.com/en/product/equities/{ticker}-XLIS",
    ".DE": "https://www.bundesanzeiger.de/pub/de/start",
    ".VI": "https://www.wienerborse.at/en/",
    ".SW": "https://www.six-group.com/en/products-services/the-swiss-stock-exchange/market-data/shares.html",
    ".ST": "https://www.nasdaqomxnordic.com/news/companynews",
    ".HE": "https://www.nasdaqomxnordic.com/news/companynews",
    ".CO": "https://www.nasdaqomxnordic.com/news/companynews",
    ".OL": "https://newsweb.oslobors.no/",
}

@st.cache_data(ttl=1800, show_spinner=False)
def get_cnmv_hechos_relevantes(ticker_base: str, limit: int = 30) -> pd.DataFrame:
    rows = []
    try:
        url  = "https://www.cnmv.es/portal/Alerta/Buscador.aspx?nombre=" + requests.utils.quote(ticker_base) + "&lang=es"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        tables = pd.read_html(resp.text, flavor="lxml") if resp.status_code == 200 else []
        for tbl in tables:
            if tbl.shape[1] >= 3:
                for _, row in tbl.iterrows():
                    vals = [str(v).strip() for v in row.values if pd.notna(v)]
                    if len(vals) >= 2:
                        rows.append({
                            "Tipo":         "Hecho Relevante",
                            "Descripción":  vals[1] if len(vals) > 1 else vals[0],
                            "Fecha":        vals[0],
                            "Ver documento": '<a href="https://www.cnmv.es/portal/hr/busquedahr?nombre=' + ticker_base + '&lang=es" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">📄 CNMV</a>',
                        })
                    if len(rows) >= limit:
                        break
            if rows:
                break
    except Exception:
        pass
    if not rows:
        rows.append({
            "Tipo":         "Portal CNMV",
            "Descripción":  "Consulta directa para " + ticker_base + " en el portal oficial",
            "Fecha":        "—",
            "Ver documento": '<a href="https://www.cnmv.es/portal/hr/busquedahr?nombre=' + ticker_base + '&lang=es" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">🔗 Abrir buscador CNMV</a>',
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=1800, show_spinner=False)
def get_euronext_filings(ticker_base: str, suffix: str) -> pd.DataFrame:
    mic_map = {".PA": "XPAR", ".AS": "XAMS", ".BR": "XBRU", ".LS": "XLIS"}
    mic     = mic_map.get(suffix, "XPAR")
    rows    = []
    try:
        url  = "https://live.euronext.com/en/ajax/getCompanyRegulatoryNews?isin=&ticker=" + ticker_base + "&market=" + mic + "&lang=en&page=1&pageSize=25"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}, timeout=15)
        if resp.status_code == 200:
            data  = resp.json()
            items = data.get("data", data if isinstance(data, list) else [])
            for item in items:
                title = item.get("title") or item.get("headline", "")
                date  = item.get("date") or item.get("publicationDate", "")
                link  = item.get("url") or item.get("pdfUrl") or item.get("link", "")
                dtype = item.get("type") or item.get("category", "Regulatory")
                if title:
                    rows.append({
                        "Tipo":         dtype,
                        "Descripción":  title,
                        "Fecha":        str(date)[:10] if date else "—",
                        "Ver documento": '<a href="' + link + '" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">📄 Abrir</a>' if link else "—",
                    })
    except Exception:
        pass
    if not rows:
        euronext_url = "https://live.euronext.com/en/product/equities/" + ticker_base + "-" + mic
        rows.append({
            "Tipo":         "Portal Euronext",
            "Descripción":  "Consulta directa para " + ticker_base + " en Euronext Live",
            "Fecha":        "—",
            "Ver documento": '<a href="' + euronext_url + '" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">🔗 Abrir Euronext Live</a>',
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=1800, show_spinner=False)
def get_lse_filings(ticker_base: str) -> pd.DataFrame:
    rows = []
    try:
        url  = "https://api.londonstockexchange.com/api/gw/lse/instruments/alldata/news/" + ticker_base
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if resp.status_code == 200:
            for item in resp.json().get("content", [])[:25]:
                title = item.get("headline", "")
                date  = item.get("announcementDate", "")[:10]
                link  = "https://www.londonstockexchange.com" + item.get("url", "")
                dtype = item.get("category", "RNS")
                rows.append({
                    "Tipo":         dtype,
                    "Descripción":  title,
                    "Fecha":        date,
                    "Ver documento": '<a href="' + link + '" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">📄 LSE</a>',
                })
    except Exception:
        pass
    if not rows:
        rows.append({
            "Tipo":         "Portal LSE",
            "Descripción":  "Anuncios regulatorios (RNS) para " + ticker_base,
            "Fecha":        "—",
            "Ver documento": '<a href="https://www.londonstockexchange.com/live-markets/company-news-and-events/" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">🔗 LSE News</a>',
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=1800, show_spinner=False)
def get_oslo_filings(ticker_base: str) -> pd.DataFrame:
    rows = []
    try:
        resp = requests.get("https://newsweb.oslobors.no/message?ticker=" + ticker_base + "&limit=25", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if resp.status_code == 200:
            for item in resp.json().get("messages", []):
                mid  = item.get("id", "")
                link = "https://newsweb.oslobors.no/message/" + str(mid) if mid else ""
                rows.append({
                    "Tipo":         item.get("category", "Regulatory"),
                    "Descripción":  item.get("title", ""),
                    "Fecha":        str(item.get("publishedTime", ""))[:10],
                    "Ver documento": '<a href="' + link + '" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">📄 Oslo</a>' if link else "—",
                })
    except Exception:
        pass
    if not rows:
        rows.append({
            "Tipo":         "Oslo Børs",
            "Descripción":  "Comunicados regulatorios para " + ticker_base,
            "Fecha":        "—",
            "Ver documento": '<a href="https://newsweb.oslobors.no/" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">🔗 Newsweb</a>',
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=1800, show_spinner=False)
def get_nordic_filings(ticker_base: str, suffix: str) -> pd.DataFrame:
    market_map = {".ST": "se", ".HE": "fi", ".CO": "dk"}
    market     = market_map.get(suffix, "se")
    rows       = []
    try:
        resp = requests.get("https://api.nasdaq.com/api/company/" + ticker_base + "/press-releases?limit=25&market=" + market, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if resp.status_code == 200:
            for item in resp.json().get("data", {}).get("rows", []):
                rows.append({
                    "Tipo":         item.get("type", "Press Release"),
                    "Descripción":  item.get("headline", ""),
                    "Fecha":        str(item.get("date", ""))[:10],
                    "Ver documento": '<a href="' + item.get("url","") + '" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">📄 Ver</a>' if item.get("url") else "—",
                })
    except Exception:
        pass
    if not rows:
        rows.append({
            "Tipo":         "Nasdaq Nordic",
            "Descripción":  "Comunicados para " + ticker_base,
            "Fecha":        "—",
            "Ver documento": '<a href="https://www.nasdaqomxnordic.com/news/companynews" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">🔗 Nasdaq Nordic</a>',
        })
    return pd.DataFrame(rows)

def get_european_filings(ticker: str) -> tuple:
    ticker_upper = ticker.upper()
    ticker_base  = ticker_upper.split(".")[0]
    for suffix in REGULATORY_SOURCES:
        if ticker_upper.endswith(suffix):
            source_name = REGULATORY_SOURCES[suffix]
            if suffix == ".MC":
                return get_cnmv_hechos_relevantes(ticker_base), "CNMV (España)"
            elif suffix in (".PA", ".AS", ".BR", ".LS"):
                return get_euronext_filings(ticker_base, suffix), "Euronext · " + source_name
            elif suffix == ".L":
                return get_lse_filings(ticker_base), "LSE / FCA (Reino Unido)"
            elif suffix == ".OL":
                return get_oslo_filings(ticker_base), "Oslo Børs (Noruega)"
            elif suffix in (".ST", ".HE", ".CO"):
                return get_nordic_filings(ticker_base, suffix), "Nasdaq Nordic · " + source_name
            else:
                fallback_url = REGULATORY_SEARCH_LINKS.get(suffix, "#").replace("{ticker}", ticker_base)
                df_fb = pd.DataFrame([{
                    "Tipo":         source_name,
                    "Descripción":  "Portal regulatorio oficial para " + ticker_base + " (" + suffix + ")",
                    "Fecha":        "—",
                    "Ver documento": '<a href="' + fallback_url + '" target="_blank" style="color:' + ACCENT_GOLD + ';font-weight:600;text-decoration:none;">🔗 Abrir portal ' + source_name + '</a>',
                }])
                return df_fb, source_name
    return pd.DataFrame(), "Desconocida"

# =========================
# VALORACIÓN
# =========================
def compute_valuations(info, currency):
    methods    = []
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

    cal_map = {"Alta": "High", "Media": "Medium", "Baja": "Low"}

    def dcf_model(fcf0, g_high, g_low, r, label, calidad, origen):
        if fcf0 is None or shares is None or shares <= 0 or r <= g_low:
            return
        pv  = sum(fcf0*(1+g_high)**t/(1+r)**t for t in range(1, 6))
        pv += sum(fcf0*(1+g_high)**5*(1+g_low)**(t-5)/(1+r)**t for t in range(6, 11))
        terminal    = fcf0*(1+g_high)**5*(1+g_low)**5*(1+g_low)/(r-g_low)
        pv_terminal = terminal/(1+r)**10
        va          = (pv + pv_terminal + cash - total_debt) / shares
        methods.append({
            "Método":    label,
            "Tipo":      "DCF",
            "Calidad":   calidad if lang=="ES" else cal_map.get(calidad, calidad),
            "Valor":     va,
            "Qué se usó": origen + " · crec. " + str(int(g_high*100)) + "%→" + str(int(g_low*100)) + "% · desc. " + str(int(r*100)) + "%",
            "Detalle":   "FCF base: " + fmt_large(fcf0) + " | g_alto=" + str(int(g_high*100)) + "% g_bajo=" + str(int(g_low*100)) + "% r=" + str(int(r*100)) + "%",
        })

    if fcf is not None:
        dcf_model(fcf, 0.15, 0.04, 0.11, "DCF Agresivo"    if lang=="ES" else "Aggressive DCF",   "Media", "FCF")
        dcf_model(fcf, 0.10, 0.03, 0.10, "DCF Base"        if lang=="ES" else "Base DCF",          "Alta",  "FCF")
        dcf_model(fcf, 0.06, 0.02, 0.09, "DCF Conservador" if lang=="ES" else "Conservative DCF", "Alta",  "FCF")

    if net_income is not None and shares and shares > 0:
        dcf_model(net_income, 0.08, 0.03, 0.10,
                  "DCF (Bº neto)" if lang=="ES" else "DCF (Net income)", "Media",
                  "Bº neto" if lang=="ES" else "Net income")

    if ebitda and ebitda > 0 and shares and shares > 0:
        for mult, cal in [(8,"Alta"),(10,"Alta"),(12,"Media"),(15,"Media"),(20,"Baja")]:
            methods.append({
                "Método":    "EV/EBITDA " + str(mult) + "×",
                "Tipo":      "Múltiplo" if lang=="ES" else "Multiple",
                "Calidad":   cal if lang=="ES" else cal_map[cal],
                "Valor":     (ebitda*mult + cash - total_debt) / shares,
                "Qué se usó": "EBITDA × " + str(mult),
                "Detalle":   "EBITDA " + fmt_large(ebitda) + " × " + str(mult),
            })

    if ebit and ebit > 0 and shares and shares > 0:
        for mult, cal in [(10,"Alta"),(14,"Media"),(18,"Baja")]:
            methods.append({
                "Método":    "EV/EBIT " + str(mult) + "×",
                "Tipo":      "Múltiplo" if lang=="ES" else "Multiple",
                "Calidad":   cal if lang=="ES" else cal_map[cal],
                "Valor":     (ebit*mult + cash - total_debt) / shares,
                "Qué se usó": "EBIT × " + str(mult),
                "Detalle":   "EBIT " + fmt_large(ebit) + " × " + str(mult),
            })

    eps_use    = eps if (eps and eps > 0) else fwd_eps
    eps_origen = ("BPA histórico" if lang=="ES" else "Historical EPS") if (eps and eps > 0) else ("BPA estimado" if lang=="ES" else "Forward EPS")

    if eps_use and eps_use > 0:
        for mult, cal in [(10,"Alta"),(15,"Alta"),(20,"Media"),(25,"Media"),(30,"Baja")]:
            methods.append({
                "Método":    "P/E " + str(mult) + "×",
                "Tipo":      "Múltiplo" if lang=="ES" else "Multiple",
                "Calidad":   cal if lang=="ES" else cal_map[cal],
                "Valor":     eps_use * mult,
                "Qué se usó": eps_origen + " × " + str(mult),
                "Detalle":   eps_origen + " " + str(round(eps_use,2)) + " × PER " + str(mult),
            })

    if revenue and shares and shares > 0:
        for mult, cal in [(1,"Alta"),(2,"Alta"),(4,"Media"),(6,"Media"),(8,"Baja")]:
            methods.append({
                "Método":    ("P/Ventas " if lang=="ES" else "P/Sales ") + str(mult) + "×",
                "Tipo":      "Múltiplo" if lang=="ES" else "Multiple",
                "Calidad":   cal if lang=="ES" else cal_map[cal],
                "Valor":     revenue * mult / shares,
                "Qué se usó": "Ventas × " + str(mult) + " ÷ acciones",
                "Detalle":   "Ventas " + fmt_large(revenue) + " × " + str(mult),
            })

    if bvps and bvps > 0:
        for mult, cal in [(1,"Alta"),(1.5,"Alta"),(2,"Media"),(3,"Media"),(4,"Baja")]:
            methods.append({
                "Método":    "P/Book " + str(mult) + "×",
                "Tipo":      "Múltiplo" if lang=="ES" else "Multiple",
                "Calidad":   cal if lang=="ES" else cal_map[cal],
                "Valor":     bvps * mult,
                "Qué se usó": "BVPS × " + str(mult),
                "Detalle":   "Valor en libros/acción " + str(round(bvps,2)) + " × " + str(mult),
            })

    if eps_use and eps_use > 0 and bvps and bvps > 0:
        methods.append({
            "Método":    "Graham Number",
            "Tipo":      "Mixto" if lang=="ES" else "Hybrid",
            "Calidad":   "Alta" if lang=="ES" else "High",
            "Valor":     math.sqrt(22.5 * eps_use * bvps),
            "Qué se usó": "√(22.5 × EPS × BVPS)",
            "Detalle":   "√(22.5 × " + str(round(eps_use,2)) + " × " + str(round(bvps,2)) + ")",
        })
        methods.append({
            "Método":    "Graham Ajustado (15×)" if lang=="ES" else "Adjusted Graham (15×)",
            "Tipo":      "Mixto" if lang=="ES" else "Hybrid",
            "Calidad":   "Media" if lang=="ES" else "Medium",
            "Valor":     math.sqrt(15 * eps_use * bvps),
            "Qué se usó": "√(15 × EPS × BVPS)",
            "Detalle":   "√(15 × " + str(round(eps_use,2)) + " × " + str(round(bvps,2)) + ")",
        })

    if div and div > 0:
        for g_div, r_div, lbl in [(0.02,0.08,"DDM (g2% r8%)"),(0.03,0.09,"DDM (g3% r9%)"),(0.05,0.10,"DDM (g5% r10%)")]:
            if r_div > g_div:
                methods.append({
                    "Método":    lbl,
                    "Tipo":      "DDM",
                    "Calidad":   "Media" if lang=="ES" else "Medium",
                    "Valor":     div*(1+g_div)/(r_div-g_div),
                    "Qué se usó": "Div×(1+g)÷(r−g)",
                    "Detalle":   "Div " + str(round(div,2)) + " g=" + str(int(g_div*100)) + "% r=" + str(int(r_div*100)) + "%",
                })

    for m in methods:
        m["Precio"]   = price
        m["Upside %"] = round((m["Valor"]-price)/price*100, 1) if price and price > 0 else None

    return methods, price

# =========================
# HEADER + LANGUAGE
# =========================
top1, top2 = st.columns([5, 1])
with top2:
    st.selectbox(TEXTS[st.session_state.language]["language"], options=["ES","EN"], key="language")

lang = st.session_state.language
T    = TEXTS[lang]

st.markdown(
    '<div class="hero-wrap fade-container">'
    '<div class="hero-title">' + T["hero_title"] + '</div>'
    '<div class="hero-sub">'   + T["hero_sub"]   + '</div>'
    '</div>'
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)

# =========================
# BÚSQUEDA
# =========================
col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input("", placeholder=T["search_placeholder"], label_visibility="collapsed")
with col_btn:
    analyze_btn = st.button(T["analyze"], use_container_width=True, type="primary")

if query != st.session_state.current_query:
    st.session_state.current_query = query

ticker_sym = ""
if query:
    suggestions = search_ticker(query)
    if suggestions:
        choice     = st.selectbox(T["suggestions"], suggestions, label_visibility="collapsed", key="ticker_suggestion")
        ticker_sym = choice.split(" — ")[0].strip()
    else:
        ticker_sym = query.strip().upper()

if analyze_btn and ticker_sym:
    st.session_state.analyzed_ticker = ticker_sym

with st.expander(T["options"], expanded=False):
    op1, op2 = st.columns([1, 2])
    with op1:
        period = st.selectbox(T["period"], ["1y","3y","5y","10y"], index=1, key="period_select")
    with op2:
        corr_tickers_input = st.text_input(T["corr_input"], value="AAPL, MSFT, GOOGL, AMZN, META", key="corr_input_box")

if "period_select" not in st.session_state:
    st.session_state.period_select = "3y"
period             = st.session_state.period_select
corr_tickers_input = st.session_state.get("corr_input_box", "AAPL, MSFT, GOOGL, AMZN, META")

# =========================
# WELCOME
# =========================
if not st.session_state.analyzed_ticker:
    st.markdown("---")
    st.markdown(
        '<div class="fade-container" style="text-align:center;color:' + TEXT_SECONDARY + ';padding:3rem 0;">'
        '<div style="font-size:3rem;">🏦</div>'
        '<div style="font-size:1.1rem;margin-top:0.5rem;">' + T["welcome_1"] + '</div>'
        '<div style="font-size:0.85rem;margin-top:0.5rem;">' + T["welcome_2"] + '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

active_ticker = st.session_state.analyzed_ticker

# =========================
# DATA
# =========================
with st.spinner(T["loading"] + " " + active_ticker + "..."):
    try:
        stock         = yf.Ticker(active_ticker)
        info          = stock.info
        hist          = stock.history(period=period)
        financials    = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow      = stock.cashflow
    except Exception as e:
        st.error("Error al obtener datos: " + str(e))
        st.stop()

price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
if price is None:
    st.error(T["price_error"])
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
    delta_str = '<span style="color:' + color_chg + ';font-size:1.05rem;">' + f"{chg:+.2f} ({chg_pct:+.2f}%)" + '</span>'
else:
    delta_str = ""

render_company_header(company_name, active_ticker, sector, industry, currency, price, delta_str)

k1, k2, k3, k4 = st.columns(4)
with k1:
    metric_card(T["market_cap"], fmt_large(info.get("marketCap")))
with k2:
    metric_card(T["high_52"], fmt_num(info.get("fiftyTwoWeekHigh")) + " " + currency)
with k3:
    metric_card(T["low_52"], fmt_num(info.get("fiftyTwoWeekLow")) + " " + currency)
with k4:
    metric_card(T["beta"], fmt_num(info.get("beta")))

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
        st.write(maybe_translate(desc)) if desc else st.info(T["no_data"])
    with c2:
        st.subheader(T["corp_data"])
        employees = info.get("fullTimeEmployees")
        render_champagne_table(pd.DataFrame({
            "Campo" if lang=="ES" else "Field": [T["country"],T["city"],T["exchange"],T["employees"],T["sector"],T["industry"]],
            "Valor" if lang=="ES" else "Value": [
                info.get("country","N/A"), info.get("city","N/A"), info.get("exchange","N/A"),
                f"{employees:,}" if employees else "N/A", sector, industry
            ]
        }))
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
        st.markdown("**" + T["market_val"] + "**")
        st.write("P/E (TTM): **" + fmt_num(pe) + "**")
        st.write("P/E (Fwd): **" + fmt_num(fwd_pe) + "**")
        st.write("P/B: **" + fmt_num(pb) + "**")
        st.write("P/S: **" + fmt_num(ps) + "**")
    with col2:
        st.markdown("**" + T["profitability"] + "**")
        st.write("ROE: **" + fmt_num(roe*100 if roe else None, 1, "%") + "**")
        st.write("ROA: **" + fmt_num(roa*100 if roa else None, 1, "%") + "**")
        st.write(("Margen bruto" if lang=="ES" else "Gross margin") + ": **" + fmt_num(gross_margin*100 if gross_margin else None, 1, "%") + "**")
        st.write(("Margen neto" if lang=="ES" else "Net margin") + ": **" + fmt_num(profit_margin*100 if profit_margin else None, 1, "%") + "**")
    with col3:
        st.markdown("**" + T["risk_liq"] + "**")
        st.write(("Deuda/Equity" if lang=="ES" else "Debt/Equity") + ": **" + fmt_num(debt_equity) + "**")
        st.write("Current ratio: **" + fmt_num(current_ratio) + "**")
        st.write("Quick ratio: **" + fmt_num(quick_ratio) + "**")
        st.write("Dividend yield: **" + fmt_num(dividend_yield*100 if dividend_yield else None, 2, "%") + "**")

    st.markdown("---")
    st.markdown("**" + T["financial_profile"] + "**")

    def norm(v, lo, hi):
        v2 = safe_float(v, None)
        if v2 is None: return 0.0
        return max(0.0, min(1.0, (v2-lo)/(hi-lo)))

    radar_labels = ["ROE","ROA",
                    "Net Margin" if lang=="EN" else "Margen neto",
                    "Low P/E"   if lang=="EN" else "P/E bajo",
                    "Low Debt"  if lang=="EN" else "Deuda baja",
                    "Liquidity" if lang=="EN" else "Liquidez"]
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
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
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
            u = row["Upside %"]; cal = row["Calidad"]
            if pd.isna(u):  base = 2
            elif u >= 40:   base = 5
            elif u >= 20:   base = 4
            elif u >= 0:    base = 3
            elif u >= -20:  base = 2
            else:           base = 1
            if cal in ["Alta","High"]:  base = min(base+1, 5)
            elif cal in ["Baja","Low"]: base = max(base-1, 1)
            return "★"*base + "☆"*(5-base)

        df_val["Score"] = df_val.apply(score_row, axis=1)

        df_tabla = pd.DataFrame({
            "Método" if lang=="ES" else "Method": df_val["Método"],
            T["type"]:            df_val["Tipo"],
            T["score"]:           df_val["Score"],
            "Upside (%)":         df_val["Upside %"].apply(lambda u: f"{u:+.1f}%" if pd.notna(u) else "N/A"),
            T["intrinsic_value"]: df_val["Valor"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            T["current_price"]:   df_val["Precio"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            T["quality"]:         df_val["Calidad"],
            T["interpretation"]:  df_val["Interpretación"],
            T["used"]:            df_val["Qué se usó"],
        })
        df_tabla = df_tabla.reindex(df_val.sort_values("Upside %", ascending=False).index)
        render_champagne_table(df_tabla, pills_cols=[T["quality"], T["interpretation"]])

        st.markdown("---")
        upsides = df_val["Upside %"].dropna()
        m1, m2, m3, m4 = st.columns(4)
        with m1: metric_card("Métodos" if lang=="ES" else "Methods", str(len(df_val)))
        with m2: metric_card("Upside mediano" if lang=="ES" else "Median upside", f"{upsides.median():+.1f}%" if len(upsides) else "N/A")
        with m3: metric_card("Upside medio"   if lang=="ES" else "Mean upside",   f"{upsides.mean():+.1f}%"   if len(upsides) else "N/A")
        with m4: metric_card("Rango"          if lang=="ES" else "Range",         f"{upsides.min():+.1f}% / {upsides.max():+.1f}%" if len(upsides) else "N/A")

        st.markdown("---")
        st.markdown("### " + T["detail_methods"])
        for _, row in df_val.sort_values("Upside %", ascending=False).reset_index(drop=True).iterrows():
            with st.expander(row["Método"] + " · " + T["intrinsic_value"] + ": " + f"{row['Valor']:.2f}" + " " + currency, expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**" + T["type"]    + ":** " + row["Tipo"])
                    st.markdown("**" + T["quality"]  + ":** " + row["Calidad"])
                    st.markdown("**" + T["current_price"] + ":** " + (f"{row['Precio']:.2f} {currency}" if pd.notna(row["Precio"]) else "N/A"))
                with c2:
                    st.markdown("**" + T["intrinsic_value"] + ":** " + f"{row['Valor']:.2f} {currency}")
                    st.markdown("**" + T["upside"] + ":** " + (f"{row['Upside %']:+.1f}%" if pd.notna(row["Upside %"]) else "N/A"))
                    st.markdown("**" + T["interpretation"] + ":** " + row["Interpretación"])
                st.markdown("**" + T["used"]        + ":** " + row["Qué se usó"])
                st.markdown("**" + T["explanation"] + ":** " + row["Detalle"])

        fig_val = px.strip(
            df_val, x="Upside %", y="Tipo", color="Tipo",
            hover_data=["Método","Valor","Qué se usó"],
            title="Distribución de upside por tipo de método" if lang=="ES" else "Upside distribution by valuation type",
            color_discrete_sequence=CHART_COLORS,
        )
        fig_val.add_vline(x=0, line_dash="dash", line_color="#7A6856", opacity=0.5)
        fig_val.update_layout(
            paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor=CARD_BG,
            height=350, font=dict(color=TEXT_PRIMARY),
            xaxis_title="Upside vs precio actual (%)" if lang=="ES" else "Upside vs current price (%)",
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
        with st.spinner("Descargando benchmarks..." if lang=="ES" else "Downloading benchmarks..."):
            data_bench = {}
            for t in tickers_all:
                try:
                    inf = yf.Ticker(t).info
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
            render_champagne_table(pd.DataFrame({
                "Ticker": df_bench["Ticker"],
                "Nombre" if lang=="ES" else "Name": df_bench["Name"],
                "Precio" if lang=="ES" else "Price": df_bench["Price"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"),
                "P/E":        df_bench["P/E"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"),
                "P/B":        df_bench["P/B"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"),
                "ROE":        df_bench["ROE"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A"),
                "Margen neto" if lang=="ES" else "Net Margin": df_bench["Net Margin"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A"),
                "Market Cap": df_bench["Market Cap"].apply(fmt_large),
            }))
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
    corr_tickers = [t.strip().upper() for t in corr_tickers_input.replace(",","\n").split("\n") if t.strip()]
    if active_ticker not in corr_tickers:
        corr_tickers.insert(0, active_ticker)

    with st.spinner("Descargando precios..." if lang=="ES" else "Downloading prices..."):
        try:
            df_dl = yf.download(corr_tickers, period=period, auto_adjust=True, progress=False)
            if isinstance(df_dl.columns, pd.MultiIndex):
                prices = df_dl.xs("Close", level=0, axis=1, drop_level=True)
            else:
                prices = df_dl["Close"].to_frame(name=corr_tickers[0]) if len(corr_tickers)==1 else df_dl["Close"]
            returns = prices.pct_change().dropna()
        except Exception as e:
            st.error("Error: " + str(e))
            returns = None

    if returns is not None and not returns.empty:
        st.markdown("#### " + T["corr_matrix"])
        fig_corr = px.imshow(returns.corr(), text_auto=".2f",
                             color_continuous_scale=["#B85C5C","#FFF8F0","#5E8B6F"], zmin=-1, zmax=1)
        fig_corr.update_layout(paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor=CARD_BG, height=420, font=dict(color=TEXT_PRIMARY))
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("#### " + T["cum_returns"])
        fig_cum = px.line((1+returns).cumprod(), labels={"value":T["cum_returns"],"index":"Date"}, color_discrete_sequence=CHART_COLORS)
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

        num_activos         = len(corr_tickers)
        rendimientos_medios = returns.mean() * 252
        matriz_cov          = returns.cov() * 252

        def stats(w):
            w  = np.array(w)
            r  = np.sum(rendimientos_medios * w)
            v  = np.sqrt(np.dot(w.T, np.dot(matriz_cov, w)))
            sh = (r - rf_rate) / v if v > 0 else 0
            return r, v, sh

        def obj(w):
            return -stats(w)[2] if objetivo == T["goal_sharpe"] else stats(w)[1]

        res = minimize(obj, [1/num_activos]*num_activos, method="SLSQP",
                       bounds=[(0,1)]*num_activos,
                       constraints={"type":"eq","fun":lambda x: np.sum(x)-1})

        if res.success:
            r_opt, v_opt, sh_opt = stats(res.x)
            st.markdown("#### " + T["portfolio_metrics"])
            mp1, mp2, mp3 = st.columns(3)
            mp1.metric(T["exp_return"], f"{r_opt*100:.2f}%")
            mp2.metric(T["volatility"], f"{v_opt*100:.2f}%")
            mp3.metric(T["sharpe"],     f"{sh_opt:.2f}")

            weight_col = "Fracción" if lang=="ES" else "Decimal"
            name_col   = "Activo"   if lang=="ES" else "Asset"
            df_pesos   = pd.DataFrame({
                name_col:  corr_tickers,
                "Peso (%)" if lang=="ES" else "Weight (%)": [f"{w*100:.2f}%" for w in res.x],
                weight_col: np.round(res.x, 4)
            }).sort_values(by=weight_col, ascending=False)
            render_champagne_table(df_pesos)

            fig_pie = px.pie(
                df_pesos[df_pesos[weight_col] > 0.001],
                values=weight_col, names=name_col,
                title=("Distribución recomendada" if lang=="ES" else "Recommended allocation") + " (" + objetivo + ")",
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
    for tab_f, df_f in zip([fs1, fs2, fs3], [financials, balance_sheet, cashflow]):
        with tab_f:
            st.markdown('<div class="fade-container">', unsafe_allow_html=True)
            df_fmt = format_financial_df(df_f)
            render_champagne_table(df_fmt) if df_fmt is not None else st.info(T["no_data"])
            st.markdown('</div>', unsafe_allow_html=True)

# -------- TAB INFORMES --------
with tab_filings:
    st.markdown('<div class="fade-container">', unsafe_allow_html=True)
    st.subheader("📋 Informes regulatorios" if lang=="ES" else "📋 Regulatory filings")

    ticker_base  = active_ticker.split(".")[0].upper()
    ticker_upper = active_ticker.upper()
    df_all       = []
    source_label = ""

    is_us_ticker = not any(ticker_upper.endswith(s) for s in SUFFIXES_NO_US)
    is_eu_ticker = any(ticker_upper.endswith(s) for s in REGULATORY_SOURCES)

    if is_us_ticker:
        with st.spinner("🔍 Buscando CIK en SEC EDGAR..."):
            cik = get_cik_from_ticker_us(ticker_base)
        if cik:
            with st.spinner("📥 Descargando filings..."):
                df_sec = get_sec_filings_metadata(cik)
            if not df_sec.empty:
                df_all.append(df_sec)
                source_label = "SEC EDGAR (EE.UU.)"
                st.success("✅ **" + str(len(df_sec)) + "** informes en la SEC para **" + ticker_base + "** (CIK: " + str(int(cik)) + ")")
            else:
                st.warning("⚠️ CIK encontrado (" + str(int(cik)) + ") pero sin filings. Puede ser un problema temporal.")
        else:
            st.info("ℹ️ No se encontró CIK para **" + ticker_base + "** en la SEC.")

    elif is_eu_ticker:
        suffix      = next((s for s in REGULATORY_SOURCES if ticker_upper.endswith(s)), None)
        source_name = REGULATORY_SOURCES.get(suffix, "")
        with st.spinner("🔍 Buscando en " + source_name + "..."):
            df_eu, source_label = get_european_filings(active_ticker)
        if df_eu is not None and not df_eu.empty:
            df_all.append(df_eu)
            real_count = len(df_eu[df_eu["Fecha"] != "—"]) if "Fecha" in df_eu.columns else len(df_eu)
            if real_count > 0:
                st.success("✅ **" + str(real_count) + "** comunicados en **" + source_label + "** para **" + ticker_base + "**")
            else:
                st.info("ℹ️ Enlace directo al portal **" + source_label + "** para **" + ticker_base + "**")
    else:
        st.info("ℹ️ Sin fuente regulatoria configurada para **" + active_ticker + "**. Verifica el sufijo (ej: .MC, .L, .PA, .AS, .MI...).")

    if df_all:
        df_filings = pd.concat(df_all, ignore_index=True)
        if "Fecha" in df_filings.columns:
            try:
                df_filings["_s"] = pd.to_datetime(df_filings["Fecha"], errors="coerce")
                df_filings.sort_values("_s", ascending=False, inplace=True)
                df_filings.drop(columns=["_s"], inplace=True)
