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
        "no_news": "No se han encontrado noticias con la configuración actual. Esto puede ocurrir por el retraso de 24 horas del plan gratuito de NewsAPI.",
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
        "very_high_conviction": "Convicción muy alta",
        "high_conviction": "Convicción alta",
        "neutral": "Neutral",
        "weak": "Débil",
        "very_weak": "Muy débil",
        "news_info_header": "Se muestran noticias de la empresa y del mercado.",
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
        "no_news": "No news was found with the current settings. This may happen because the free NewsAPI plan has a 24-hour delay.",
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
        "very_high_conviction": "Very high conviction",
        "high_conviction": "High conviction",
        "neutral": "Neutral",
        "weak": "Weak",
        "very_weak": "Very weak",
        "news_info_header": "Company and market news are shown.",
    },
}

def tr(key):
    return TEXTS[st.session_state.lang].get(key, key)

# =========================
# COLORES Y ESTILOS
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
        return "N/A" if st.session_state.lang == "en" else "N/D"
    return f"{v:.{decimals}f}{suffix}"

def fmt_large(x):
    v = safe_float(x, None)
    if v is None:
        return "N/A" if st.session_state.lang == "en" else "N/D"
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
    destino = st.session_state.lang
    try:
        return GoogleTranslator(source="auto", target=destino).translate(texto)
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

def interpretar_upside(u):
    if pd.isna(u):
        return "N/A" if st.session_state.lang == "en" else "N/D"
    if u >= 40:
        return tr("very_undervalued")
    if u >= 20:
        return tr("undervalued")
    if u >= -10:
        return tr("fairly_valued")
    if u >= -30:
        return tr("overvalued")
    return tr("very_overvalued")

def score_method(upside, calidad):
    if pd.isna(upside):
        base = 2
    elif upside >= 40:
        base = 5
    elif upside >= 20:
        base = 4
    elif upside >= 0:
        base = 3
    elif upside >= -20:
        base = 2
    else:
        base = 1

    labels_es = {
        5: "Convicción muy alta",
        4: "Convicción alta",
        3: "Neutral",
        2: "Débil",
        1: "Muy débil",
    }
    labels_en = {
        5: "Very high conviction",
        4: "High conviction",
        3: "Neutral",
        2: "Weak",
        1: "Very weak",
    }
    labels = labels_en if st.session_state.lang == "en" else labels_es

    if calidad in ["Alta", "High"]:
        base = min(base + 1, 5)
    elif calidad in ["Baja", "Low"]:
        base = max(base - 1, 1)

    return f"{'★'*base}{'☆'*(5-base)} · {labels[base]}"

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

    calidad_high = "High" if st.session_state.lang == "en" else "Alta"
    calidad_medium = "Medium" if st.session_state.lang == "en" else "Media"
    calidad_low = "Low" if st.session_state.lang == "en" else "Baja"

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
            "Supuestos": (
                f"High growth {g_high*100:.0f}% for 5 years, terminal growth {g_low*100:.0f}%, discount rate {r*100:.0f}%."
                if st.session_state.lang == "en"
                else f"Crecimiento alto {g_high*100:.0f}% 5 años, crecimiento terminal {g_low*100:.0f}%, descuento {r*100:.0f}%."
            ),
        })

    if fcf is not None:
        dcf_model(fcf, 0.15, 0.04, 0.11, "Aggressive DCF" if st.session_state.lang == "en" else "DCF agresivo", calidad_medium)
        dcf_model(fcf, 0.10, 0.03, 0.10, "Base DCF" if st.session_state.lang == "en" else "DCF base", calidad_high)
        dcf_model(fcf, 0.06, 0.02, 0.09, "Conservative DCF" if st.session_state.lang == "en" else "DCF conservador", calidad_high)

    if net_income is not None and shares and shares > 0:
        dcf_model(
            net_income,
            0.08,
            0.03,
            0.10,
            "DCF using net income" if st.session_state.lang == "en" else "DCF con beneficio neto",
            calidad_medium,
        )

    if ebitda is not None and ebitda > 0 and shares and shares > 0:
        for mult, cal in [(8, calidad_high), (10, calidad_high), (12, calidad_medium), (15, calidad_medium), (20, calidad_low)]:
            ev = ebitda * mult
            methods.append({
                "Método": f"EV/EBITDA {mult}x",
                "Tipo": "Multiple" if st.session_state.lang == "en" else "Múltiplo",
                "Calidad": cal,
                "Valor": (ev + cash - total_debt) / shares,
                "Supuestos": (
                    f"EBITDA ({fmt_large(ebitda)}) multiplied by {mult}x, adjusted for net cash/debt."
                    if st.session_state.lang == "en"
                    else f"Se multiplica el EBITDA ({fmt_large(ebitda)}) por {mult}x y se ajusta por caja y deuda neta."
                ),
            })

    if ebit is not None and ebit > 0 and shares and shares > 0:
        for mult, cal in [(10, calidad_high), (14, calidad_medium), (18, calidad_low)]:
            ev = ebit * mult
            methods.append({
                "Método": f"EV/EBIT {mult}x",
                "Tipo": "Multiple" if st.session_state.lang == "en" else "Múltiplo",
                "Calidad": cal,
                "Valor": (ev + cash - total_debt) / shares,
                "Supuestos": (
                    f"EBIT ({fmt_large(ebit)}) multiplied by {mult}x, adjusted for net cash/debt."
                    if st.session_state.lang == "en"
                    else f"Se multiplica el EBIT ({fmt_large(ebit)}) por {mult}x y se ajusta por caja y deuda neta."
                ),
            })

    eps_use = eps if (eps and eps > 0) else fwd_eps
    if eps_use and eps_use > 0:
        for mult, cal in [(10, calidad_high), (15, calidad_high), (20, calidad_medium), (25, calidad_medium), (30, calidad_low)]:
            methods.append({
                "Método": f"Target P/E {mult}x" if st.session_state.lang == "en" else f"PER objetivo {mult}x",
                "Tipo": "Multiple" if st.session_state.lang == "en" else "Múltiplo",
                "Calidad": cal,
                "Valor": eps_use * mult,
                "Supuestos": (
                    f"A {mult}x P/E is applied to EPS of {eps_use:.2f}."
                    if st.session_state.lang == "en"
                    else f"Se aplica un PER de {mult}x sobre el BPA de {eps_use:.2f}."
                ),
            })

    if revenue is not None and shares and shares > 0:
        for mult, cal in [(1, calidad_high), (2, calidad_high), (4, calidad_medium), (6, calidad_medium), (8, calidad_low)]:
            methods.append({
                "Método": f"P/Sales {mult}x" if st.session_state.lang == "en" else f"P/Ventas {mult}x",
                "Tipo": "Multiple" if st.session_state.lang == "en" else "Múltiplo",
                "Calidad": cal,
                "Valor": revenue * mult / shares,
                "Supuestos": (
                    f"{mult}x is applied to total revenue of {fmt_large(revenue)} and divided by shares outstanding."
                    if st.session_state.lang == "en"
                    else f"Se aplica {mult}x sobre ventas totales de {fmt_large(revenue)} y se divide por acciones."
                ),
            })

    if bvps and bvps > 0:
        for mult, cal in [(1, calidad_high), (1.5, calidad_high), (2, calidad_medium), (3, calidad_medium), (4, calidad_low)]:
            methods.append({
                "Método": f"P/Book {mult}x" if st.session_state.lang == "en" else f"P/Valor contable {mult}x",
                "Tipo": "Multiple" if st.session_state.lang == "en" else "Múltiplo",
                "Calidad": cal,
                "Valor": bvps * mult,
                "Supuestos": (
                    f"{mult}x is applied to book value per share of {bvps:.2f}."
                    if st.session_state.lang == "en"
                    else f"Se aplica {mult}x sobre el valor contable por acción de {bvps:.2f}."
                ),
            })

    if eps_use and eps_use > 0 and bvps and bvps > 0:
        graham = math.sqrt(22.5 * eps_use * bvps)
        methods.append({
            "Método": "Graham Number" if st.session_state.lang == "en" else "Número de Graham",
            "Tipo": "Hybrid" if st.session_state.lang == "en" else "Mixto",
            "Calidad": calidad_high,
            "Valor": graham,
            "Supuestos": (
                f"Calculated as sqrt(22.5 × EPS {eps_use:.2f} × BVPS {bvps:.2f})."
                if st.session_state.lang == "en"
                else f"Se calcula como raíz de 22.5 × BPA ({eps_use:.2f}) × valor contable por acción ({bvps:.2f})."
            ),
        })
        graham_adj = math.sqrt(15 * eps_use * bvps)
        methods.append({
            "Método": "Adjusted Graham" if st.session_state.lang == "en" else "Graham ajustado",
            "Tipo": "Hybrid" if st.session_state.lang == "en" else "Mixto",
            "Calidad": calidad_medium,
            "Valor": graham_adj,
            "Supuestos": (
                f"Calculated as sqrt(15 × EPS {eps_use:.2f} × BVPS {bvps:.2f})."
                if st.session_state.lang == "en"
                else f"Se calcula como raíz de 15 × BPA ({eps_use:.2f}) × valor contable por acción ({bvps:.2f})."
            ),
        })

    if div and div > 0:
        ddm_labels = [
            (0.02, 0.08, "DDM g 2%, r 8%"),
            (0.03, 0.09, "DDM g 3%, r 9%"),
            (0.05, 0.10, "DDM g 5%, r 10%"),
        ]
        for g_div, r_div, label_div in ddm_labels:
            if r_div > g_div:
                val_ddm = div * (1 + g_div) / (r_div - g_div)
                methods.append({
                    "Método": label_div,
                    "Tipo": "DDM",
                    "Calidad": calidad_medium,
                    "Valor": val_ddm,
                    "Supuestos": (
                        f"Gordon Growth model with dividend {div:.2f}, growth {g_div*100:.0f}% and discount rate {r_div*100:.0f}%."
                        if st.session_state.lang == "en"
                        else f"Modelo Gordon-Shapiro con dividendo {div:.2f}, crecimiento {g_div*100:.0f}% y descuento {r_div*100:.0f}%."
                    ),
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

# =========================
# BUSCADOR
# =========================
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
# DATOS
# =========================
with st.spinner(f"{tr('loading_data')} {active_ticker}..."):
    try:
        stock = yf.Ticker(active_ticker)
        info = stock.info
        hist = stock.history(period=period)
    except Exception as e:
        st.error(f"{tr('data_error')}: {e}")
        st.stop()

price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
if price is None:
    st.error(tr("price_error"))
    st.stop()

company_name = info.get("longName") or info.get("shortName") or active_ticker
sector = info.get("sector", "N/A" if st.session_state.lang == "en" else "N/D")
industry = info.get("industry", "N/A" if st.session_state.lang == "en" else "N/D")
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
tab_emp, tab_rat, tab_val, tab_bench, tab_corr, tab_price, tab_port, tab_news = st.tabs(
    [
        tr("company"),
        tr("ratios"),
        tr("valuation"),
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
            (tr("country"), info.get("country", "N/A" if st.session_state.lang == "en" else "N/D")),
            (tr("city"), info.get("city", "N/A" if st.session_state.lang == "en" else "N/D")),
            (tr("exchange"), info.get("exchange", "N/A" if st.session_state.lang == "en" else "N/D")),
            (tr("employees"), f"{employees:,}" if employees else ("N/A" if st.session_state.lang == "en" else "N/D")),
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

    st.markdown("---")
    st.markdown(f"**{tr('financial_profile')}**")

    def norm(v, lo, hi):
        v2 = safe_float(v, None)
        if v2 is None:
            return 0.0
        return max(0.0, min(1.0, (v2 - lo) / (hi - lo)))

    radar_labels = [
        tr("roe"),
        tr("roa"),
        tr("net_margin"),
        tr("trailing_pe"),
        tr("debt_equity"),
        tr("current_ratio"),
    ]
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
            line_color=ACCENT_BLUE,
            fillcolor="rgba(56,189,248,0.3)",
        )
    )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ==== VALORACIÓN ====
with tab_val:
    st.subheader(tr("intrinsic_valuation"))
    methods, current_price = compute_valuations(info, currency)

    if not methods:
        st.warning(tr("insufficient_valuation_data"))
    else:
        df_val = pd.DataFrame(methods)
        df_val["Interpretación"] = df_val["Upside %"].apply(interpretar_upside)
        df_val["Score"] = df_val.apply(lambda row: score_method(row["Upside %"], row["Calidad"]), axis=1)

        def flag_icon(u):
            if pd.isna(u):
                return "⚪"
            if u >= 20:
                return "🟢"
            if u >= -10:
                return "🟡"
            return "🔴"

        df_tabla = pd.DataFrame({
            "Method" if st.session_state.lang == "en" else "Método": df_val["Método"],
            "Type" if st.session_state.lang == "en" else "Tipo": df_val["Tipo"],
            "Score": df_val["Score"],
            "Flag": df_val["Upside %"].apply(flag_icon),
            "Upside (%)": df_val["Upside %"].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else ("N/A" if st.session_state.lang == "en" else "N/D")),
            tr("intrinsic_value"): df_val["Valor"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else ("N/A" if st.session_state.lang == "en" else "N/D")),
            tr("current_price"): df_val["Precio"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else ("N/A" if st.session_state.lang == "en" else "N/D")),
            tr("quality"): df_val["Calidad"],
            tr("interpretation"): df_val["Interpretación"],
        }).reindex(df_val.sort_values("Upside %", ascending=False).index)

        st.dataframe(df_tabla, use_container_width=True, hide_index=True)

        st.markdown("---")

        upsides = df_val["Upside %"].dropna()
        m1, m2, m3, m4 = st.columns(4)
        for col, label, val in [
            (m1, tr("methods_calculated"), str(len(df_val))),
            (m2, tr("median_upside"), f"{upsides.median():+.1f}%" if len(upsides) else ("N/A" if st.session_state.lang == "en" else "N/D")),
            (m3, tr("mean_upside"), f"{upsides.mean():+.1f}%" if len(upsides) else ("N/A" if st.session_state.lang == "en" else "N/D")),
            (m4, tr("upside_range"), f"{upsides.min():+.1f}% / {upsides.max():+.1f}%" if len(upsides) else ("N/A" if st.session_state.lang == "en" else "N/D")),
        ]:
            with col:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">{label}</div>'
                    f'<div class="metric-value">{val}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        tipo_dcf = "DCF"
        tipo_multiple = "Multiple" if st.session_state.lang == "en" else "Múltiplo"
        tipo_hybrid = "Hybrid" if st.session_state.lang == "en" else "Mixto"
        tipo_ddm = "DDM"

        fig_val = px.strip(
            df_val,
            x="Upside %",
            y="Tipo",
            color="Tipo",
            hover_data=["Método", "Valor", "Supuestos"],
            title="Upside distribution by method type" if st.session_state.lang == "en" else "Distribución de upside por tipo de método",
            color_discrete_map={
                tipo_dcf: "#38BDF8",
                tipo_multiple: "#A78BFA",
                tipo_hybrid: "#FB923C",
                tipo_ddm: "#34D399",
            },
        )
        fig_val.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.4)
        fig_val.add_vline(
            x=30,
            line_dash="dot",
            line_color="#22C55E",
            opacity=0.5,
            annotation_text="30% margin of safety" if st.session_state.lang == "en" else "Margen seg. 30%",
        )
        fig_val.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
            xaxis_title="Upside vs current price (%)" if st.session_state.lang == "en" else "Upside vs precio actual (%)",
        )
        st.plotly_chart(fig_val, use_container_width=True)

        fig_bar = px.bar(
            df_val.sort_values("Valor"),
            x="Valor",
            y="Método",
            color="Tipo",
            orientation="h",
            title=(
                f"Intrinsic value by method vs current price ({current_price:.2f} {currency})"
                if st.session_state.lang == "en"
                else f"Valor intrínseco por método vs precio actual ({current_price:.2f} {currency})"
            ),
            color_discrete_map={
                tipo_dcf: "#38BDF8",
                tipo_multiple: "#A78BFA",
                tipo_hybrid: "#FB923C",
                tipo_ddm: "#34D399",
            },
        )
        fig_bar.add_vline(
            x=current_price,
            line_dash="dash",
            line_color="#EF4444",
            annotation_text=f"Price: {current_price:.2f}" if st.session_state.lang == "en" else f"Precio: {current_price:.2f}",
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=max(400, len(df_val) * 22),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown(f"### {tr('how_calculated')}")
        for _, row in df_val.sort_values("Upside %", ascending=False).iterrows():
            with st.expander(f"{row['Método']} · {row['Tipo']} · {fmt_num(row['Upside %'], 1, '%')}"):
                st.write(f"**{tr('quality')}:** {row['Calidad']}")
                st.write(f"**{tr('intrinsic_value')}:** {fmt_num(row['Valor'])} {currency}")
                st.write(f"**{tr('current_price')}:** {fmt_num(row['Precio'])} {currency}")
                st.write(f"**{tr('interpretation')}:** {row['Interpretación']}")
                st.write(f"**{tr('calculation')}:** {row['Supuestos']}")

# ==== BENCHMARKS ====
with tab_bench:
    st.subheader(tr("sector_benchmarks"))
    peers = get_benchmark_list(info, active_ticker)
    if not peers:
        st.info(tr("no_benchmarks"))
    else:
        tickers_all = [active_ticker] + peers
        with st.spinner("Downloading benchmarks..." if st.session_state.lang == "en" else "Descargando benchmarks..."):
            data = {}
            for t in tickers_all:
                try:
                    tk = yf.Ticker(t)
                    inf = tk.info
                    data[t] = {
                        "Nombre": inf.get("shortName", t),
                        "PER": safe_float(inf.get("trailingPE")),
                        "P/VC": safe_float(inf.get("priceToBook")),
                        "ROE": safe_float(inf.get("returnOnEquity")),
                        "Margen neto": safe_float(inf.get("profitMargins")),
                        "Precio": safe_float(inf.get("currentPrice")) or safe_float(inf.get("regularMarketPrice")),
                        "Capitalización": safe_float(inf.get("marketCap")),
                    }
                except Exception:
                    continue

        if len(data) <= 1:
            st.warning(tr("benchmarks_error"))
        else:
            df_bench = pd.DataFrame.from_dict(data, orient="index").reset_index().rename(columns={"index": "Ticker"})
            df_view = pd.DataFrame({
                "Ticker": df_bench["Ticker"],
                "Name" if st.session_state.lang == "en" else "Nombre": df_bench["Nombre"],
                tr("current_price"): df_bench["Precio"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else ("N/A" if st.session_state.lang == "en" else "N/D")),
                tr("trailing_pe"): df_bench["PER"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else ("N/A" if st.session_state.lang == "en" else "N/D")),
                tr("pb"): df_bench["P/VC"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else ("N/A" if st.session_state.lang == "en" else "N/D")),
                tr("roe"): df_bench["ROE"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else ("N/A" if st.session_state.lang == "en" else "N/D")),
                tr("net_margin"): df_bench["Margen neto"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else ("N/A" if st.session_state.lang == "en" else "N/D")),
                tr("market_cap"): df_bench["Capitalización"].apply(fmt_large),
            }).reindex(df_bench.sort_values("Capitalización", ascending=False).index)

            st.dataframe(df_view, use_container_width=True, hide_index=True)
            st.markdown("---")

            fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comp.add_trace(
                go.Bar(x=df_bench["Ticker"], y=df_bench["PER"], name=tr("trailing_pe"), marker_color=ACCENT_BLUE),
                secondary_y=False,
            )
            fig_comp.add_trace(
                go.Scatter(
                    x=df_bench["Ticker"],
                    y=df_bench["ROE"] * 100,
                    name=f"{tr('roe')} (%)",
                    mode="lines+markers",
                    line_color=ACCENT_GREEN,
                ),
                secondary_y=True,
            )
            fig_comp.update_yaxes(title_text=tr("trailing_pe"), secondary_y=False)
            fig_comp.update_yaxes(title_text=f"{tr('roe')} (%)", secondary_y=True)
            fig_comp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400,
            )
            st.plotly_chart(fig_comp, use_container_width=True)

# ==== CORRELACIONES ====
with tab_corr:
    st.subheader(tr("correlation_returns"))
    corr_tickers = [t.strip().upper() for t in corr_tickers_input.replace(",", "\n").split("\n") if t.strip()]
    if active_ticker not in corr_tickers:
        corr_tickers.insert(0, active_ticker)

    with st.spinner("Downloading historical prices..." if st.session_state.lang == "en" else "Descargando precios históricos..."):
        try:
            df_download = yf.download(corr_tickers, period=period, auto_adjust=True, progress=False)
            if isinstance(df_download.columns, pd.MultiIndex):
                prices = df_download.xs("Close", level=0, axis=1, drop_level=True)
            else:
                if len(corr_tickers) == 1:
                    prices = df_download["Close"].to_frame(name=corr_tickers[0])
                else:
                    prices = df_download["Close"]
            returns = prices.pct_change().dropna()
        except Exception as e:
            st.error(f"{'Could not download prices' if st.session_state.lang == 'en' else 'No se pudieron descargar precios'}: {e}")
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

        st.markdown(f"#### {tr('cumulative_returns')}")
        cum = (1 + returns).cumprod()
        fig_cum = px.line(cum, labels={"value": tr("cumulative_returns"), "index": "Date" if st.session_state.lang == "en" else "Fecha"})
        fig_cum.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )
        st.plotly_chart(fig_cum, use_container_width=True)

# ==== PRECIO ====
with tab_price:
    st.subheader(tr("historical_price_volume"))
    if hist is None or hist.empty:
        st.warning(tr("no_historical_data"))
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
                name=tr("ohlc")
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
                "Asset" if st.session_state.lang == "en" else "Activo": corr_tickers,
                "Optimal weight (%)" if st.session_state.lang == "en" else "Ponderación óptima (%)": [f"{w*100:.2f}%" for w in pesos_optimos],
                "Decimal fraction" if st.session_state.lang == "en" else "Fracción decimal": np.round(pesos_optimos, 4),
            }).sort_values(
                by="Decimal fraction" if st.session_state.lang == "en" else "Fracción decimal",
                ascending=False
            )

            st.dataframe(df_pesos, use_container_width=True, hide_index=True)

            weight_col = "Decimal fraction" if st.session_state.lang == "en" else "Fracción decimal"
            asset_col = "Asset" if st.session_state.lang == "en" else "Activo"

            fig_pie = px.pie(
                df_pesos[df_pesos[weight_col] > 0.001],
                values=weight_col,
                names=asset_col,
                title=(
                    f"Recommended capital allocation ({objetivo})"
                    if st.session_state.lang == "en"
                    else f"Distribución recomendada de capital ({objetivo})"
                ),
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
                    descripcion = art.get("description") or art.get("content") or ("No summary available." if st.session_state.lang == "en" else "Sin resumen disponible.")
                    descripcion = traducir_texto(descripcion)
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
                    descripcion = art.get("description") or art.get("content") or ("No summary available." if st.session_state.lang == "en" else "Sin resumen disponible.")
                    descripcion = traducir_texto(descripcion)
                    url = art.get("url")

                    with st.expander(f"{titulo} · {fuente} · {fecha}"):
                        st.write(descripcion)
                        if url:
                            st.markdown(f"[{tr('read_more')}]({url})")
