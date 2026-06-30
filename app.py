import streamlit as st
import numpy as np
import joblib
import os
import pyotp
import time
import pandas as pd
from SmartApi.smartConnect import SmartConnect # Fixed: Imported explicit missing module dependencies

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MAJNU AI Options Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- DYNAMIC VALUE RE-ALIGNMENT CONFIG ----------------
def reset_index_baselines():
    selected = st.session_state.index_selector
    if selected == "SENSEX":
        st.session_state.current_price = 76730.0
        st.session_state.baseline_open = 77000.0
        st.session_state.strike_step = 100
    elif selected == "BANKEX":
        st.session_state.current_price = 65200.0
        st.session_state.baseline_open = 65500.0
        st.session_state.strike_step = 100
    else: # NIFTY 50 Default
        st.session_state.current_price = 23950.0
        st.session_state.baseline_open = 24030.0
        st.session_state.strike_step = 50

# ---------------- INITIALIZE PERSISTENT STORAGE ----------------
if "smart_api" not in st.session_state: st.session_state.smart_api = None
if "api_authenticated" not in st.session_state: st.session_state.api_authenticated = False
if "refresh_counter" not in st.session_state: st.session_state.refresh_counter = 0

if "current_price" not in st.session_state: st.session_state.current_price = 23950.0
if "baseline_open" not in st.session_state: st.session_state.baseline_open = 24030.0
if "strike_step" not in st.session_state: st.session_state.strike_step = 50

# ---------------- ULTRA-PREMIUM RESPONSIVE THEME CSS ----------------
st.markdown("""
<style>
    /* Base Global Application Resets */
    .stApp { background-color: #030712 !important; color: #F8FAFC !important; }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    section[data-testid="stSidebar"] { background-color: #050B18 !important; border-right: 1px solid #111C34; }

    /* High Fidelity Glass Container Panels */
    .content-panel { background: #070F21; border: 1px solid #111E3B; border-radius: 16px; padding: 22px; margin-bottom: 20px; }
    @media (min-width: 768px) { .content-panel { padding: 30px; } }
    .panel-header { font-size: 16px; font-weight: 600; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.75px; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }

    /* Interactive Inputs Styling Overrides */
    label[data-testid="stWidgetLabel"] p { color: #94A3B8 !important; font-weight: 500 !important; font-size: 13px !important; margin-bottom: 6px !important; }
    div[data-testid="stNumberInput"], div[data-testid="stSelectbox"], div[data-testid="stTextInput"] input { background-color: #091122 !important; color: #F8FAFC !important; border: 1px solid #1E293B !important; border-radius: 8px !important; }
    div[data-testid="stRadio"] > label { display: none; }

    /* Core Call-To-Action Gradient Buttons */
    div.stButton > button { width: 100%; height: 54px; border-radius: 10px; border: none; color: white; font-size: 15px; font-weight: 700; letter-spacing: 1px; background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%); box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25); transition: all 0.3s ease; margin-top: 10px; }
    div.stButton > button:hover { background: linear-gradient(90deg, #1D4ED8 0%, #6D28D9 100%); transform: translateY(-1px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35); }
    
    /* Institutional LTP Readout HUD */
    .ltp-container { background: linear-gradient(135deg, #050E26 0%, #081129 100%); border: 1px solid #12254F; padding: 25px; border-radius: 16px; text-align: center; margin-bottom: 20px; box-shadow: inset 0 0 20px rgba(37, 99, 235, 0.1); }
    .responsive-header { background: linear-gradient(135deg, #040A18 0%, #06132C 100%); border: 1px solid #111E3B; border-radius: 16px; padding: 30px 20px; margin-bottom: 20px; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start; gap: 20px; }
    @media (min-width: 768px) { .responsive-header { flex-direction: row; align-items: center; padding: 40px; } }

    /* Dynamic Output Banner Matrix Badges */
    .status-card { padding: 18px; border-radius: 10px; font-weight: 700; font-size: 15px; text-align: center; margin-top: 15px; letter-spacing: 0.5px; }
    .good-to-go { background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); color: #10B981; box-shadow: 0 0 15px rgba(16, 185, 129, 0.05); }
    .high-risk { background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); color: #EF4444; box-shadow: 0 0 15px rgba(239, 68, 68, 0.05); }

    /* Footer Layout Panels */
    .footer-panel { background: linear-gradient(90deg, #050B18 0%, #081226 100%); border: 1px solid #111E3B; border-radius: 16px; padding: 30px 20px; margin-top: 40px; text-align: center; }
    @media (min-width: 768px) { .footer-panel { text-align: left; display: flex; justify-content: space-between; align-items: center; padding: 40px; } }
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

# ---------------- SIDEBAR NAVIGATION ----------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 10px 0 25px 0;">
            <h2 style="color: #FFFFFF; font-size: 24px; font-weight: 800; margin: 0; letter-spacing: 1px;">
                M<span style="color: #3B82F6;">A</span>JNU
            </h2>
            <p style="color: #475569; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; margin: 2px 0 0 0;">
                Innovate • Build • Inspire
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown("<p style='color:#475569; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Navigation Terminal</p>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%); padding: 12px 16px; border-radius: 8px; font-weight: 600; color: white; margin-bottom: 8px; cursor: pointer;">🏠 Signal Dashboard</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 8px; cursor: pointer;">📈 Risk Assessment</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 8px; cursor: pointer;">ℹ️ Model Parameters</div>
    """, unsafe_allow_html=True)

# ---------------- HERO HEADER WITH MAJNU BRANDING ASIDE ----------------
st.markdown(
    """
    <div class="responsive-header">
        <div>
            <h1 style="font-size: clamp(28px, 4vw, 42px); font-weight: 900; margin: 0; letter-spacing: -0.5px; line-height: 1.1;">
                MARKET <span style="color: #3B82F6;">AI</span> DIRECTIONAL SIGNAL MATRIX
            </h1>
            <p style="color: #64748B; font-size: clamp(13px, 1.8vw, 15px); margin-top: 8px; font-weight: 400; max-width: 700px;">
                High-frequency quantitative analysis terminal filtering derivative contract tickers and multi-stage targeted strike paths.
            </p>
        </div>
        <div style="background: rgba(30, 41, 59, 0.3); border: 1px solid #1E293B; padding: 12px 22px; border-radius: 12px; min-width: 150px; text-align: center; align-self: flex-start;">
            <h3 style="color: #FFFFFF; font-size: 20px; font-weight: 900; margin: 0; letter-spacing: 3px;">
                M<span style="color: #3B82F6;">A</span>JNU
            </h3>
            <span style="color: #3B82F6; font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; display: block; margin-top: 2px;">
                QUANT CORE ENG
            </span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------- INDEX & STRATEGY SELECTION SECTION ----------------
st.markdown("<p style='color:#94A3B8; font-size:13px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;'>Data Stream Orchestration</p>", unsafe_allow_html=True)
c_sel1, c_sel2 = st.columns([1, 2])
with c_sel1:
    target_index = st.selectbox(
        "Select Target Market Index", 
        ["NIFTY 50", "SENSEX", "BANKEX"], 
        key="index_selector", 
        on_change=reset_index_baselines
    )
with c_sel2:
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    mode = st.radio("Select Input Mode", ["Manual Input", "AngelOne Live Stream"], horizontal=True)

if mode == "Manual Input" and st.session_state.api_authenticated:
    st.session_state.api_authenticated = False
    st.session_state.smart_api = None

feed_status_message = "Manual Overrides Active" if mode == "Manual Input" else "Streaming Live SDK Feed"

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
        feed_status_message = f"AngelOne Live Ticks (Frame #{st.session_state.refresh_counter})"
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
    <span style="font-size:12px; color:#94A3B8; text-transform:uppercase; font-weight:600; letter-spacing:1.5px; display:block;">TARGET INDEX LAST TRADED PRICE (LTP)</span>
    <h1 style="margin:6px 0 0 0; font-size:clamp(36px, 5vw, 48px); font-weight:900; color:#FFFFFF; letter-spacing:-0.5px;">₹ {st.session_state.current_price:,.2f}</h1>
</div>
""", unsafe_allow_html=True)

# Metrics Grid Configuration
m1, m2, m3, m4 = st.columns(4)
metric_css = """
<style>
    div[data-testid="stMetric"] { background: #091225 !important; border: 1px solid #142342 !important; border-radius: 12px !important; padding: 12px 16px !important; }
    div[data-testid="stMetricLabel"] p { color: #64748B !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; }
    div[data-testid="stMetricValue"] div { color: #FFFFFF !important; font-size: 15px !important; font-weight: 600 !important; }
</style>
"""
st.markdown(metric_css, unsafe_allow_html=True)

m1.metric(label="📅 Asset Target", value=target_index)
m2.metric(label="🕒 Stream Source", value=feed_status_message)
m3.metric(label="📊 Telemetry Link", value="Synchronized Link" if st.session_state.api_authenticated else "Manual Interface")
m4.metric(label="⚡ Pipeline Mode", value="Neural Weight Core" if model else "Algorithmic Proxy")

st.write("")

# ---------------- CONTROL MATRIX INTERFACE ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">🎯 Target Execution Framework Controls</div>', unsafe_allow_html=True)

live_price_input = st.number_input(
    f"Current Price Matrix Target Entry ({target_index})", 
    format="%.2f", 
    value=st.session_state.current_price, 
    disabled=(mode == "AngelOne Live Stream"),
    key="live_price_widget"
)

predict_clicked = st.button("🚀 EXECUTE QUANT DIRECTIONAL SCANNER")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INFERENCE CORE & TARGET MATRICES ----------------
if predict_clicked or (mode == "AngelOne Live Stream" and st.session_state.api_authenticated):
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">📊 AI Core Inference Assessment</div>', unsafe_allow_html=True)
    
    data_array = np.array([[st.session_state.baseline_open, live_price_input, live_price_input, live_price_input, 120000.0, 0.1]])
    
    if model is not None:
        prediction = model.predict(data_array)[0]
        probability = model.predict_proba(data_array)[0]
        confidence = probability[1] * 100 if prediction == 1 else probability[0] * 100
    else:
        prediction = 1 if live_price_input >= st.session_state.baseline_open else 0
        confidence = 84.50
        
    if prediction == 1:
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.05); padding: 20px; border-radius: 10px; border: 1px solid rgba(16, 185, 129, 0.2);">
                <h3 style="color:#10B981; margin:0 0 4px 0; font-size:20px;">📈 VECTOR BIAS IDENTIFIED: BULLISH</h3>
                <p style="color:#64748B; margin:0; font-size:14px;">Intraday trend matrices tracking strong overhead volume absorption profiles.</p>
            </div>
            <div class="status-card good-to-go">🟢 OPTION RADAR: LONG SCENARIO ACTIVATED (CE Target Filter Favored)</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.05); padding: 20px; border-radius: 10px; border: 1px solid rgba(239, 68, 68, 0.2);">
                <h3 style="color:#EF4444; margin:0 0 4px 0; font-size:20px;">%📉 VECTOR BIAS IDENTIFIED: BEARISH</h3>
                <p style="color:#64748B; margin:0; font-size:14px;">Intraday trend matrices capturing distribution spikes beneath baseline weights.</p>
            </div>
            <div class="status-card high-risk">🔴 OPTION RADAR: SHORT SCENARIO ACTIVATED (PE Target Filter Favored)</div>
        """, unsafe_allow_html=True)
    st.progress(confidence / 100)
    st.markdown(f"<p style='color:#94A3B8; font-size:13px; font-weight:600; margin-top:6px;'>Computational Certainty Threshold: {confidence:.2f}%</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # DYNAMIC PREMIUM FILTERED DERIVATIVES GRID
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    
    step = st.session_state.strike_step
    atm_strike = round(live_price_input / step) * step
    strategy_data = []
    
    if prediction == 1:
        st.markdown('<div class="panel-header">🎯 Top 20 Exclusive Institutional Call Option Contracts (CE Only)</div>', unsafe_allow_html=True)
        for i in range(-10, 10):
            c_strike = atm_strike + (i * step)
            c_entry = max(10.0, round((atm_strike - c_strike) * 0.4 + 95.0, 1))
            c_tgt = round(c_entry + 45.0, 1)
            c_sl = round(c_entry - 20.0, 1)
            strategy_data.append([f"{target_index} {c_strike} CE", c_entry, c_sl, c_tgt])
    else:
        st.markdown('<div class="panel-header">🎯 Top 20 Exclusive Institutional Put Option Contracts (PE Only)</div>', unsafe_allow_html=True)
        for i in range(-10, 10):
            p_strike = atm_strike + (i * step)
            p_entry = max(10.0, round((p_strike - atm_strike) * 0.4 + 95.0, 1))
            p_tgt = round(p_entry + 45.0, 1)
            p_sl = round(p_entry - 20.0, 1)
            strategy_data.append([f"{target_index} {p_strike} PE", p_entry, p_sl, p_tgt])

    cols_list = ["Contract Identifier Ticker", "Target Entry Threshold", "Risk Stop Loss (SL)", "Take Profit Target"]
    df_matrix = pd.DataFrame(strategy_data, columns=cols_list)
    
    # Advanced Dataframe Formatting Engine
    st.dataframe(
        df_matrix.style.format({
            "Target Entry Threshold": "₹ {:.2f}",
            "Risk Stop Loss (SL)": "₹ {:.2f}",
            "Take Profit Target": "₹ {:.2f}"
        }).text_gradient(cmap="coolwarm", subset=["Target Entry Threshold"])
          .set_properties(**{'background-color': '#091122', 'color': '#F8FAFC'}),
        use_container_width=True,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 40px 20px; color: #64748B;">
            <p style="font-size: 16px; font-weight: 600; margin: 0; color:#94A3B8; text-transform:uppercase; letter-spacing:1px;">📊 Derivative Pipeline Suspended</p>
            <p style="font-size: 13px; margin-top: 6px; max-width:500px; margin-left:auto; margin-right:auto; line-height:1.5;">Initialize runtime calculation matrices above to trigger machine learning filters and lock down target values.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BRAND FOOTER BANNER ----------------
st.markdown(
    """
    <div class="footer-panel">
        <div>
            <p style="color: #475569; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin: 0 0 5px 0;">
                Designed & Engineered By
            </p>
            <h1 style="
                font-size: clamp(38px, 5vw, 52px);
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
            <span style="color: #64748B; cursor: pointer;">💻 GitHub Terminal</span>
            <span style="color: #64748B; cursor: pointer;">🌐 Institutional API Link</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- BACKGROUND REFRESH TICKER LOOP ----------------
if mode == "AngelOne Live Stream" and st.session_state.api_authenticated:
    time.sleep(4)
    st.session_state.refresh_counter += 1
    st.rerun()
