import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import math
import datetime as dt
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

if "analyzed_ticker" not in st.session_state:
    st.session_state.analyzed_ticker = None
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "lang" not in st.session_state:
    st.session_state.lang = "es"

# =========================
# IDIOMAS
# =========================
LANG_OPTIONS = {
    "Español": "es",
    "English": "en",
}

TEXTS = {
    "es": {
        "hero_sub": "Value Investing · Análisis fundamental de empresas cotizadas",
        "search_placeholder": "🔎 Busca una empresa o ticker (ej: Apple, AAPL, Stellantis, TEF.MC...)",
        "analyze": "Analizar →",
        "options": "⚙️ Opciones de análisis",
        "period": "Período histórico",
        "corr_input": "Tickers para correlación y cartera (separados por comas)",
        "language": "Idioma",
        "welcome_1": "Introduce el nombre o ticker de una empresa y pulsa",
        "welcome_2": "Ejemplos: Apple · MSFT · Stellantis · TEF.MC · SAN.MC · Inditex",
        "company": "Empresa",
        "ratios": "Ratios",
        "valuation": "Valoración",
        "statements": "Estados contables",
        "benchmarks": "Benchmarks",
        "correlations": "Correlaciones",
        "price": "Precio",
        "portfolio": "Optimización de cartera",
        "news": "Noticias",
        "business_description": "Descripción del negocio",
        "corporate_data": "Datos corporativos",
        "country": "País",
        "city": "Ciudad",
        "exchange": "Bolsa",
        "employees": "Empleados",
        "sector": "Sector",
        "industry": "Industria",
        "no_description": "No hay descripción disponible.",
        "relevant_news": "Noticias relevantes",
        "company_news": "Noticias de la empresa",
        "market_news": "Noticias generales de mercado",
        "read_more": "Leer noticia completa",
        "no_news": "No se han encontrado noticias con la configuración actual.",
        "no_api_key": "No se ha configurado la clave NEWS_API_KEY en Secrets.",
        "loading_news": "Cargando noticias...",
        "loading_data": "Cargando datos de",
        "market_cap": "Capitalización bursátil",
        "high_52w": "Máximo 52 semanas",
        "low_52w": "Mínimo 52 semanas",
        "beta": "Beta",
        "market_valuation": "Valoración de mercado",
        "profitability": "Rentabilidad",
        "risk_liquidity": "Riesgo y liquidez",
        "trailing_pe": "PER (12 meses)",
        "forward_pe": "PER adelantado",
        "pb": "P/Valor contable",
        "ps": "P/Ventas",
        "roe": "ROE",
        "roa": "ROA",
        "gross_margin": "Margen bruto",
        "net_margin": "Margen neto",
        "debt_equity": "Deuda/Patrimonio",
        "current_ratio": "Ratio corriente",
        "quick_ratio": "Quick ratio",
        "dividend_yield": "Rentabilidad por dividendo",
        "financial_profile": "Perfil financiero (radar)",
        "intrinsic_valuation": "Valoración intrínseca — todos los métodos",
        "insufficient_valuation_data": "No se pudieron calcular valoraciones por falta de datos.",
        "methods_calculated": "Métodos calculados",
        "median_upside": "Upside mediano",
        "mean_upside": "Upside medio",
        "upside_range": "Rango de upside",
        "how_calculated": "Cómo se calcula cada método",
        "quality": "Calidad",
        "intrinsic_value": "Valor intrínseco",
        "current_price": "Precio actual",
        "interpretation": "Interpretación",
        "calculation": "Cálculo",
        "sector_benchmarks": "Comparación con benchmarks del sector",
        "no_benchmarks": "No hay benchmarks definidos para este sector.",
        "benchmarks_error": "No se pudieron cargar datos de benchmarks.",
        "correlation_returns": "Correlación de rentabilidades",
        "correlation_matrix": "Matriz de correlación",
        "cumulative_returns": "Retornos acumulados",
        "historical_price_volume": "Histórico de precio y volumen",
        "no_historical_data": "No hay datos históricos disponibles.",
        "markowitz": "Optimización de cartera de Markowitz",
        "optimize_selection": "Configura las variables para optimizar tu selección actual de activos.",
        "optimizer_goal": "Objetivo del optimizador",
        "maximize_sharpe": "Maximizar ratio Sharpe",
        "min_variance": "Minimizar varianza",
        "risk_free_rate": "Tasa libre de riesgo anualizada (%)",
        "optimal_metrics": "Métricas de la cartera óptima",
        "expected_return": "Rentabilidad esperada anual",
        "portfolio_volatility": "Volatilidad de la cartera",
        "sharpe_ratio": "Ratio Sharpe",
        "optimizer_error": "El algoritmo de optimización no pudo converger en una solución válida.",
        "insufficient_hist_data": "Datos históricos insuficientes. Asegúrate de configurar los tickers correctamente en las opciones superiores.",
        "suggestions": "Sugerencias",
        "description": "Descripción",
        "ohlc": "OHLC",
        "volume": "Volumen",
        "price_error": "No se pudo obtener el precio de mercado. Verifica el ticker.",
        "data_error": "Error al obtener datos",
        "very_undervalued": "Muy infravalorada",
        "undervalued": "Infravalorada",
        "fairly_valued": "En línea",
        "overvalued": "Sobrevalorada",
        "very_overvalued": "Muy sobrevalorada",
        "news_info_header": "Se muestran noticias de la empresa y del mercado.",
        "income_statement": "Cuenta de resultados",
        "balance_sheet": "Balance",
        "cash_flow": "Flujo de caja",
        "annual": "Anual",
        "quarterly": "Trimestral",
        "statement_type": "Tipo de estado",
        "statement_period": "Período",
        "no_statement_data": "No hay datos disponibles para este estado contable.",
        "financial_statements": "Estados contables",
        "download_ready": "Tabla interactiva disponible",
        "comparison_view": "Vista comparativa",
        "select_metrics": "Selecciona métricas para comparar",
        "available_years": "Años/fechas disponibles",
        "statement_chart": "Evolución histórica de partidas",
        "no_metrics_selected": "Selecciona al menos una partida para visualizar la comparación.",
        "comparison_table": "Tabla histórica comparativa",
        "top_lines": "Partidas principales",
        "concept": "Concepto",
        "official_filings": "Informes oficiales",
        "filing_source": "Fuente del informe",
        "sec_source": "SEC (EEUU)",
        "cnmv_source": "CNMV (España)",
        "filing_type": "Tipo de informe",
        "lookup_filing": "Buscar informe",
        "download_sec_filing": "Descargar documento SEC",
        "open_document": "Abrir documento",
        "enter_cik": "CIK de la compañía (10 dígitos, opcional si existe mapeo)",
        "filing_found": "Informe localizado",
        "filing_not_found": "No se encontró un informe reciente de ese tipo.",
        "sec_error": "Error al consultar la SEC",
        "cnmv_info": "La CNMV publica los informes financieros en su portal oficial.",
        "open_cnmv": "Abrir buscador CNMV",
        "using_mapped_cik": "Usando CIK mapeado automáticamente",
        "invalid_cik": "Introduce un CIK válido.",
        "direct_download_failed": "No se pudo descargar el documento directamente.",
    },
    "en": {
        "hero_sub": "Value Investing · Fundamental analysis of listed companies",
        "search_placeholder": "🔎 Search for a company or ticker (e.g. Apple, AAPL, Stellantis, TEF.MC...)",
        "analyze": "Analyze →",
        "options": "⚙️ Analysis options",
        "period": "Historical period",
        "corr_input": "Tickers for correlation and portfolio (comma separated)",
        "language": "Language",
        "welcome_1": "Enter a company name or ticker and click",
        "welcome_2": "Examples: Apple · MSFT · Stellantis · TEF.MC · SAN.MC · Inditex",
        "company": "Company",
        "ratios": "Ratios",
        "valuation": "Valuation",
        "statements": "Financial statements",
        "benchmarks": "Benchmarks",
        "correlations": "Correlations",
        "price": "Price",
        "portfolio": "Portfolio optimization",
        "news": "News",
        "business_description": "Business description",
        "corporate_data": "Corporate data",
        "country": "Country",
        "city": "City",
        "exchange": "Exchange",
        "employees": "Employees",
        "sector": "Sector",
        "industry": "Industry",
        "no_description": "No description available.",
        "relevant_news": "Relevant news",
        "company_news": "Company news",
        "market_news": "General market news",
        "read_more": "Read full article",
        "no_news": "No news was found with the current settings.",
        "no_api_key": "NEWS_API_KEY has not been configured in Secrets.",
        "loading_news": "Loading news...",
        "loading_data": "Loading data for",
        "market_cap": "Market cap",
        "high_52w": "52W high",
        "low_52w": "52W low",
        "beta": "Beta",
        "market_valuation": "Market valuation",
        "profitability": "Profitability",
        "risk_liquidity": "Risk and liquidity",
        "trailing_pe": "P/E (TTM)",
        "forward_pe": "Forward P/E",
        "pb": "P/Book",
        "ps": "P/Sales",
        "roe": "ROE",
        "roa": "ROA",
        "gross_margin": "Gross margin",
        "net_margin": "Net margin",
        "debt_equity": "Debt/Equity",
        "current_ratio": "Current ratio",
        "quick_ratio": "Quick ratio",
        "dividend_yield": "Dividend yield",
        "financial_profile": "Financial profile (radar)",
        "intrinsic_valuation": "Intrinsic valuation — all methods",
        "insufficient_valuation_data": "Valuations could not be calculated due to insufficient data.",
        "methods_calculated": "Methods calculated",
        "median_upside": "Median upside",
        "mean_upside": "Mean upside",
        "upside_range": "Upside range",
        "how_calculated": "How each method is calculated",
        "quality": "Quality",
        "intrinsic_value": "Intrinsic value",
        "current_price": "Current price",
        "interpretation": "Interpretation",
        "calculation": "Calculation",
        "sector_benchmarks": "Sector benchmark comparison",
        "no_benchmarks": "No benchmarks defined for this sector.",
        "benchmarks_error": "Benchmark data could not be loaded.",
        "correlation_returns": "Return correlations",
        "correlation_matrix": "Correlation matrix",
        "cumulative_returns": "Cumulative returns",
        "historical_price_volume": "Historical price and volume",
        "no_historical_data": "No historical data available.",
        "markowitz": "Markowitz portfolio optimization",
        "optimize_selection": "Configure the variables to optimize your current asset selection.",
        "optimizer_goal": "Optimizer goal",
        "maximize_sharpe": "Maximize Sharpe ratio",
        "min_variance": "Minimize variance",
        "risk_free_rate": "Annualized risk-free rate (%)",
        "optimal_metrics": "Optimal portfolio metrics",
        "expected_return": "Expected annual return",
        "portfolio_volatility": "Portfolio volatility",
        "sharpe_ratio": "Sharpe ratio",
        "optimizer_error": "The optimization algorithm could not converge to a valid solution.",
        "insufficient_hist_data": "Insufficient historical data. Make sure the tickers are configured correctly in the options above.",
        "suggestions": "Suggestions",
        "description": "Description",
        "ohlc": "OHLC",
        "volume": "Volume",
        "price_error": "Could not retrieve market price. Check the ticker.",
        "data_error": "Error retrieving data",
        "very_undervalued": "Very undervalued",
        "undervalued": "Undervalued",
        "fairly_valued": "Fairly valued",
        "overvalued": "Overvalued",
        "very_overvalued": "Very overvalued",
        "news_info_header": "Company and market news are shown.",
        "income_statement": "Income statement",
        "balance_sheet": "Balance sheet",
        "cash_flow": "Cash flow",
        "annual": "Annual",
        "quarterly": "Quarterly",
        "statement_type": "Statement type",
        "statement_period": "Period",
        "no_statement_data": "No data available for this financial statement.",
        "financial_statements": "Financial statements",
        "download_ready": "Interactive table available",
        "comparison_view": "Comparison view",
        "select_metrics": "Select metrics to compare",
        "available_years": "Available years/dates",
        "statement_chart": "Historical trend of line items",
        "no_metrics_selected": "Select at least one line item to visualize the comparison.",
        "comparison_table": "Historical comparison table",
        "top_lines": "Main line items",
        "concept": "Concept",
        "official_filings": "Official filings",
        "filing_source": "Filing source",
        "sec_source": "SEC (US)",
        "cnmv_source": "CNMV (Spain)",
        "filing_type": "Filing type",
        "lookup_filing": "Search filing",
        "download_sec_filing": "Download SEC document",
        "open_document": "Open document",
        "enter_cik": "Company CIK (10 digits, optional if mapping exists)",
        "filing_found": "Filing found",
        "filing_not_found": "No recent filing of that type was found.",
        "sec_error": "Error while querying the SEC",
        "cnmv_info": "CNMV publishes financial reports in its official portal.",
        "open_cnmv": "Open CNMV search",
        "using_mapped_cik": "Using automatically mapped CIK",
        "invalid_cik": "Enter a valid CIK.",
        "direct_download_failed": "The document could not be downloaded directly.",
    },
}

def tr(key):
    return TEXTS[st.session_state.lang].get(key, key)

# =========================
# COLORES Y ESTILOS CSS
# =========================
ACCENT_BLUE = "#38BDF8"
ACCENT_GREEN = "#22C55E"
ACCENT_RED = "#EF4444"
TEXT_PRIMARY = "#E5E7EB"
TEXT_SECONDARY = "#9CA3AF"
CARD_BG = "#111827"
BORDER = "#1F2937"

st.markdown(
    f"""
    <style>
    [data-testid="collapsedControl"] {{ display: none; }}
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1300px;
    }}
    .stApp {{
        background: radial-gradient(circle at top left, #111827 0, #020617 55%);
        color: {TEXT_PRIMARY};
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }}
    .hero-title {{
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        text-align: center;
        background: linear-gradient(90deg, {ACCENT_BLUE}, {ACCENT_GREEN});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }}
    .hero-sub {{
        text-align: center;
        color: {TEXT_SECONDARY};
        font-size: 1rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }}
    .metric-card {{
        background: {CARD_BG};
        border-radius: 10px;
        padding: 0.8rem 1rem;
        border: 1px solid {BORDER};
        margin-bottom: 0.4rem;
    }}
    .metric-label {{
        color: {TEXT_SECONDARY};
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.2rem;
    }}
    .metric-value {{
        font-size: 1.1rem;
        font-weight: 600;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.9rem;
        padding: 0.75rem 1.25rem;
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

def traducir_texto(texto):
    if not texto:
        return ""
    try:
        return GoogleTranslator(source="auto", target=st.session_state.lang).translate(texto)
    except Exception:
        return texto

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

def format_financial_df(df):
    if df is None or df.empty:
        return pd.DataFrame(), []

    df = df.copy()

    try:
        ordered_cols = sorted(df.columns, reverse=False)
        df = df[ordered_cols]
        formatted_cols = [pd.to_datetime(c).strftime("%Y-%m-%d") for c in df.columns]
        df.columns = formatted_cols
    except Exception:
        df.columns = [str(c) for c in df.columns]

    available_periods = list(df.columns)

    df = df.reset_index()
    first_col = df.columns[0]
    df = df.rename(columns={first_col: tr("concept")})

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df, available_periods

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

def get_company_news(api_key, active_ticker, company_name):
    desde = (dt.datetime.utcnow() - dt.timedelta(days=3)).strftime("%Y-%m-%d")
    query = f'"{active_ticker}" OR "{company_name}"'
    params = {
        "q": query,
        "from": desde,
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": api_key,
    }
    try:
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=15)
        data = resp.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        return []
    except Exception:
        return []

def get_market_news(api_key):
    try:
        resp = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "country": "us",
                "category": "business",
                "pageSize": 10,
                "apiKey": api_key,
            },
            timeout=15,
        )
        data = resp.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        return []
    except Exception:
        return []

SEC_TICKER_CIK = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "META": "0001326801",
    "TSLA": "0001318605",
    "NVDA": "0001045810",
    "BRK-B": "0001067983",
    "JPM": "0000019617",
    "KO": "0000021344",
}

def get_sec_latest_filing(cik, form_type, user_agent="Your Name your@email.com"):
    headers = {"User-Agent": user_agent}
    cik = str(cik).zfill(10)

    url_sub = f"https://data.sec.gov/submissions/CIK{cik}.json"
    resp = requests.get(url_sub, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    filings = data.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    accessions = filings.get("accessionNumber", [])
    primary_docs = filings.get("primaryDocument", [])
    filing_dates = filings.get("filingDate", [])

    for form, acc, doc, fdate in zip(forms, accessions, primary_docs, filing_dates):
        if form == form_type:
            acc_nodash = acc.replace("-", "")
            cik_int = str(int(cik))
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{doc}"
            return {
                "form": form,
                "date": fdate,
                "url": doc_url,
                "accession": acc,
            }

    return None

# =========================
# VALORACIÓN
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

# =========================
# CABECERA
# =========================
st.markdown('<div class="hero-title">📊 Equity Terminal</div>', unsafe_allow_html=True)

lang_col1, lang_col2, lang_col3 = st.columns([4, 1.2, 0.8])
with lang_col2:
    current_label = "Español" if st.session_state.lang == "es" else "English"
    selected_lang_label = st.selectbox(
        tr("language"),
        options=list(LANG_OPTIONS.keys()),
        index=list(LANG_OPTIONS.keys()).index(current_label),
    )
    st.session_state.lang = LANG_OPTIONS[selected_lang_label]

st.markdown(f'<div class="hero-sub">{tr("hero_sub")}</div>', unsafe_allow_html=True)

col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input(
        "",
        placeholder=tr("search_placeholder"),
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button(tr("analyze"), use_container_width=True, type="primary")

if query != st.session_state.current_query:
    st.session_state.current_query = query

ticker_sym = ""
if query:
    suggestions = search_ticker(query)
    if suggestions:
        choice = st.selectbox(tr("suggestions"), suggestions, label_visibility="collapsed")
        ticker_sym = choice.split(" — ")[0].strip()
    else:
        ticker_sym = query.strip().upper()

if analyze_btn and ticker_sym:
    st.session_state.analyzed_ticker = ticker_sym

with st.expander(tr("options"), expanded=False):
    op1, op2 = st.columns([1, 2])
    with op1:
        period = st.selectbox(tr("period"), ["1y", "3y", "5y", "10y"], index=1)
    with op2:
        corr_tickers_input = st.text_input(
            tr("corr_input"),
            value="AAPL, MSFT, GOOGL, AMZN, META",
        )

if not st.session_state.analyzed_ticker:
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center; color:{TEXT_SECONDARY}; padding: 3rem 0;">
            <div style="font-size:3rem;">🏦</div>
            <div style="font-size:1.1rem; margin-top:0.5rem;">
                {tr("welcome_1")} <b>{tr("analyze")}</b>
            </div>
            <div style="font-size:0.85rem; margin-top:0.5rem;">
                {tr("welcome_2")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

active_ticker = st.session_state.analyzed_ticker

# =========================
# EXTRACCIÓN DE DATOS
# =========================
with st.spinner(f"{tr('loading_data')} {active_ticker}..."):
    try:
        stock = yf.Ticker(active_ticker)
        info = stock.info
        hist = stock.history(period=period)

        financials_annual = stock.financials
        balance_annual = stock.balance_sheet
        cashflow_annual = stock.cashflow

        financials_quarterly = stock.quarterly_financials
        balance_quarterly = stock.quarterly_balance_sheet
        cashflow_quarterly = stock.quarterly_cashflow
    except Exception as e:
        st.error(f"{tr('data_error')}: {e}")
        st.stop()

price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
if price is None:
    st.error(tr("price_error"))
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
    delta_str = f'<span style="color:{color_chg}">{chg:+.2f} ({chg_pct:+.2f}%)</span>'
else:
    delta_str = ""

st.markdown(
    f"""
    <div style="margin: 1.2rem 0 0.3rem 0;">
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

mc = fmt_large(info.get("marketCap"))
high52 = fmt_num(info.get("fiftyTwoWeekHigh"))
low52 = fmt_num(info.get("fiftyTwoWeekLow"))
beta_v = fmt_num(info.get("beta"))

k1, k2, k3, k4 = st.columns(4)
for col, label, val in [
    (k1, tr("market_cap"), mc),
    (k2, tr("high_52w"), f"{high52} {currency}"),
    (k3, tr("low_52w"), f"{low52} {currency}"),
    (k4, tr("beta"), beta_v),
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
tab_emp, tab_rat, tab_val, tab_stmt, tab_bench, tab_corr, tab_price, tab_port, tab_news = st.tabs(
    [
        tr("company"),
        tr("ratios"),
        tr("valuation"),
        tr("statements"),
        tr("benchmarks"),
        tr("correlations"),
        tr("price"),
        tr("portfolio"),
        tr("news"),
    ]
)

# ==== EMPRESA ====
with tab_emp:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(tr("business_description"))
        desc = info.get("longBusinessSummary")
        if desc:
            st.write(traducir_texto(desc))
        else:
            st.info(tr("no_description"))
    with c2:
        st.subheader(tr("corporate_data"))
        employees = info.get("fullTimeEmployees")
        for label, val in [
            (tr("country"), info.get("country", "N/A")),
            (tr("city"), info.get("city", "N/A")),
            (tr("exchange"), info.get("exchange", "N/A")),
            (tr("employees"), f"{employees:,}" if employees else "N/A"),
            (tr("sector"), sector),
            (tr("industry"), industry),
        ]:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{val}</div></div>',
                unsafe_allow_html=True,
            )

# ==== RATIOS ====
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
        st.markdown(f"**{tr('market_valuation')}**")
        st.write(f"{tr('trailing_pe')}: **{fmt_num(pe)}**")
        st.write(f"{tr('forward_pe')}: **{fmt_num(fwd_pe)}**")
        st.write(f"{tr('pb')}: **{fmt_num(pb)}**")
        st.write(f"{tr('ps')}: **{fmt_num(ps)}**")
    with col2:
        st.markdown(f"**{tr('profitability')}**")
        st.write(f"{tr('roe')}: **{fmt_num(roe*100 if roe else None, 1, '%')}**")
        st.write(f"{tr('roa')}: **{fmt_num(roa*100 if roa else None, 1, '%')}**")
        st.write(f"{tr('gross_margin')}: **{fmt_num(gross_margin*100 if gross_margin else None, 1, '%')}**")
        st.write(f"{tr('net_margin')}: **{fmt_num(profit_margin*100 if profit_margin else None, 1, '%')}**")
    with col3:
        st.markdown(f"**{tr('risk_liquidity')}**")
        st.write(f"{tr('debt_equity')}: **{fmt_num(debt_equity)}**")
        st.write(f"{tr('current_ratio')}: **{fmt_num(current_ratio)}**")
        st.write(f"{tr('quick_ratio')}: **{fmt_num(quick_ratio)}**")
        st.write(f"{tr('dividend_yield')}: **{fmt_num(dividend_yield*100 if dividend_yield else None, 2, '%')}**")

# ==== VALORACIÓN ====
with tab_val:
    st.subheader(tr("intrinsic_valuation"))
    methods, current_price = compute_valuations(info, currency)

    if not methods:
        st.warning(tr("insufficient_valuation_data"))
    else:
        df_val = pd.DataFrame(methods)
        st.dataframe(df_val.sort_values("Upside %", ascending=False), use_container_width=True, hide_index=True)

# ==== ESTADOS CONTABLES ====
with tab_stmt:
    st.subheader(tr("financial_statements"))

    s1, s2 = st.columns(2)
    with s1:
        statement_type = st.selectbox(
            tr("statement_type"),
            [tr("income_statement"), tr("balance_sheet"), tr("cash_flow")]
        )
    with s2:
        statement_period = st.selectbox(
            tr("statement_period"),
            [tr("annual"), tr("quarterly")]
        )

    if statement_type == tr("income_statement"):
        raw_df = financials_annual if statement_period == tr("annual") else financials_quarterly
    elif statement_type == tr("balance_sheet"):
        raw_df = balance_annual if statement_period == tr("annual") else balance_quarterly
    else:
        raw_df = cashflow_annual if statement_period == tr("annual") else cashflow_quarterly

    df_stmt, available_periods = format_financial_df(raw_df)

    if df_stmt.empty:
        st.warning(tr("no_statement_data"))
    else:
        st.markdown(f"### {tr('comparison_table')}")
        st.caption(f"{tr('available_years')}: {', '.join(available_periods)}")
        st.caption(tr("download_ready"))

        st.dataframe(
            df_stmt,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(col, format="%.0f")
                for col in df_stmt.columns[1:]
            }
        )

        st.markdown("---")
        st.markdown(f"### {tr('comparison_view')}")

        concept_col = tr("concept")
        metric_options = df_stmt[concept_col].dropna().astype(str).tolist()
        default_metrics = metric_options[:5] if len(metric_options) >= 5 else metric_options

        selected_metrics = st.multiselect(
            tr("select_metrics"),
            options=metric_options,
            default=default_metrics
        )

        if not selected_metrics:
            st.info(tr("no_metrics_selected"))
        else:
            df_chart = df_stmt[df_stmt[concept_col].isin(selected_metrics)].copy()
            df_chart_long = df_chart.melt(
                id_vars=[concept_col],
                var_name="Date" if st.session_state.lang == "en" else "Fecha",
                value_name="Value" if st.session_state.lang == "en" else "Valor"
            )

            x_col = "Date" if st.session_state.lang == "en" else "Fecha"
            y_col = "Value" if st.session_state.lang == "en" else "Valor"

            fig_stmt = px.line(
                df_chart_long,
                x=x_col,
                y=y_col,
                color=concept_col,
                markers=True,
                title=tr("statement_chart")
            )
            fig_stmt.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=500,
                xaxis_title=x_col,
                yaxis_title=y_col,
                legend_title=tr("top_lines"),
            )
            st.plotly_chart(fig_stmt, use_container_width=True)

    st.markdown("---")
    st.subheader(tr("official_filings"))

    source_col1, source_col2 = st.columns(2)
    with source_col1:
        filing_source = st.selectbox(
            tr("filing_source"),
            [tr("sec_source"), tr("cnmv_source")]
        )

    if filing_source == tr("sec_source"):
        mapped_cik = SEC_TICKER_CIK.get(active_ticker.upper(), "")
        if mapped_cik:
            st.caption(f"{tr('using_mapped_cik')}: {mapped_cik}")

        sec_cik = st.text_input(
            tr("enter_cik"),
            value=mapped_cik
        )

        sec_form = st.selectbox(
            tr("filing_type"),
            ["10-K", "10-Q", "20-F", "8-K"]
        )

        if st.button(tr("lookup_filing")):
            if not sec_cik:
                st.warning(tr("invalid_cik"))
            else:
                try:
                    filing_data = get_sec_latest_filing(sec_cik, sec_form)

                    if not filing_data:
                        st.info(tr("filing_not_found"))
                    else:
                        st.success(f"{tr('filing_found')}: {filing_data['form']} · {filing_data['date']}")
                        st.markdown(f"[{tr('open_document')}]({filing_data['url']})")

                        headers = {"User-Agent": "Your Name your@email.com"}
                        file_resp = requests.get(filing_data["url"], headers=headers, timeout=30)

                        if file_resp.status_code == 200:
                            st.download_button(
                                label=tr("download_sec_filing"),
                                data=file_resp.content,
                                file_name=f"{active_ticker}_{filing_data['form']}_{filing_data['date']}.html",
                                mime="text/html",
                            )
                        else:
                            st.warning(tr("direct_download_failed"))

                except Exception as e:
                    st.error(f"{tr('sec_error')}: {e}")

    else:
        st.info(tr("cnmv_info"))
        st.markdown(
            f"[{tr('open_cnmv')}](https://www.cnmv.es/portal/consultas/em_inffinanual?id=EE&lang=es)"
        )

# ==== BENCHMARKS ====
with tab_bench:
    st.subheader(tr("sector_benchmarks"))
    peers = get_benchmark_list(info, active_ticker)
    if not peers:
        st.info(tr("no_benchmarks"))
    else:
        tickers_all = [active_ticker] + peers
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
            st.warning(tr("benchmarks_error"))
        else:
            df_bench = pd.DataFrame.from_dict(data, orient="index").reset_index().rename(columns={"index": "Ticker"})
            st.dataframe(df_bench, use_container_width=True, hide_index=True)

# ==== CORRELACIONES ====
with tab_corr:
    st.subheader(tr("correlation_returns"))
    corr_tickers = [t.strip().upper() for t in corr_tickers_input.replace(",", "\n").split("\n") if t.strip()]
    if active_ticker not in corr_tickers:
        corr_tickers.insert(0, active_ticker)

    try:
        df_download = yf.download(corr_tickers, period=period, auto_adjust=True, progress=False)
        if isinstance(df_download.columns, pd.MultiIndex):
            prices = df_download.xs("Close", level=0, axis=1, drop_level=True)
        else:
            prices = df_download["Close"].to_frame(name=corr_tickers[0]) if len(corr_tickers) == 1 else df_download["Close"]
        returns = prices.pct_change().dropna()
    except Exception:
        returns = None

    if returns is not None and not returns.empty:
        corr = returns.corr()
        st.markdown(f"#### {tr('correlation_matrix')}")
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        fig_corr.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )
        st.plotly_chart(fig_corr, use_container_width=True)

# ==== PRECIO ====
with tab_price:
    st.subheader(tr("historical_price_volume"))
    if hist is None or hist.empty:
        st.warning(tr("no_historical_data"))
    else:
        fig_price = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig_price.add_trace(
            go.Candlestick(
                x=hist.index, open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=hist["Close"], name=tr("ohlc")
            ),
            row=1, col=1,
        )
        fig_price.add_trace(
            go.Bar(x=hist.index, y=hist["Volume"], name=tr("volume"), marker_color=ACCENT_BLUE),
            row=2, col=1,
        )
        fig_price.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_price, use_container_width=True)

# ==== OPTIMIZACIÓN ====
with tab_port:
    st.subheader(tr("markowitz"))

    if returns is not None and not returns.empty:
        st.markdown(tr("optimize_selection"))

        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            objetivo = st.selectbox(
                tr("optimizer_goal"),
                [tr("maximize_sharpe"), tr("min_variance")]
            )
        with c_opt2:
            rf_rate = st.number_input(tr("risk_free_rate"), value=4.0, step=0.1) / 100

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
            if objetivo == tr("maximize_sharpe"):
                return -estadisticas_cartera(weights)[2]
            return estadisticas_cartera(weights)[1]

        restricciones = ({"type": "eq", "fun": lambda x: np.sum(x) - 1},)
        limites = tuple((0, 1) for _ in range(num_activos))
        pesos_iniciales = [1.0 / num_activos] * num_activos

        resultado_opt = minimize(
            funcion_a_minimizar,
            pesos_iniciales,
            method="SLSQP",
            bounds=limites,
            constraints=restricciones
        )

        if resultado_opt.success:
            pesos_optimos = resultado_opt.x
            r_opt, vol_opt, sharpe_opt = estadisticas_cartera(pesos_optimos)

            st.markdown(f"#### {tr('optimal_metrics')}")
            m_p1, m_p2, m_p3 = st.columns(3)
            m_p1.metric(tr("expected_return"), f"{r_opt*100:.2f}%")
            m_p2.metric(tr("portfolio_volatility"), f"{vol_opt*100:.2f}%")
            m_p3.metric(tr("sharpe_ratio"), f"{sharpe_opt:.2f}")

            df_pesos = pd.DataFrame({
                "Activo": corr_tickers,
                "Ponderación Óptima (%)": [f"{w*100:.2f}%" for w in pesos_optimos],
                "Fracción Decimal": np.round(pesos_optimos, 4)
            }).sort_values(by="Fracción Decimal", ascending=False)

            st.dataframe(df_pesos, use_container_width=True, hide_index=True)

            fig_pie = px.pie(
                df_pesos[df_pesos["Fracción Decimal"] > 0.001],
                values="Fracción Decimal",
                names="Activo",
                title=f"Distribución recomendada de capital ({objetivo})",
                color_discrete_sequence=[ACCENT_BLUE, ACCENT_GREEN, "#A78BFA", "#FB923C", "#60A5FA", "#F472B6"]
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.error(tr("optimizer_error"))
    else:
        st.warning(tr("insufficient_hist_data"))

# ==== NOTICIAS ====
with tab_news:
    st.subheader(tr("relevant_news"))

    api_key = st.secrets.get("NEWS_API_KEY", None)
    if not api_key:
        st.warning(tr("no_api_key"))
    else:
        with st.spinner(tr("loading_news")):
            noticias_empresa = get_company_news(api_key, active_ticker, company_name)
            noticias_mercado = get_market_news(api_key)

        if not noticias_empresa and not noticias_mercado:
            st.info(tr("no_news"))
        else:
            st.caption(tr("news_info_header"))

            if noticias_empresa:
                st.markdown(f"### {tr('company_news')}")
                for art in noticias_empresa:
                    titulo = traducir_texto(art.get("title", "Untitled"))
                    fuente = art.get("source", {}).get("name", "Unknown source")
                    fecha = (art.get("publishedAt") or "")[:16].replace("T", " ")
                    descripcion = traducir_texto(art.get("description") or art.get("content") or "")
                    url = art.get("url")
                    with st.expander(f"{titulo} · {fuente} · {fecha}"):
                        st.write(descripcion)
                        if url:
                            st.markdown(f"[{tr('read_more')}]({url})")

            if noticias_mercado:
                st.markdown(f"### {tr('market_news')}")
                for art in noticias_mercado:
                    titulo = traducir_texto(art.get("title", "Untitled"))
                    fuente = art.get("source", {}).get("name", "Unknown source")
                    fecha = (art.get("publishedAt") or "")[:16].replace("T", " ")
                    descripcion = traducir_texto(art.get("description") or art.get("content") or "")
                    url = art.get("url")
                    with st.expander(f"{titulo} · {fuente} · {fecha}"):
                        st.write(descripcion)
                        if url:
                            st.markdown(f"[{tr('read_more')}]({url})")
