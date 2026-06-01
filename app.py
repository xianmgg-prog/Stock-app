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

# ============== CONFIGURACIÓN DE PÁGINA ==============
st.set_page_config(
    page_title="Equity Terminal — Value Investing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============== SESSION STATE ========================
if "analyzed_ticker" not in st.session_state:
    st.session_state.analyzed_ticker = None
if "current_query" not in st.session_state:
    st.session_state.current_query = ""
if "language" not in st.session_state:
    st.session_state.language = "ES"

# ============== PALETA CHAMPAGNE =====================
ACCENT_GOLD      = "#B68A52"
ACCENT_GOLD_SOFT = "#D6B98C"
ACCENT_GREEN     = "#5E8B6F"
ACCENT_RED       = "#B85C5C"
BG_MAIN          = "#F7F1E8"
BG_GRAD_1        = "#F3E7D7"
BG_GRAD_2        = "#EADBC8"
CARD_BG          = "#FFFDF9"
CARD_BG_2        = "#F9F4EC"
BORDER           = "#D9C8B4"
TEXT_PRIMARY     = "#2F241B"
TEXT_SECONDARY   = "#7A6856"
TABLE_HEADER_BG  = "#EFE2D2"
TABLE_ROW_BG     = "#FFFDF9"
TABLE_ALT_BG     = "#FAF5EE"
TABLE_BORDER     = "#D8C7B2"
CHART_COLORS     = ["#B68A52", "#8C6A43", "#5E8B6F", "#A47E5B", "#C2A27B"]

# ============== TEXTOS MULTIIDIOMA ==================
TEXTS = {
    "ES": {
        "hero_title": "Equity Terminal",
        "hero_sub": "Value Investing · Análisis fundamental de empresas cotizadas",
        "search_placeholder": "🔎 Busca una empresa o ticker (ej: AAPL, MSFT, TEF.MC...)",
        "analyze": "Analizar →",
        "suggestions": "Sugerencias",
        "options": "⚙️ Opciones de análisis",
        "period": "Período histórico",
        "corr_input": "Tickers para correlación y cartera (separados por comas)",
        "welcome_1": "Introduce el nombre o ticker de una empresa y pulsa Analizar →",
        "welcome_2": "Ejemplos: AAPL · MSFT · TEF.MC · SAN.MC · ITX.MC",
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
        "methods": "Métodos",
        "median_up": "Upside mediano",
        "mean_up": "Upside medio",
        "range": "Rango",
    },
    "EN": {
        "hero_title": "Equity Terminal",
        "hero_sub": "Value Investing · Fundamental analysis of listed companies",
        "search_placeholder": "🔎 Search a company or ticker (e.g. AAPL, MSFT, TEF.MC...)",
        "analyze": "Analyze →",
        "suggestions": "Suggestions",
        "options": "⚙️ Analysis options",
        "period": "Historical period",
        "corr_input": "Tickers for correlation and portfolio (comma separated)",
        "welcome_1": "Enter a company name or ticker and press Analyze →",
        "welcome_2": "Examples: AAPL · MSFT · TEF.MC · SAN.MC · ITX.MC",
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
        "methods": "Methods",
        "median_up": "Median upside",
        "mean_up": "Mean upside",
        "range": "Range",
    },
}

# ============== CSS GLOBAL ===========================
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

# ============== HELPERS ==============================
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
    return tr_text(text, "en") if st.session_state.language == "EN" else text

def safe_float(x, default=None):
    if x is None:
        return default
    try:
        if isinstance(x, str) and x.strip() == "":
            return default
        v = float(x)
        return default if (math.isnan(v) or math.isinf(v)) else v
    except Exception:
        return default

def fmt_num(x, decimals=2, suffix=""):
    v = safe_float(x, None)
    return "N/A" if v is None else f"{v:.{decimals}f}{suffix}"

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

def render_champagne_table(df: pd.DataFrame, pills_cols=None, html_cols=None):
    pills_cols = pills_cols or []
    html_cols  = html_cols  or []
    def pill_class(val):
        v = str(val).lower()
        if any(x in v for x in ["alta","high","infraval","underval","buy"]):
            return "pill pill-green"
        if any(x in v for x in ["baja","low","sobreval","overval","sell"]):
            return "pill pill-red"
        return "pill pill-gold"
    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col in df.columns:
            val = row[col]
            display = "N/A" if pd.isna(val) else str(val)
            if col in html_cols:
                cells += f"<td>{display}</td>"
            elif col in pills_cols:
                cells += f'<td><span class="{pill_class(display)}">{display}</span></td>'
            else:
                cells += f"<td>{display}</td>"
        rows_html += f"<tr>{cells}</tr>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    st.markdown(
        f"""
        <div class="champ-table-wrap fade-container">
          <table class="champ-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

def search_ticker(query: str):
    if not query:
        return []
    try:
        url  = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=US&quotesCount=8&newsCount=0"
        r    = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        data = r.json()
        return [
            f"{q.get('symbol','')} — {(q.get('longname') or q.get('shortname',''))} ({q.get('exchDisp','')})"
            for q in data.get("quotes", [])
            if q.get("quoteType") in ("EQUITY","ETF")
        ]
    except Exception:
        return []

DEFAULT_BENCHMARKS = {
    "Technology":             ["AAPL","MSFT","GOOGL","META","AMZN"],
    "Communication Services": ["GOOGL","META","NFLX","DIS"],
    "Financial Services":     ["JPM","BAC","C","GS"],
    "Consumer Cyclical":      ["AMZN","TSLA","HD","MCD"],
    "Energy":                 ["XOM","CVX","BP","TTE"],
}

def get_benchmark_list(info, main_ticker):
    peers = DEFAULT_BENCHMARKS.get(info.get("sector"), [])
    return [p for p in peers if p.upper() != main_ticker.upper()][:4]

def format_financial_df(df):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return None
    out = df.copy()
    if out.shape[1] > 6:
        out = out.iloc[:, :6]
    new_cols = []
    for c in out.columns:
        if hasattr(c, "date"):
            new_cols.append(str(c.date()))
        else:
            s = str(c)
            new_cols.append(s[:10])
    out.columns = new_cols
    def _fmt_cell(x):
        if pd.isna(x):
            return "N/A"
        if isinstance(x, (int,float,np.number)):
            return fmt_large(x)
        if isinstance(x,str):
            try:
                v = float(x)
                return fmt_large(v)
            except Exception:
                return x
        return str(x)
    try:
        out = out.applymap(_fmt_cell)
    except AttributeError:
        return None
    out = out.reset_index()
    out.rename(columns={"index": "Concepto" if lang=="ES" else "Item"}, inplace=True)
    return out

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
    cal_map    = {"Alta":"High","Media":"Medium","Baja":"Low"}
    def add(label,tipo,cal,valor,usado,detalle):
        methods.append({
            "Método": label,
            "Tipo": tipo,
            "Calidad": cal if lang=="ES" else cal_map.get(cal,cal),
            "Valor": valor,
            "Qué se usó": usado,
            "Detalle": detalle,
        })
    def dcf(fcf0,g_high,g_low,r,label,cal,origen):
        if not (fcf0 and shares and shares>0 and r>g_low): return
        pv  = sum(fcf0*(1+g_high)**t/(1+r)**t for t in range(1,6))
        pv += sum(fcf0*(1+g_high)**5*(1+g_low)**(t-5)/(1+r)**t for t in range(6,11))
        tv  = fcf0*(1+g_high)**5*(1+g_low)**5*(1+g_low)/(r-g_low)
        va  = (pv + tv/(1+r)**10 + cash - total_debt) / shares
        add(label,"DCF",cal,va, f"{origen} g={int(g_high*100)}%→{int(g_low*100)}% r={int(r*100)}%", f"{origen} {fmt_large(fcf0)}")
    if fcf:
        dcf(fcf,0.15,0.04,0.11,"DCF Agresivo" if lang=="ES" else "Aggressive DCF","Media","FCF")
        dcf(fcf,0.10,0.03,0.10,"DCF Base"     if lang=="ES" else "Base DCF","Alta","FCF")
        dcf(fcf,0.06,0.02,0.09,"DCF Conservador" if lang=="ES" else "Conservative DCF","Alta","FCF")
    if net_income and shares and shares>0:
        dcf(net_income,0.08,0.03,0.10,"DCF (Bº neto)" if lang=="ES" else "DCF (Net income)","Media","Bº neto")
    mult_tipo = "Múltiplo" if lang=="ES" else "Multiple"
    if ebitda and ebitda>0 and shares and shares>0:
        for m,c in [(8,"Alta"),(10,"Alta"),(12,"Media"),(15,"Media"),(20,"Baja")]:
            add(f"EV/EBITDA {m}×",mult_tipo,c,(ebitda*m+cash-total_debt)/shares,f"EBITDA×{m}",f"EBITDA {fmt_large(ebitda)}")
    if ebit and ebit>0 and shares and shares>0:
        for m,c in [(10,"Alta"),(14,"Media"),(18,"Baja")]:
            add(f"EV/EBIT {m}×",mult_tipo,c,(ebit*m+cash-total_debt)/shares,f"EBIT×{m}",f"EBIT {fmt_large(ebit)}")
    eps_use = eps if (eps and eps>0) else fwd_eps
    eps_lbl = ("BPA histórico" if lang=="ES" else "Historical EPS") if (eps and eps>0) else ("BPA estimado" if lang=="ES" else "Forward EPS")
    if eps_use and eps_use>0:
        for m,c in [(10,"Alta"),(15,"Alta"),(20,"Media"),(25,"Media"),(30,"Baja")]:
            add(f"P/E {m}×",mult_tipo,c,eps_use*m,f"{eps_lbl}×{m}",f"{eps_lbl} {round(eps_use,2)}")
    if revenue and shares and shares>0:
        lbl = "P/Ventas " if lang=="ES" else "P/Sales "
        for m,c in [(1,"Alta"),(2,"Alta"),(4,"Media"),(6,"Media"),(8,"Baja")]:
            add(f"{lbl}{m}×",mult_tipo,c,revenue*m/shares,f"Ventas×{m}",f"Ventas {fmt_large(revenue)}")
    if bvps and bvps>0:
        for m,c in [(1,"Alta"),(1.5,"Alta"),(2,"Media"),(3,"Media"),(4,"Baja")]:
            add(f"P/Book {m}×",mult_tipo,c,bvps*m,f"BVPS×{m}",f"BVPS {round(bvps,2)}")
    hybrid = "Mixto" if lang=="ES" else "Hybrid"
    if eps_use and eps_use>0 and bvps and bvps>0:
        add("Graham Number",hybrid,"Alta",math.sqrt(22.5*eps_use*bvps),"√(22.5×EPS×BVPS)",f"√(22.5×{round(eps_use,2)}×{round(bvps,2)})")
        add("Graham Ajustado (15×)" if lang=="ES" else "Adjusted Graham (15×)",hybrid,"Media",
            math.sqrt(15*eps_use*bvps),"√(15×EPS×BVPS)",f"√(15×{round(eps_use,2)}×{round(bvps,2)})")
    if div and div>0:
        for g,r,lbl in [(0.02,0.08,"DDM (g2% r8%)"),(0.03,0.09,"DDM (g3% r9%)"),(0.05,0.10,"DDM (g5% r10%)")]:
            if r>g:
                add(lbl,"DDM","Media",div*(1+g)/(r-g),"Div×(1+g)÷(r−g)",f"Div={round(div,2)} g={int(g*100)}% r={int(r*100)}%")
    for m in methods:
        m["Precio"]   = price
        m["Upside %"] = round((m["Valor"]-price)/price*100,1) if price and price>0 else None
    return methods, price

# ============== HEADER + LANGUAGE ====================
top1, top2 = st.columns([5,1])
with top2:
    st.selectbox(TEXTS[st.session_state.language]["language"], options=["ES","EN"], key="language")
lang = st.session_state.language
T    = TEXTS[lang]
st.markdown(
    f"""
    <div class="hero-wrap fade-container">
      <div class="hero-title">{T['hero_title']}</div>
      <div class="hero-sub">{T['hero_sub']}</div>
    </div>
    <div class="soft-divider"></div>
    """,
    unsafe_allow_html=True,
)

# ============== BÚSQUEDA =============================
col_search, col_btn = st.columns([4,1])
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
    op1, op2 = st.columns([1,2])
    with op1:
        period = st.selectbox(T["period"], ["1y","3y","5y","10y"], index=1, key="period_select")
    with op2:
        corr_tickers_input = st.text_input(T["corr_input"], value="AAPL, MSFT, GOOGL, AMZN, META", key="corr_input_box")
period             = st.session_state.get("period_select","3y")
corr_tickers_input = st.session_state.get("corr_input_box","AAPL, MSFT, GOOGL, AMZN, META")

# ============== WELCOME ==============================
if not st.session_state.analyzed_ticker:
    st.markdown("---")
    st.markdown(
        f"""
        <div class="fade-container" style="text-align:center;color:{TEXT_SECONDARY};padding:3rem 0;">
          <div style="font-size:3rem;">🏦</div>
          <div style="font-size:1.1rem;margin-top:0.5rem;">{T['welcome_1']}</div>
          <div style="font-size:0.85rem;margin-top:0.5rem;">{T['welcome_2']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

active_ticker = st.session_state.analyzed_ticker

# ============== DATA =================================
with st.spinner(f"{T['loading']} {active_ticker}..."):
    try:
        stock         = yf.Ticker(active_ticker)
        info          = stock.info
        hist          = stock.history(period=period)
        financials    = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow      = stock.cashflow
    except Exception as e:
        st.error("Error: " + str(e))
        st.stop()
price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
if price is None:
    st.error(T["price_error"])
    st.stop()
company_name = info.get("longName") or info.get("shortName") or active_ticker
sector       = info.get("sector","N/A")
industry     = info.get("industry","N/A")
currency     = info.get("currency","USD")
prev_close   = safe_float(info.get("previousClose"))
if price and prev_close:
    chg     = price - prev_close
    chg_pct = chg/prev_close*100
    color   = ACCENT_GREEN if chg>=0 else ACCENT_RED
    delta   = f'<span style="color:{color};font-size:1.05rem;">{chg:+.2f} ({chg_pct:+.2f}%)</span>'
else:
    delta = ""
st.markdown(
    f"""
    <div class="company-header fade-container">
      <div class="company-name">{company_name}</div>
      <div class="company-meta">{active_ticker} · {sector} · {industry} · {currency}</div>
      <div class="company-price">{price:.2f} {currency} {delta}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
k1,k2,k3,k4 = st.columns(4)
with k1: st.metric(T["market_cap"], fmt_large(info.get("marketCap")))
with k2: st.metric(T["high_52"],    f"{fmt_num(info.get('fiftyTwoWeekHigh'))} {currency}")
with k3: st.metric(T["low_52"],     f"{fmt_num(info.get('fiftyTwoWeekLow'))} {currency}")
with k4: st.metric(T["beta"],       fmt_num(info.get("beta")))
returns = None

# ============== TABS =================================
tab_emp, tab_rat, tab_val, tab_bench, tab_corr, tab_price, tab_port, tab_fin = st.tabs([
    T["company"], T["ratios"], T["valuation"], T["benchmarks"],
    T["correlations"], T["price"], T["portfolio"], T["financials"]
])

# --- Empresa ---
with tab_emp:
    c1,c2 = st.columns([2,1])
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

# --- Ratios ---
with tab_rat:
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
    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown("**" + T["market_val"] + "**")
        st.write("P/E (TTM): **" + fmt_num(pe) + "**")
        st.write("P/E (Fwd): **" + fmt_num(fwd_pe) + "**")
        st.write("P/B: **" + fmt_num(pb) + "**")
        st.write("P/S: **" + fmt_num(ps) + "**")
    with col2:
        st.markdown("**" + T["profitability"] + "**")
        st.write("ROE: **" + fmt_num(roe*100 if roe else None,1,"%") + "**")
        st.write("ROA: **" + fmt_num(roa*100 if roa else None,1,"%") + "**")
        st.write(("Margen bruto" if lang=="ES" else "Gross margin") + ": **" + fmt_num(gross_margin*100 if gross_margin else None,1,"%") + "**")
        st.write(("Margen neto" if lang=="ES" else "Net margin") + ": **" + fmt_num(profit_margin*100 if profit_margin else None,1,"%") + "**")
    with col3:
        st.markdown("**" + T["risk_liq"] + "**")
        st.write(("Deuda/Equity" if lang=="ES" else "Debt/Equity") + ": **" + fmt_num(debt_equity) + "**")
        st.write("Current ratio: **" + fmt_num(current_ratio) + "**")
        st.write("Quick ratio: **" + fmt_num(quick_ratio) + "**")
        st.write("Dividend yield: **" + fmt_num(dividend_yield*100 if dividend_yield else None,2,"%") + "**")

# --- Valoración ---
with tab_val:
    st.subheader(T["intrinsic_title"])
    methods, current_price = compute_valuations(info,currency)
    if not methods:
        st.warning(T["valuation_warn"])
    else:
        df_val = pd.DataFrame(methods)
        def rango_upside(u):
            if pd.isna(u): return "N/A"
            if lang=="ES":
                if u>=40:  return "Muy infravalorado"
                if u>=20:  return "Infravalorado"
                if u>=-10: return "En línea"
                if u>=-30: return "Sobrevalorado"
                return "Muy sobrevalorado"
            else:
                if u>=40:  return "Deeply undervalued"
                if u>=20:  return "Undervalued"
                if u>=-10: return "Fairly valued"
                if u>=-30: return "Overvalued"
                return "Deeply overvalued"
        df_val["Interpretación"] = df_val["Upside %"].apply(rango_upside)
        def score_row(row):
            u,cal = row["Upside %"], row["Calidad"]
            base = 2
            if pd.notna(u):
                if u>=40: base=5
                elif u>=20: base=4
                elif u>=0: base=3
                elif u>=-20: base=2
                else: base=1
            if cal in ["Alta","High"]: base=min(base+1,5)
            elif cal in ["Baja","Low"]: base=max(base-1,1)
            return "★"*base + "☆"*(5-base)
        df_val["Score"] = df_val.apply(score_row,axis=1)
        df_sorted = df_val.sort_values("Upside %",ascending=False)
        df_tabla = pd.DataFrame({
            "Método" if lang=="ES" else "Method": df_sorted["Método"],
            T["type"]: df_sorted["Tipo"],
            T["score"]: df_sorted["Score"],
            "Upside (%)": df_sorted["Upside %"].apply(lambda u: f"{u:+.1f}%" if pd.notna(u) else "N/A"),
            T["intrinsic_value"]: df_sorted["Valor"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            T["current_price"]: df_sorted["Precio"].apply(lambda v: f"{v:.2f}" if pd.notna(v) else "N/A"),
            T["quality"]: df_sorted["Calidad"],
            T["interpretation"]: df_sorted["Interpretación"],
            T["used"]: df_sorted["Qué se usó"],
        })
        render_champagne_table(df_tabla, pills_cols=[T["quality"],T["interpretation"]])

# --- Benchmarks ---
with tab_bench:
    st.subheader(T["bench_title"])
    peers = get_benchmark_list(info,active_ticker)
    if not peers:
        st.info(T["bench_none"])
    else:
        data_bench = {}
        for t in [active_ticker]+peers:
            try:
                inf = yf.Ticker(t).info
                data_bench[t] = {
                    "Name": inf.get("shortName",t),
                    "P/E":  safe_float(inf.get("trailingPE")),
                    "P/B":  safe_float(inf.get("priceToBook")),
                    "ROE":  safe_float(inf.get("returnOnEquity")),
                    "Net Margin": safe_float(inf.get("profitMargins")),
                    "Price": safe_float(inf.get("currentPrice")) or safe_float(inf.get("regularMarketPrice")),
                    "Market Cap": safe_float(inf.get("marketCap")),
                }
            except Exception:
                continue
        if len(data_bench)<=1:
            st.warning(T["bench_warn"])
        else:
            df_b = pd.DataFrame.from_dict(data_bench,orient="index").reset_index().rename(columns={"index":"Ticker"})
            render_champagne_table(pd.DataFrame({
                "Ticker": df_b["Ticker"],
                "Nombre" if lang=="ES" else "Name": df_b["Name"],
                "Precio" if lang=="ES" else "Price": df_b["Price"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"),
                "P/E": df_b["P/E"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"),
                "P/B": df_b["P/B"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"),
                "ROE": df_b["ROE"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A"),
                "Margen neto" if lang=="ES" else "Net Margin": df_b["Net Margin"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A"),
                "Market Cap": df_b["Market Cap"].apply(fmt_large),
            }))

# --- Correlaciones ---
with tab_corr:
    st.subheader(T["corr_title"])
    corr_tickers = [t.strip().upper() for t in corr_tickers_input.replace(",","\n").split("\n") if t.strip()]
    if active_ticker not in corr_tickers:
        corr_tickers.insert(0,active_ticker)
    try:
        df_dl = yf.download(corr_tickers, period=period, auto_adjust=True, progress=False)
        prices = df_dl.xs("Close",level=0,axis=1,drop_level=True) if isinstance(df_dl.columns,pd.MultiIndex) else df_dl["Close"].to_frame(name=corr_tickers[0])
        returns = prices.pct_change().dropna()
    except Exception as e:
        st.error("Error: " + str(e))
        returns = None
    if returns is not None and not returns.empty:
        st.markdown("#### " + T["corr_matrix"])
        fig_c = px.imshow(returns.corr(), text_auto=".2f",
                          color_continuous_scale=["#B85C5C","#FFF8F0","#5E8B6F"], zmin=-1, zmax=1)
        st.plotly_chart(fig_c, use_container_width=True)
        st.markdown("#### " + T["cum_returns"])
        fig_cr = px.line((1+returns).cumprod(), color_discrete_sequence=CHART_COLORS)
        st.plotly_chart(fig_cr, use_container_width=True)

# --- Precio ---
with tab_price:
    st.subheader(T["price_hist"])
    if hist is None or hist.empty:
        st.warning(T["price_hist_warn"])
    else:
        fig_p = make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=0.03,row_heights=[0.7,0.3])
        fig_p.add_trace(go.Candlestick(x=hist.index, open=hist["Open"], high=hist["High"],
                                       low=hist["Low"], close=hist["Close"], name="OHLC"),
                        row=1,col=1)
        fig_p.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume", marker_color=ACCENT_GOLD),
                        row=2,col=1)
        fig_p.update_layout(height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_p, use_container_width=True)

# --- Portfolio ---
with tab_port:
    st.subheader(T["portfolio_title"])
    if returns is not None and not returns.empty:
        st.markdown(T["portfolio_cfg"])
        c1,c2 = st.columns(2)
        with c1: objetivo = st.selectbox(T["optimizer_goal"], [T["goal_sharpe"],T["goal_var"]], key="portfolio_goal")
        with c2: rf_rate  = st.number_input(T["rf_rate"], value=4.0, step=0.1)/100
        n   = len(corr_tickers)
        mu  = returns.mean()*252
        cov = returns.cov()*252
        def stats(w):
            w = np.array(w)
            r = np.sum(mu*w)
            v = np.sqrt(np.dot(w.T,np.dot(cov,w)))
            sh = (r-rf_rate)/v if v>0 else 0
            return r,v,sh
        res = minimize(
            lambda w: -stats(w)[2] if objetivo==T["goal_sharpe"] else stats(w)[1],
            [1/n]*n, method="SLSQP", bounds=[(0,1)]*n,
            constraints={"type":"eq","fun":lambda x: np.sum(x)-1}
        )
        if res.success:
            r_opt,v_opt,sh_opt = stats(res.x)
            p1,p2,p3 = st.columns(3)
            p1.metric(T["exp_return"], f"{r_opt*100:.2f}%")
            p2.metric(T["volatility"], f"{v_opt*100:.2f}%")
            p3.metric(T["sharpe"], f"{sh_opt:.2f}")
    else:
        st.warning(T["portfolio_warn"])

# --- Financials ---
with tab_fin:
    st.subheader(T["financials_title"])
    fin_tabs = st.tabs([T["income_stmt"],T["balance_sheet"],T["cash_flow"]])
    data_frames = [financials, balance_sheet, cashflow]
    for inner_tab, df_f in zip(fin_tabs,data_frames):
        with inner_tab:
            df_fmt = None
            try:
                df_fmt = format_financial_df(df_f)
            except Exception:
                df_fmt = None
            if df_fmt is not None:
                render_champagne_table(df_fmt)
            else:
                st.info(T["no_data"])
