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

# =========================
# COLORES Y ESTILOS
# =========================
ACCENT_BLUE = "#38BDF8"
ACCENT_GREEN = "#22C55E"
ACCENT_RED = "#EF4444"
ACCENT_ORANGE = "#F59E0B"
TEXT_PRIMARY = "#E5E7EB"
TEXT_SECONDARY = "#9CA3AF"
CARD_BG = "#111827"
BORDER = "#1F2937"
BG = "#020617"

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
        margin-bottom: 2rem;
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
    .metric-sub {{
        color: {TEXT_SECONDARY};
        font-size: 0.75rem;
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
        return "N/D"
    return f"{v:.{decimals}f}{suffix}"

def fmt_large(x):
    v = safe_float(x, None)
    if v is None:
        return "N/D"
    sign = -1 if v < 0 else 1
    v = abs(v)
    if v >= 1e12:
        return f"{sign*v/1e12:.2f}T"
    elif v >= 1e9:
        return f"{sign*v/1e9:.2f}B"
    elif v >= 1e6:
        return f"{sign*v/1e6:.2f}M"
    return f"{sign*v:.0f}"

def traducir_a_es(texto):
    if not texto:
        return ""
    try:
        return GoogleTranslator(source="auto", target="es").translate(texto)
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
        return "N/D"
    if u >= 40:
        return "Muy infravalorada"
    if u >= 20:
        return "Infravalorada"
    if u >= -10:
        return "En línea"
    if u >= -30:
        return "Sobrevalorada"
    return "Muy sobrevalorada"

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

    if calidad == "Alta":
        base = min(base + 1, 5)
    elif calidad == "Baja":
        base = max(base - 1, 1)

    labels = {
        5: "Convicción muy alta",
        4: "Convicción alta",
        3: "Neutral",
        2: "Débil",
        1: "Muy débil",
    }
    return f"{'★'*base}{'☆'*(5-base)} · {labels[base]}"

def get_news(api_key, active_ticker, company_name):
    hoy = dt.date.today().isoformat()
    consulta_empresa = f'"{active_ticker}" OR "{company_name}"'
    consulta_mercado = (
        '"stock market" OR "financial markets" OR inflation OR "interest rates" '
        'OR "S&P 500" OR Nasdaq OR "bond yields" OR recession OR Federal Reserve'
    )
    query_total = f"({consulta_empresa}) OR ({consulta_mercado})"

    params = {
        "q": query_total,
        "from": hoy,
        "sortBy": "publishedAt",
        "pageSize": 20,
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

# =========================
# MÉTODOS DE VALORACIÓN
# =========================
def compute_valuations(info, currency):
    methods = []

    price   = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
    shares  = safe_float(info.get("sharesOutstanding"))
    fcf     = safe_float(info.get("freeCashflow"))
    revenue = safe_float(info.get("totalRevenue"))
    ebitda  = safe_float(info.get("ebitda"))
    ebit    = safe_float(info.get("ebit"))
    bvps    = safe_float(info.get("bookValue"))
    eps     = safe_float(info.get("trailingEps"))
    fwd_eps = safe_float(info.get("forwardEps"))
    div     = safe_float(info.get("dividendRate"))
    total_debt = safe_float(info.get("totalDebt"), 0.0)
    cash    = safe_float(info.get("totalCash"), 0.0)
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
            "Supuestos": f"Crecimiento alto {g_high*100:.0f}% 5 años, crecimiento terminal {g_low*100:.0f}%, descuento {r*100:.0f}%",
        })

    if fcf is not None:
        dcf_model(fcf, 0.15, 0.04, 0.11, "DCF agresivo", "Media")
        dcf_model(fcf, 0.10, 0.03, 0.10, "DCF base", "Alta")
        dcf_model(fcf, 0.06, 0.02, 0.09, "DCF conservador", "Alta")

    if net_income is not None and shares and shares > 0:
        dcf_model(net_income, 0.08, 0.03, 0.10, "DCF con beneficio neto", "Media")

    if ebitda is not None and ebitda > 0 and shares and shares > 0:
        for mult, cal in [(8, "Alta"), (10, "Alta"), (12, "Media"), (15, "Media"), (20, "Baja")]:
            ev = ebitda * mult
            methods.append({
                "Método": f"EV/EBITDA {mult}x",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": (ev + cash - total_debt) / shares,
                "Supuestos": f"Se multiplica el EBITDA ({fmt_large(ebitda)}) por {mult}x y se ajusta por caja y deuda neta.",
            })

    if ebit is not None and ebit > 0 and shares and shares > 0:
        for mult, cal in [(10, "Alta"), (14, "Media"), (18, "Baja")]:
            ev = ebit * mult
            methods.append({
                "Método": f"EV/EBIT {mult}x",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": (ev + cash - total_debt) / shares,
                "Supuestos": f"Se multiplica el EBIT ({fmt_large(ebit)}) por {mult}x y se ajusta por caja y deuda neta.",
            })

    eps_use = eps if (eps and eps > 0) else fwd_eps
    if eps_use and eps_use > 0:
        for mult, cal in [(10, "Alta"), (15, "Alta"), (20, "Media"), (25, "Media"), (30, "Baja")]:
            methods.append({
                "Método": f"PER objetivo {mult}x",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": eps_use * mult,
                "Supuestos": f"Se aplica un PER de {mult}x sobre el BPA de {eps_use:.2f}.",
            })

    if revenue is not None and shares and shares > 0:
        for mult, cal in [(1, "Alta"), (2, "Alta"), (4, "Media"), (6, "Media"), (8, "Baja")]:
            methods.append({
                "Método": f"P/Ventas {mult}x",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": revenue * mult / shares,
                "Supuestos": f"Se aplica {mult}x sobre ventas totales de {fmt_large(revenue)} y se divide por acciones.",
            })

    if bvps and bvps > 0:
        for mult, cal in [(1, "Alta"), (1.5, "Alta"), (2, "Media"), (3, "Media"), (4, "Baja")]:
            methods.append({
                "Método": f"P/Valor contable {mult}x",
                "Tipo": "Múltiplo",
                "Calidad": cal,
                "Valor": bvps * mult,
                "Supuestos": f"Se aplica {mult}x sobre el valor contable por acción de {bvps:.2f}.",
            })

    if eps_use and eps_use > 0 and bvps and bvps > 0:
        graham = math.sqrt(22.5 * eps_use * bvps)
        methods.append({
            "Método": "Número de Graham",
            "Tipo": "Mixto",
            "Calidad": "Alta",
            "Valor": graham,
            "Supuestos": f"Se calcula como raíz de 22.5 × BPA ({eps_use:.2f}) × valor contable por acción ({bvps:.2f}).",
        })
        graham_adj = math.sqrt(15 * eps_use * bvps)
        methods.append({
            "Método": "Graham ajustado",
            "Tipo": "Mixto",
            "Calidad": "Media",
            "Valor": graham_adj,
            "Supuestos": f"Se calcula como raíz de 15 × BPA ({eps_use:.2f}) × valor contable por acción ({bvps:.2f}).",
        })

    if div and div > 0:
        for g_div, r_div, label_div in [
            (0.02, 0.08, "DDM g 2%, r 8%"),
            (0.03, 0.09, "DDM g 3%, r 9%"),
            (0.05, 0.10, "DDM g 5%, r 10%"),
        ]:
            if r_div > g_div:
                val_ddm = div * (1 + g_div) / (r_div - g_div)
                methods.append({
                    "Método": label_div,
                    "Tipo": "DDM",
                    "Calidad": "Media",
                    "Valor": val_ddm,
                    "Supuestos": f"Modelo Gordon-Shapiro con dividendo {div:.2f}, crecimiento {g_div*100:.0f}% y descuento {r_div*100:.0f}%.",
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
# INTERFAZ PRINCIPAL
# =========================
st.markdown('<div class="hero-title">📊 Equity Terminal</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Value Investing · Análisis fundamental de empresas cotizadas</div>', unsafe_allow_html=True)

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
    st.markdown("---")
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
# EXTRACCIÓN DE DATOS
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
    st.error("No se pudo obtener el precio de mercado. Verifica el ticker.")
    st.stop()

company_name = info.get("longName") or info.get("shortName") or active_ticker
sector   = info.get("sector", "N/D")
industry = info.get("industry", "N/D")
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
    (k1, "Capitalización bursátil", mc),
    (k2, "Máximo 52 semanas", f"{high52} {currency}"),
    (k3, "Mínimo 52 semanas", f"{low52} {currency}"),
    (k4, "Beta", beta_v),
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
    ["Empresa", "Ratios", "Valoración", "Benchmarks", "Correlaciones", "Precio", "Optimización de cartera", "Noticias"]
)

# ==== EMPRESA ====
with tab_emp:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Descripción del negocio")
        desc = info.get("longBusinessSummary")
        if desc:
            st.write(traducir_a_es(desc))
        else:
            st.info("No hay descripción disponible.")
    with c2:
        st.subheader("Datos corporativos")
        employees = info.get("fullTimeEmployees")
        for label, val in [
            ("País", info.get("country", "N/D")),
            ("Ciudad", info.get("city", "N/D")),
            ("Bolsa", info.get("exchange", "N/D")),
            ("Empleados", f"{employees:,}" if employees else "N/D"),
            ("Sector", sector),
            ("Industria", industry),
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
        st.markdown("**Valoración de mercado**")
        st.write(f"PER (12 meses): **{fmt_num(pe)}**")
        st.write(f"PER adelantado: **{fmt_num(fwd_pe)}**")
        st.write(f"P/Valor contable: **{fmt_num(pb)}**")
        st.write(f"P/Ventas: **{fmt_num(ps)}**")
    with col2:
        st.markdown("**Rentabilidad**")
        st.write(f"ROE: **{fmt_num(roe*100 if roe else None, 1, '%')}**")
        st.write(f"ROA: **{fmt_num(roa*100 if roa else None, 1, '%')}**")
        st.write(f"Margen bruto: **{fmt_num(gross_margin*100 if gross_margin else None, 1, '%')}**")
        st.write(f"Margen neto: **{fmt_num(profit_margin*100 if profit_margin else None, 1, '%')}**")
    with col3:
        st.markdown("**Riesgo y liquidez**")
        st.write(f"Deuda/Patrimonio: **{fmt_num(debt_equity)}**")
        st.write(f"Ratio corriente: **{fmt_num(current_ratio)}**")
        st.write(f"Quick ratio: **{fmt_num(quick_ratio)}**")
        st.write(f"Rentabilidad por dividendo: **{fmt_num(dividend_yield*100 if dividend_yield else None, 2, '%')}**")

    st.markdown("---")
    st.markdown("**Perfil financiero (radar)**")

    def norm(v, lo, hi):
        v2 = safe_float(v, None)
        if v2 is None:
            return 0.0
        return max(0.0, min(1.0, (v2 - lo) / (hi - lo)))

    radar_labels = ["ROE", "ROA", "Margen neto", "PER bajo", "Deuda baja", "Liquidez"]
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
    st.subheader("Valoración intrínseca — todos los métodos")
    methods, current_price = compute_valuations(info, currency)

    if not methods:
        st.warning("No se pudieron calcular valoraciones por falta de datos.")
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
            "Método": df_val["Método"],
            "Tipo": df_val["Tipo"],
            "Score": df_val["Score"],
            "Flag": df_val["Upside %"].apply(flag_icon),
            "Upside (%)": df_val["Upside %"].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/D"),
            "Valor intrínseco": df_val["Valor"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/D"),
            "Precio actual": df_val["Precio"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/D"),
            "Calidad": df_val["Calidad"],
            "Interpretación": df_val["Interpretación"],
        }).reindex(df_val.sort_values("Upside %", ascending=False).index)

        st.dataframe(df_tabla, use_container_width=True, hide_index=True)

        st.markdown("---")

        upsides = df_val["Upside %"].dropna()
        m1, m2, m3, m4 = st.columns(4)
        for col, label, val in [
            (m1, "Métodos calculados", str(len(df_val))),
            (m2, "Upside mediano", f"{upsides.median():+.1f}%" if len(upsides) else "N/D"),
            (m3, "Upside medio", f"{upsides.mean():+.1f}%" if len(upsides) else "N/D"),
            (m4, "Rango de upside", f"{upsides.min():+.1f}% / {upsides.max():+.1f}%" if len(upsides) else "N/D"),
        ]:
            with col:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-label">{label}</div>'
                    f'<div class="metric-value">{val}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        fig_val = px.strip(
            df_val,
            x="Upside %",
            y="Tipo",
            color="Tipo",
            hover_data=["Método", "Valor", "Supuestos"],
            title="Distribución de upside por tipo de método",
            color_discrete_map={
                "DCF": "#38BDF8",
                "Múltiplo": "#A78BFA",
                "Mixto": "#FB923C",
                "DDM": "#34D399",
            },
        )
        fig_val.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.4)
        fig_val.add_vline(x=30, line_dash="dot", line_color="#22C55E", opacity=0.5, annotation_text="Margen seg. 30%")
        fig_val.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
            xaxis_title="Upside vs precio actual (%)",
        )
        st.plotly_chart(fig_val, use_container_width=True)

        fig_bar = px.bar(
            df_val.sort_values("Valor"),
            x="Valor",
            y="Método",
            color="Tipo",
            orientation="h",
            title=f"Valor intrínseco por método vs precio actual ({current_price:.2f} {currency})",
            color_discrete_map={
                "DCF": "#38BDF8",
                "Múltiplo": "#A78BFA",
                "Mixto": "#FB923C",
                "DDM": "#34D399",
            },
        )
        fig_bar.add_vline(x=current_price, line_dash="dash", line_color="#EF4444", annotation_text=f"Precio: {current_price:.2f}")
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=max(400, len(df_val) * 22),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### Cómo se calcula cada método")
        for _, row in df_val.sort_values("Upside %", ascending=False).iterrows():
            with st.expander(f"{row['Método']} · {row['Tipo']} · {fmt_num(row['Upside %'], 1, '%')}"):
                st.write(f"**Calidad:** {row['Calidad']}")
                st.write(f"**Valor intrínseco:** {fmt_num(row['Valor'])} {currency}")
                st.write(f"**Precio actual:** {fmt_num(row['Precio'])} {currency}")
                st.write(f"**Interpretación:** {row['Interpretación']}")
                st.write(f"**Cálculo:** {row['Supuestos']}")

# ==== BENCHMARKS ====
with tab_bench:
    st.subheader("Comparación con benchmarks del sector")
    peers = get_benchmark_list(info, active_ticker)
    if not peers:
        st.info("No hay benchmarks definidos para este sector.")
    else:
        tickers_all = [active_ticker] + peers
        with st.spinner("Descargando benchmarks..."):
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
            st.warning("No se pudieron cargar datos de benchmarks.")
        else:
            df_bench = pd.DataFrame.from_dict(data, orient="index").reset_index().rename(columns={"index": "Ticker"})
            df_view = pd.DataFrame({
                "Ticker": df_bench["Ticker"],
                "Nombre": df_bench["Nombre"],
                "Precio": df_bench["Precio"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/D"),
                "PER": df_bench["PER"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/D"),
                "P/VC": df_bench["P/VC"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/D"),
                "ROE": df_bench["ROE"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/D"),
                "Margen neto": df_bench["Margen neto"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/D"),
                "Capitalización": df_bench["Capitalización"].apply(fmt_large),
            }).reindex(df_bench.sort_values("Capitalización", ascending=False).index)

            st.dataframe(df_view, use_container_width=True, hide_index=True)
            st.markdown("---")

            fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comp.add_trace(
                go.Bar(x=df_bench["Ticker"], y=df_bench["PER"], name="PER", marker_color=ACCENT_BLUE),
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
            fig_comp.update_yaxes(title_text="PER", secondary_y=False)
            fig_comp.update_yaxes(title_text="ROE (%)", secondary_y=True)
            fig_comp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400,
            )
            st.plotly_chart(fig_comp, use_container_width=True)

# ==== CORRELACIONES ====
with tab_corr:
    st.subheader("Correlación de rentabilidades")
    corr_tickers = [t.strip().upper() for t in corr_tickers_input.replace(",", "\n").split("\n") if t.strip()]
    if active_ticker not in corr_tickers:
        corr_tickers.insert(0, active_ticker)

    with st.spinner("Descargando precios históricos..."):
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
            st.error(f"No se pudieron descargar precios: {e}")
            returns = None

    if returns is not None and not returns.empty:
        corr = returns.corr()
        st.markdown("#### Matriz de correlación")
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        fig_corr.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("#### Retornos acumulados")
        cum = (1 + returns).cumprod()
        fig_cum = px.line(cum, labels={"value": "Retorno acumulado", "index": "Fecha"})
        fig_cum.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )
        st.plotly_chart(fig_cum, use_container_width=True)

# ==== PRECIO ====
with tab_price:
    st.subheader("Histórico de precio y volumen")
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
                name="OHLC"
            ),
            row=1, col=1,
        )
        fig_price.add_trace(
            go.Bar(x=hist.index, y=hist["Volume"], name="Volumen", marker_color=ACCENT_BLUE),
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
    st.subheader("Optimización de cartera de Markowitz")

    if returns is not None and not returns.empty:
        st.markdown("Configura las variables para optimizar tu selección actual de activos.")

        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            objetivo = st.selectbox(
                "Objetivo del optimizador",
                ["Maximizar ratio Sharpe", "Minimizar varianza"]
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
            if objetivo == "Maximizar ratio Sharpe":
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

            st.markdown("#### Métricas de la cartera óptima")
            m_p1, m_p2, m_p3 = st.columns(3)
            m_p1.metric("Rentabilidad esperada anual", f"{r_opt*100:.2f}%")
            m_p2.metric("Volatilidad de la cartera", f"{vol_opt*100:.2f}%")
            m_p3.metric("Ratio Sharpe", f"{sharpe_opt:.2f}")

            df_pesos = pd.DataFrame({
                "Activo": corr_tickers,
                "Ponderación óptima (%)": [f"{w*100:.2f}%" for w in pesos_optimos],
                "Fracción decimal": np.round(pesos_optimos, 4),
            }).sort_values(by="Fracción decimal", ascending=False)

            st.dataframe(df_pesos, use_container_width=True, hide_index=True)

            fig_pie = px.pie(
                df_pesos[df_pesos["Fracción decimal"] > 0.001],
                values="Fracción decimal",
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
            st.error("El algoritmo de optimización no pudo converger en una solución válida.")
    else:
        st.warning("Datos históricos insuficientes. Asegúrate de configurar los tickers correctamente en las opciones superiores.")

# ==== NOTICIAS ====
with tab_news:
    st.subheader("Noticias relevantes del día")
    api_key = st.secrets.get("NEWS_API_KEY", None)

    if not api_key:
        st.warning("No se ha configurado la clave NEWS_API_KEY en Secrets.")
    else:
        with st.spinner("Cargando noticias..."):
            articles = get_news(api_key, active_ticker, company_name)

        if not articles:
            st.info("No se encontraron noticias relevantes para hoy.")
        else:
            st.markdown(
                f"Se muestran noticias sobre **{company_name}** y también noticias generales de mercado del día."
            )
            st.markdown("---")

            for art in articles:
                titulo = art.get("title", "Sin título")
                fuente = art.get("source", {}).get("name", "Fuente desconocida")
                fecha = art.get("publishedAt", "")[:16].replace("T", " ")
                descripcion = art.get("description") or art.get("content") or "Sin resumen disponible."
                descripcion = traducir_a_es(descripcion)
                url = art.get("url")

                with st.expander(f"{titulo} · {fuente} · {fecha}"):
                    st.write(descripcion)
                    if url:
                        st.markdown(f"[Leer noticia completa]({url})")
