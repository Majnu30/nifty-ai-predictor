import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
import time
import requests
import pyotp
import json

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- THEME & RESPONSIVE UI CSS ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #030712 !important;
        color: #F8FAFC !important;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    section[data-testid="stSidebar"] {
        background-color: #050B18 !important;
        border-right: 1px solid #111C34;
    }

    .content-panel {
        background: #070F21;
        border: 1px solid #111E3B;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    @media (min-width: 768px) {
        .content-panel { padding: 30px; }
    }
    
    .panel-header {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }

    label[data-testid="stWidgetLabel"] p {
        color: #94A3B8 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }

    div[data-testid="stNumberInput"], div[data-testid="stSelectbox"], div[data-testid="stTextInput"] input {
        background-color: #091122 !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="stRadio"] > label {
        display: none;
    }
    
    div.stButton > button {
        width: 100%;
        height: 52px;
        border-radius: 10px;
        border: none;
        color: white;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%);
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25);
        transition: all 0.3s ease;
        margin-top: 10px;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(90deg, #1D4ED8 0%, #6D28D9 100%);
        transform: translateY(-1px);
    }
    
    .responsive-header {
        background: linear-gradient(135deg, #040A18 0%, #06132C 100%); 
        border: 1px solid #111E3B; 
        border-radius: 16px; 
        padding: 30px 20px; 
        margin-bottom: 20px; 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
        gap: 20px;
    }

    @media (min-width: 768px) {
        .responsive-header {
            flex-direction: row;
            align-items: center;
            padding: 40px;
        }
    }

    .result-layout {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 20px;
        padding: 10px 0;
    }
    
    @media (min-width: 576px) {
        .result-layout {
            flex-direction: row;
            text-align: left;
            gap: 35px;
        }
    }
    
    .result-circle-base {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        flex-shrink: 0;
    }

    .result-circle-placeholder { border: 2px dashed #1E293B; color: #475569; }
    .result-circle-bullish { border: 3px solid #10B981; background: rgba(16, 185, 129, 0.05); box-shadow: 0 0 15px rgba(16, 185, 129, 0.2); }
    .result-circle-bearish { border: 3px solid #EF4444; background: rgba(239, 68, 68, 0.05); box-shadow: 0 0 15px rgba(239, 68, 68, 0.2); }

    .footer-panel {
        background: linear-gradient(90deg, #050B18 0%, #081226 100%);
        border: 1px solid #111E3B;
        border-radius: 16px;
        padding: 30px 20px;
        margin-top: 40px;
        text-align: center;
    }
    
    @media (min-width: 768px) {
        .footer-panel {
            text-align: left;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 40px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SAFE HIGH-SPEED MODEL RESILIENCY LOADING ----------------
@st.cache_resource
def load_ml_model():
    try:
        for path in ["models/nifty_model.pkl", "nifty_model.pkl"]:
            if os.path.exists(path):
                return joblib.load(path)
    except Exception:
        pass  
    return None

model = load_ml_model()

# ---------------- SIDEBAR NAVIGATION ----------------
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0 25px 0;">
            <h2 style="color: #FFFFFF; font-size: 24px; font-weight: 800; margin: 0; letter-spacing: 1px;">
                M<span style="color: #3B82F6;">A</span>JNU
            </h2>
            <p style="color: #475569; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; margin: 2px 0 0 0;">
                Innovate • Build • Inspire
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<p style='color:#475569; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Navigation</p>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%); padding: 12px 16px; border-radius: 8px; font-weight: 600; color: white; margin-bottom: 8px; cursor: pointer;">🏠 Home</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 8px; cursor: pointer;">📈 Predict</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 8px; cursor: pointer;">ℹ️ About</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 20px; cursor: pointer;">✉️ Contact</div>
    """, unsafe_allow_html=True)

# ---------------- HERO HEADER ----------------
st.markdown("""
    <div class="responsive-header">
        <div>
            <h1 style="font-size: clamp(32px, 5vw, 48px); font-weight: 900; margin: 0; letter-spacing: -0.5px; line-height: 1.1;">
                MARKET <span style="color: #3B82F6;">AI</span> PREDICTOR
            </h1>
            <p style="color: #64748B; font-size: clamp(14px, 2vw, 16px); margin-top: 10px; font-weight: 400; max-width: 600px;">
                High-Speed Quantitative Engine for Live Options Trading Vectors.
            </p>
        </div>
        <div style="background: rgba(30, 41, 59, 0.3); border: 1px solid #1E293B; padding: 15px 25px; border-radius: 12px; min-width: 160px; text-align: center;">
            <h3 style="color: #FFFFFF; font-size: 22px; font-weight: 900; margin: 0; letter-spacing: 3px;">
                M<span style="color: #3B82F6;">A</span>JNU
            </h3>
            <span style="color: #3B82F6; font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; display: block; margin-top: 2px;">
                OFFICIAL ENGINE
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- INDEX SELECTION & DATA MODE ----------------
st.markdown("<p style='color:#94A3B8; font-size:14px; font-weight:500; margin-bottom:4px;'>Target Market Index</p>", unsafe_allow_html=True)
target_index = st.selectbox("Select Index", ["NIFTY 50", "SENSEX", "BANKEX"], label_visibility="collapsed")

st.markdown("<p style='color:#94A3B8; font-size:14px; font-weight:500; margin-top:12px; margin-bottom:4px;'>Data Intake Strategy</p>", unsafe_allow_html=True)
mode = st.radio("Select Input Mode", ["Manual Input", "Real-Time Cloud Feed"], horizontal=True)

open_price, high_price, low_price, close_price, volume, previous_return = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
api_authenticated = False
feed_status_message = "Awaiting Live Stream Initialization"

# --- OPEN STABLE FINANCIAL API PROTOCOL ---
def fetch_live_market_ticks(index_name):
    ticker_map = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "BANKEX": "BSE-BANK.BO"}
    ticker = ticker_map.get(index_name, "^NSEI")
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=5).json()
        result = res['chart']['result'][0]
        indicators = result['indicators']['quote'][0]
        
        o = float(indicators['open'][0] or 0)
        h = float(indicators['high'][0] or 0)
        l = float(indicators['low'][0] or 0)
        c = float(indicators['close'][0] or result['meta']['regularMarketPrice'])
        v = float(indicators['volume'][0] or 0)
        pr = ((c - o) / o) * 100 if o > 0 else 0.0
        return o, h, l, c, v, pr, True
    except Exception:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, False

# ---------------- AUTOMATIC CLOUD STREAM ROUTING ----------------
if mode == "Real-Time Cloud Feed":
    open_price, high_price, low_price, close_price, volume, previous_return, api_authenticated = fetch_live_market_ticks(target_index)
    if api_authenticated:
        feed_status_message = "Live Global Matrix Feed Connected"
    else:
        st.error("Temporary downstream sync error. Please try clicking or changing the index selection target.")

# ---------------- METRICS HUD STATUS DISPLAY ----------------
m1, m2, m3, m4 = st.columns([1, 1, 1, 1])
metric_css = """
<style>
    div[data-testid="stMetric"] { background: #091225 !important; border: 1px solid #142342 !important; border-radius: 12px !important; padding: 12px 16px !important; }
    div[data-testid="stMetricLabel"] p { color: #64748B !important; font-size: 12px !important; text-transform: uppercase; }
    div[data-testid="stMetricValue"] div { color: #FFFFFF !important; font-size: 16px !important; font-weight: 600 !important; }
</style>
"""
st.markdown(metric_css, unsafe_allow_html=True)

m1.metric(label="📅 Target Index", value=target_index)
m2.metric(label="🕒 Feed Source", value=feed_status_message if mode == "Real-Time Cloud Feed" else "Manual Matrix")
m3.metric(label="📊 Pipeline Status", value="Tick Live" if api_authenticated else "Awaiting Tuning")
m4.metric(label="⚡ Engine Core", value="ML Inference Ready" if model else "Simulated Mode")

st.write("")

# ---------------- MAIN PANEL INPUT CONTROLS ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown(f'<div class="panel-header">📊 Dynamic Matrix Tuning: {target_index}</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="medium")

with c1:
    open_price = st.number_input("Open Price (₹)", format="%.2f", value=open_price, disabled=(mode == "Real-Time Cloud Feed"))
    low_price = st.number_input("Low Price (₹)", format="%.2f", value=low_price, disabled=(mode == "Real-Time Cloud Feed"))
    volume = st.number_input("Trading Volume", format="%.2f", value=volume, disabled=(mode == "Real-Time Cloud Feed"))

with c2:
    high_price = st.number_input("High Price (₹)", format="%.2f", value=high_price, disabled=(mode == "Real-Time Cloud Feed"))
    close_price = st.number_input("Close Price (₹)", format="%.2f", value=close_price, disabled=(mode == "Real-Time Cloud Feed"))
    previous_return = st.number_input("Previous Session Return (%)", format="%.2f", value=previous_return, disabled=(mode == "Real-Time Cloud Feed"))

predict_clicked = st.button("🚀 EXECUTE PREDICTION MATRIX")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INFERENCE CALCULATION BLOCK ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">🎯 Inference Pipeline Output</div>', unsafe_allow_html=True)

if predict_clicked:
    data_array = np.array([[open_price, high_price, low_price, close_price, volume, previous_return]])
    
    if model is not None:
        prediction = model.predict(data_array)[0]
        probability = model.predict_proba(data_array)[0]
    else:
        prediction = 1 if close_price >= open_price else 0
        probability = [0.18, 0.82] if prediction == 1 else [0.82, 0.18]
        
    if prediction == 1:
        confidence = probability[1] * 100
        st.markdown(f"""
            <div class="result-layout">
                <div class="result-circle-base result-circle-bullish">🐂</div>
                <div>
                    <h2 style="color: #10B981; margin: 0; font-size: clamp(20px, 4vw, 28px); font-weight: 700;">PROJECTION VECTOR: BULLISH (UP)</h2>
                    <p style="color: #64748B; margin: 4px 0 12px 0; font-size: 14px;">Inference models capture structural support trends shifting upward.</p>
                    <span style="color: #F8FAFC; font-weight: 500; font-size: 15px;">Confidence Threshold: <b style="color:#10B981;">{confidence:.2f}%</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        confidence = probability[0] * 100
        st.markdown(f"""
            <div class="result-layout">
                <div class="result-circle-base result-circle-bearish">🐻</div>
                <div>
                    <h2 style="color: #EF4444; margin: 0; font-size: clamp(20px, 4vw, 28px); font-weight: 700;">PROJECTION VECTOR: BEARISH (DOWN)</h2>
                    <p style="color: #64748B; margin: 4px 0 12px 0; font-size: 14px;">Inference models capture overhead resistance distributions building momentum.</p>
                    <span style="color: #F8FAFC; font-weight: 500; font-size: 15px;">Confidence Threshold: <b style="color:#EF4444;">{confidence:.2f}%</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.progress(confidence / 100)
else:
    st.markdown("""
        <div class="result-layout">
            <div class="result-circle-base result-circle-placeholder">---</div>
            <div>
                <h2 style="color: #475569; margin: 0; font-size: 24px; font-weight: 700;">--</h2>
                <p style="color: #64748B; margin: 2px 0 8px 0; font-size: 13px;">Awaiting prediction runtime trigger initialization.</p>
                <span style="color: #475569; font-weight: 500; font-size: 14px;">Confidence Threshold: --%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.progress(0.0)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BRAND FOOTER BANNER ----------------
st.markdown("""
    <div class="footer-panel">
        <div>
            <p style="color: #475569; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin: 0 0 5px 0;">
                Designed By
            </p>
            <h1 style="
                font-size: clamp(40px, 6vw, 56px);
                font-weight: 900;
                margin: 0;
                background: linear-gradient(90deg, #3B82F6 0%, #C084FC 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: 6px;
                line-height: 1;
            ">
                MAJNU
            </h1>
            <p style="color: #3B82F6; font-size: 13px; margin-top: 10px; font-weight: 500;">
                Code. Create. Conquer.
            </p>
        </div>
        <div style="display: flex; gap: 20px; align-items: center; justify-content: center; margin-top: 20px; opacity: 0.6; font-size: 14px;">
            <span style="color: #64748B; cursor: pointer;">💻 GitHub</span>
            <span style="color: #64748B; cursor: pointer;">🌐 LinkedIn</span>
            <span style="color: #64748B; cursor: pointer;">🐦 Twitter</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
