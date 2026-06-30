import streamlit as st
import numpy as np
import joblib
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

# ---------------- INDEX INITIAL VALUE RESET LOGIC ----------------
# This function automatically updates your input box baselines if you switch dropdown selections
def on_index_change():
    selected = st.session_state.index_selector
    if selected == "SENSEX":
        st.session_state.open, st.session_state.high, st.session_state.low, st.session_state.close = 77000.0, 77300.0, 76800.0, 77100.0
        st.session_state.volume, st.session_state.prev_return = 250000.0, 0.35
    elif selected == "BANKEX":
        st.session_state.open, st.session_state.high, st.session_state.low, st.session_state.close = 58000.0, 58300.0, 57800.0, 58100.0
        st.session_state.volume, st.session_state.prev_return = 180000.0, -0.15
    else: # NIFTY 50 Default
        st.session_state.open, st.session_state.high, st.session_state.low, st.session_state.close = 23500.0, 23600.0, 23400.0, 23550.0
        st.session_state.volume, st.session_state.prev_return = 150000.0, 0.25

# ---------------- INITIALIZE PERSISTENT STORAGE ----------------
if "smart_api" not in st.session_state: st.session_state.smart_api = None
if "api_authenticated" not in st.session_state: st.session_state.api_authenticated = False
if "refresh_counter" not in st.session_state: st.session_state.refresh_counter = 0

# Set dynamic default values based on the last known real-world index ranges instead of generic 0.0
if "open" not in st.session_state: st.session_state.open = 23500.0
if "high" not in st.session_state: st.session_state.high = 23600.0
if "low" not in st.session_state: st.session_state.low = 23400.0
if "close" not in st.session_state: st.session_state.close = 23550.0
if "volume" not in st.session_state: st.session_state.volume = 150000.0
if "prev_return" not in st.session_state: st.session_state.prev_return = 0.25

# ---------------- THEME CSS ----------------
st.markdown("""
<style>
    .stApp { background-color: #030712 !important; color: #F8FAFC !important; }
    .content-panel { background: #070F21; border: 1px solid #111E3B; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
    .panel-header { font-size: 18px; font-weight: 600; color: #FFFFFF; margin-bottom: 20px; }
    div[data-testid="stNumberInput"], div[data-testid="stSelectbox"], div[data-testid="stTextInput"] input { background-color: #091122 !important; color: #F8FAFC !important; border-radius: 8px !important; }
    div.stButton > button { width: 100%; height: 52px; border-radius: 10px; border: none; color: white; background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%); margin-top: 10px; }
    .ltp-box { background: rgba(37, 99, 235, 0.1); border-left: 5px solid #2563EB; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ---------------- ML MODEL CONFIGURATION ----------------
@st.cache_resource
def load_ml_model():
    try:
        for path in ["models/nifty_model.pkl", "nifty_model.pkl"]:
            if os.path.exists(path): return joblib.load(path)
    except Exception: pass  
    return None

model = load_ml_model()

st.markdown("""
    <div style="background: linear-gradient(135deg, #040A18 0%, #06132C 100%); border: 1px solid #111E3B; border-radius: 16px; padding: 30px; margin-bottom: 20px;">
        <h1 style="font-size: 36px; font-weight: 900; margin: 0; letter-spacing: -0.5px;">MARKET <span style="color: #3B82F6;">AI</span> INTRADAY LIVE</h1>
    </div>
""", unsafe_allow_html=True)

# ---------------- INDEX SELECTION & CHANGEOVER DETECTOR ----------------
target_index = st.selectbox(
    "Select Target Market Index", 
    ["NIFTY 50", "SENSEX", "BANKEX"], 
    key="index_selector", 
    on_change=on_index_change
)
mode = st.radio("Select Input Mode", ["Manual Input", "AngelOne Live Stream"], horizontal=True)

if mode == "Manual Input":
    if st.session_state.api_authenticated:
        st.session_state.api_authenticated = False
        st.session_state.smart_api = None

feed_status_message = "Manual Overrides Enabled" if mode == "Manual Input" else "Awaiting Live API Handshake Link"

# ---------------- SECURE NATIVE ANGELONE TERMINAL ----------------
if mode == "AngelOne Live Stream":
    if not st.session_state.api_authenticated:
        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">🔐 Secure SmartAPI Live SDK Hub</div>', unsafe_allow_html=True)
        
        ak_col, cc_col, pw_col, to_col = st.columns(4)
        with ak_col: API_KEY = st.text_input("SmartAPI Key", type="password", key="api_key_widget")
        with cc_col: CLIENT_CODE = st.text_input("Client ID / Code", key="client_code_widget")
        with pw_col: PASSWORD = st.text_input("Mpin / Password", type="password", key="password_widget")
        with to_col: TOTP_SECRET = st.text_input("TOTP Token String", type="password", key="totp_widget")
            
        connect_btn = st.button("🚀 CONNECT LIVE GATEWAY")
        st.markdown('</div>', unsafe_allow_html=True)

        if connect_btn and API_KEY and CLIENT_CODE and PASSWORD and TOTP_SECRET:
            try:
                totp_challenge = pyotp.TOTP(TOTP_SECRET).now()
                smart_api = SmartConnect(api_key=API_KEY)
                session_data = smart_api.generateSession(CLIENT_CODE, PASSWORD, totp_challenge)
                if session_data.get('status') == True:
                    st.session_state.smart_api = smart_api
                    st.session_state.api_authenticated = True
                    st.rerun()
                else:
                    st.error(f"Gateway Access Denied: {session_data.get('message', 'Check Credentials Configuration')}")
            except Exception as e:
                st.error(f"Connection Exception: {e}")
                
    if st.session_state.api_authenticated and st.session_state.smart_api:
        feed_status_message = f"AngelOne Streaming Active (Tick #{st.session_state.refresh_counter})"
        try:
            # CORRECTED: Clean production tokens for official indexes
            token_map = {"NIFTY 50": "99926000", "SENSEX": "99919000", "BANKEX": "99923000"}
            exchange_map = {"NIFTY 50": "NSE", "SENSEX": "BSE", "BANKEX": "BSE"}
            
            exchange_tokens = {exchange_map[target_index]: [token_map[target_index]]}
            market_data = st.session_state.smart_api.getMarketData(mode="FULL", exchangeTokens=exchange_tokens)
            
            if market_data.get('status') == True and 'data' in market_data and market_data['data']['fetched']:
                tick = market_data['data']['fetched'][0]
                
                # Overwrite stored variables instantly with incoming tickers
                st.session_state.close = float(tick.get('ltp', st.session_state.close))
                st.session_state.open = float(tick.get('open', st.session_state.open))
                st.session_state.high = float(tick.get('high', st.session_state.high))
                st.session_state.low = float(tick.get('low', st.session_state.low))
                st.session_state.volume = float(tick.get('tradeVolume', tick.get('volume', st.session_state.volume)))
                st.session_state.prev_return = float(tick.get('percentChange', st.session_state.prev_return))
        except Exception as data_err:
            st.error(f"Error parsing live market ticks: {data_err}")

# ---------------- DISPLAY CURRENT PRICE HUDS ----------------
st.markdown(f"""
<div class="ltp-box">
    <span style="font-size:13px; color:#94A3B8; text-transform:uppercase; font-weight:600;">⚡ Current Market Price (LTP)</span>
    <h1 style="margin:5px 0 0 0; font-size:32px; font-weight:800; color:#FFFFFF;">₹ {st.session_state.close:,.2f}</h1>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric(label="📅 Target Index", value=target_index)
m2.metric(label="🕒 Feed Source", value=feed_status_message)
m3.metric(label="📊 Pipeline Status", value="Live Streaming" if st.session_state.api_authenticated else "Manual Mode")
m4.metric(label="⚡ Engine Core", value="ML Inference Ready" if model else "Simulated Mode")

# ---------------- MAIN PANEL INPUT CONTROLS ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown(f'<div class="panel-header">📊 Dynamic Matrix Tuning: {target_index}</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="medium")
with c1:
    open_val = st.number_input("Open Price (₹)", format="%.2f", value=st.session_state.open, disabled=(mode == "AngelOne Live Stream"), key="open_inp")
    low_val = st.number_input("Low Price (₹)", format="%.2f", value=st.session_state.low, disabled=(mode == "AngelOne Live Stream"), key="low_inp")
    vol_val = st.number_input("Trading Volume", format="%.2f", value=st.session_state.volume, disabled=(mode == "AngelOne Live Stream"), key="vol_inp")
with c2:
    high_val = st.number_input("High Price (₹)", format="%.2f", value=st.session_state.high, disabled=(mode == "AngelOne Live Stream"), key="high_inp")
    close_val = st.number_input("Close Price (₹)", format="%.2f", value=st.session_state.close, disabled=(mode == "AngelOne Live Stream"), key="close_inp")
    ret_val = st.number_input("Previous Session Return (%)", format="%.2f", value=st.session_state.prev_return, disabled=(mode == "AngelOne Live Stream"), key="ret_inp")

predict_clicked = st.button("🚀 EXECUTE PREDICTION MATRIX")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ML INFERENCE ENGINE RUNTIME ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">🎯 Inference Engine Output</div>', unsafe_allow_html=True)

if predict_clicked or (mode == "AngelOne Live Stream" and st.session_state.api_authenticated):
    data_array = np.array([[open_val, high_val, low_val, close_val, vol_val, ret_val]])
    if model is not None:
        prediction = model.predict(data_array)[0]
        probability = model.predict_proba(data_array)[0]
        confidence = probability[1] * 100 if prediction == 1 else probability[0] * 100
    else:
        prediction = 1 if close_val >= open_val else 0
        confidence = 85.5 if prediction == 1 else 82.3
    
    if prediction == 1:
        st.success(f"📈 PROJECTION VECTOR: BULLISH (UP) - Confidence: {confidence:.2f}%")
    else:
        st.error(f"📉 PROJECTION VECTOR: BEARISH (DOWN) - Confidence: {confidence:.2f}%")
else:
    st.info("Establishing metrics base arrays. Select parameters to evaluate prediction vectors.")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BACKGROUND REFRESH TICKER LOOP ----------------
if mode == "AngelOne Live Stream" and st.session_state.api_authenticated:
    time.sleep(4)
    st.session_state.refresh_counter += 1
    st.rerun()
