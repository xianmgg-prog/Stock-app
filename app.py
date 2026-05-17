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
    initial_sidebar_state="expanded",
)

# =========================
# TEMA OSCURO PROFESIONAL
# =========================
PRIMARY_BG = "#050816"
SECONDARY_BG = "#0B1020"
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
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1400px;
    }}
    body {{
        background-color: {PRIMARY_BG};
    }}
    .stApp {{
        background: radial-gradient(circle at top left, #111827 0, #020617 55%);
        color: {TEXT_PRIMARY};
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }}
    .css-18e3th9 {{
        background-color: transparent !important;
    }}
    .css-1d391kg, .stSidebar {{
        background: linear-gradient(180deg, #020617 0, #020617 40px, #020617 100%);
        border-right: 1px solid {BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.9rem;
        padding: 0.75rem 1.25rem;
    }}
    .big-title {{
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }}
    .tagline {{
        color: {TEXT_SECONDARY};
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
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
    .val-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }}
    .val-table th {{
        text-align: left;
        padding: 0.4rem 0.6rem;
        border-bottom: 1px solid {BORDER};
        color: {TEXT_SECONDARY};
        font-weight: 500;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    .val-table td {{
        padding: 0.35rem 0.6rem;
        border-bottom: 1px solid rgba(31,41,55,0.6);
    }}
    .val-method {{
        font-weight: 500;
    }}
    .val-num {{
        font-family: "JetBrains Mono", ui-monospace, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        text-align: right;
    }}
    .margin-good {{
        color: {ACCENT_GREEN};
        font-weight: 600;
        text-align: right;
    }}
    .margin-ok {{
        color: {ACCENT_BLUE};
        font-weight: 600;
        text-align: right;
    }}
    .margin-fair {{
        color: #EAB308;
        font-weight: 600;
        text-align: right;
    }}
    .margin-poor {{
        color: {ACCENT_RED};
        font-weight: 600;
        text-align: right;
    }}
    .bench-header {{
        font-size: 0.8rem;
        color: {TEXT_SECONDARY};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
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


def margin_badge(upside_pct):
    v = safe_float(upside_pct, None)
    if v is None:
        return "N/A", "margin-fair"
    if v >= 30:
        return f"+{v:.1f}%", "margin-good"
    if v >= 10:
        return f"+{v:.1f}%", "margin-ok"
    if v >= -10:
        return f"{v:.1f}%", "margin-fair"
    return f"{v:.1f}%", "margin-poor"


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

    price = safe_float(info.get("currentPrice")) or safe_float(
        info.get("regularMarketPrice")
    )
    shares = safe_float(info.get("sharesOutstanding"))
    fcf = safe_float(info.get("freeCashflow"))
    revenue = safe_float(info.get("totalRevenue"))
    ebitda = safe_float(info.get("ebitda"))
    bvps = safe_float(info.get("bookValue"))
    eps = safe_float(info.get("trailingEps"))
    forward_eps = safe_float(info.get("forwardEps"))
    total_debt = safe_float(info.get("totalDebt"), 0.0)
    cash = safe_float(info.get("totalCash"), 0.0)

    # 1) DCF FCF-based
    if fcf is not None and shares and shares > 0:
        g_high = 0.10
        g_low = 0.03
        r = 0.10

        fcf0 = fcf
        pv = 0.0
        for t in range(1, 6):
            f = fcf0 * (1 + g_high) ** t
            pv += f / (1 + r) ** t
        for t in range(6, 11):
            f = fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** (t - 5)
            pv += f / (1 + r) ** t
        terminal = (
            fcf0 * (1 + g_high) ** 5 * (1 + g_low) ** 5 * (1 + g_low) / (r - g_low)
        )
        pv_terminal = terminal / (1 + r) ** 10
        equity_value = pv + pv_terminal + cash - total_debt
        value_per_share = equity_value / shares
        methods.append(
            {
                "name": "DCF (FCF basado)",
                "value": value_per_share,
                "params": "g 10%→3%, r 10%",
            }
        )

    # 2) EV/EBITDA
    if ebitda is not None and ebitda > 0 and shares and shares > 0:
        target_multiple = 12.0
        enterprise_value = ebitda * target_multiple
        equity_value = enterprise_value + cash - total_debt
        value_per_share = equity_value / shares
        methods.append(
            {
                "name": f"EV/EBITDA ({target_multiple:.0f}×)",
                "value": value_per_share,
                "params": f"EBITDA={fmt_large(ebitda)}",
            }
        )

    # 3) P/S objetivo
    if revenue is not None and shares and shares > 0:
        target_ps = 5.0
        equity_value = revenue * target_ps
        value_per_share = equity_value / shares
        methods.append(
            {
                "name": "P/Ventas (P/S)",
                "value": value_per_share,
                "params": f"Ventas={fmt_large(revenue)}  mult={target_ps:.1f}×",
            }
        )

    # 4) P/B objetivo
    if bvps is not None and bvps > 0:
        target_pb = 2.0
        value_per_share = bvps * target_pb
        methods.append(
            {
                "name": "P/Valor en Libros (P/B)",
                "value": value_per_share,
                "params": f"BVPS={bvps:.2f}  mult={target_pb:.1f}×",
            }
        )

    # 5) Graham Number
    if eps is None or eps <= 0:
        eps_use = forward_eps
    else:
        eps_use = eps
    if eps_use is not None and eps_use > 0 and bvps is not None and bvps > 0:
        graham = math.sqrt(22.5 * eps_use * bvps)
        methods.append(
            {
                "name": "Graham Number",
                "value": graham,
                "params": f"EPS={eps_use:.2f}  BVPS={bvps:.2f}",
            }
        )

    return methods, price


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Configuración")

    query = st.text_input(
        "🔎 Buscar empresa o ticker",
        value="Apple",
        help="Escribe el nombre (Apple, Amper, Stellantis...) o el ticker (AAPL, TEF.MC...).",
    )

    suggestions = search_ticker(query) if query else []
    if suggestions:
        choice = st.selectbox("Sugerencias", suggestions)
        ticker = choice.split(" — ")[0].strip()
    else:
        st.caption("No hay sugerencias, se usará el texto como ticker directo.")
        ticker = query.strip().upper()

    st.markdown("---")
    corr_tickers_text = st.text_area(
        "Tickers para correlación (uno por línea)",
        value="AAPL\nMSFT\nGOOGL\nAMZN\nMETA",
    )
    period = st.selectbox("Período histórico", ["1y", "3y", "5y", "10y"], index=1)
    analyze_btn = st.button("🔍 Analizar", use_container_width=True, type="primary")

if not analyze_btn:
    st.markdown(
        """
        <div class="big-title">📊 Equity Terminal</div>
        <p class="tagline">Escribe una empresa a la izquierda y pulsa <b>Analizar</b></p>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# =========================
# CARGA DE DATOS
# =========================
ticker_sym = ticker.strip().upper()

with st.spinner(f"Cargando datos de {ticker_sym}..."):
    try:
        stock = yf.Ticker(ticker_sym)
        info = stock.info
        hist = stock.history(period=period)
    except Exception as e:
        st.error(f"Error al obtener datos de Yahoo Finance: {e}")
        st.stop()

price = safe_float(info.get("currentPrice")) or safe_float(
    info.get("regularMarketPrice")
)
if price is None:
    st.error("No se pudo obtener el precio de mercado. Verifica el ticker.")
    st.stop()

company_name = info.get("longName") or info.get("shortName") or ticker_sym
sector = info.get("sector", "N/A")
industry = info.get("industry", "N/A")
currency = info.get("currency", "USD")

# CABECERA
st.markdown(
    f"""
    <div class="big-title">
        <span>📈 Equity Terminal</span>
    </div>
    <div class="tagline">
        {company_name} ({ticker_sym}) · {sector} · {industry} · Cotizado en {currency}
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("")

tab_emp, tab_rat, tab_val, tab_bench, tab_corr, tab_price = st.tabs(
    ["🏢 Empresa", "📊 Ratios", "🎯 Valoración", "📚 Benchmarks", "📉 Correlaciones", "📈 Precio"]
)

# ==== TAB EMPRESA ====
with tab_emp:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Perfil de la compañía")
        desc = info.get("longBusinessSummary")
        if desc:
            st.write(desc)
        else:
            st.info("No hay descripción disponible.")

    with c2:
        st.subheader("Snapshot de mercado")
        prev_close = safe_float(info.get("previousClose"))
        if price and prev_close:
            chg = price - prev_close
            chg_pct = chg / prev_close * 100
            delta_str = f"{chg:+.2f} ({chg_pct:+.2f}%)"
        else:
            delta_str = "N/A"

        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Precio actual</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{price:.2f} {currency} <span class="metric-sub">{delta_str}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        mc = fmt_large(info.get("marketCap"))
        high52 = fmt_num(info.get("fiftyTwoWeekHigh"))
        low52 = fmt_num(info.get("fiftyTwoWeekLow"))

        c2a, c2b = st.columns(2)
        with c2a:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Market Cap</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{mc}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2b:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">52W Range</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value">{low52} – {high52} {currency}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    c3, c4, c5, c6 = st.columns(4)
    employees = info.get("fullTimeEmployees")
    with c3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Empleados</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{employees:,}' if employees else '<div class="metric-value">N/A',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">País</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{info.get("country","N/A")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Ciudad</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{info.get("city","N/A")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with c6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Exchange</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-value">{info.get("exchange","N/A")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

# ==== TAB RATIOS ====
with tab_rat:
    st.subheader("Ratios clave")

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
    beta = safe_float(info.get("beta"))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Valoración**")
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
        st.write(f"Beta: **{fmt_num(beta)}**")
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
        rows_html = ""
        filtered_methods = []

        for m in methods:
            name = m["name"]
            val = m["value"]
            params = m["params"]

            if current_price:
                upside = (val - current_price) / current_price * 100
            else:
                upside = None

            # Filtro: ocultar métodos extremadamente alejados del precio
            if upside is not None and (upside < -80 or upside > 200):
                continue

            margin_str, css_class = margin_badge(upside)
            filtered_methods.append((name, val, params, margin_str, css_class))

        if not filtered_methods:
            st.info("Las valoraciones calculadas son extremas; se han ocultado por seguridad.")
        else:
            for name, val, params, margin_str, css_class in filtered_methods:
                rows_html += f"""
                <tr>
                  <td class="val-method">{name}</td>
                  <td style="color:{TEXT_SECONDARY};font-size:10px;">{params}</td>
                  <td class="val-num">{currency} {val:.2f}</td>
                  <td class="val-num">{currency} {current_price:.2f}</td>
                  <td class="{css_class}">{margin_str}</td>
                </tr>
                """

            table_html = f"""
            <table class="val-table">
              <thead>
                <tr>
                  <th>Método</th>
                  <th>Parámetros</th>
                  <th>Valor intrínseco</th>
                  <th>Precio mercado</th>
                  <th>Margen seg.</th>
                </tr>
              </thead>
              <tbody>
                {rows_html}
              </tbody>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)

            df_val = pd.DataFrame(
                {"Método": [m[0] for m in filtered_methods], "Valor": [m[1] for m in filtered_methods]}
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
                line_color="red",
                annotation_text=f"Precio: {current_price:.2f}",
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
        st.info("No hay benchmarks definidos para este sector. Puedes ampliar DEFAULT_BENCHMARKS en el código.")
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
                        "sector": inf.get("sector", ""),
                        "pe": safe_float(inf.get("trailingPE")),
                        "pb": safe_float(inf.get("priceToBook")),
                        "roe": safe_float(inf.get("returnOnEquity")),
                        "margin": safe_float(inf.get("profitMargins")),
                        "price": safe_float(inf.get("currentPrice")) or safe_float(
                            inf.get("regularMarketPrice")
                        ),
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

            st.markdown('<div class="bench-header">Ratios comparables</div>', unsafe_allow_html=True)
            st.dataframe(
                df_bench[
                    ["Ticker", "name", "pe", "pb", "roe", "margin", "price", "marketCap"]
                ].rename(
                    columns={
                        "name": "Nombre",
                        "pe": "P/E",
                        "pb": "P/B",
                        "roe": "ROE",
                        "margin": "Margen neto",
                        "price": "Precio",
                        "marketCap": "Market Cap",
                    }
                ),
                use_container_width=True,
            )

            st.markdown("#### P/E y ROE vs peers")

            pe_series = df_bench["pe"]
            roe_series = df_bench["roe"]

            fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comp.add_trace(
                go.Bar(
                    x=df_bench["Ticker"],
                    y=pe_series,
                    name="P/E",
                    marker_color=ACCENT_BLUE,
                ),
                secondary_y=False,
            )
            fig_comp.add_trace(
                go.Scatter(
                    x=df_bench["Ticker"],
                    y=roe_series * 100,
                    name="ROE (%)",
                    mode="lines+markers",
                    line_color=ACCENT_GREEN,
                ),
                secondary_y=True,
            )
            fig_comp.update_yaxes(title_text="P/E", secondary_y=False)
            fig_comp.update_yaxes(title_text="ROE (%)", secondary_y=True)
            fig_comp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400,
            )
            st.plotly_chart(fig_comp, use_container_width=True)

# ==== TAB CORRELACIONES ====
with tab_corr:
    st.subheader("Correlación de rentabilidades")
    corr_tickers = [t.strip().upper() for t in corr_tickers_text.split("\n") if t.strip()]
    if ticker_sym not in corr_tickers:
        corr_tickers.insert(0, ticker_sym)

    with st.spinner("Descargando precios históricos..."):
        try:
            prices = yf.download(
                corr_tickers, period=period, auto_adjust=True, progress=False
            )["Close"]
            if isinstance(prices, pd.Series):
                prices = prices.to_frame(name=corr_tickers[0])
            returns = prices.pct_change().dropna()
        except Exception as e:
            st.error(f"No se pudo descargar precios: {e}")
            returns = None

    if returns is not None and not returns.empty:
        corr = returns.corr()
        st.markdown("#### Matriz de correlación")
        fig_corr = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
        )
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

# ==== TAB PRECIO ====
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
            row_heights=[0.7, 0.3],
        )
        fig_price.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name="OHLC",
            ),
            row=1,
            col=1,
        )
        fig_price.add_trace(
            go.Bar(
                x=hist.index,
                y=hist["Volume"],
                name="Volumen",
                marker_color=ACCENT_BLUE,
            ),
            row=2,
            col=1,
        )
        fig_price.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_price, use_container_width=True)
