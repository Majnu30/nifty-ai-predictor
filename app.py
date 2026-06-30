import streamlit as st
import numpy as np
import joblib
import pandas as pd
import os
import pyotp
import time
from SmartApi import SmartConnect

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- AUTO REFRESH STREAM MATRIX ----------------
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

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
</style>
""", unsafe_allow_html=True)

# ---------------- SAFE HIGH-SPEED MODEL LOADING ----------------
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

# ---------------- HERO HEADER ----------------
st.markdown("""
    <div style="background: linear-gradient(135deg, #040A18 0%, #06132C 100%); border: 1px solid #111E3B; border-radius: 16px; padding: 30px; margin-bottom: 20px;">
        <h1 style="font-size: 36px; font-weight: 900; margin: 0; letter-spacing: -0.5px;">
            MARKET <span style="color: #3B82F6;">AI</span> INTRADAY PREDICTOR
        </h1>
    </div>
    """, unsafe_allow_html=True)

# ---------------- INDEX SELECTION & DATA MODE ----------------
target_index = st.selectbox("Select Target Market Index", ["NIFTY 50", "SENSEX", "BANKEX"])
mode = st.radio("Select Input Mode", ["Manual Input", "AngelOne Live Stream"], horizontal=True)

# Instantiating base matrix values
open_price, high_price, low_price, close_price, volume, previous_return = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
api_authenticated = False
feed_status_message = "Awaiting Live Stream Initialization"

# ---------------- OFFICIAL SMARTAPI SDK IMPLEMENTATION ----------------
if mode == "AngelOne Live Stream":
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🔐 Secure SmartAPI SDK Intraday Link</div>', unsafe_allow_html=True)
    
    ak_col, cc_col, pw_col, to_col = st.columns(4)
    with ak_col:
        API_KEY = st.text_input("SmartAPI Key", type="password")
    with cc_col:
        CLIENT_CODE = st.text_input("Client ID / Code")
    with pw_col:
        PASSWORD = st.text_input("Mpin / Password", type="password")
    with to_col:
        TOTP_SECRET = st.text_input("TOTP Token String", type="password")
        
    st.markdown('</div>', unsafe_allow_html=True)

    if API_KEY and CLIENT_CODE and PASSWORD and TOTP_SECRET:
        try:
            totp_challenge = pyotp.TOTP(TOTP_SECRET).now()
            smart_api = SmartConnect(api_key=API_KEY)
            session_data = smart_api.generateSession(CLIENT_CODE, PASSWORD, totp_challenge)
            
            if session_data.get('status') == True:
                api_authenticated = True
                feed_status_message = f"AngelOne Streaming Active (Tick #{st.session_state.refresh_counter})"
                
                token_map = {"NIFTY 50": "26000", "SENSEX": "1", "BANKEX": "12"}
                exchange_map = {"NIFTY 50": "NSE", "SENSEX": "BSE", "BANKEX": "BSE"}
                
                exchange_tokens = {exchange_map[target_index]: [token_map[target_index]]}
                market_data = smart_api.getMarketData(mode="FULL", exchangeTokens=exchange_tokens)
                
                if market_data.get('status') == True and 'data' in market_data and 'fetched' in market_data['data'] and market_data['data']['fetched']:
                    tick = market_data['data']['fetched'][0]
                    
                    # CORRECTED: Explicitly mapping all 6 vectors from AngelOne response
                    close_price = float(tick.get('ltp', 0))
                    open_price = float(tick.get('open', 0))
                    high_price = float(tick.get('high', 0))
                    low_price = float(tick.get('low', 0))
                    volume = float(tick.get('tradeVolume', tick.get('volume', 0)))
                    previous_return = float(tick.get('percentChange', 0))
                else:
                    st.error("Intraday parsing mismatch. Ensure market hours are active or use Manual tuning.")
            else:
                st.error(f"SmartAPI SDK Gateway Access Denied: {session_data.get('message', 'Check verification keys')}")
        except Exception as sdk_err:
            st.error(f"SmartAPI Connection Exception Core: {sdk_err}")

# ---------------- METRICS HUD STATUS DISPLAY ----------------
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="📅 Target Index", value=target_index)
m2.metric(label="🕒 Feed Source", value=feed_status_message if mode == "AngelOne Live Stream" else "Manual Matrix")
m3.metric(label="📊 Pipeline Status", value="Intraday Live Tracker" if api_authenticated else "Offline")
m4.metric(label="⚡ Engine Core", value="ML Inference Ready" if model else "Simulated Mode")

# ---------------- MAIN PANEL INPUT CONTROLS ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown(f'<div class="panel-header">📊 Dynamic Matrix Tuning: {target_index}</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="medium")
with c1:
    open_price = st.number_input("Open Price (₹)", format="%.2f", value=open_price, disabled=(mode == "AngelOne Live Stream"))
    low_price = st.number_input("Low Price (₹)", format="%.2f", value=low_price, disabled=(mode == "AngelOne Live Stream"))
    volume = st.number_input("Trading Volume", format="%.2f", value=volume, disabled=(mode == "AngelOne Live Stream"))
with c2:
    high_price = st.number_input("High Price (₹)", format="%.2f", value=high_price, disabled=(mode == "AngelOne Live Stream"))
    close_price = st.number_input("Close Price (₹)", format="%.2f", value=close_price, disabled=(mode == "AngelOne Live Stream"))
    previous_return = st.number_input("Previous Session Return (%)", format="%.2f", value=previous_return, disabled=(mode == "AngelOne Live Stream"))

predict_clicked = st.button("🚀 EXECUTE PREDICTION MATRIX")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INFERENCE CALCULATION BLOCK ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)

# Rule: Always run prediction on live data loop OR on button click
if predict_clicked or (mode == "AngelOne Live Stream" and api_authenticated):
    # CORRECTED: Building structured array using all 6 real-time data inputs
    data_array = np.array([[open_price, high_price, low_price, close_price, volume, previous_return]])
    
    if model is not None:
        prediction = model.predict(data_array)[0]
        probability = model.predict_proba(data_array)[0]
        confidence = probability[1] * 100 if prediction == 1 else probability[0] * 100
    else:
        # Fallback simulation logic if nifty_model.pkl is missing
        prediction = 1 if close_price >= open_price else 0
        confidence = 85.5 if prediction == 1 else 82.3
    
    if prediction == 1:
        st.success(f"📈 PROJECTION VECTOR: BULLISH (UP) - Live Intraday Confidence: {confidence:.2f}%")
    else:
        st.error(f"📉 PROJECTION VECTOR: BEARISH (DOWN) - Live Intraday Confidence: {confidence:.2f}%")
else:
    st.info("Awaiting input execution matrix trigger parameters.")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- AUTO LIVE TRACKING RUNTIME ----------------
if mode == "AngelOne Live Stream" and api_authenticated:
    time.sleep(5)
    st.session_state.refresh_counter += 1
    st.rerun()
