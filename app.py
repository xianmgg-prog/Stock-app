import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

st.set_page_config(page_title="Analizador de Acciones", layout="wide", page_icon="📈")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab"] { font-size: 16px; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analizador de Acciones — Value Investing")

def search_ticker(query):
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=US&quotesCount=8&newsCount=0"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        quotes = r.json().get("quotes", [])
        return [f"{q.get('symbol','')} — {q.get('longname') or q.get('shortname','')} ({q.get('exchDisp','')})"
                for q in quotes if q.get("quoteType") in ["EQUITY","ETF"]]
    except:
        return []

with st.sidebar:
    st.header("⚙️ Configuración")
    search_query = st.text_input("🔍 Buscar empresa o ticker", value="Apple")
    suggestions = search_ticker(search_query) if search_query else []
    if suggestions:
        selected = st.selectbox("Sugerencias", suggestions)
        ticker_input = selected.split(" — ")[0].strip()
    else:
        ticker_input = search_query.upper().strip()
        st.caption("Usando como ticker directo")
    st.divider()
    tickers_corr = st.text_area("Tickers para correlación", value="AAPL\nMSFT\nGOOGL\nAMZN\nMETA")
    period = st.selectbox("Período histórico", ["1y","2y","3y","5y"], index=2)
    analyze_btn = st.button("🔍 Analizar", use_container_width=True, type="primary")

def get_safe(d, key):
    val = d.get(key)
    return "N/A" if val in [None, float("inf"), float("-inf")] else val

def fmt(val, dec=2, suf=""):
    if val == "N/A": return "N/A"
    try: return f"{round(float(val), dec)}{suf}"
    except: return "N/A"

def fmt_large(val):
    if val == "N/A": return "N/A"
