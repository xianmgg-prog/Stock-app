"""
╔══════════════════════════════════════════════════════════════╗
║          EQUITY TERMINAL — Value Investing Dashboard         ║
║          Bloomberg-style professional UI                     ║
╚══════════════════════════════════════════════════════════════╝
Stack: Python · Streamlit · yfinance · Plotly · Pandas · NumPy
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import math
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Equity Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  DESIGN SYSTEM — BLOOMBERG DARK THEME
# ─────────────────────────────────────────────
COLORS = {
    "bg_primary":    "#0A0E1A",
    "bg_secondary":  "#0F1525",
    "bg_card":       "#141B2E",
    "bg_hover":      "#1A2340",
    "border":        "#1E2D4A",
    "border_accent": "#2A3F6E",
    "text_primary":  "#E8EDF5",
    "text_secondary":"#8A9BB5",
    "text_muted":    "#4A5A78",
    "accent_blue":   "#1E90FF",
    "accent_cyan":   "#00D4FF",
    "accent_gold":   "#FFB800",
    "accent_green":  "#00C896",
    "accent_red":    "#FF4560",
    "accent_purple": "#7B5EA7",
    "gradient_1":    "#1E90FF",
    "gradient_2":    "#00D4FF",
}

# Base style dicts — referenced individually to avoid duplicate-key conflicts
_AXIS_STYLE = dict(
    gridcolor=COLORS["border"], gridwidth=0.5,
    linecolor=COLORS["border_accent"], tickcolor=COLORS["text_muted"],
    tickfont=dict(color=COLORS["text_muted"], size=10),
    zerolinecolor=COLORS["border"],
)
_LEGEND_STYLE = dict(
    bgcolor="rgba(20,27,46,0.8)", bordercolor=COLORS["border_accent"],
    borderwidth=1, font=dict(color=COLORS["text_secondary"], size=10),
)
_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'Courier New', 'IBM Plex Mono', monospace", color=COLORS["text_secondary"], size=11),
    title=dict(font=dict(color=COLORS["text_primary"], size=14, family="'Courier New', monospace")),
    xaxis=_AXIS_STYLE,
    yaxis=_AXIS_STYLE,
    legend=_LEGEND_STYLE,
    hoverlabel=dict(
        bgcolor=COLORS["bg_card"], bordercolor=COLORS["accent_blue"],
        font=dict(color=COLORS["text_primary"], size=11),
    ),
    margin=dict(l=40, r=20, t=40, b=40),
)

def base_layout(**overrides):
    """Return a merged layout dict with base styles plus caller overrides."""
    layout = dict(_BASE_LAYOUT)
    layout.update(overrides)
    return layout

CSS = f"""
<style>
  /* ── IMPORTS ── */
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

  /* ── ROOT TOKENS ── */
  :root {{
    --bg-primary:    {COLORS['bg_primary']};
    --bg-secondary:  {COLORS['bg_secondary']};
    --bg-card:       {COLORS['bg_card']};
    --border:        {COLORS['border']};
    --border-accent: {COLORS['border_accent']};
    --text-primary:  {COLORS['text_primary']};
    --text-secondary:{COLORS['text_secondary']};
    --text-muted:    {COLORS['text_muted']};
    --accent-blue:   {COLORS['accent_blue']};
    --accent-cyan:   {COLORS['accent_cyan']};
    --accent-gold:   {COLORS['accent_gold']};
    --accent-green:  {COLORS['accent_green']};
    --accent-red:    {COLORS['accent_red']};
  }}

  /* ── GLOBAL RESET ── */
  html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', 'Helvetica Neue', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
  }}

  /* ── APP BACKGROUND ── */
  .stApp {{
    background: linear-gradient(135deg, #080C18 0%, #0A0E1A 50%, #0C1220 100%) !important;
  }}

  /* ── SCANLINE OVERLAY ── */
  .stApp::before {{
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.03) 2px,
      rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
    z-index: 0;
  }}

  /* ── SIDEBAR ── */
  section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0A0E1A 0%, #0C1422 100%) !important;
    border-right: 1px solid var(--border-accent) !important;
    min-width: 300px !important;
  }}
  section[data-testid="stSidebar"] > div {{
    padding-top: 1rem !important;
  }}

  /* ── SIDEBAR HEADER ── */
  .sidebar-logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border: 1px solid var(--border-accent);
    border-radius: 4px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, rgba(30,144,255,0.08), rgba(0,212,255,0.04));
  }}
  .sidebar-logo .logo-mark {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 20px;
    color: var(--accent-cyan);
    font-weight: 600;
    letter-spacing: -1px;
  }}
  .sidebar-logo .logo-text {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--text-secondary);
    letter-spacing: 2px;
    text-transform: uppercase;
    line-height: 1.3;
  }}
  .sidebar-logo .logo-sub {{
    font-size: 9px;
    color: var(--text-muted);
    letter-spacing: 1px;
  }}

  /* ── SECTION LABELS ── */
  .sidebar-section {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 4px;
    margin: 16px 0 8px 0;
  }}

  /* ── INPUTS ── */
  .stTextInput input, .stSelectbox select, .stMultiSelect > div {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 3px !important;
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
  }}
  .stTextInput input:focus {{
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 1px var(--accent-blue), 0 0 12px rgba(30,144,255,0.15) !important;
    outline: none !important;
  }}

  /* ── PRIMARY BUTTON ── */
  .stButton > button[kind="primary"], .stButton > button {{
    background: linear-gradient(135deg, var(--accent-blue), #1470CC) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 8px 20px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(30,144,255,0.25) !important;
  }}
  .stButton > button:hover {{
    background: linear-gradient(135deg, #2AA0FF, #1E90FF) !important;
    box-shadow: 0 4px 20px rgba(30,144,255,0.4) !important;
    transform: translateY(-1px) !important;
  }}

  /* ── TABS ── */
  .stTabs [data-baseweb="tab-list"] {{
    background: var(--bg-secondary) !important;
    border-bottom: 1px solid var(--border-accent) !important;
    gap: 0 !important;
    padding: 0 !important;
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-muted) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    transition: all 0.2s !important;
  }}
  .stTabs [data-baseweb="tab"]:hover {{
    color: var(--text-secondary) !important;
    background: rgba(30,144,255,0.05) !important;
  }}
  .stTabs [aria-selected="true"] {{
    color: var(--accent-cyan) !important;
    border-bottom: 2px solid var(--accent-cyan) !important;
    background: rgba(0,212,255,0.05) !important;
  }}
  .stTabs [data-baseweb="tab-panel"] {{
    background: transparent !important;
    padding: 20px 0 !important;
  }}

  /* ── METRIC CARDS ── */
  .metric-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-blue);
    border-radius: 4px;
    padding: 14px 16px;
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
  }}
  .metric-card::before {{
    content: '';
    position: absolute; top: 0; right: 0;
    width: 60px; height: 60px;
    background: radial-gradient(circle at top right, rgba(30,144,255,0.06), transparent);
  }}
  .metric-card:hover {{
    border-color: var(--border-accent);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  }}
  .metric-card.green  {{ border-left-color: var(--accent-green); }}
  .metric-card.red    {{ border-left-color: var(--accent-red); }}
  .metric-card.gold   {{ border-left-color: var(--accent-gold); }}
  .metric-card.purple {{ border-left-color: var(--accent-purple); }}
  .metric-card.cyan   {{ border-left-color: var(--accent-cyan); }}

  .metric-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 6px;
  }}
  .metric-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -0.5px;
  }}
  .metric-sub {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    margin-top: 4px;
  }}
  .metric-delta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    margin-top: 4px;
  }}
  .delta-up   {{ color: var(--accent-green); }}
  .delta-down {{ color: var(--accent-red); }}

  /* ── INFO PANELS ── */
  .info-panel {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 12px;
  }}
  .info-panel h4 {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent-cyan);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 12px;
  }}
  .info-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px solid rgba(30,45,74,0.5);
    font-size: 12px;
  }}
  .info-row:last-child {{ border-bottom: none; }}
  .info-key {{
    font-family: 'IBM Plex Mono', monospace;
    color: var(--text-muted);
    font-size: 11px;
  }}
  .info-val {{
    font-family: 'IBM Plex Mono', monospace;
    color: var(--text-primary);
    font-weight: 500;
    font-size: 12px;
  }}

  /* ── TICKER HEADER ── */
  .ticker-header {{
    background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
    border: 1px solid var(--border-accent);
    border-radius: 4px;
    padding: 20px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
  }}
  .ticker-header::after {{
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan), transparent);
  }}
  .ticker-symbol {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -1px;
  }}
  .ticker-name {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 2px;
  }}
  .ticker-exchange {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: var(--accent-gold);
    text-transform: uppercase;
    margin-top: 4px;
  }}
  .ticker-price-block {{
    text-align: right;
  }}
  .ticker-price {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 32px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -1px;
  }}
  .ticker-change-up  {{ font-family: 'IBM Plex Mono', monospace; font-size: 14px; color: var(--accent-green); font-weight: 500; }}
  .ticker-change-dn  {{ font-family: 'IBM Plex Mono', monospace; font-size: 14px; color: var(--accent-red);   font-weight: 500; }}

  /* ── STATUS CHIPS ── */
  .chip {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-weight: 600;
    margin-left: 8px;
  }}
  .chip-green  {{ background: rgba(0,200,150,0.12); color: var(--accent-green); border: 1px solid rgba(0,200,150,0.3); }}
  .chip-red    {{ background: rgba(255,69,96,0.12);  color: var(--accent-red);   border: 1px solid rgba(255,69,96,0.3); }}
  .chip-gold   {{ background: rgba(255,184,0,0.12);  color: var(--accent-gold);  border: 1px solid rgba(255,184,0,0.3); }}
  .chip-blue   {{ background: rgba(30,144,255,0.12); color: var(--accent-blue);  border: 1px solid rgba(30,144,255,0.3); }}

  /* ── VALUATION TABLE ── */
  .val-table {{
    width: 100%;
    border-collapse: collapse;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
  }}
  .val-table th {{
    background: var(--bg-secondary);
    color: var(--text-muted);
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border-accent);
  }}
  .val-table td {{
    padding: 9px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);
    vertical-align: middle;
  }}
  .val-table tr:hover td {{ background: var(--bg-hover); }}
  .val-table td.val-method {{ color: var(--text-primary); font-weight: 500; }}
  .val-table td.val-num {{ color: var(--accent-cyan); text-align: right; }}
  .val-table td.margin-good  {{ color: var(--accent-green); font-weight: 600; text-align: right; }}
  .val-table td.margin-ok    {{ color: var(--accent-gold);  font-weight: 600; text-align: right; }}
  .val-table td.margin-poor  {{ color: var(--accent-red);   font-weight: 600; text-align: right; }}

  /* ── MISC STREAMLIT OVERRIDES ── */
  div[data-testid="stMetric"] {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px;
  }}
  div[data-testid="stMetric"] label {{ color: var(--text-muted) !important; font-size: 10px !important; }}
  div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ color: var(--text-primary) !important; }}

  .stAlert {{ background: rgba(30,144,255,0.06) !important; border: 1px solid rgba(30,144,255,0.2) !important; border-radius: 4px !important; }}
  .stSuccess {{ background: rgba(0,200,150,0.06) !important; border: 1px solid rgba(0,200,150,0.2) !important; }}
  .stWarning {{ background: rgba(255,184,0,0.06) !important; border: 1px solid rgba(255,184,0,0.2) !important; }}
  .stError   {{ background: rgba(255,69,96,0.06)  !important; border: 1px solid rgba(255,69,96,0.2) !important; }}

  div.stSelectbox > div[data-baseweb="select"] > div {{
    background: var(--bg-card) !important;
    border-color: var(--border-accent) !important;
    font-family: 'IBM Plex Mono', monospace !important;
  }}

  /* ── SCROLLBAR ── */
  ::-webkit-scrollbar {{ width: 4px; height: 4px; }}
  ::-webkit-scrollbar-track {{ background: var(--bg-primary); }}
  ::-webkit-scrollbar-thumb {{ background: var(--border-accent); border-radius: 2px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: var(--accent-blue); }}

  /* ── DIVIDER ── */
  hr {{ border-color: var(--border) !important; margin: 12px 0 !important; }}

  /* ── BLINKING CURSOR ── */
  @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0}} }}
  .cursor {{ animation: blink 1.2s infinite; color: var(--accent-cyan); }}

  /* ── TOOLTIP HELPER ── */
  .tooltip-text {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    color: var(--text-muted);
    font-style: italic;
    margin-top: 2px;
  }}

  /* header bar line */
  .section-divider {{
    height: 1px;
    background: linear-gradient(90deg, var(--accent-blue), transparent);
    margin: 16px 0;
    opacity: 0.4;
  }}

  /* loading pill */
  .loading-pill {{
    display: inline-block;
    background: rgba(30,144,255,0.1);
    border: 1px solid rgba(30,144,255,0.3);
    color: var(--accent-blue);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    padding: 4px 10px;
    border-radius: 2px;
    text-transform: uppercase;
  }}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def fmt(val, fmt_str="{:.2f}", fallback="N/A"):
    """Safe format helper."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return fallback
    try:
        return fmt_str.format(val)
    except Exception:
        return str(val)


def fmt_large(val, fallback="N/A"):
    """Format large numbers with B/M/K suffixes."""
    if val is None:
        return fallback
    try:
        val = float(val)
        if abs(val) >= 1e12:
            return f"{val/1e12:.2f}T"
        if abs(val) >= 1e9:
            return f"{val/1e9:.2f}B"
        if abs(val) >= 1e6:
            return f"{val/1e6:.2f}M"
        if abs(val) >= 1e3:
            return f"{val/1e3:.2f}K"
        return f"{val:.2f}"
    except Exception:
        return fallback


def safe_get(d, key, fallback=None):
    val = d.get(key, fallback)
    if val == "" or val is None:
        return fallback
    try:
        if isinstance(val, float) and math.isnan(val):
            return fallback
    except Exception:
        pass
    return val


def metric_card(label, value, sub=None, delta=None, color="blue"):
    delta_html = ""
    if delta is not None:
        cls = "delta-up" if str(delta).startswith("+") else "delta-down"
        delta_html = f'<div class="metric-delta {cls}">{delta}</div>'
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="metric-card {color}">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      {sub_html}
      {delta_html}
    </div>
    """


def chip(text, style="blue"):
    return f'<span class="chip chip-{style}">{text}</span>'


def section_header(title):
    st.markdown(f"""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:2px;
                text-transform:uppercase;color:{COLORS['text_muted']};
                border-bottom:1px solid {COLORS['border']};padding-bottom:6px;margin:20px 0 14px 0;">
      <span style="color:{COLORS['accent_cyan']};margin-right:8px;">▸</span>{title}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  YAHOO FINANCE SEARCH
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def search_companies(query: str):
    """Search Yahoo Finance for company suggestions."""
    if len(query) < 2:
        return []
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&lang=en-US&region=US&quotesCount=8&newsCount=0"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        results = []
        for q in data.get("quotes", []):
            symbol = q.get("symbol", "")
            name = q.get("longname") or q.get("shortname", symbol)
            exchange = q.get("exchDisp", "")
            qtype = q.get("quoteType", "")
            if qtype in ("EQUITY", "ETF") and symbol:
                results.append({"symbol": symbol, "name": name, "exchange": exchange})
        return results
    except Exception:
        return []


@st.cache_data(ttl=60, show_spinner=False)
def load_ticker_info(ticker: str) -> dict:
    """Load ticker info dict (serializable)."""
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


@st.cache_data(ttl=60, show_spinner=False)
def load_ticker_history(ticker: str, period: str) -> pd.DataFrame:
    """Load price history for a given period (serializable)."""
    try:
        df = yf.Ticker(ticker).history(period=period)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    # Logo block
    st.markdown("""
    <div class="sidebar-logo">
      <div class="logo-mark">▶▷</div>
      <div>
        <div class="logo-text">Equity Terminal</div>
        <div class="logo-sub">Value Investing Suite · v2.0</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SEARCH ──
    st.markdown('<div class="sidebar-section">Security Search</div>', unsafe_allow_html=True)
    search_query = st.text_input(
        "", placeholder="Search company or ticker…",
        label_visibility="collapsed",
        key="search_input"
    )

    selected_ticker = st.session_state.get("selected_ticker", "")

    if search_query:
        with st.spinner(""):
            suggestions = search_companies(search_query)
        if suggestions:
            opts = {f"{s['symbol']} — {s['name']} ({s['exchange']})": s["symbol"] for s in suggestions}
            chosen = st.selectbox(
                "", options=list(opts.keys()),
                label_visibility="collapsed",
                key="suggestion_box"
            )
            if chosen:
                selected_ticker = opts[chosen]
                st.session_state["selected_ticker"] = selected_ticker
        else:
            st.markdown('<div class="tooltip-text">No results found.</div>', unsafe_allow_html=True)

    # Manual override
    manual = st.text_input("", placeholder="Or enter ticker directly (e.g. AAPL)",
                           label_visibility="collapsed", key="manual_ticker")
    if manual:
        selected_ticker = manual.upper().strip()
        st.session_state["selected_ticker"] = selected_ticker

    if selected_ticker:
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                    color:{COLORS['accent_cyan']};padding:6px 10px;
                    background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.2);
                    border-radius:3px;margin-top:4px;">
          ● &nbsp;{selected_ticker}
        </div>
        """, unsafe_allow_html=True)

    # ── CORRELATION ──
    st.markdown('<div class="sidebar-section">Correlation</div>', unsafe_allow_html=True)
    corr_input = st.text_input("", placeholder="Tickers: SPY, QQQ, MSFT…",
                               label_visibility="collapsed", key="corr_tickers")
    corr_tickers = [t.strip().upper() for t in corr_input.split(",") if t.strip()] if corr_input else []

    # ── PERIOD ──
    st.markdown('<div class="sidebar-section">Historical Period</div>', unsafe_allow_html=True)
    period_map = {
        "6 Months":  "6mo",
        "1 Year":    "1y",
        "2 Years":   "2y",
        "5 Years":   "5y",
        "10 Years":  "10y",
        "Max":       "max",
    }
    period_label = st.selectbox("", list(period_map.keys()), index=1,
                                label_visibility="collapsed", key="period_select")
    selected_period = period_map[period_label]

    st.markdown("<br>", unsafe_allow_html=True)

    analyze_btn = st.button("⬡  ANALYZE", type="primary")

    # ── CLOCK ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:{COLORS['text_muted']};
                text-align:center;padding:8px;border-top:1px solid {COLORS['border']};">
      {datetime.utcnow().strftime('%Y-%m-%d  %H:%M UTC')}
      <br>Data via Yahoo Finance · Real-time
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN AREA — IDLE STATE
# ─────────────────────────────────────────────

if not selected_ticker:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:70vh;text-align:center;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:48px;color:{COLORS['border_accent']};
                  letter-spacing:-2px;margin-bottom:12px;">▶▷</div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:20px;color:{COLORS['text_secondary']};
                  letter-spacing:4px;text-transform:uppercase;">EQUITY TERMINAL</div>
      <div style="font-family:'IBM Plex Sans',sans-serif;font-size:13px;color:{COLORS['text_muted']};
                  margin-top:8px;max-width:400px;line-height:1.7;">
        Professional value investing analysis.<br>Search for a company in the sidebar to begin.
      </div>
      <div style="margin-top:32px;display:flex;gap:16px;flex-wrap:wrap;justify-content:center;">
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};border:1px solid {COLORS['border']};padding:4px 10px;border-radius:2px;">AAPL</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};border:1px solid {COLORS['border']};padding:4px 10px;border-radius:2px;">MSFT</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};border:1px solid {COLORS['border']};padding:4px 10px;border-radius:2px;">GOOGL</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};border:1px solid {COLORS['border']};padding:4px 10px;border-radius:2px;">AMZN</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};border:1px solid {COLORS['border']};padding:4px 10px;border-radius:2px;">NVDA</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};border:1px solid {COLORS['border']};padding:4px 10px;border-radius:2px;">BRK-B</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────

if analyze_btn or selected_ticker:
    with st.spinner(f"Fetching data for {selected_ticker}…"):
        info   = load_ticker_info(selected_ticker)
        hist_1y = load_ticker_history(selected_ticker, "1y")

    if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None):
        if hist_1y.empty:
            st.error(f"⚠  Could not retrieve data for **{selected_ticker}**. "
                     "Please verify the ticker symbol and try again.")
            st.stop()

    # ── TICKER HEADER ──
    price     = safe_get(info, "currentPrice") or safe_get(info, "regularMarketPrice", 0)
    prev_close = safe_get(info, "previousClose", price or 1)
    change     = (price - prev_close) if price and prev_close else 0
    pct_change = (change / prev_close * 100) if prev_close else 0
    chg_sign   = "+" if change >= 0 else ""
    chg_class  = "ticker-change-up" if change >= 0 else "ticker-change-dn"
    chg_chip   = chip("▲ GAIN", "green") if change >= 0 else chip("▼ LOSS", "red")

    company_name = safe_get(info, "longName") or safe_get(info, "shortName", selected_ticker)
    sector       = safe_get(info, "sector", "—")
    industry     = safe_get(info, "industry", "—")
    exchange     = safe_get(info, "exchange", "—")
    currency     = safe_get(info, "currency", "USD")
    mktcap       = safe_get(info, "marketCap")
    vol          = safe_get(info, "volume")
    day_lo       = safe_get(info, "dayLow")
    day_hi       = safe_get(info, "dayHigh")
    week52_lo    = safe_get(info, "fiftyTwoWeekLow")
    week52_hi    = safe_get(info, "fiftyTwoWeekHigh")

    st.markdown(f"""
    <div class="ticker-header">
      <div>
        <div class="ticker-symbol">{selected_ticker}
          {chg_chip}
          {chip(exchange, "gold") if exchange != "—" else ""}
        </div>
        <div class="ticker-name">{company_name}</div>
        <div class="ticker-exchange">{sector} &nbsp;·&nbsp; {industry}</div>
      </div>
      <div class="ticker-price-block">
        <div class="ticker-price">{currency} {fmt(price, "{:,.2f}")}</div>
        <div class="{chg_class}">{chg_sign}{fmt(change, "{:+.2f}")} &nbsp; ({chg_sign}{fmt(pct_change, "{:.2f}")}%)</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};margin-top:4px;">
          Vol {fmt_large(vol)} &nbsp;·&nbsp; Mkt Cap {fmt_large(mktcap)}
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};">
          Day {fmt(day_lo, '{:.2f}')} – {fmt(day_hi, '{:.2f}')}
          &nbsp;·&nbsp; 52W {fmt(week52_lo, '{:.2f}')} – {fmt(week52_hi, '{:.2f}')}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──
    tab_company, tab_ratios, tab_valuation, tab_corr, tab_price = st.tabs([
        "◈  Company",
        "◈  Financials",
        "◈  Valuation",
        "◈  Correlations",
        "◈  Price Chart",
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — COMPANY
    # ══════════════════════════════════════════
    with tab_company:
        section_header("Company Overview")

        col1, col2 = st.columns([1.1, 1])

        with col1:
            # Key facts
            facts = {
                "CEO":           safe_get(info, "companyOfficers", [{}])[0].get("name") if safe_get(info, "companyOfficers") else "—",
                "Employees":     fmt_large(safe_get(info, "fullTimeEmployees")),
                "Country":       safe_get(info, "country", "—"),
                "City":          safe_get(info, "city", "—"),
                "Website":       safe_get(info, "website", "—"),
                "IPO Year":      safe_get(info, "ipoExpectedDate", "—"),
                "Fiscal Year End": safe_get(info, "fiscalYearEnd", "—"),
            }
            rows_html = ""
            for k, v in facts.items():
                if v and v != "—" and v != "N/A":
                    rows_html += f'<div class="info-row"><span class="info-key">{k}</span><span class="info-val">{v}</span></div>'

            st.markdown(f"""
            <div class="info-panel">
              <h4>Identity</h4>
              {rows_html}
            </div>
            """, unsafe_allow_html=True)

            # Business summary
            summary = safe_get(info, "longBusinessSummary", "No description available.")
            section_header("Business Summary")
            st.markdown(f"""
            <div style="font-family:'IBM Plex Sans',sans-serif;font-size:12px;line-height:1.75;
                        color:{COLORS['text_secondary']};background:{COLORS['bg_card']};
                        border:1px solid {COLORS['border']};border-radius:4px;padding:16px;">
              {summary}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            section_header("Key Metrics Snapshot")

            metrics = [
                ("Market Cap",     fmt_large(mktcap),                              "blue"),
                ("Enterprise Value",fmt_large(safe_get(info, "enterpriseValue")),  "cyan"),
                ("Revenue (TTM)",   fmt_large(safe_get(info, "totalRevenue")),      "green"),
                ("Net Income (TTM)",fmt_large(safe_get(info, "netIncomeToCommon")), "gold"),
                ("Gross Profit",    fmt_large(safe_get(info, "grossProfits")),      "purple"),
                ("Free Cash Flow",  fmt_large(safe_get(info, "freeCashflow")),      "green"),
                ("Total Cash",      fmt_large(safe_get(info, "totalCash")),         "blue"),
                ("Total Debt",      fmt_large(safe_get(info, "totalDebt")),         "red"),
            ]

            for i in range(0, len(metrics), 2):
                c1, c2 = st.columns(2)
                lbl, val, col = metrics[i]
                c1.markdown(metric_card(lbl, val, color=col), unsafe_allow_html=True)
                if i + 1 < len(metrics):
                    lbl2, val2, col2_ = metrics[i + 1]
                    c2.markdown(metric_card(lbl2, val2, color=col2_), unsafe_allow_html=True)
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — FINANCIAL RATIOS
    # ══════════════════════════════════════════
    with tab_ratios:
        section_header("Valuation Ratios")

        # Tooltips / descriptions
        RATIO_TIPS = {
            "P/E Ratio":       "Price / Earnings. < 15 historically cheap, > 25 expensive.",
            "Forward P/E":     "Uses next-year earnings estimates. Lower = more value.",
            "P/B Ratio":       "Price / Book Value. Graham considers < 1.5 attractive.",
            "P/S Ratio":       "Price / Sales. Useful for unprofitable companies.",
            "EV/EBITDA":       "Enterprise multiple. < 10 often considered undervalued.",
            "EV/Revenue":      "Useful for comparing across different capital structures.",
        }

        val_ratios = {
            "P/E Ratio":   safe_get(info, "trailingPE"),
            "Forward P/E": safe_get(info, "forwardPE"),
            "P/B Ratio":   safe_get(info, "priceToBook"),
            "P/S Ratio":   safe_get(info, "priceToSalesTrailing12Months"),
            "EV/EBITDA":   safe_get(info, "enterpriseToEbitda"),
            "EV/Revenue":  safe_get(info, "enterpriseToRevenue"),
        }

        cols = st.columns(3)
        for i, (name, val) in enumerate(val_ratios.items()):
            fval = fmt(val, "{:.2f}")
            tip  = RATIO_TIPS.get(name, "")
            cols[i % 3].markdown(metric_card(name, fval, sub=tip[:40]+"…" if len(tip) > 40 else tip, color="blue"),
                                 unsafe_allow_html=True)

        section_header("Profitability")

        prof_ratios = {
            "ROE":            safe_get(info, "returnOnEquity"),
            "ROA":            safe_get(info, "returnOnAssets"),
            "Gross Margin":   safe_get(info, "grossMargins"),
            "Operating Margin": safe_get(info, "operatingMargins"),
            "Net Margin":     safe_get(info, "profitMargins"),
            "Revenue Growth": safe_get(info, "revenueGrowth"),
            "Earnings Growth":safe_get(info, "earningsGrowth"),
            "EBITDA Margin":  safe_get(info, "ebitdaMargins"),
        }

        prof_tips = {
            "ROE":            "Return on Equity. > 15% is strong.",
            "ROA":            "Return on Assets. > 5% is healthy.",
            "Gross Margin":   "Revenue minus COGS / Revenue.",
            "Operating Margin":"EBIT / Revenue. Core profitability.",
            "Net Margin":     "Net income / Revenue. Bottom line.",
            "Revenue Growth": "YoY revenue growth rate.",
            "Earnings Growth":"YoY earnings growth rate.",
            "EBITDA Margin":  "EBITDA / Revenue.",
        }

        cols2 = st.columns(4)
        for i, (name, val) in enumerate(prof_ratios.items()):
            pct_val = fmt(val * 100, "{:.1f}%") if val is not None else "N/A"
            tip = prof_tips.get(name, "")
            color = "green" if val and val > 0 else "red"
            cols2[i % 4].markdown(metric_card(name, pct_val, sub=tip[:40]+"…" if len(tip) > 40 else tip, color=color),
                                  unsafe_allow_html=True)

        section_header("Debt & Liquidity")

        debt_ratios = {
            "Debt/Equity":       safe_get(info, "debtToEquity"),
            "Current Ratio":     safe_get(info, "currentRatio"),
            "Quick Ratio":       safe_get(info, "quickRatio"),
            "Interest Coverage": safe_get(info, "interestCoverage"),
        }
        debt_tips = {
            "Debt/Equity":       "Total debt / equity. < 1 is conservative.",
            "Current Ratio":     "Current assets / liabilities. > 1.5 is healthy.",
            "Quick Ratio":       "Liquid assets / liabilities. > 1 is safe.",
            "Interest Coverage": "EBIT / interest. > 3 comfortable.",
        }
        cols3 = st.columns(4)
        for i, (name, val) in enumerate(debt_ratios.items()):
            fval = fmt(val, "{:.2f}")
            tip  = debt_tips.get(name, "")
            cols3[i].markdown(metric_card(name, fval, sub=tip[:50]+"…" if len(tip)>50 else tip, color="gold"),
                              unsafe_allow_html=True)

        # Radar Chart
        section_header("Ratio Radar")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        def norm(val, low, high):
            if val is None: return 0.0
            return max(0.0, min(1.0, (val - low) / (high - low)))

        radar_metrics = {
            "ROE":          norm(safe_get(info, "returnOnEquity"),             0,    0.4),
            "ROA":          norm(safe_get(info, "returnOnAssets"),             0,    0.2),
            "Net Margin":   norm(safe_get(info, "profitMargins"),              0,    0.3),
            "Low P/E":      norm(1 / (safe_get(info, "trailingPE") or 999),   0,    0.1),
            "Low Debt/Eq":  norm(1 / ((safe_get(info, "debtToEquity") or 100)/100 + 0.01), 0, 1),
            "Current Ratio":norm(safe_get(info, "currentRatio"),              0,    3),
        }

        categories = list(radar_metrics.keys())
        values     = list(radar_metrics.values())
        values_    = values + [values[0]]
        categories_ = categories + [categories[0]]

        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=values_, theta=categories_,
            fill="toself",
            fillcolor=f"rgba(30,144,255,0.15)",
            line=dict(color=COLORS["accent_blue"], width=2),
            name=selected_ticker,
        ))
        radar_fig.update_layout(base_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                angularaxis=dict(
                    tickfont=dict(size=10, color=COLORS["text_secondary"],
                                  family="'IBM Plex Mono',monospace"),
                    linecolor=COLORS["border_accent"],
                ),
                radialaxis=dict(
                    visible=True, range=[0, 1],
                    tickfont=dict(size=9, color=COLORS["text_muted"]),
                    linecolor=COLORS["border"],
                    gridcolor=COLORS["border"],
                ),
            ),
            showlegend=False,
            height=340,
            margin=dict(l=60, r=60, t=30, b=30),
        ))
        st.plotly_chart(radar_fig, use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 3 — VALUATION
    # ══════════════════════════════════════════
    with tab_valuation:
        section_header("Intrinsic Value Estimates")

        current_price = price or 0

        # ── DCF ──
        eps         = safe_get(info, "trailingEps") or 0
        growth_rate = safe_get(info, "earningsGrowth") or safe_get(info, "revenueGrowth") or 0.05
        growth_rate = min(max(growth_rate, 0), 0.30)
        discount    = 0.10
        terminal_g  = 0.025

        projected_eps = eps
        total_pv      = 0
        years         = 10
        for y in range(1, years + 1):
            projected_eps *= (1 + growth_rate)
            total_pv += projected_eps / ((1 + discount) ** y)
        terminal_val = projected_eps * (1 + terminal_g) / (discount - terminal_g)
        terminal_pv  = terminal_val / ((1 + discount) ** years)
        dcf_value    = total_pv + terminal_pv

        shares       = safe_get(info, "sharesOutstanding") or 1
        fcf          = safe_get(info, "freeCashflow") or 0
        fcf_ps       = fcf / shares if shares else 0
        fcf_growth   = growth_rate
        fcf_total_pv = 0
        proj_fcf     = fcf_ps
        for y in range(1, years + 1):
            proj_fcf  *= (1 + fcf_growth)
            fcf_total_pv += proj_fcf / ((1 + discount) ** y)
        fcf_terminal = proj_fcf * (1 + terminal_g) / (discount - terminal_g)
        fcf_value    = fcf_total_pv + fcf_terminal / ((1 + discount) ** years)

        # ── EV/EBITDA ──
        ebitda       = safe_get(info, "ebitda") or 0
        ev_mult      = 12
        ev_ebitda_ev = ebitda * ev_mult
        net_debt     = (safe_get(info, "totalDebt") or 0) - (safe_get(info, "totalCash") or 0)
        equity_from_ev = (ev_ebitda_ev - net_debt) / shares if shares else 0

        # ── P/S ──
        rev          = safe_get(info, "totalRevenue") or 0
        sector_ps    = safe_get(info, "priceToSalesTrailing12Months") or 2.0
        ps_est       = (rev * sector_ps) / shares if shares else 0

        # ── P/B ──
        bvps         = safe_get(info, "bookValue") or 0
        pb_mult      = safe_get(info, "priceToBook") or 2.0
        pb_est       = bvps * pb_mult

        # ── Graham Number ──
        graham_num   = math.sqrt(22.5 * max(eps, 0) * max(bvps, 0)) if eps > 0 and bvps > 0 else None

        def margin_class(val, price):
            if val <= 0 or price <= 0:
                return "margin-poor", "N/A"
            ms = (val - price) / val * 100
            if ms >= 30:
                return "margin-good",  f"+{ms:.1f}%"
            elif ms >= 10:
                return "margin-ok",    f"+{ms:.1f}%"
            else:
                pct = abs(ms)
                return "margin-poor",  f"-{pct:.1f}%"

        rows = [
            ("DCF (EPS-based)",    dcf_value,       f"g={growth_rate*100:.1f}%  r={discount*100:.0f}%"),
            ("DCF (FCF-based)",    fcf_value,        f"g={fcf_growth*100:.1f}%  r={discount*100:.0f}%"),
            ("EV/EBITDA (12×)",    equity_from_ev,   f"EBITDA={fmt_large(ebitda)}"),
            ("P/S Multiple",       ps_est,           f"Rev={fmt_large(rev)}  mult={sector_ps:.1f}×"),
            ("P/B Multiple",       pb_est,           f"BVPS={fmt(bvps)}  mult={pb_mult:.1f}×"),
            ("Graham Number",      graham_num,       f"EPS={fmt(eps)}  BVPS={fmt(bvps)}"),
        ]

        table_rows = ""
        for method, est_val, params in rows:
            if est_val and est_val > 0:
                cls, ms_str = margin_class(est_val, current_price)
                table_rows += f"""
                <tr>
                  <td class="val-method">{method}</td>
                  <td style="color:{COLORS['text_muted']};font-size:10px;">{params}</td>
                  <td class="val-num">{currency} {fmt(est_val, '{:,.2f}')}</td>
                  <td class="val-num">{currency} {fmt(current_price, '{:,.2f}')}</td>
                  <td class="{cls}">{ms_str}</td>
                </tr>
                """
            else:
                table_rows += f"""
                <tr>
                  <td class="val-method">{method}</td>
                  <td style="color:{COLORS['text_muted']};font-size:10px;">{params}</td>
                  <td class="val-num" colspan="3" style="color:{COLORS['text_muted']};">Insufficient data</td>
                </tr>
                """

        st.markdown(f"""
        <div class="info-panel" style="overflow-x:auto;">
          <h4>Margin of Safety Analysis — Current Price: {currency} {fmt(current_price, '{:,.2f}')}</h4>
          <table class="val-table">
            <thead>
              <tr>
                <th>Method</th>
                <th>Parameters</th>
                <th style="text-align:right;">Est. Value</th>
                <th style="text-align:right;">Market Price</th>
                <th style="text-align:right;">Margin of Safety</th>
              </tr>
            </thead>
            <tbody>
              {table_rows}
            </tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:{COLORS['text_muted']};
                    padding:8px 12px;border-left:2px solid {COLORS['border_accent']};margin-top:8px;">
          ⚠ Valuation models use simplified assumptions. Always verify inputs. Growth rates capped at 30%.
          Margin of Safety: <span style="color:{COLORS['accent_green']}">≥30% strong</span> ·
          <span style="color:{COLORS['accent_gold']}">10–30% moderate</span> ·
          <span style="color:{COLORS['accent_red']}">below 10% / negative = overvalued</span>
        </div>
        """, unsafe_allow_html=True)

        # DCF sensitivity chart
        section_header("DCF Sensitivity — Growth Rate vs Discount Rate")
        growth_rates  = [0.03, 0.05, 0.08, 0.10, 0.15, 0.20]
        discount_rates = [0.08, 0.10, 0.12, 0.15]
        z_data = []
        for dr in discount_rates:
            row_vals = []
            for gr in growth_rates:
                gr_ = min(gr, 0.29)
                pe  = eps
                pv  = 0
                for y in range(1, 11):
                    pe *= (1 + gr_)
                    pv += pe / ((1 + dr) ** y)
                tv  = pe * (1 + 0.025) / (dr - 0.025)
                tv_pv = tv / ((1 + dr) ** 10)
                row_vals.append(round(pv + tv_pv, 2))
            z_data.append(row_vals)

        heat_fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=[f"{g*100:.0f}%" for g in growth_rates],
            y=[f"{d*100:.0f}%" for d in discount_rates],
            colorscale=[[0, COLORS["accent_red"]], [0.5, COLORS["accent_gold"]], [1, COLORS["accent_green"]]],
            hovertemplate="Growth: %{x}<br>Discount: %{y}<br>DCF Value: $%{z:.2f}<extra></extra>",
            text=[[f"${v:.0f}" for v in row] for row in z_data],
            texttemplate="%{text}",
            textfont=dict(size=11, family="IBM Plex Mono"),
            showscale=True,
            colorbar=dict(
                tickfont=dict(color=COLORS["text_muted"], size=9),
                outlinecolor=COLORS["border"],
            ),
        ))
        heat_fig.update_layout(base_layout(
            xaxis_title="Growth Rate",
            yaxis_title="Discount Rate",
            height=260,
            annotations=[
                dict(x=f"{growth_rate*100:.0f}%", y=f"{discount*100:.0f}%",
                     text="◆", showarrow=False,
                     font=dict(size=20, color="white"))
            ] if f"{growth_rate*100:.0f}%" in [f"{g*100:.0f}%" for g in growth_rates] else []
        ))
        st.plotly_chart(heat_fig, use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 4 — CORRELATIONS
    # ══════════════════════════════════════════
    with tab_corr:
        all_tickers = [selected_ticker] + corr_tickers
        all_tickers = list(dict.fromkeys(all_tickers))  # deduplicate

        if len(all_tickers) < 2:
            st.info("Add comparison tickers in the sidebar (e.g. SPY, QQQ, MSFT) to see correlations.")
        else:
            with st.spinner("Loading correlation data…"):
                try:
                    raw_all = yf.download(
                        all_tickers, period=selected_period,
                        auto_adjust=True, progress=False
                    )
                    if isinstance(raw_all.columns, pd.MultiIndex):
                        raw = raw_all["Close"]
                    else:
                        raw = raw_all  # single-ticker fallback
                    if isinstance(raw, pd.Series):
                        raw = raw.to_frame(name=all_tickers[0])
                    raw = raw.dropna(how="all")
                except Exception as e:
                    st.error(f"Could not download data: {e}")
                    raw = pd.DataFrame()

            if not raw.empty:
                returns = raw.pct_change().dropna()
                corr    = returns.corr()

                section_header("Correlation Matrix")
                corr_fig = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns.tolist(),
                    y=corr.index.tolist(),
                    colorscale=[
                        [0,   COLORS["accent_red"]],
                        [0.5, COLORS["bg_card"]],
                        [1,   COLORS["accent_green"]],
                    ],
                    zmin=-1, zmax=1,
                    text=corr.round(2).values,
                    texttemplate="%{text}",
                    textfont=dict(size=11, color=COLORS["text_primary"],
                                  family="IBM Plex Mono"),
                    hovertemplate="%{x} / %{y}: %{z:.3f}<extra></extra>",
                    showscale=True,
                    colorbar=dict(
                        tickfont=dict(color=COLORS["text_muted"], size=9),
                        outlinecolor=COLORS["border"],
                    ),
                ))
                corr_fig.update_layout(base_layout(
                    height=max(280, 60 * len(all_tickers)),
                    xaxis=dict(**_AXIS_STYLE, tickangle=-30,
                               tickfont=dict(size=11, color=COLORS["text_secondary"])),
                    yaxis=dict(**_AXIS_STYLE, tickfont=dict(size=11, color=COLORS["text_secondary"])),
                ))
                st.plotly_chart(corr_fig, use_container_width=True)

                # Cumulative returns
                section_header("Cumulative Returns")
                cum_returns = (1 + returns).cumprod() - 1

                cum_fig = go.Figure()
                palette = [COLORS["accent_cyan"], COLORS["accent_gold"],
                           COLORS["accent_green"], COLORS["accent_purple"],
                           COLORS["accent_red"], "#FF6B6B", "#4ECDC4"]

                for i, col in enumerate(cum_returns.columns):
                    cum_fig.add_trace(go.Scatter(
                        x=cum_returns.index, y=cum_returns[col] * 100,
                        name=col,
                        line=dict(color=palette[i % len(palette)], width=2),
                        hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}}%<extra></extra>",
                    ))

                cum_fig.add_hline(y=0, line_dash="dot", line_color=COLORS["border_accent"], line_width=1)
                cum_fig.update_layout(base_layout(
                    height=380,
                    yaxis_title="Cumulative Return (%)",
                    hovermode="x unified",
                ))
                st.plotly_chart(cum_fig, use_container_width=True)

                # Sharpe ratios
                section_header("Risk-Adjusted Performance")
                risk_cols = st.columns(len(all_tickers))
                for i, ticker in enumerate(all_tickers):
                    if ticker in returns.columns:
                        ann_ret = returns[ticker].mean() * 252
                        ann_std = returns[ticker].std() * (252 ** 0.5)
                        sharpe  = ann_ret / ann_std if ann_std > 0 else 0
                        vol_pct = ann_std * 100
                        col_clr = "green" if sharpe > 1 else ("gold" if sharpe > 0.5 else "red")
                        risk_cols[i].markdown(
                            metric_card(ticker,
                                        f"{sharpe:.2f}",
                                        sub=f"Sharpe Ratio",
                                        delta=f"Vol {vol_pct:.1f}%",
                                        color=col_clr),
                            unsafe_allow_html=True
                        )

    # ══════════════════════════════════════════
    #  TAB 5 — PRICE CHART
    # ══════════════════════════════════════════
    with tab_price:
        section_header("OHLC Price & Volume")

        with st.spinner("Loading price history…"):
            hist = load_ticker_history(selected_ticker, selected_period)
            if hist.empty:
                hist = hist_1y

        if hist is not None and not hist.empty:
            # Flatten MultiIndex if needed
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = [c[0] for c in hist.columns]

            # Moving averages
            hist["MA20"]  = hist["Close"].rolling(20).mean()
            hist["MA50"]  = hist["Close"].rolling(50).mean()
            hist["MA200"] = hist["Close"].rolling(200).mean()

            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.75, 0.25],
            )

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist["Open"], high=hist["High"],
                low=hist["Low"],   close=hist["Close"],
                increasing_line_color=COLORS["accent_green"],
                increasing_fillcolor=f"rgba(0,200,150,0.7)",
                decreasing_line_color=COLORS["accent_red"],
                decreasing_fillcolor=f"rgba(255,69,96,0.7)",
                name="OHLC",
                hovertext=[f"O:{o:.2f}  H:{h:.2f}  L:{l:.2f}  C:{c:.2f}"
                           for o, h, l, c in zip(hist["Open"], hist["High"], hist["Low"], hist["Close"])],
            ), row=1, col=1)

            # MAs
            for ma, color, dash in [("MA20", COLORS["accent_cyan"], "solid"),
                                     ("MA50", COLORS["accent_gold"], "dot"),
                                     ("MA200", COLORS["accent_purple"], "dash")]:
                if not hist[ma].isna().all():
                    fig.add_trace(go.Scatter(
                        x=hist.index, y=hist[ma],
                        line=dict(color=color, width=1.2, dash=dash),
                        name=ma, opacity=0.8,
                        hovertemplate=f"{ma}: %{{y:.2f}}<extra></extra>",
                    ), row=1, col=1)

            # Volume bars
            colors_vol = [COLORS["accent_green"] if c >= o else COLORS["accent_red"]
                          for o, c in zip(hist["Open"], hist["Close"])]
            fig.add_trace(go.Bar(
                x=hist.index, y=hist["Volume"],
                marker_color=colors_vol,
                marker_opacity=0.6,
                name="Volume",
                hovertemplate="Vol: %{y:,.0f}<extra></extra>",
            ), row=2, col=1)

            # Layout
            fig.update_layout(base_layout(
                height=560,
                xaxis_rangeslider_visible=False,
                xaxis2=dict(
                    **_AXIS_STYLE,
                    title="",
                    rangeselector=dict(
                        bgcolor=COLORS["bg_card"],
                        activecolor=COLORS["accent_blue"],
                        bordercolor=COLORS["border"],
                        buttons=[
                            dict(count=1,  label="1M",  step="month", stepmode="backward"),
                            dict(count=3,  label="3M",  step="month", stepmode="backward"),
                            dict(count=6,  label="6M",  step="month", stepmode="backward"),
                            dict(count=1,  label="YTD", step="year",  stepmode="todate"),
                            dict(count=1,  label="1Y",  step="year",  stepmode="backward"),
                            dict(step="all", label="All"),
                        ],
                        font=dict(color=COLORS["text_secondary"], size=10,
                                  family="IBM Plex Mono"),
                    ),
                ),
                yaxis=dict(**_AXIS_STYLE, title="Price"),
                yaxis2=dict(**_AXIS_STYLE, title="Volume"),
                legend=dict(**_LEGEND_STYLE, orientation="h", y=1.02, x=0),
                hovermode="x unified",
            ))

            st.plotly_chart(fig, use_container_width=True)

            # Price stats
            section_header("Period Statistics")
            period_ret = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
            max_price  = hist["High"].max()
            min_price  = hist["Low"].min()
            avg_vol    = hist["Volume"].mean()
            volatility = hist["Close"].pct_change().std() * (252 ** 0.5) * 100

            stat_cols = st.columns(5)
            stat_data = [
                ("Period Return",  f"{period_ret:+.2f}%",   "green" if period_ret >= 0 else "red"),
                ("Period High",    f"${max_price:,.2f}",    "blue"),
                ("Period Low",     f"${min_price:,.2f}",    "blue"),
                ("Avg Volume",     fmt_large(avg_vol),       "cyan"),
                ("Annualised Vol", f"{volatility:.1f}%",    "gold"),
            ]
            for i, (lbl, val, col) in enumerate(stat_data):
                stat_cols[i].markdown(metric_card(lbl, val, color=col), unsafe_allow_html=True)
        else:
            st.error("No price history available for this ticker.")
