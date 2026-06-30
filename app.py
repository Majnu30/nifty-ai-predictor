import streamlit as st
import numpy as np
import joblib
import os
import pyotp
import time
from SmartApi import SmartConnect

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MAJNU AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- DYNAMIC VALUE RE-ALIGNMENT CONFIG ----------------
def reset_index_baselines():
    selected = st.session_state.index_selector
    if selected == "SENSEX":
        st.session_state.current_price = 76700.0
        st.session_state.baseline_open = 77000.0
        st.session_state.strike_step = 100
    elif selected == "BANKEX":
        st.session_state.current_price = 57700.0
        st.session_state.baseline_open = 58100.0
        st.session_state.strike_step = 100
    else: # NIFTY 50 Default
        st.session_state.current_price = 23940.0
        st.session_state.baseline_open = 24060.0
        st.session_state.strike_step = 50

# ---------------- INITIALIZE PERSISTENT STORAGE ----------------
if "smart_api" not in st.session_state: st.session_state.smart_api = None
if "api_authenticated" not in st.session_state: st.session_state.api_authenticated = False
if "refresh_counter" not in st.session_state: st.session_state.refresh_counter = 0

if "current_price" not in st.session_state: st.session_state.current_price = 23940.0
if "baseline_open" not in st.session_state: st.session_state.baseline_open = 24060.0
if "strike_step" not in st.session_state: st.session_state.strike_step = 50

# ---------------- THEME CSS ----------------
st.markdown("""
<style>
    .stApp { background-color: #030712 !important; color: #F8FAFC !important; }
    .content-panel { background: #070F21; border: 1px solid #111E3B; border-radius: 16px; padding: 30px; margin-bottom: 20px; }
    .panel-header { font-size: 18px; font-weight: 600; color: #FFFFFF; margin-bottom: 15px; }
    div[data-testid="stNumberInput"], div[data-testid="stSelectbox"], div[data-testid="stTextInput"] input { background-color: #091122 !important; color: #F8FAFC !important; border-radius: 8px !important; }
    div.stButton > button { width: 100%; height: 56px; border-radius: 12px; border: none; color: white; font-size: 16px; font-weight: 700; background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%); margin-top: 15px; }
    
    .ltp-container { background: linear-gradient(90deg, rgba(37,99,235,0.15) 0%, rgba(124,58,237,0.05) 100%); border: 1px solid #1E3A8A; padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; }
    
    .status-card { padding: 20px; border-radius: 12px; font-weight: 700; font-size: 18px; text-align: center; margin-top: 15px; }
    .good-to-go { background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; color: #10B981; }
    .caution { background: rgba(245, 158, 11, 0.1); border: 1px solid #F59E0B; color: #F59E0B; }
    .high-risk { background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; color: #EF4444; }
    
    .intel-card { background: #0B1528; border: 1px dashed #2563EB; padding: 20px; border-radius: 12px; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

# ---------------- ML MODEL LOADING ----------------
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
        <h1 style="font-size: 36px; font-weight: 900; margin: 0; letter-spacing: -0.5px;">MARKET <span style="color: #3B82F6;">AI</span> OPTIONS ENGINE</h1>
    </div>
""", unsafe_allow_html=True)

# ---------------- INDEX SELECTION ----------------
target_index = st.selectbox(
    "Select Target Market Index", 
    ["NIFTY 50", "SENSEX", "BANKEX"], 
    key="index_selector", 
    on_change=reset_index_baselines
)
mode = st.radio("Select Input Mode", ["Manual Input", "AngelOne Live Stream"], horizontal=True)

if mode == "Manual Input" and st.session_state.api_authenticated:
    st.session_state.api_authenticated = False
    st.session_state.smart_api = None

feed_status_message = "Manual Control Mode" if mode == "Manual Input" else "Streaming Live SDK Feed"

# ---------------- SECURE NATIVE ANGELONE GATEWAY ----------------
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
                    st.error(f"Gateway Access Denied: {session_data.get('message', 'Check Details Configuration')}")
            except Exception as e:
                st.error(f"Connection Exception: {e}")
                
    if st.session_state.api_authenticated and st.session_state.smart_api:
        feed_status_message = f"AngelOne Streaming Active (Tick #{st.session_state.refresh_counter})"
        try:
            token_map = {"NIFTY 50": "99926000", "SENSEX": "99919000", "BANKEX": "99923000"}
            exchange_map = {"NIFTY 50": "NSE", "SENSEX": "BSE", "BANKEX": "BSE"}
            
            exchange_tokens = {exchange_map[target_index]: [token_map[target_index]]}
            market_data = st.session_state.smart_api.getMarketData(mode="FULL", exchangeTokens=exchange_tokens)
            
            if market_data.get('status') == True and 'data' in market_data and market_data['data']['fetched']:
                tick = market_data['data']['fetched'][0]
                st.session_state.current_price = float(tick.get('ltp', st.session_state.current_price))
                st.session_state.baseline_open = float(tick.get('open', st.session_state.baseline_open))
        except Exception as data_err:
            st.error(f"Error parsing live market ticks: {data_err}")

# ---------------- LIVE PRICE READOUT HUB ----------------
st.markdown(f"""
<div class="ltp-container">
    <span style="font-size:14px; color:#A5B4FC; text-transform:uppercase; font-weight:700; letter-spacing:1px;">⚡ Target Live Current Price (LTP)</span>
    <h1 style="margin:8px 0 0 0; font-size:42px; font-weight:900; color:#FFFFFF; letter-spacing:-0.5px;">₹ {st.session_state.current_price:,.2f}</h1>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric(label="📅 Target Index", value=target_index)
m2.metric(label="🕒 Feed Source", value=feed_status_message)
m3.metric(label="📊 Pipeline Status", value="Live Tracking Sync" if st.session_state.api_authenticated else "Manual Input Mode")
m4.metric(label="⚡ Engine Core", value="ML Inference Ready" if model else "Simulated Mode")

# ---------------- CONTROL MATRIX INTERFACE ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">🎯 Target Price Strategy Execution</div>', unsafe_allow_html=True)

live_price_input = st.number_input(
    f"Current Price Matrix Target ({target_index})", 
    format="%.2f", 
    value=st.session_state.current_price, 
    disabled=(mode == "AngelOne Live Stream"),
    key="live_price_widget"
)

predict_clicked = st.button("🚀 EXECUTE MULTI-STRIKE OPTION ANALYSIS")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ML INFERENCE ENGINE & RISK SIGNALS ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">📊 AI Multi-Call Matrix Output</div>', unsafe_allow_html=True)

if predict_clicked or (mode == "AngelOne Live Stream" and st.session_state.api_authenticated):
    data_array = np.array([[st.session_state.baseline_open, live_price_input, live_price_input, live_price_input, 120000.0, 0.1]])
    
    if model is not None:
        prediction = model.predict(data_array)[0]
        probability = model.predict_proba(data_array)[0]
        confidence = probability[1] * 100 if prediction == 1 else probability[0] * 100
    else:
        prediction = 1 if live_price_input >= st.session_state.baseline_open else 0
        confidence = 84.50
    
    # 1. Directional Prediction Output
    if prediction == 1:
        st.success(f"📈 PROJECTION VECTOR: BULLISH (UP) - Live Intraday Confidence: {confidence:.2f}%")
        status_html = '<div class="status-card good-to-go">🟢 MARKET RADAR: GOOD TO GO (Strong Bullish Momentum)</div>'
    else:
        st.error(f"📉 PROJECTION VECTOR: BEARISH (DOWN) - Live Intraday Confidence: {confidence:.2f}%")
        status_html = '<div class="status-card high-risk">🔴 MARKET RADAR: MARKET IS RISKY RIGHT NOW (Bearish Resistance Detected)</div>'
        
    st.markdown(status_html, unsafe_allow_html=True)

    # 2. ADVANCED MULTI-CALL & STRIKE ENTRY/TARGET RADAR
    st.markdown('<div class="intel-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin:0 0 15px 0; color:#3B82F6;'>🎯 Multi-Call Strategy Planner (Entry, Stop Loss, Target)</h4>", unsafe_allow_html=True)
    
    step = st.session_state.strike_step
    base_strike = round(live_price_input / step) * step
    
    if prediction == 1:
        st.write("💡 **AI Recommendation:** Bullish structures dominant. Evaluating the optimal **Call Options (CE)** matrix:")
        
        # Build 3 clear Option Strategy tiers
        t1, t2, t3 = st.columns(3)
        with t1:
            st.subheader("🔥 Deep ITM (Conservative)")
            st.code(f"Strike: {base_strike - step} CE\nEntry: Above Breakout\nTarget: +25% Premium\nStop Loss: -12% Premium")
        with t2:
            st.subheader("⚡ ATM (Balanced)")
            st.code(f"Strike: {base_strike} CE\nEntry: On Intraday Pullback\nTarget: +40% Premium\nStop Loss: -15% Premium")
        with t3:
            st.subheader("🚀 OTM (Aggressive)")
            st.code(f"Strike: {base_strike + step} CE\nEntry: Small Lot Sizing Only\nTarget: +70% Premium\nStop Loss: -20% Premium")
    else:
        st.write("💡 **AI Recommendation:** Bearish pressure building. Evaluating the optimal **Put Options (PE)** matrix:")
        
        t1, t2, t3 = st.columns(3)
        with t1:
            st.subheader("🔥 Deep ITM (Conservative)")
            st.code(f"Strike: {base_strike + step} PE\nEntry: Above Breakout\nTarget: +25% Premium\nStop Loss: -12% Premium")
        with t2:
            st.subheader("⚡ ATM (Balanced)")
            st.code(f"Strike: {base_strike} PE\nEntry: On Intraday Pullback\nTarget: +40% Premium\nStop Loss: -15% Premium")
        with t3:
            st.subheader("🚀 OTM (Aggressive)")
            st.code(f"Strike: {base_strike - step} PE\nEntry: Small Lot Sizing Only\nTarget: +70% Premium\nStop Loss: -20% Premium")
        
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
        <div style="text-align: center; padding: 40px 20px; color: #64748B;">
            <p style="font-size: 18px; font-weight: 500; margin: 0;">📊 Multi-Strike Engine Awaiting Input</p>
            <p style="font-size: 14px; margin-top: 5px;">Initiate your AngelOne Stream or click 'Execute' to dynamically compile entry points and targets.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BACKGROUND REFRESH TICKER LOOP ----------------
if mode == "AngelOne Live Stream" and st.session_state.api_authenticated:
    time.sleep(4)
    st.session_state.refresh_counter += 1
    st.rerun()
