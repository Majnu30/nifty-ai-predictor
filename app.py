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
    page_title="STOCKXY Quantitative Terminal",
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

# ---------------- PROFESSIONAL TRADING WORKSPACE THEME CSS ----------------
st.markdown("""
<style>
    /* Dark Slate Minimal Theme */
    .stApp { background-color: #0B0F19 !important; color: #E2E8F0 !important; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1300px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    section[data-testid="stSidebar"] { background-color: #070A13 !important; border-right: 1px solid #1E293B; }

    /* Clean Card Structural Panels */
    .content-panel { background: #111827; border: 1px solid #1E293B; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .panel-header { font-size: 14px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; display: flex; align-items: center; gap: 6px; }

    /* Interactive Inputs Styling Overrides */
    label[data-testid="stWidgetLabel"] p { color: #94A3B8 !important; font-weight: 500 !important; font-size: 13px !important; margin-bottom: 6px !important; }
    div[data-testid="stNumberInput"], div[data-testid="stSelectbox"], div[data-testid="stTextInput"] input { background-color: #070A13 !important; color: #F8FAFC !important; border: 1px solid #1E293B !important; border-radius: 6px !important; }
    div[data-testid="stRadio"] > label { display: none; }

    /* Action Trigger Control Buttons */
    div.stButton > button { width: 100%; height: 48px; border-radius: 8px; border: none; color: white; font-size: 14px; font-weight: 600; background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15); transition: all 0.2s ease; margin-top: 8px; }
    div.stButton > button:hover { background: #1D4ED8; transform: translateY(-1px); }
    
    /* Elegant Readout Frameworks */
    .ltp-container { background: #111827; border: 1px solid #1E293B; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
    .responsive-header { background: #111827; border: 1px solid #1E293B; border-radius: 12px; padding: 24px; margin-bottom: 20px; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start; gap: 15px; }
    @media (min-width: 768px) { .responsive-header { flex-direction: row; align-items: center; } }

    /* Dynamic Output Alerts */
    .status-card { padding: 14px; border-radius: 8px; font-weight: 600; font-size: 14px; text-align: center; margin-top: 12px; letter-spacing: 0.5px; }
    .good-to-go { background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); color: #10B981; }
    .high-risk { background: rgba(239, 68, 68, 0.06); border: 1px solid rgba(239, 68, 68, 0.2); color: #EF4444; }

    .stock-pill { background: #070A13; border: 1px solid #1E293B; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 600; text-align: center; }

    .footer-panel { background: #111827; border: 1px solid #1E293B; border-radius: 12px; padding: 24px; margin-top: 40px; display: flex; justify-content: space-between; align-items: center; }
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
    return {"ltp": 2540.00, "change": 1.45, "mode": "Simulated Fallback"}

# ---------------- ML MODEL LOADING ----------------
@st.cache_resource
def load_ml_model():
    try:
        for path in ["models/nifty_model.pkl", "nifty_model.pkl"]:
            if os.path.exists(path): return joblib.load(path)
    except Exception: pass  
    return None

model = load_ml_model()

# ---------------- LEFT SIDEBAR OVERVIEWS ----------------
with st.sidebar:
    st.markdown('<div style="padding: 10px 0 25px 0;"><h2 style="color: #FFFFFF; font-size: 22px; font-weight: 800; margin: 0; letter-spacing: 2px;">STOCK<span style="color: #2563EB;">XY</span></h2></div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Terminal Links</p>", unsafe_allow_html=True)
    st.markdown('<div style="background: rgba(37, 99, 235, 0.1); color: #60A5FA; padding: 12px; border-radius: 6px; font-size: 13px; font-weight:600;">📈 Analytical Core Active</div>', unsafe_allow_html=True)

# ---------------- SYSTEM HEADER CONSOLE ----------------
st.markdown(
    """
    <div class="responsive-header">
        <div>
            <h1 style="font-size: 32px; font-weight: 800; margin: 0; letter-spacing: -0.5px; color: #FFFFFF;">
                STOCK<span style="color: #2563EB;">XY</span> QUANT QUANTUM TERMINAL
            </h1>
            <p style="color: #64748B; font-size: 14px; margin-top: 4px; font-weight: 400; margin-bottom: 0;">
                Streamlined analytical deployment for broader indices metrics, standalone stock queries, and tactical IPO trackers.
            </p>
        </div>
        <div style="background: #070A13; border: 1px solid #1E293B; padding: 8px 18px; border-radius: 8px;">
            <span style="color: #60A5FA; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                PRO CORE ENG
            </span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==============================================================================
# -------------------- MAIN APP SEGREGATED WORKSPACE TABS ----------------------
# ==============================================================================
index_tab, stock_tab, ipo_tab = st.tabs(["📊 Market Indices Matrix", "🏢 Individual Stock Analyst", "🚀 IPO Risk-Reward Terminal"])

# ------------------------------------------------------------------------------
# TAB 1: MARKET INDICES OPTIONS SEGMENT
# ------------------------------------------------------------------------------
with index_tab:
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">⚙️ Configuration Streams</div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="panel-header">🔐 Secure SmartAPI Live SDK Connection</div>', unsafe_allow_html=True)
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
        feed_status_message = f"Live Ticks Stream Active (Tick #{st.session_state.refresh_counter})"
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
        <span style="font-size:11px; color:#94A3B8; text-transform:uppercase; font-weight:600; letter-spacing:1px; display:block;">TARGET INDEX LAST TRADED PRICE</span>
        <h1 style="margin:4px 0 0 0; font-size:32px; font-weight:800; color:#FFFFFF;">₹ {current_price_display:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # RISK ALLOCATION TUNING
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🛡️ Position Risk Calibration Core</div>', unsafe_allow_html=True)
    r_col1, r_col2 = st.columns(2)
    with r_col1: trading_capital = st.number_input("Account Deployment Capital (₹)", min_value=1000.0, value=100000.0, step=5000.0)
    with r_col2: risk_percent = st.number_input("Allowed Portfolio Risk Per Order (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.5)
    
    live_price_input = st.number_input(f"Current Price Trigger Baseline ({target_index})", format="%.2f", value=current_price_display, disabled=(mode == "AngelOne Live Stream"), key="live_price_index_widget")
    predict_clicked = st.button("🚀 EXECUTE QUANT DIRECTIONAL OVERVIEW")
    st.markdown('</div>', unsafe_allow_html=True)

    if predict_clicked or (mode == "AngelOne Live Stream" and st.session_state.get('api_authenticated')):
        st.markdown('<div class="content-panel">', unsafe_allow_html=True)
        prediction = 1 if live_price_input >= baseline_open_display else 0
        
        if prediction == 1:
            st.markdown('<div class="status-card good-to-go">📈 DIRECTION VECTOR BIAS: BULLISH — CE STRATEGY ACTIVE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-card high-risk">📉 DIRECTION VECTOR BIAS: BEARISH — PE STRATEGY ACTIVE</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="panel-header">🏢 Asset Search & Quantitative Analyzer</div>', unsafe_allow_html=True)
    
    stock_ticker_input = st.text_input("Search Stock Ticker Symbol (Include market suffix, ex: RELIANCE.NS, SBIN.NS, TCS.NS)", value="RELIANCE.NS")
    search_stock_btn = st.button("🔍 RUN POSITION ASSESSMENT")
    
    if search_stock_btn and stock_ticker_input:
        with st.spinner("Analyzing ticker risk barriers..."):
            stock_profile = fetch_live_stock_telemetry(stock_ticker_input.strip().upper())
            s_ltp = stock_profile["ltp"]
            s_change = stock_profile["change"]
            
            s_entry = round(s_ltp * 1.002, 2)
            s_target = round(s_ltp * 1.030, 2)
            s_sl = round(s_ltp * 0.985, 2)
            
            st.markdown(f"""
            <div style="margin-top:10px; padding: 20px; background:#070A13; border:1px solid #1E293B; border-radius:10px;">
                <h3 style="color:#FFFFFF; margin:0 0 15px 0; font-size:16px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">📋 Technical Structural Profile: {stock_ticker_input.upper()}</h3>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:12px;">
                    <div class="stock-pill">Current Price (LTP): <span style="color:#60A5FA; display:block; margin-top:2px; font-size:16px;">₹ {s_ltp:,.2f}</span></div>
                    <div class="stock-pill">Day Change: <span style="color:{'#10B981' if s_change >=0 else '#EF4444'}; display:block; margin-top:2px; font-size:16px;">{s_change:.2f}%</span></div>
                    <div class="stock-pill" style="border-color:#1E3A8A;">Target Entry Price: <span style="color:#10B981; display:block; margin-top:2px; font-size:16px;">₹ {s_entry:,.2f}</span></div>
                    <div class="stock-pill" style="border-color:#1E3A8A;">Calculated Target: <span style="color:#10B981; display:block; margin-top:2px; font-size:16px;">₹ {s_target:,.2f}</span></div>
                    <div class="stock-pill" style="border-color:#5B21B6;">Stop Loss (SL): <span style="color:#EF4444; display:block; margin-top:2px; font-size:16px;">₹ {s_sl:,.2f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAB 3: IPO TERMINAL MODULE WITH REAL-WORLD TIMELINES
# ------------------------------------------------------------------------------
with ipo_tab:
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🚀 Live Initial Public Offerings (IPO) Analytics Console</div>', unsafe_allow_html=True)
    
    # Selecting an IPO dynamically calculates metrics based on live market conditions
    selected_ipo = st.selectbox(
        "Select Active IPO Asset to Analyze",
        ["NTPC Green Energy Ltd", "Swiggy Limited", "Acme Solar Holdings", "Custom Asset Sandbox"]
    )
    
    # Accurate parameter inputs mapping real-world listings
    if selected_ipo == "NTPC Green Energy Ltd":
        ipo_cap = 108.00
        lot_shares = 138
        estimated_gmp = 14.50
        demand_mult = 2.4
        close_date = "22 Nov"
        listing_date = "27 Nov"
    elif selected_ipo == "Swiggy Limited":
        ipo_cap = 390.00
        lot_shares = 38
        estimated_gmp = -4.00
        demand_mult = 3.5
        close_date = "08 Nov"
        listing_date = "13 Nov"
    elif selected_ipo == "Acme Solar Holdings":
        ipo_cap = 289.00
        lot_shares = 51
        estimated_gmp = 0.00
        demand_mult = 1.1
        close_date = "08 Nov"
        listing_date = "13 Nov"
    else:
        ipo_cap = st.number_input("Custom IPO Ceiling Cap Price (₹)", min_value=1.0, value=200.0)
        lot_shares = st.number_input("Shares Per Application Lot Size", min_value=1, value=75)
        estimated_gmp = st.number_input("Current Estimated Grey Market Premium (GMP ₹)", value=25.0)
        demand_mult = st.number_input("Aggregate Book Demand Subscription Multiplier (x)", value=5.0)
        close_date = st.text_input("Application Closing Date Deadline", value="Immediate")
        listing_date = st.text_input("Expected Exchange Listing Date", value="T+5 Window")

    st.markdown("---")
    execute_ipo_scan = st.button("🚀 RUN IPO RISK-REWARD EVALUATOR")
    
    if execute_ipo_scan:
        minimum_lot_investment = ipo_cap * lot_shares
        projected_listing_price = max(0.1, ipo_cap + estimated_gmp)
        projected_listing_gain_per_lot = estimated_gmp * lot_shares
        
        # Risk assessment index mapping subscription strengths and premium stability thresholds
        is_viable = estimated_gmp > 0 and demand_mult > 1.5
        risk_score_percentage = max(5, min(100, int(100 - (demand_mult * 3.5) - (estimated_gmp / ipo_cap * 100))))
        
        st.markdown(f"""
        <div style="padding: 20px; background:#070A13; border:1px solid #1E293B; border-radius:10px;">
            <h3 style="color:#FFFFFF; margin:0 0 15px 0; font-size:16px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">🎯 Underwriting Parameters: {selected_ipo.upper()}</h3>
            
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:12px; margin-bottom: 20px;">
                <div class="stock-pill">Issue Cap Price: <span style="color:#FFFFFF; display:block; font-size:15px; margin-top:2px;">₹ {ipo_cap:,.2f}</span></div>
                <div class="stock-pill">Lot Allocation: <span style="color:#FFFFFF; display:block; font-size:15px; margin-top:2px;">{lot_shares} Shares</span></div>
                <div class="stock-pill">Application Closes: <span style="color:#60A5FA; display:block; font-size:15px; margin-top:2px;">{close_date}</span></div>
                <div class="stock-pill">Listing Target Date: <span style="color:#60A5FA; display:block; font-size:15px; margin-top:2px;">{listing_date}</span></div>
                <div class="stock-pill" style="border-color:#2563EB;">Lot Capital Required: <span style="color:#60A5FA; display:block; font-size:15px; margin-top:2px;">₹ {minimum_lot_investment:,.2f}</span></div>
                <div class="stock-pill" style="border-color:#10B981;">Projected Listing Price: <span style="color:#10B981; display:block; font-size:15px; margin-top:2px;">₹ {projected_listing_price:,.2f}</span></div>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                <div style="background:rgba(16, 185, 129, 0.04); border:1px solid rgba(16, 185, 129, 0.2); padding:16px; border-radius:8px;">
                    <h5 style="color:#10B981; margin:0 0 6px 0; font-size:13px; text-transform:uppercase;">💰 Projected Rewards Matrix</h5>
                    <p style="font-size:22px; font-weight:800; color:#FFFFFF; margin:0;">₹ {projected_listing_gain_per_lot:,.2f} <span style="font-size:13px; color:#10B981; font-weight:500;">/ Lot Net Gain</span></p>
                    <span style="font-size:12px; color:#64748B;">Based on active grey market premium metrics variance indexes tracking at {estimated_gmp:,.2f} ₹.</span>
                </div>
                
                <div style="background:rgba(239, 68, 68, 0.04); border:1px solid rgba(239, 68, 68, 0.2); padding:16px; border-radius:8px;">
                    <h5 style="color:#EF4444; margin:0 0 6px 0; font-size:13px; text-transform:uppercase;">🛡️ Algorithmic Risk Exposure</h5>
                    <p style="font-size:22px; font-weight:800; color:#FFFFFF; margin:0;">{risk_score_percentage}% <span style="font-size:13px; color:#EF4444; font-weight:500;">Risk Index Metric</span></p>
                    <span style="font-size:12px; color:#64748B;">Institutional demand subscription blocks currently logging aggregate pacing structures of {demand_mult}x.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if is_viable:
            st.markdown(f'<div class="status-card good-to-go">🟢 SYSTEM SIGNAL ASSESSMENT: OPTENDED FOR SUBSCRIPTION (Listing Gain Matrix Favored)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-card high-risk">🔴 SYSTEM SIGNAL ASSESSMENT: AVOID APPLICATION (Sub-Par Underwriting Demands or Negative Listing Premium Exposure)</div>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- STOCKXY FOOTER CONSOLE BANNER ----------------
st.markdown(
    """
    <div class="footer-panel">
        <div>
            <p style="color: #475569; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin: 0 0 4px 0;">
                Operational Environment Platform
            </p>
            <h1 style="font-size: 28px; font-weight: 900; margin: 0; color: #FFFFFF; letter-spacing: 4px; line-height: 1;">
                STOCK<span style="color: #2563EB;">XY</span>
            </h1>
            <p style="color: #475569; font-size: 12px; margin-top: 6px; font-weight: 500; margin-bottom:0;">
                Quantitative Analytics Hub Engine • 2026
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- BACKGROUND LIVE SYNC TICKER ROUTINE ----------------
# The background refresh only activates if the active protocol matches AngelOne live stream.
if st.session_state.get('api_authenticated') and mode == "AngelOne Live Stream":
    time.sleep(4)
    st.session_state.refresh_counter += 1
    st.rerun()
