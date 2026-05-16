import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Analizador de Acciones", layout="wide", page_icon="📈")

st.markdown("""
<style>
    .metric-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        border-left: 4px solid #7c3aed;
    }
    .stTabs [data-baseweb="tab"] { font-size: 16px; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analizador de Acciones — Value Investing")
st.caption("Ratios financieros · Valoración · Correlaciones · Información de empresa")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuración")
    ticker_input = st.text_input("Ticker principal", value="AAPL", help="Ej: AAPL, MSFT, STLA, GOOGL")
    tickers_corr = st.text_area("Tickers para correlación (uno por línea)", value="AAPL\nMSFT\nGOOGL\nAMZN\nMETA")
    period = st.selectbox("Período histórico", ["1y", "2y", "3y", "5y"], index=2)
    analyze_btn = st.button("🔍 Analizar", use_container_width=True, type="primary")

def get_safe(d, key, default="N/A"):
    val = d.get(key, default)
    return val if val not in [None, "None", float("inf"), float("-inf")] else default

def fmt(val, decimals=2, suffix=""):
    if val == "N/A": return "N/A"
    try: return f"{round(float(val), decimals)}{suffix}"
    except: return "N/A"

def fmt_large(val):
    if val == "N/A": return "N/A"
    try:
        v = float(val)
        if v >= 1e12: return f"${v/1e12:.2f}T"
        if v >= 1e9: return f"${v/1e9:.2f}B"
        if v >= 1e6: return f"${v/1e6:.2f}M"
        return f"${v:,.0f}"
    except: return "N/A"

if analyze_btn or True:
    ticker_sym = ticker_input.upper().strip()

    with st.spinner(f"Cargando datos de {ticker_sym}..."):
        try:
            stock = yf.Ticker(ticker_sym)
            info = stock.info
            hist = stock.history(period=period)
        except Exception as e:
            st.error(f"Error al obtener datos: {e}")
            st.stop()

    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        st.warning("No se encontraron datos. Verifica el ticker.")
        st.stop()

    tabs = st.tabs(["🏢 Empresa", "📊 Ratios", "🎯 Valoración", "📉 Correlaciones", "📈 Precio"])

    # ===== TAB 1: EMPRESA =====
    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"{get_safe(info, 'longName')} ({ticker_sym})")
            st.caption(f"🏭 {get_safe(info,'sector')} · {get_safe(info,'industry')} · {get_safe(info,'country')}")
            desc = get_safe(info, "longBusinessSummary")
            if desc != "N/A":
                with st.expander("📋 Descripción de la empresa"):
                    st.write(desc)
        with col2:
            price = get_safe(info, "currentPrice") or get_safe(info, "regularMarketPrice")
            prev = get_safe(info, "previousClose")
            try:
                change = ((float(price) - float(prev)) / float(prev)) * 100
                delta_str = f"{change:+.2f}%"
            except: delta_str = None
            st.metric("💰 Precio actual", fmt(price, 2, " $"), delta=delta_str)
            st.metric("📦 Market Cap", fmt_large(get_safe(info, "marketCap")))
            st.metric("📅 52W High", fmt(get_safe(info, "fiftyTwoWeekHigh"), 2, " $"))
            st.metric("📅 52W Low", fmt(get_safe(info, "fiftyTwoWeekLow"), 2, " $"))

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Empleados", f"{get_safe(info,'fullTimeEmployees'):,}" if get_safe(info,'fullTimeEmployees') != "N/A" else "N/A")
        c2.metric("Sede", get_safe(info, "city"))
        c3.metric("Divisa", get_safe(info, "currency"))
        c4.metric("Exchange", get_safe(info, "exchange"))

    # ===== TAB 2: RATIOS =====
    with tabs[1]:
        st.subheader("📊 Ratios Financieros")

        pe = get_safe(info, "trailingPE")
        pb = get_safe(info, "priceToBook")
        ps = get_safe(info, "priceToSalesTrailing12Months")
        ev_ebitda = get_safe(info, "enterpriseToEbitda")
        roe = get_safe(info, "returnOnEquity")
        roa = get_safe(info, "returnOnAssets")
        profit_margin = get_safe(info, "profitMargins")
        op_margin = get_safe(info, "operatingMargins")
        debt_equity = get_safe(info, "debtToEquity")
        current_ratio = get_safe(info, "currentRatio")
        quick_ratio = get_safe(info, "quickRatio")
        dividend_yield = get_safe(info, "dividendYield")
        peg = get_safe(info, "pegRatio")
        eps = get_safe(info, "trailingEps")
        beta = get_safe(info, "beta")

        st.markdown("#### 💹 Valoración de Mercado")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("P/E (TTM)", fmt(pe))
        c2.metric("P/B", fmt(pb))
        c3.metric("P/S", fmt(ps))
        c4.metric("EV/EBITDA", fmt(ev_ebitda))
        c5.metric("PEG Ratio", fmt(peg))

        st.markdown("#### 💰 Rentabilidad")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ROE", fmt(roe, 2, " %") if roe != "N/A" else "N/A")
        c2.metric("ROA", fmt(roa, 2, " %") if roa != "N/A" else "N/A")
        c3.metric("Margen Neto", fmt(profit_margin, 2, " %") if profit_margin != "N/A" else "N/A")
        c4.metric("Margen Operativo", fmt(op_margin, 2, " %") if op_margin != "N/A" else "N/A")

        st.markdown("#### 🏦 Liquidez y Deuda")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Ratio", fmt(current_ratio))
        c2.metric("Quick Ratio", fmt(quick_ratio))
        c3.metric("Deuda/Equity", fmt(debt_equity))
        c4.metric("Beta", fmt(beta))

        st.markdown("#### 📤 Dividendo y EPS")
        c1, c2 = st.columns(2)
        c1.metric("Dividend Yield", fmt(dividend_yield, 4, " %") if dividend_yield != "N/A" else "N/A")
        c2.metric("EPS (TTM)", fmt(eps, 2, " $"))

        # Radar chart de ratios normalizados
        st.divider()
        st.markdown("#### 🕸️ Perfil financiero (radar)")

        def norm(val, low, high):
            try:
                v = float(val)
                return max(0, min(1, (v - low) / (high - low)))
            except: return 0

        radar_vals = [
            norm(roe if roe == "N/A" else float(roe)*100, 0, 40),
            norm(roa if roa == "N/A" else float(roa)*100, 0, 20),
            norm(profit_margin if profit_margin == "N/A" else float(profit_margin)*100, 0, 30),
            1 - norm(pe, 0, 50),
            1 - norm(debt_equity, 0, 200),
            norm(current_ratio, 0, 3),
        ]
        radar_labels = ["ROE", "ROA", "Margen Neto", "P/E bajo", "Deuda baja", "Liquidez"]
        radar_vals += [radar_vals[0]]
        radar_labels += [radar_labels[0]]

        fig_radar = go.Figure(go.Scatterpolar(
            r=radar_vals, theta=radar_labels, fill="toself",
            line_color="#7c3aed", fillcolor="rgba(124,58,237,0.3)"
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            height=400, paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
            font=dict(color="white")
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ===== TAB 3: VALORACIÓN =====
    with tabs[2]:
        st.subheader("🎯 Métodos de Valoración")

        price_val = get_safe(info, "currentPrice") or get_safe(info, "regularMarketPrice")
        bvps = get_safe(info, "bookValue")
        eps_val = get_safe(info, "trailingEps")
        growth = get_safe(info, "earningsGrowth") or get_safe(info, "revenueGrowth")

        results = {}

        # Graham Number
        try:
            gn = np.sqrt(22.5 * float(eps_val) * float(bvps))
            results["Graham Number"] = round(gn, 2)
        except: results["Graham Number"] = None

        # DCF simplificado
        st.markdown("#### 📐 DCF Simplificado")
        col1, col2, col3 = st.columns(3)
        with col1:
            fcf_raw = get_safe(info, "freeCashflow")
            fcf_default = round(float(fcf_raw)/1e9, 2) if fcf_raw != "N/A" else 1.0
            fcf = st.number_input("Free Cash Flow (B$)", value=fcf_default, step=0.1)
        with col2:
            g_rate = st.slider("Tasa de crecimiento (%)", 0.0, 30.0, 8.0, 0.5)
        with col3:
            discount = st.slider("Tasa de descuento (%)", 5.0, 20.0, 10.0, 0.5)

        shares = get_safe(info, "sharesOutstanding")
        try:
            g = g_rate / 100
            d = discount / 100
            fcf_b = fcf * 1e9
            dcf_val = sum([fcf_b * (1 + g)**i / (1 + d)**i for i in range(1, 11)])
            terminal = (fcf_b * (1 + g)**10 * (1 + 0.03)) / (d - 0.03)
            total_dcf = (dcf_val + terminal) / float(shares)
            results["DCF (10 años)"] = round(total_dcf, 2)
            st.success(f"💡 Valor intrínseco DCF: **${total_dcf:.2f}** por acción")
        except Exception as e:
            st.warning(f"No se pudo calcular DCF: {e}")

        # PEG-based
        try:
            if float(eps_val) > 0 and growth != "N/A":
                peg_val = float(eps_val) * float(growth) * 100 * 15
                results["Valoración PEG (x15 EPS growth)"] = round(peg_val, 2)
        except: pass

        # Tabla de resultados
        if results:
            st.divider()
            st.markdown("#### 📋 Resumen de valoraciones")
            try:
                p = float(price_val)
                rows = []
                for method, val in results.items():
                    if val:
                        upside = ((val - p) / p) * 100
                        signal = "🟢 Infravalorada" if upside > 10 else ("🔴 Sobrevalorada" if upside < -10 else "🟡 Justa")
                        rows.append({"Método": method, "Valor Objetivo ($)": val, "Precio Actual ($)": round(p, 2), "Upside/Downside (%)": round(upside, 1), "Señal": signal})
                if rows:
                    df_val = pd.DataFrame(rows)
                    st.dataframe(df_val, use_container_width=True, hide_index=True)

                    fig_bar = px.bar(df_val, x="Método", y="Valor Objetivo ($)",
                        color="Señal", title="Valor objetivo por método vs precio actual",
                        color_discrete_map={"🟢 Infravalorada": "#22c55e", "🔴 Sobrevalorada": "#ef4444", "🟡 Justa": "#eab308"})
                    fig_bar.add_hline(y=p, line_dash="dash", line_color="white", annotation_text=f"Precio actual: ${p:.2f}")
                    fig_bar.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font=dict(color="white"))
                    st.plotly_chart(fig_bar, use_container_width=True)
            except: pass

    # ===== TAB 4: CORRELACIONES =====
    with tabs[3]:
        st.subheader("📉 Análisis de Correlaciones")
        ticker_list = [t.strip().upper() for t in tickers_corr.strip().split("\n") if t.strip()]
        if ticker_sym not in ticker_list:
            ticker_list.insert(0, ticker_sym)

        with st.spinner("Descargando precios históricos..."):
            try:
                raw = yf.download(ticker_list, period=period, auto_adjust=True, progress=False)["Close"]
                if isinstance(raw, pd.Series):
                    raw = raw.to_frame(name=ticker_list[0])
                returns = raw.pct_change().dropna()
                corr = returns.corr()

                fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                    title="Matriz de correlación de retornos diarios", zmin=-1, zmax=1)
                fig_corr.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font=dict(color="white"))
                st.plotly_chart(fig_corr, use_container_width=True)

                st.markdown("#### 📈 Retornos acumulados")
                cum_returns = (1 + returns).cumprod()
                fig_cum = px.line(cum_returns, title="Retorno acumulado por activo",
                    labels={"value": "Retorno acumulado", "variable": "Ticker"})
                fig_cum.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font=dict(color="white"))
                st.plotly_chart(fig_cum, use_container_width=True)

                st.markdown("#### 📊 Estadísticas de retornos")
                stats = returns.describe().T
                stats["Sharpe (aprox)"] = returns.mean() / returns.std() * np.sqrt(252)
                st.dataframe(stats.round(4), use_container_width=True)

            except Exception as e:
                st.error(f"Error al calcular correlaciones: {e}")

    # ===== TAB 5: PRECIO =====
    with tabs[4]:
        st.subheader(f"📈 Histórico de precio — {ticker_sym}")
        if not hist.empty:
            fig_price = make_subplots(rows=2, cols=1, shared_xaxes=True,
                row_heights=[0.7, 0.3], subplot_titles=["Precio (OHLC)", "Volumen"])
            fig_price.add_trace(go.Candlestick(
                x=hist.index, open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=hist["Close"], name="OHLC"), row=1, col=1)
            fig_price.add_trace(go.Bar(x=hist.index, y=hist["Volume"],
                name="Volumen", marker_color="#7c3aed"), row=2, col=1)
            fig_price.update_layout(
                paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                font=dict(color="white"), xaxis_rangeslider_visible=False, height=600)
            st.plotly_chart(fig_price, use_container_width=True)
        else:
            st.warning("No hay datos históricos disponibles.")
