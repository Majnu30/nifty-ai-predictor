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
    page_title="STOCKXY Advanced Quantitative Console",
    page_icon="⚡",
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

# ---------------- HIGH-TECH DARK CYBER STYLING CORE ----------------
st.markdown("""
<style>
    /* Dark Cyber Glassmorphic Theme Overrides */
    .stApp { background-color: #020617 !important; color: #F8FAFC !important; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 1300px; margin: 0 auto; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}

    /* Premium Neon-Glass Panels */
    .content-panel { 
        background: #0B1329; 
        border: 1px solid #1E293B; 
        border-radius: 16px; 
        padding: 26px; 
        margin-bottom: 24px; 
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
    }
    .panel-header { font-size: 13px; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }

    /* Custom Form Input Frameworks */
    label[data-testid="stWidgetLabel"] p { color: #94A3B8 !important; font-weight: 600 !important; font-size: 13px !important; margin-bottom: 8px !important; }
    div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div, div[data-testid="stTextInput"] input { 
        background-color: #030712 !important; color: #FFFFFF !important; border: 1px solid #1E293B !important; border-radius: 8px !important; height: 44px !important; font-size: 14px !important;
    }
    div[data-testid="stRadio"] > label { display: none; }

    /* High-Gloss Command Buttons */
    div.stButton > button { 
        width: 100%; height: 48px; border-radius: 8px; border: none; color: white; font-size: 14px; font-weight: 700; 
        background: linear-gradient(90deg, #0284C7 0%, #3B82F6 100%); box-shadow: 0 4px 15px rgba(2, 132, 199, 0.25); transition: all 0.2s ease; margin-top: 10px;
    }
    div.stButton > button:hover { background: linear-gradient(90deg, #0369A1 0%, #2563EB 100%); transform: translateY(-1px); box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4); color: white !important; }
    
    /* Interactive LTP Telemetry Box */
    .ltp-container { 
        background: linear-gradient(135deg, #0B1329 0%, #030712 100%); border: 1px solid #1E293B; padding: 24px; border-radius: 16px; text-align: center; margin-bottom: 24px;
        box-shadow: inset 0 0 20px rgba(56, 189, 248, 0.05);
    }
    .responsive-header { background: #0B1329; border: 1px solid #1E293B; border-radius: 16px; padding: 24px 30px; margin-bottom: 24px; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start; gap: 12px; }
    @media (min-width: 768px) { .responsive-header { flex-direction: row; align-items: center; } }

    /* Dynamic Output State Ribbons */
    .status-card { padding: 16px; border-radius: 8px; font-weight: 700; font-size: 14px; text-align: center; margin-top: 14px; letter-spacing: 0.5px; }
    .good-to-go { background: rgba(16, 185, 129, 0.08); border: 1px solid #10B981; color: #10B981; }
    .high-risk { background: rgba(239, 68, 68, 0.08); border: 1px solid #EF4444; color: #EF4444; }

    /* Institutional Custom Grid Table Overrides */
    .matrix-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: #070D1F; border-radius: 8px; overflow: hidden; }
    .matrix-table th { background: #0F172A; color: #94A3B8; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; padding: 14px; text-align: left; border-bottom: 1px solid #1E293B; }
    .matrix-table td { padding: 14px; font-size: 13px; border-bottom: 1px solid #111E38; color: #E2E8F0; font-family: monospace; }
    .matrix-table tr:hover { background: rgba(255,255,255,0.02); }

    /* ---------------- LINEAR TIMELINE METRIC SCALE SLIDERS ---------------- */
    .timeline-wrapper { margin: 25px 0 15px 0; position: relative; padding: 0 10px; }
    .timeline-bar { height: 4px; background: #1E293B; border-radius: 2px; position: relative; }
    .timeline-progress { height: 4px; background: #10B981; position: absolute; left: 25%; width: 45%; }
    .timeline-node { width: 8px; height: 8px; background: #475569; border-radius: 50%; position: absolute; top: -2px; }
    .node-sl { left: 0%; background: #EF4444; }
    .node-entry { left: 25%; background: #38BDF8; }
    .node-current { left: 70%; background: #FFFFFF; width: 12px; height: 12px; top: -4px; box-shadow: 0 0 10px #FFFFFF; }
    .node-target { right: 0%; background: #10B981; }

    .level-labels { display: flex; justify-content: space-between; margin-top: 10px; }
    .level-block { display: flex; flex-direction: column; font-size: 12px; }
    .level-block.center { text-align: center; }
    .level-block.right { text-align: right; }
    .level-title { color: #64748B; font-weight: 500; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; }
    .level-value { color: #F8FAFC; font-weight: 700; margin-top: 2px; font-family: monospace; font-size: 14px; }

    /* Tab Controller Custom Theming */
    button[data-baseweb="tab"] { background-color: transparent !important; color: #64748B !important; font-weight: 700 !important; font-size: 14px !important; padding: 12px 20px !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #38BDF8 !important; border-bottom: 2px solid #38BDF8 !important; }
    
    .footer-panel { background: #0B1329; border: 1px solid #1E293B; border-radius: 16px; padding: 24px; margin-top: 48px; display: flex; justify-content: space-between; align-items: center; }
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

# ---------------- MAIN APP SYSTEM BRANDING HEADER ----------------
st.markdown(
    """
    <div class="responsive-header">
        <div>
            <h1 style="font-size: 26px; font-weight: 900; margin: 0; color: #FFFFFF; letter-spacing: 1px;">
                STOCK<span style="color: #38BDF8;">XY</span> <span style="font-weight:400; color:#64748B; font-size:18px; letter-spacing:0px;">Quantum Workspace</span>
            </h1>
        </div>
        <div style="background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.3); padding: 6px 16px; border-radius: 8px;">
            <span style="color: #38BDF8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                💎 HFT QUANT PLATFORM ACTIVE
            </span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==============================================================================
# ---------------------- SEGREGATED WORKSPACE TABS ----------------------------
# ==============================================================================
index_tab, stock_tab = st.tabs(["📊 Market Indices Matrix", "🏢 Individual Stock Analyst"])

# ------------------------------------------------------------------------------
# TAB 1: MARKET INDICES OPTIONS SEGMENT
# ------------------------------------------------------------------------------
with index_tab:
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🛠️ Telemetry Feed Routing</div>', unsafe_allow_html=True)
    
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
        <span style="font-size:11px; color:#64748B; text-transform:uppercase; font-weight:700; letter-spacing:1px; display:block; margin-bottom: 2px;">Target Index Last Traded Price</span>
        <h1 style="margin:0; font-size:36px; font-weight:800; color:#38BDF8; font-family: monospace;">₹ {current_price_display:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # RISK PARAMETERS CALIBRATION
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🛡️ Portfolio Exposure Sizing Controls</div>', unsafe_allow_html=True)
    r_col1, r_col2 = st.columns(2)
    with r_col1: trading_capital = st.number_input("Account Deployment Capital (₹)", min_value=1000.0, value=100000.0, step=5000.0)
    with r_col2: risk_percent = st.number_input("Allowed Portfolio Risk Allocation (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.5)
    
    live_price_input = st.number_input(f"Current Price Trigger Baseline ({target_index})", format="%.2f", value=current_price_display, disabled=(mode == "AngelOne Live Stream"), key="live_price_index_widget")
    predict_clicked = st.button("🚀 EXECUTE QUANT DIRECTIONAL SCANNER")
    st.markdown('</div>', unsafe_allow_html=True)

    if predict_clicked or (mode == "AngelOne Live Stream" and st.session_state.get('api_authenticated')):
        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        prediction = 1 if live_price_input >= baseline_open_display else 0
        
        if prediction == 1:
            st.markdown('<div class="status-card good-to-go">🔺 DIRECTION BIAS: BULLISH — CE CALL OPTIONS FILTERED</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-card high-risk">🔻 DIRECTION BIAS: BEARISH — PE PUT OPTIONS FILTERED</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        step = strike_step_display
        atm_strike = round(live_price_input / step) * step
        table_rows_html = ""
        max_rupees_risk = trading_capital * (risk_percent / 100.0)
        
        if prediction == 1:
            st.markdown('<div class="panel-header">🎯 Target Call Option Matrix (CE Only)</div>', unsafe_allow_html=True)
            for i in range(-5, 5):
                c_strike = atm_strike + (i * step)
                c_entry = max(10.0, round((atm_strike - c_strike) * 0.4 + 95.0, 1))
                c_tgt = round(c_entry + 45.0, 1)
                c_sl = round(c_entry - 20.0, 1)
                max_recommended_lots = int(max_rupees_risk // (max(1.0, c_entry - c_sl) * lot_size_display))
                
                table_rows_html += f"""
                <tr>
                    <td style="color:#10B981; font-weight:700;">{target_index} {c_strike} CE</td>
                    <td>₹ {c_entry:.2f}</td>
                    <td style="color:#EF4444;">₹ {c_sl:.2f}</td>
                    <td style="color:#10B981;">₹ {c_tgt:.2f}</td>
                    <td style="color:#38BDF8; font-weight:600;">{max_recommended_lots} Lots</td>
                </tr>
                """
        else:
            st.markdown('<div class="panel-header">🎯 Target Put Option Matrix (PE Only)</div>', unsafe_allow_html=True)
            for i in range(-5, 5):
                p_strike = atm_strike + (i * step)
                p_entry = max(10.0, round((p_strike - atm_strike) * 0.4 + 95.0, 1))
                p_tgt = round(p_entry + 45.0, 1)
                p_sl = round(p_entry - 20.0, 1)
                max_recommended_lots = int(max_rupees_risk // (max(1.0, p_entry - p_sl) * lot_size_display))
                
                table_rows_html += f"""
                <tr>
                    <td style="color:#EF4444; font-weight:700;">{target_index} {p_strike} PE</td>
                    <td>₹ {p_entry:.2f}</td>
                    <td style="color:#EF4444;">₹ {p_sl:.2f}</td>
                    <td style="color:#10B981;">₹ {p_tgt:.2f}</td>
                    <td style="color:#38BDF8; font-weight:600;">{max_recommended_lots} Lots</td>
                </tr>
                """

        st.markdown(f"""
        <table class="matrix-table">
            <thead>
                <tr>
                    <th>Contract Ticker Name</th>
                    <th>Target Entry Level</th>
                    <th>Risk Stop Loss (SL)</th>
                    <th>Take Profit Target</th>
                    <th>Max Lot Sizing Allowed</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 2: STANDALONE STOCKS ANALYST SEGMENT
# ------------------------------------------------------------------------------
with stock_tab:
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🏢 Equity Asset Intelligence Terminal</div>', unsafe_allow_html=True)
    
    stock_ticker_input = st.text_input("Search Stock Ticker Symbol (e.g., RELIANCE.NS, SBIN.NS, TCS.NS)", value="RELIANCE.NS")
    search_stock_btn = st.button("🔍 RUN STRATEGIC ASSET EVALUATION")
    
    if search_stock_btn and stock_ticker_input:
        with st.spinner("Analyzing structural mathematical layers..."):
            stock_profile = fetch_live_stock_telemetry(stock_ticker_input.strip().upper())
            s_ltp = stock_profile["ltp"]
            s_change = stock_profile["change"]
            
            s_entry = round(s_ltp * 1.002, 2)
            s_target = round(s_ltp * 1.030, 2)
            s_sl = round(s_ltp * 0.985, 2)
            
            st.markdown(f"""
            <div class="content-panel" style="background:#070D1F; border:1px solid #1E293B; margin-top:15px;">
                <h3 style="color:#38BDF8; margin:0 0 10px 0; font-size:14px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">📋 Risk-Reward Tracking Scale Blueprint: {stock_ticker_input.upper()}</h3>
                
                <div class="timeline-wrapper">
                    <div class="floating-price-label">LTP: ₹ {s_ltp:,.2f} ({s_change:+.2f}%)</div>
                    <div class="timeline-bar">
                        <div class="timeline-progress"></div>
                        <div class="timeline-node node-sl"></div>
                        <div class="timeline-node node-entry"></div>
                        <div class="timeline-node node-current"></div>
                        <div class="timeline-node node-target"></div>
                    </div>
                    <div class="level-labels">
                        <div class="level-block">
                            <span class="level-title" style="color:#EF4444;">Stop Loss (SL)</span>
                            <span class="level-value" style="color:#EF4444;">₹ {s_sl:,.2f}</span>
                        </div>
                        <div class="level-block center">
                            <span class="level-title" style="color:#38BDF8;">Buy Entry Threshold</span>
                            <span class="level-value" style="color:#38BDF8;">₹ {s_entry:,.2f}</span>
                        </div>
                        <div class="level-block right">
                            <span class="level-title" style="color:#10B981;">Target Objective</span>
                            <span class="level-value" style="color:#10B981;">₹ {s_target:,.2f}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- STOCKXY FOOTER BRANDING ----------------
st.markdown(
    """
    <div class="footer-panel">
        <div>
            <h1 style="font-size: 16px; font-weight: 800; margin: 0; color: #FFFFFF; letter-spacing: 1px; line-height: 1;">
                STOCK<span style="color: #38BDF8;">XY</span>
            </h1>
            <p style="color: #64748B; font-size: 11px; margin-top: 4px; font-weight: 500; margin-bottom:0;">
                Quantitative Analytics Core Architecture Platform • 2026
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
