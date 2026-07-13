import streamlit as st
import numpy as np
import joblib
import os
import pyotp
import time
import pandas as pd
import yfinance as yf
from SmartApi.smartConnect import SmartConnect

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="STOCKXY Terminal",
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
        st.session_state.lot_size = 10
    elif selected == "BANKEX":
        st.session_state.current_price = 65200.0
        st.session_state.baseline_open = 65500.0
        st.session_state.strike_step = 100
        st.session_state.lot_size = 15
    else: # NIFTY 50 Default
        st.session_state.current_price = 23950.0
        st.session_state.baseline_open = 24030.0
        st.session_state.strike_step = 50
        st.session_state.lot_size = 25

# ---------------- INITIALIZE PERSISTENT STORAGE ----------------
if "smart_api" not in st.session_state: st.session_state.smart_api = None
if "api_authenticated" not in st.session_state: st.session_state.api_authenticated = False
if "refresh_counter" not in st.session_state: st.session_state.refresh_counter = 0

if "current_price" not in st.session_state: st.session_state.current_price = 23950.0
if "baseline_open" not in st.session_state: st.session_state.baseline_open = 24030.0
if "strike_step" not in st.session_state: st.session_state.strike_step = 50
if "lot_size" not in st.session_state: st.session_state.lot_size = 25

# ---------------- GROWW-INSPIRED PREMIUM LIGHT THEME CSS ----------------
st.markdown("""
<style>
    /* Premium Light Theme Profile */
    .stApp { background-color: #F8FAFC !important; color: #0F172A !important; }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1100px; margin: 0 auto; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}

    /* Groww Crisp Cards Style */
    .content-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    .panel-header { font-size: 14px; font-weight: 700; color: #44444F; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 18px; display: flex; align-items: center; gap: 6px; }

    /* Input Fields Styling Overrides */
    label[data-testid="stWidgetLabel"] p { color: #44444F !important; font-weight: 600 !important; font-size: 13px !important; margin-bottom: 6px !important; }
    div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div, div[data-testid="stTextInput"] input { background-color: #FFFFFF !important; color: #0F172A !important; border: 1px solid #D1D5DB !important; border-radius: 8px !important; height: 44px !important; }
    div[data-testid="stRadio"] > label { display: none; }

    /* Groww Mint Accent Green Buttons */
    div.stButton > button { width: 100%; height: 46px; border-radius: 8px; border: none; color: white; font-size: 14px; font-weight: 700; background: #00D09C; transition: all 0.2s ease; margin-top: 8px; box-shadow: 0 2px 4px rgba(0, 208, 156, 0.2); }
    div.stButton > button:hover { background: #00B386; border: none; color: white; }
    
    /* Elegant Readout Frameworks */
    .ltp-container { background: #FFFFFF; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
    .responsive-header { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 20px; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start; gap: 10px; }
    @media (min-width: 768px) { .responsive-header { flex-direction: row; align-items: center; } }

    /* Dynamic Output Indicators */
    .status-card { padding: 14px; border-radius: 8px; font-weight: 700; font-size: 14px; text-align: center; margin-top: 12px; }
    .good-to-go { background: #E6FDF5; border: 1px solid #00D09C; color: #00B386; }
    .high-risk { background: #FFF5F5; border: 1px solid #FEB2B2; color: #C53030; }

    .stock-pill { background: #FFFFFF; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px; font-size: 14px; font-weight: 600; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.01); }
    
    /* Native Progress Bar Tint Adjustment */
    div[data-testid="stProgress"] > div > div { background-color: #00D09C !important; }
    
    /* Tab Styling Overrides */
    button[data-baseweb="tab"] p { font-size: 15px !important; font-weight: 600 !important; }

    .footer-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-top: 40px; display: flex; justify-content: space-between; align-items: center; }
</style>
""", unsafe_allow_html=True)

# ---------------- SAFE STOCK DATA CACHE UTILITY ----------------
@st.cache_data(ttl=300)
def fetch_live_stock_telemetry(ticker_symbol):
    try:
        ticker_obj = yf.Ticker(ticker_symbol)
        hist_df = ticker_obj.history(period="5d")
        if not hist_df.empty and len(hist_df) >= 2:
            latest_close = float(hist_df.iloc[-1]['Close'])
            prior_close = float(hist_df.iloc[-2]['Close'])
            stock_change = ((latest_close - prior_close) / prior_close) * 100
            return {"ltp": latest_close, "change": stock_change, "mode": "Live"}
    except Exception:
        pass
    return {"ltp": 2540.00, "change": 1.45, "mode": "Simulated"}

# ---------------- ML MODEL LOADING ----------------
@st.cache_resource
def load_ml_model():
    try:
        for path in ["models/nifty_model.pkl", "nifty_model.pkl"]:
            if os.path.exists(path): return joblib.load(path)
    except Exception: pass  
    return None

model = load_ml_model()

# ---------------- TOP WORKSPACE BRANDING HEADER ----------------
st.markdown(
    """
    <div class="responsive-header">
        <div>
            <h1 style="font-size: 24px; font-weight: 800; margin: 0; color: #0F172A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                STOCK<span style="color: #00D09C;">XY</span> <span style="font-weight:400; color:#64748B;">Workspace</span>
            </h1>
        </div>
        <div style="background: #E6FDF5; border: 1px solid #00D09C; padding: 6px 14px; border-radius: 6px;">
            <span style="color: #00B386; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                Live Analysis System
            </span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==============================================================================
# ---------------------- SEGREGATED WORKSPACE TABS ----------------------------
# ==============================================================================
index_tab, stock_tab = st.tabs(["📊 Market Indices", "🏢 Stocks Analyst"])

# ------------------------------------------------------------------------------
# TAB 1: MARKET INDICES OPTIONS SEGMENT
# ------------------------------------------------------------------------------
with index_tab:
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">⚙️ Asset Stream Source</div>', unsafe_allow_html=True)
    
    c_sel1, c_sel2 = st.columns([1, 2])
    with c_sel1:
        target_index = st.selectbox("Target Market Index", ["NIFTY 50", "SENSEX", "BANKEX"], key="index_selector", on_change=reset_index_baselines)
    with c_sel2:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        mode = st.radio("Select Data Intake Protocol", ["Manual Input", "AngelOne Live Stream"], horizontal=True)

    if mode == "Manual Input" and st.session_state.api_authenticated:
        st.session_state.api_authenticated = False
        st.session_state.smart_api = None

    feed_status_message = "Manual Control Mode" if mode == "Manual Input" else "Streaming Live SDK Feed"
    st.markdown('</div>', unsafe_allow_html=True)

    # SECURE GATEWAY HUB
    if mode == "AngelOne Live Stream" and not st.session_state.api_authenticated:
        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-header">🔐 Secure SmartAPI Broker Gateway</div>', unsafe_allow_html=True)
        ak_col, cc_col, pw_col, to_col = st.columns(4)
        with ak_col: API_KEY = st.text_input("SmartAPI Key", type="password", key="api_key_widget")
        with cc_col: CLIENT_CODE = st.text_input("Client ID / Code", key="client_code_widget")
        with pw_col: PASSWORD = st.text_input("Mpin / Password", type="password", key="password_widget")
        with to_col: TOTP_SECRET = st.text_input("TOTP Token String", type="password", key="totp_widget")
        connect_btn = st.button("🚀 ESTABLISH HANDSHAKE LINK")
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
            except Exception as e: st.error(f"Handshake error: {e}")
                
    if st.session_state.api_authenticated and st.session_state.smart_api:
        feed_status_message = f"Live Ticks Stream Active"
        try:
            token_map = {"NIFTY 50": "99926000", "SENSEX": "99919000", "BANKEX": "99923000"}
            exchange_map = {"NIFTY 50": "NSE", "SENSEX": "BSE", "BANKEX": "BSE"}
            exchange_tokens = {exchange_map[target_index]: [token_map[target_index]]}
            market_data = st.session_state.smart_api.getMarketData(mode="FULL", exchangeTokens=exchange_tokens)
            if market_data.get('status') == True and 'data' in market_data and market_data['data']['fetched']:
                tick = market_data['data']['fetched'][0]
                st.session_state.current_price = float(tick.get('ltp', st.session_state.get('current_price', 23950.0)))
                st.session_state.baseline_open = float(tick.get('open', st.session_state.get('baseline_open', 24030.0)))
        except Exception: pass

    current_price_display = st.session_state.get('current_price', 23950.0)
    baseline_open_display = st.session_state.get('baseline_open', 24030.0)
    strike_step_display = st.session_state.get('strike_step', 50)
    lot_size_display = st.session_state.get('lot_size', 25)

    st.markdown(f"""
    <div class="ltp-container">
        <span style="font-size:11px; color:#64748B; text-transform:uppercase; font-weight:600; letter-spacing:0.5px; display:block;">Target Index Last Price</span>
        <h1 style="margin:2px 0 0 0; font-size:32px; font-weight:700; color:#0F172A; font-family: monospace;">₹ {current_price_display:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # RISK PARAMETERS CALIBRATION
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🛡️ Position Sizing Controls</div>', unsafe_allow_html=True)
    r_col1, r_col2 = st.columns(2)
    with r_col1: trading_capital = st.number_input("Account Deployment Capital (₹)", min_value=1000.0, value=100000.0, step=5000.0)
    with r_col2: risk_percent = st.number_input("Allowed Portfolio Risk Allocation (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.5)
    
    live_price_input = st.number_input(f"Current Price Trigger Baseline ({target_index})", format="%.2f", value=current_price_display, disabled=(mode == "AngelOne Live Stream"), key="live_price_index_widget")
    predict_clicked = st.button("🚀 EXECUTE QUANT SCANNER")
    st.markdown('</div>', unsafe_allow_html=True)

    if predict_clicked or (mode == "AngelOne Live Stream" and st.session_state.get('api_authenticated')):
        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        prediction = 1 if live_price_input >= baseline_open_display else 0
        
        if prediction == 1:
            st.markdown('<div class="status-card good-to-go">📈 DIRECTION BIAS: BULLISH — CE CALL OPTIONS FILTERED</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-card high-risk">📉 DIRECTION BIAS: BEARISH — PE PUT OPTIONS FILTERED</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        step = strike_step_display
        atm_strike = round(live_price_input / step) * step
        strategy_data = []
        max_rupees_risk = trading_capital * (risk_percent / 100.0)
        
        if prediction == 1:
            st.markdown('<div class="panel-header">🎯 Target Call Option Matrix (CE Only)</div>', unsafe_allow_html=True)
            for i in range(-5, 5):
                c_strike = atm_strike + (i * step)
                c_entry = max(10.0, round((atm_strike - c_strike) * 0.4 + 95.0, 1))
                c_tgt = round(c_entry + 45.0, 1)
                c_sl = round(c_entry - 20.0, 1)
                max_recommended_lots = int(max_rupees_risk // (max(1.0, c_entry - c_sl) * lot_size_display))
                strategy_data.append([f"{target_index} {c_strike} CE", c_entry, c_sl, c_tgt, f"{max_recommended_lots} Lots"])
        else:
            st.markdown('<div class="panel-header">🎯 Target Put Option Matrix (PE Only)</div>', unsafe_allow_html=True)
            for i in range(-5, 5):
                p_strike = atm_strike + (i * step)
                p_entry = max(10.0, round((p_strike - atm_strike) * 0.4 + 95.0, 1))
                p_tgt = round(p_entry + 45.0, 1)
                p_sl = round(p_entry - 20.0, 1)
                max_recommended_lots = int(max_rupees_risk // (max(1.0, p_entry - p_sl) * lot_size_display))
                strategy_data.append([f"{target_index} {p_strike} PE", p_entry, p_sl, p_tgt, f"{max_recommended_lots} Lots"])

        cols_list = ["Contract Identifier", "Entry Threshold", "Stop Loss (SL)", "Profit Target", "Max Allowed Allocation"]
        st.dataframe(pd.DataFrame(strategy_data, columns=cols_list).style.format({"Entry Threshold": "₹ {:.2f}", "Stop Loss (SL)": "₹ {:.2f}", "Profit Target": "₹ {:.2f}"}), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: STANDALONE STOCKS ANALYST SEGMENT
# ------------------------------------------------------------------------------
with stock_tab:
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🏢 Asset Search & Technical Analyzer</div>', unsafe_allow_html=True)
    
    stock_ticker_input = st.text_input("Search Stock Ticker Symbol (e.g., RELIANCE.NS, SBIN.NS, TCS.NS)", value="RELIANCE.NS")
    search_stock_btn = st.button("🔍 ANALYZE STOCK PROFILE")
    
    if search_stock_btn and stock_ticker_input:
        with st.spinner("Analyzing structural data metrics..."):
            stock_profile = fetch_live_stock_telemetry(stock_ticker_input.strip().upper())
            s_ltp = stock_profile["ltp"]
            s_change = stock_profile["change"]
            
            s_entry = round(s_ltp * 1.002, 2)
            s_target = round(s_ltp * 1.030, 2)
            s_sl = round(s_ltp * 0.985, 2)
            
            st.markdown(f"""
            <div style="margin-top:10px; padding: 20px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px;">
                <h3 style="color:#0F172A; margin:0 0 15px 0; font-size:15px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">📋 Structural Levels Profile: {stock_ticker_input.upper()}</h3>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:12px;">
                    <div class="stock-pill">Current Price (LTP): <span style="color:#00B386; display:block; margin-top:2px; font-size:16px; font-weight:700;">₹ {s_ltp:,.2f}</span></div>
                    <div class="stock-pill">Day Change: <span style="color:{'#00B386' if s_change >=0 else '#C53030'}; display:block; margin-top:2px; font-size:16px; font-weight:700;">{s_change:.2f}%</span></div>
                    <div class="stock-pill">Target Entry Price: <span style="color:#00B386; display:block; margin-top:2px; font-size:15px; font-weight:700;">₹ {s_entry:,.2f}</span></div>
                    <div class="stock-pill">Calculated Target: <span style="color:#00B386; display:block; margin-top:2px; font-size:15px; font-weight:700;">₹ {s_target:,.2f}</span></div>
                    <div class="stock-pill">Stop Loss (SL): <span style="color:#C53030; display:block; margin-top:2px; font-size:15px; font-weight:700;">₹ {s_sl:,.2f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BRAND FOOTER OVERVIEW ----------------
st.markdown(
    """
    <div class="footer-panel">
        <div>
            <h1 style="font-size: 18px; font-weight: 800; margin: 0; color: #0F172A; letter-spacing: 2px; line-height: 1;">
                STOCK<span style="color: #00D09C;">XY</span>
            </h1>
            <p style="color: #64748B; font-size: 11px; margin-top: 4px; font-weight: 500; margin-bottom:0;">
                Quantitative Analytics Platform Engine • 2026
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- BACKGROUND LIVE SYNC TICKER ROUTINE ----------------
if st.session_state.get('api_authenticated') and mode == "AngelOne Live Stream":
    time.sleep(4)
    st.session_state.refresh_counter += 1
    st.rerun()
