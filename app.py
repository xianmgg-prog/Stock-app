# =========================
# CARGA DE DATOS PRINCIPALES
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

# =========================
# CABECERA
# =========================
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

# =========================
# TABS PRINCIPALES
# =========================
tab_emp, tab_rat, tab_val, tab_bench, tab_corr, tab_price = st.tabs(
    ["🏢 Empresa", "📊 Ratios", "🎯 Valoración", "📚 Benchmarks", "📉 Correlaciones", "📈 Precio"]
)

# ========= TAB 1: EMPRESA =========
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

# ========= TAB 2: RATIOS =========
with tab_rat:
    st.subheader("Ratios clave")

    pe = safe_float(info.get("trailingPE"))
    fwd_pe = safe_float(info.get("forwardPE"))
    pb = safe_float(info.get("priceToBook"))
    ps = safe_float(info.get("priceToSalesTrailing12Months"))
    roe = safe_float(info.get("returnOnEquity"))
    roa = safe_float(info.get("returnOnAssets"))
    profit_margin = safe_float(info.get("profitMargins"))
    op_margin = safe_float(info.get("operatingMargins"))
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

    # Radar simple
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

# ========= TAB 3: VALORACIÓN =========
with tab_val:
    st.subheader("Valoración intrínseca por métodos")

    methods, current_price = compute_valuations(info)

    if not methods:
        st.warning("No se pudo calcular ninguna valoración por falta de datos.")
    else:
        # Tabla HTML de valoraciones
        rows_html = ""
        for m in methods:
            name = m["name"]
            val = m["value"]
            params = m["params"]
            if current_price:
                upside = (val - current_price) / current_price * 100
            else:
                upside = None
            margin_str, css_class = margin_badge(upside)
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

        # Gráfico barras valor objetivo vs precio
        df_val = pd.DataFrame(
            {
                "Método": [m["name"] for m in methods],
                "Valor": [m["value"] for m in methods],
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
            line_color="red",
            annotation_text=f"Precio: {current_price:.2f}",
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ========= TAB 4: BENCHMARKS =========
with tab_bench:
    st.subheader("Comparación con benchmarks del sector")

    peers = get_benchmark_list(info, ticker_sym)
    if not peers:
        st.info("No hay benchmarks definidos para este sector. Puedes ampliar el diccionario DEFAULT_BENCHMARKS en el código.")
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

            # Gráfico P/E y ROE comparados
            st.markdown("#### P/E y ROE vs peers")
            fig_comp = make_subplots(specs=[[{"secondary_y": True}]])
            fig_comp.add_trace(
                go.Bar(
                    x=df_bench["Ticker"],
                    y=df_bench["pe"],
                    name="P/E",
                    marker_color=ACCENT_BLUE,
                ),
                secondary_y=False,
            )
            fig_comp.add_trace(
                go.Scatter(
                    x=df_bench["Ticker"],
                    y=df_bench["roe"] * 100,
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

# ========= TAB 5: CORRELACIONES =========
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

# ========= TAB 6: PRECIO =========
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
