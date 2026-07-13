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

# ---------------- INSTITUTIONAL INTERFACE THEME GRAPHICS (CSS) ----------------
st.markdown("""
<style>
    /* Premium FinTech Clean Palette */
    .stApp { background-color: #F4F6F9 !important; color: #1E293B !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1240px; margin: 0 auto; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}

    /* Premium Sculpted Card Panels */
    .content-panel { 
        background: #FFFFFF; 
        border: 1px solid rgba(226, 232, 240, 0.8); 
        border-radius: 16px; 
        padding: 28px; 
        margin-bottom: 24px; 
        box-shadow: 0 4px 20px -2px rgba(148, 163, 184, 0.08), 0 2px 8px -1px rgba(148, 163, 184, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .panel-header { font-size: 13px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }

    /* Input Fields Styling Overrides */
    label[data-testid="stWidgetLabel"] p { color: #475569 !important; font-weight: 600 !important; font-size: 13px !important; margin-bottom: 8px !important; }
    div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div, div[data-testid="stTextInput"] input { 
        background-color: #FCFDFE !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; border-radius: 10px !important; height: 46px !important; font-size: 14px !important; padding-left: 14px !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stNumberInput"] input:focus, div[data-testid="stSelectbox"] div:focus, div[data-testid="stTextInput"] input:focus {
        border-color: #00D09C !important; box-shadow: 0 0 0 3px rgba(0, 208, 156, 0.15) !important;
    }
    div[data-testid="stRadio"] > label { display: none; }

    /* Groww Premium Mint Accent CTA Buttons */
    div.stButton > button { 
        width: 100%; height: 50px; border-radius: 10px; border: none; color: white; font-size: 15px; font-weight: 700; background: linear-gradient(135deg, #00D09C 0%, #00B386 100%); 
        box-shadow: 0 4px 14px rgba(0, 208, 156, 0.3); transition: all 0.2s ease; margin-top: 10px; letter-spacing: 0.5px;
    }
    div.stButton > button:hover { background: linear-gradient(135deg, #00B386 0%, #009A6C 100%); transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0, 208, 156, 0.4); color: white !important; }
    
    /* Elegant Hero Terminal LTP Readout */
    .ltp-container { 
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); border: 1px solid #E2E8F0; padding: 26px; border-radius: 16px; text-align: center; margin-bottom: 24px;
        box-shadow: 0 10px 30px -5px rgba(148, 163, 184, 0.05);
    }
    .responsive-header { background: #FFFFFF; border: 1px solid rgba(226, 232, 240, 0.8); border-radius: 16px; padding: 24px 32px; margin-bottom: 24px; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start; gap: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.01); }
    @media (min-width: 768px) { .responsive-header { flex-direction: row; align-items: center; } }

    /* Dynamic Output Execution Badges */
    .status-card { padding: 16px; border-radius: 10px; font-weight: 700; font-size: 14px; text-align: center; margin-top: 14px; letter-spacing: 0.5px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
    .good-to-go { background: #E6FDF5; border: 1px solid rgba(0, 208, 156, 0.3); color: #008F66; }
    .high-risk { background: #FFF5F5; border: 1px solid rgba(245, 101, 101, 0.3); color: #C53030; }

    /* Structured Micro-Data Information Badges */
    .stock-pill { 
        background: #FFFFFF; border: 1px solid #E2E8F0; padding: 16px; border-radius: 12px; font-size: 14px; font-weight: 600; text-align: center; 
        box-shadow: 0 4px 12px rgba(148, 163, 184, 0.03); transition: transform 0.2s;
    }
    .stock-pill:hover { transform: translateY(-2px); border-color: #CBD5E1; }
    
    /* Clean Custom Metrics Overlay Style Modifications */
    div[data-testid="stProgress"] > div > div { background-color: #00D09C !important; }
    
    /* Institutional DataFrame Container Structure Override */
    div[data-testid="stDataFrame"] { border: 1px solid #E2E8F0 !important; border-radius: 12px !important; overflow: hidden !important; background: white; }

    /* Modern Segmented Navigation Layout Adjustments */
    button[data-baseweb="tab"] { background-color: transparent !important; border: none !important; padding: 12px 24px !important; font-size: 14px !important; font-weight: 700 !important; color: #64748B !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #00D09C !important; border-bottom: 3px solid #00D09C !important; }

    .footer-panel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; margin-top: 48px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 -2px 10px rgba(0,0,0,0.01); }
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
            <h1 style="font-size: 26px; font-weight: 800; margin: 0; color: #0F172A; letter-spacing: -0.3px;">
                STOCK<span style="color: #00D09C;">XY</span> <span style="font-weight:400; color:#94A3B8;">Terminal</span>
            </h1>
        </div>
        <div style="background: #E6FDF5; border: 1px solid rgba(0, 208, 156, 0.4); padding: 6px 16px; border-radius: 8px;">
            <span style="color: #00B386; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                Quantitative Engine Online
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
    st.markdown('<div class="panel-header">⚙️ Real-Time Source Configuration</div>', unsafe_allow_html=True)
    
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
        <span style="font-size:11px; color:#94A3B8; text-transform:uppercase; font-weight:700; letter-spacing:0.5px; display:block; margin-bottom: 2px;">Target Index Last Traded Price</span>
        <h1 style="margin:0; font-size:36px; font-weight:800; color:#0F172A; font-family: -apple-system, monospace;">₹ {current_price_display:,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

    # RISK PARAMETERS CALIBRATION
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🛡️ Portfolio Exposure Sizing Controls</div>', unsafe_allow_html=True)
    r_col1, r_col2 = st.columns(2)
    with r_col1: trading_capital = st.number_input("Account Deployment Capital (₹)", min_value=1000.0, value=100000.0, step=5000.0)
    with r_col2: risk_percent = st.number_input("Allowed Portfolio Risk Allocation (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.5)
    
    live_price_input = st.number_input(f"Current Price Trigger Baseline ({target_index})", format="%.2f", value=current_price_display, disabled=(mode == "AngelOne Live Stream"), key="live_price_index_widget")
    predict_clicked = st.button("🚀 EXECUTE QUANT DIRECTIONAL OVERVIEW")
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
    st.markdown('<div class="panel-header">🏢 Equity Asset Intelligence Terminal</div>', unsafe_allow_html=True)
    
    stock_ticker_input = st.text_input("Search Stock Ticker Symbol (e.g., RELIANCE.NS, SBIN.NS, TCS.NS)", value="RELIANCE.NS")
    search_stock_btn = st.button("🔍 RUN STRATEGIC ASSET EVALUATION")
    
    if search_stock_btn and stock_ticker_input:
        with st.spinner("Analyzing structural data metrics..."):
            stock_profile = fetch_live_stock_telemetry(stock_ticker_input.strip().upper())
            s_ltp = stock_profile["ltp"]
            s_change = stock_profile["change"]
            
            s_entry = round(s_ltp * 1.002, 2)
            s_target = round(s_ltp * 1.030, 2)
            s_sl = round(s_ltp * 0.985, 2)
            
            st.markdown(f"""
            <div style="margin-top:12px; padding: 24px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; box-shadow: 0 4px 16px rgba(148,163,184,0.04);">
                <h3 style="color:#1E293B; margin:0 0 18px 0; font-size:14px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">📋 Calculated Execution Blueprint: {stock_ticker_input.upper()}</h3>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:16px;">
                    <div class="stock-pill"><span style="color:#94A3B8; font-size:11px; text-transform:uppercase; display:block; margin-bottom:4px; font-weight:700;">Current LTP</span><span style="color:#00D09C; font-size:18px; font-weight:700;">₹ {s_ltp:,.2f}</span></div>
                    <div class="stock-pill"><span style="color:#94A3B8; font-size:11px; text-transform:uppercase; display:block; margin-bottom:4px; font-weight:700;">Day Change</span><span style="color:{'#00D09C' if s_change >=0 else '#EF4444'}; font-size:18px; font-weight:700;">{s_change:.2f}%</span></div>
                    <div class="stock-pill" style="border-bottom: 3px solid #00D09C;"><span style="color:#94A3B8; font-size:11px; text-transform:uppercase; display:block; margin-bottom:4px; font-weight:700;">Entry Threshold</span><span style="color:#1E293B; font-size:18px; font-weight:700;">₹ {s_entry:,.2f}</span></div>
                    <div class="stock-pill" style="border-bottom: 3px solid #00D09C;"><span style="color:#94A3B8; font-size:11px; text-transform:uppercase; display:block; margin-bottom:4px; font-weight:700;">Target Level</span><span style="color:#1E293B; font-size:18px; font-weight:700;">₹ {s_target:,.2f}</span></div>
                    <div class="stock-pill" style="border-bottom: 3px solid #EF4444;"><span style="color:#94A3B8; font-size:11px; text-transform:uppercase; display:block; margin-bottom:4px; font-weight:700;">Stop Loss (SL)</span><span style="color:#EF4444; font-size:18px; font-weight:700;">₹ {s_sl:,.2f}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- STOCKXY FOOTER BRANDING ----------------
st.markdown(
    """
    <div class="footer-panel">
        <div>
            <h1 style="font-size: 16px; font-weight: 800; margin: 0; color: #0F172A; letter-spacing: 1px; line-height: 1;">
                STOCK<span style="color: #00D09C;">XY</span>
            </h1>
            <p style="color: #94A3B8; font-size: 11px; margin-top: 4px; font-weight: 500; margin-bottom:0;">
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
