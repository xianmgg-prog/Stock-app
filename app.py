import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import math

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
# COLORES
# =========================
PRIMARY_BG = "#050816"
CARD_BG = "#111827"
ACCENT_BLUE = "#38BDF8"
ACCENT_GREEN = "#22C55E"
ACCENT_RED = "#EF4444"
TEXT_PRIMARY = "#E5E7EB"
TEXT_SECONDARY = "#9CA3AF"
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
        margin-bottom: 2rem;
    }}
    .metric-card {{
        background: {CARD_BG};
        border-radius: 10px;
        padding: 0.8rem 1rem;
        border: 1px solid {BORDER};
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
    .bench-header {{
        font-size: 0.8rem;
        color: {TEXT_SECONDARY};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
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
        s = f"{sign*v/1e12:.2f}T"
    elif v >= 1e9:
        s = f"{sign*v/1e9:.2f}B"
    elif v >= 1e6:
        s = f"{sign*v/1e6:.2f}M"
    else:
        s = f"{sign*v:.0f}"
    return s


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
    "Energy": ["XOM", "CVX", "BP", "TOT"],
}


def get_benchmark_list(info, main_ticker):
    sector = info.get("sector")
    peers = DEFAULT_BENCHMARKS.get(sector, [])
    peers = [p for p in peers if p.upper() != main_ticker.upper()]
    return peers[:4]


def compute_valuations(info):
    methods = []
    price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
    shares = safe_float(info.get("sharesOutstanding"))
    fcf = safe_float(info.get("freeCashflow"))
    revenue = safe_float(info.get("totalRevenue"))
    ebitda = safe_float(info.get("ebitda"))
    bvps = safe_float(info.get("bookValue"))
    eps = safe_float(info.get("trailingEps"))
    forward_eps = safe_float(info.get("forwardEps"))
    total_debt = safe_float(info.get("totalDebt"), 0.0)
    cash = safe_float(info.get("totalCash"), 0.0)

    if fcf is not None and shares and shares > 0:
        g_high, g_low, r = 0.10, 0.03, 0.10
        fcf0 = fcf
        pv = 0.0
        for t in range(1, 6):
            pv += fcf0 * (1 + g_high) ** t / (1 + r) ** t
        for t in range(6, 11):
            pv += fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** (t - 5) / (1 + r) ** t
        terminal = fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** 5 * (1 + g_low) / (r - g_low)
        pv_terminal = terminal / (1 + r) ** 10
        equity_value = pv + pv_terminal + cash - total_debt
        methods.append({"name": "DCF (FCF)", "value": equity_value / shares, "params": "g 10%→3%, r 10%"})

    if ebitda is not None and ebitda > 0 and shares and shares > 0:
        ev = ebitda * 12.0
        methods.append({"name": "EV/EBITDA (12×)", "value": (ev + cash - total_debt) / shares, "params": f"EBITDA={fmt_large(ebitda)}"})

    if revenue is not None and shares and shares > 0:
        methods.append({"name": "P/Ventas (5×)", "value": revenue * 5.0 / shares, "params": f"Ventas={fmt_large(revenue)}"})

    if bvps is not None and bvps > 0:
        methods.append({"name": "P/Valor Libros (2×)", "value": bvps * 2.0, "params": f"BVPS={bvps:.2f}"})

    eps_use = eps if (eps and eps > 0) else forward_eps
    if eps_use and eps_use > 0 and bvps and bvps > 0:
        methods.append({"name": "Graham Number", "value": math.sqrt(22.5 * eps_use * bvps), "params": f"EPS={eps_use:.2f} BVPS={bvps:.2f}"})

    return methods, price


# =========================
# HERO
# =========================
st.markdown('<div class="hero-title">📊 Equity Terminal</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Value Investing · Análisis fundamental de empresas cotizadas</div>', unsafe_allow_html=True)

# =========================
# BÚSQUEDA + OPCIONES
# =========================
col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input(
        "",
        placeholder="🔎  Busca una empresa o ticker  (ej: Apple, AAPL, Stellantis, TEF.MC...)",
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button("Analizar →", use_container_width=True, type="primary")

# Sugerencias
if query:
    suggestions = search_ticker(query)
    if suggestions:
        choice = st.selectbox("Sugerencias", suggestions, label_visibility="collapsed")
        ticker_sym = choice.split(" — ")[0].strip()
    else:
        ticker_sym = query.strip().upper()
else:
    ticker_sym = ""

# Opciones avanzadas en expander
with st.expander("⚙️ Opciones de análisis", expanded=False):
    op1, op2 = st.columns([1, 2])
    with op1:
        period = st.selectbox(
            "Período histórico",
            ["1y", "3y", "5y", "10y"],
            index=1,
        )
    with op2:
        corr_tickers_input = st.text_input(
            "Tickers para correlación (separados por comas)",
            value="AAPL, MSFT, GOOGL, AMZN, META",
        )

corr_tickers_text = corr_tickers_input if "corr_tickers_input" in dir() else "AAPL\nMSFT\nGOOGL\nAMZN\nMETA"

if not analyze_btn or not ticker_sym:
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

# =========================
# CARGA DE DATOS
# =========================
with st.spinner(f"Cargando datos de {ticker_sym}..."):
    try:
        stock = yf.Ticker(ticker_sym)
        info = stock.info
        hist = stock.history(period=period)
    except Exception as e:
        st.error(f"Error al obtener datos de Yahoo Finance: {e}")
        st.stop()

price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice"))
if price is None:
    st.error("No se pudo obtener el precio de mercado. Verifica el ticker.")
    st.stop()

company_name = info.get("longName") or info.get("shortName") or ticker_sym
sector = info.get("sector", "N/A")
industry = info.get("industry", "N/A")
currency = info.get("currency", "USD")

# CABECERA DE EMPRESA
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
    <div style="margin: 1.2rem 0 0.5rem 0;">
        <span style="font-size:1.6rem;font-weight:700;">{company_name}</span>
        <span style="color:{TEXT_SECONDARY};font-size:1rem;margin-left:0.8rem;">{ticker_sym} · {sector} · {industry} · {currency}</span>
    </div>
    <div style="font-size:2rem;font-weight:700;margin-bottom:0.2rem;">
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
    (k1, "Market Cap", mc),
    (k2, "52W Máx", f"{high52} {currency}"),
    (k3, "52W Mín", f"{low52} {currency}"),
    (k4, "Beta", beta_v),
]:
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("")

# =========================
# TABS
# =========================
tab_emp, tab_rat, tab_val, tab_bench, tab_corr, tab_price = st.tabs(
    ["🏢 Empresa", "📊 Ratios", "🎯 Valoración", "📚 Benchmarks", "📉 Correlaciones", "📈 Precio"]
)

# ==== TAB EMPRESA ====
with tab_emp:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Descripción")
        desc = info.get("longBusinessSummary")
        if desc:
            st.write(desc)
        else:
            st.info("No hay descripción disponible.")
    with c2:
        st.subheader("Datos corporativos")
        employees = info.get("fullTimeEmployees")
        for label, val in [
            ("País", info.get("country", "N/A")),
            ("Ciudad", info.get("city", "N/A")),
            ("Exchange", info.get("exchange", "N/A")),
            ("Empleados", f"{employees:,}" if employees else "N/A"),
            ("Sector", sector),
            ("Industria", industry),
        ]:
            st.markdown(
                f'<div class="metric-card" style="margin-bottom:0.4rem;"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>',
                unsafe_allow_html=True,
            )

# ==== TAB RATIOS ====
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
        st.write(f"P/E (TTM): **{fmt_num(pe)}**")
        st.write(f"P/E (Fwd): **{fmt_num(fwd_pe)}**")
        st.write(f"P/B: **{fmt_num(pb)}**")
        st.write(f"P/S: **{fmt_num(ps)}**")
    with col2:
        st.markdown("**Rentabilidad**")
        st.write(f"ROE: **{fmt_num(roe*100 if roe else None, 1, '%')}**")
        st.write(f"ROA: **{fmt_num(roa*100 if roa else None, 1, '%')}**")
        st.write(f"Margen bruto: **{fmt_num(gross_margin*100 if gross_margin else None, 1, '%')}**")
        st.write(f"Margen neto: **{fmt_num(profit_margin*100 if profit_margin else None, 1, '%')}**")
    with col3:
        st.markdown("**Riesgo y liquidez**")
        st.write(f"Deuda/Equity: **{fmt_num(debt_equity)}**")
        st.write(f"Current ratio: **{fmt_num(current_ratio)}**")
        st.write(f"Quick ratio: **{fmt_num(quick_ratio)}**")
        st.write(f"Dividend yield: **{fmt_num(dividend_yield*100 if dividend_yield else None, 2, '%')}**")

    st.markdown("---")
    st.markdown("**Perfil financiero (radar)**")

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

# ==== TAB VALORACIÓN ====
with tab_val:
    st.subheader("Valoración intrínseca por métodos")
    methods, current_price = compute_valuations(info)

    if not methods:
        st.warning("No se pudo calcular ninguna valoración por falta de datos.")
    else:
        registros = []
        for m in methods:
            name = m["name"]
            val = m["value"]
            params = m["params"]

            if current_price:
                upside = (val - current_price) / current_price * 100
            else:
                upside = None

            if upside is not None and (upside < -80 or upside > 200):
                continue

            if upside is None:
                margen_txt = "N/A"
            elif upside >= 30:
                margen_txt = f"{upside:.1f}% ▲ alto"
            elif upside >= 10:
                margen_txt = f"{upside:.1f}% ↑ bueno"
            elif upside >= -10:
                margen_txt = f"{upside:.1f}% → neutral"
            else:
                margen_txt = f"{upside:.1f}% ▼ malo"

            registros.append(
                {
                    "Método": name,
                    "Parámetros": params,
                    "Valor intrínseco": f"{currency} {val:.2f}",
                    "Precio mercado": f"{currency} {current_price:.2f}",
                    "Margen seg.": margen_txt,
                }
            )

        if not registros:
            st.info("Las valoraciones calculadas son extremas; se han ocultado por seguridad.")
        else:
            df_val_tabla = pd.DataFrame(registros)
            st.dataframe(df_val_tabla, use_container_width=True)

            df_val = pd.DataFrame(
                {
                    "Método": [r["Método"] for r in registros],
                    "Valor": [float(r["Valor intrínseco"].split()[1]) for r in registros],
                }
            )
            fig_bar = px.bar(
                df_val,
                x="Método",
                y="Valor",
                title="Valor intrínseco por método vs precio actual",
                color="Valor",
                color_continuous_scale="Blues",
            )
            fig_bar.add_hline(
                y=current_price,
                line_dash="dash",
                line_color=ACCENT_RED,
                annotation_text=f"Precio actual: {current_price:.2f}",
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# ==== TAB BENCHMARKS ====
with tab_bench:
    st.subheader("Comparación con benchmarks del sector")
    peers = get_benchmark_list(info, ticker_sym)
    if not peers:
        st.info("No hay benchmarks definidos para este sector.")
    else:
        tickers_all = [ticker_sym] + peers
        with st.spinner("Descargando datos de benchmarks..."):
            data = {}
            for t in tickers_all:
                try:
                    tk = yf.Ticker(t)
                    inf = tk.info
                    data[t] = {
                        "name": inf.get("shortName", t),
                        "pe": safe_float(inf.get("trailingPE")),
                        "pb": safe_float(inf.get("priceToBook")),
                        "roe": safe_float(inf.get("returnOnEquity")),
                        "margin": safe_float(inf.get("profitMargins")),
                        "price": safe_float(inf.get("currentPrice")) or safe_float(inf.get("regularMarketPrice")),
                        "marketCap": safe_float(inf.get("marketCap")),
                    }
                except Exception:
                    continue

        if len(data) <= 1:
            st.warning("No se pudieron cargar datos suficientes de benchmarks.")
        else:
            df_bench = pd.DataFrame.from_dict(data, orient="index")
            df_bench.index.name = "Ticker"
            df_bench.reset_index(inplace=True)

            st.dataframe(
                df_bench[["Ticker", "name", "pe", "pb", "roe", "margin", "price", "marketCap"]].rename(
                    columns={"name": "Nombre", "pe": "P/E", "pb": "P/B", "roe": "ROE",
                              "margin": "Margen neto", "price": "Precio", "marketCap": "Market Cap"}
                ),
                use_container_width=True,
            )

            fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comp.add_trace(
                go.Bar(x=df_bench["Ticker"], y=df_bench["pe"], name="P/E", marker_color=ACCENT_BLUE),
                secondary_y=False,
            )
            fig_comp.add_trace(
                go.Scatter(x=df_bench["Ticker"], y=df_bench["roe"] * 100, name="ROE (%)",
                           mode="lines+markers", line_color=ACCENT_GREEN),
                secondary_y=True,
            )
            fig_comp.update_yaxes(title_text="P/E", secondary_y=False)
            fig_comp.update_yaxes(title_text="ROE (%)", secondary_y=True)
            fig_comp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
            st.plotly_chart(fig_comp, use_container_width=True)

# ==== TAB CORRELACIONES ====
with tab_corr:
    st.subheader("Correlación de rentabilidades")
    corr_tickers = [t.strip().upper() for t in corr_tickers_text.replace(",", "\n").split("\n") if t.strip()]
    if ticker_sym not in corr_tickers:
        corr_tickers.insert(0, ticker_sym)

    with st.spinner("Descargando precios históricos..."):
        try:
            prices = yf.download(corr_tickers, period=period, auto_adjust=True, progress=False)["Close"]
            if isinstance(prices, pd.Series):
                prices = prices.to_frame(name=corr_tickers[0])
            returns = prices.pct_change().dropna()
        except Exception as e:
            st.error(f"No se pudo descargar precios: {e}")
            returns = None

    if returns is not None and not returns.empty:
        corr = returns.corr()
        st.markdown("#### Matriz de correlación")
        fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("#### Retornos acumulados")
        cum = (1 + returns).cumprod()
        fig_cum = px.line(cum, labels={"value": "Retorno acumulado", "index": "Fecha"})
        fig_cum.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
        st.plotly_chart(fig_cum, use_container_width=True)

# ==== TAB PRECIO ====
with tab_price:
    st.subheader("Histórico de precio y volumen")
    if hist is None or hist.empty:
        st.warning("No hay datos históricos disponibles.")
    else:
        fig_price = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                  vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig_price.add_trace(
            go.Candlestick(x=hist.index, open=hist["Open"], high=hist["High"],
                           low=hist["Low"], close=hist["Close"], name="OHLC"),
            row=1, col=1,
        )
        fig_price.add_trace(
            go.Bar(x=hist.index, y=hist["Volume"], name="Volumen", marker_color=ACCENT_BLUE),
            row=2, col=1,
        )
        fig_price.update_layout(
            height=600, xaxis_rangeslider_visible=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_price, use_container_width=True)
