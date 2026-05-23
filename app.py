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

# ==========================================
# INICIALIZACIÓN SEGURA DEL ESTADO
# ==========================================
if "analyzed_ticker" not in st.session_state:
    st.session_state["analyzed_ticker"] = ""

# ==========================================
# CONFIGURACIÓN DE COLORES (PALETA VS CODE LIGHT)
# ==========================================
ACCENT_BLUE = "#268BD2"
ACCENT_GREEN = "#2AA198"
ACCENT_RED = "#D30102"
ACCENT_OCHRE = "#B58900"
TEXT_PRIMARY = "#433F38"
TEXT_SECONDARY = "#7A756B"
CARD_BG = "#F4EFCF"
BORDER = "#EAE4CD"
BG_MAIN = "#FDF6E3"

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
        background-color: {BG_MAIN};
        color: {TEXT_PRIMARY};
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }}
    .hero-title {{
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        text-align: center;
        background: linear-gradient(90deg, {ACCENT_BLUE}, {ACCENT_OCHRE});
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
        border-radius: 8px;
        padding: 0.8rem 1rem;
        border: 1px solid {BORDER};
        margin-bottom: 0.4rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
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
        color: {TEXT_PRIMARY};
    }}
    .metric-sub {{
        color: {TEXT_SECONDARY};
        font-size: 0.75rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        
