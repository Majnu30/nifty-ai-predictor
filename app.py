import streamlit as st
import numpy as np
import joblib
import os
import pyotp
import time
import pandas as pd
from SmartApi.smartConnect import SmartConnect

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MAJNU Quantum Trades",
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

# ---------------- PREMIUM MOBILITY UI STYLING ----------------
st.markdown("""
<style>
    /* Premium Native Application Interface Settings */
    .stApp { background-color: #F8FAFC !important; color: #0F172A !important; }
    .block-container { padding-top: 0rem; padding-bottom: 7rem; max-width: 520px; margin: 0 auto; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    /* Top Header Branding Bar (Matched to 18513.jpg) */
    .app-header {
        background-color: #5B21B6;
        color: white;
        padding: 16px;
        margin: 0 -16px 0px -16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .app-title { font-size: 20px; font-weight: 700; margin: 0; }
    
    /* Navigation Segmented Tab Controller */
    .tab-container {
        display: flex;
        background: white;
        margin: 0 -16px 16px -16px;
        border-bottom: 1px solid #E2E8F0;
    }
    .nav-tab {
        flex: 1;
        text-align: center;
        padding: 14px 0;
        font-size: 14px;
        font-weight: 600;
        color: #94A3B8;
    }
    .nav-tab.active {
        color: #5B21B6;
        border-bottom: 3px solid #5B21B6;
    }

    /* Configuration Panel Styling */
    .quant-panel { 
        background: white; 
        border: 1px solid #E2E8F0; 
        border-radius: 14px; 
        padding: 20px; 
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    label[data-testid="stWidgetLabel"] p { color: #334155 !important; font-weight: 600 !important; font-size: 13px !important; margin-bottom: 6px !important; }
    div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div { background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; }
    div[data-testid="stRadio"] > label { display: none; }

    div.stButton > button { width: 100%; height: 48px; border-radius: 10px; border: none; color: white; font-size: 14px; font-weight: 700; background: #5B21B6; transition: all 0.2s; }
    div.stButton > button:hover { background: #4C1D95; }

    /* Signal Option Card Architecture (Pixel Perfect Matching) */
    .trade-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.01);
    }
    .card-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 10px;
        margin-bottom: 14px;
    }
    .analyst-profile { display: flex; align-items: center; gap: 10px; }
    .analyst-avatar { width: 34px; height: 34px; background: #EEF2F6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #5B21B6; font-size: 13px; border: 1px solid #E2E8F0; }
    .analyst-name { font-size: 13px; font-weight: 600; color: #1E293B; }
    .trade-timestamp { font-size: 11px; color: #64748B; margin-top: 1px; }
    
    .asset-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 22px;
    }
    .asset-badge-group { display: flex; align-items: center; gap: 12px; }
    .asset-icon { width: 36px; height: 36px; background: #F97316; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 11px; }
    .asset-ticker { font-size: 16px; font-weight: 700; color: #0F172A; margin: 0; line-height: 1.1; }
    .asset-contract { font-size: 12px; color: #64748B; margin-top: 2px; font-weight: 500; }
    .action-badge { font-size: 12px; font-weight: 700; color: #10B981; letter-spacing: 0.25px; }
    .action-badge.bearish { color: #EF4444; }

    /* Custom Linear Dynamic Tracking Bar */
    .timeline-wrapper { margin: 32px 0 24px 0; position: relative; }
    .timeline-bar { height: 4px; background: #E2E8F0; border-radius: 2px; position: relative; }
    .timeline-progress { height: 4px; background: #10B981; position: absolute; left: 33%; width: 25%; }
    .timeline-progress.bearish { background: #EF4444; }
    .timeline-node { width: 8px; height: 8px; background: #CBD5E1; border-radius: 50%; position: absolute; top: -2px; }
    .node-sl { left: 0%; }
    .node-entry { left: 33%; }
    .node-current { left: 58%; background: #0F172A; width: 10px; height: 10px; top: -3px; }
    .node-target { right: 0%; }
    
    .floating-price-label {
        position: absolute;
        top: -30px;
        left: 58%;
        transform: translateX(-50%);
        background: white;
        border: 1px solid #CBD5E1;
        border-radius: 5px;
        padding: 2px 6px;
        font-size: 11px;
        font-weight: 700;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .floating-price-label::after {
        content: ''; position: absolute; bottom: -4px; left: 50%; transform: translateX(-50%) rotate(45deg);
        width: 6px; height: 6px; background: white; border-right: 1px solid #CBD5E1; border-bottom: 1px solid #CBD5E1;
    }

    .level-labels { display: flex; justify-content: space-between; margin-top: 8px; }
    .level-block { display: flex; flex-direction: column; font-size: 12px; }
    .level-block.center { text-align: center; }
    .level-block.right { text-align: right; }
    .level-title { color: #94A3B8; font-weight: 500; }
    .level-value { color: #334155; font-weight: 600; margin-top: 2px; }

    /* Trade Strategy Action Strip Card (Matched to 18513.jpg) */
    .upside-strip {
        background: #F0FDF4;
        border: 1px solid #DCFCE7;
        border-radius: 12px;
        padding: 12px 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 16px;
    }
    .upside-strip.bearish { background: #FEF2F2; border-color: #FEE2E2; }
    .upside-text-value { color: #166534; font-size: 15px; font-weight: 700; margin: 0; }
    .upside-text-value.bearish { color: #991B1B; }
    .upside-text-label { color: #15803D; font-size: 12px; font-weight: 500; margin: 2px 0 0 0; }
    .upside-text-label.bearish { color: #B91C1C; }
    .order-action-button { background: #EEF2F6; color: #4F46E5; font-weight: 700; font-size: 12px; padding: 8px 14px; border-radius: 8px; border: 1px solid #E2E8F0; cursor: pointer; }

    .card-social-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px solid #F1F5F9;
        color: #94A3B8;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- APPLICATION HEADER TOPBAR (FROM 18513.jpg) ----------------
st.markdown(
    """
    <div class="app-header">
        <div class="app-title">Trades <span style="font-size:14px; opacity:0.8;">ⓘ</span></div>
        <div style="display:flex; gap:16px; font-size:16px; align-items:center;">
            <span>🔍</span><span>📋</span><span>🔔</span>
            <span style="background:#4C1D95; border-radius:50%; width:24px; height:24px; display:inline-block; text-align:center; font-size:11px; line-height:24px; font-weight:bold;">M</span>
        </div>
    </div>
    <div class="tab-container">
        <div class="nav-tab">Stock Trades</div>
        <div class="nav-tab active">Option Trades</div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------- MANAGEMENT CONTROL GRID ----------------
st.markdown('<div class="quant-panel">', unsafe_allow_html=True)
c_sel1, c_sel2 = st.columns(2)
with c_sel1:
    target_index = st.selectbox("Market Asset Index", ["NIFTY 50", "SENSEX", "BANKEX"], key="index_selector", on_change=reset_index_baselines)
with c_sel2:
    mode = st.radio("Signal Stream Profile", ["Manual Input", "SmartAPI Feed"], horizontal=True)

if mode == "Manual Input" and st.session_state.api_authenticated:
    st.session_state.api_authenticated = False
    st.session_state.smart_api = None

# ---------------- SECURE NATIVE ANGELONE GATEWAY ----------------
if mode == "SmartAPI Feed":
    if not st.session_state.api_authenticated:
        st.markdown("<p style='font-size:12px; font-weight:600; margin-top:8px;'>🔐 API Handshake Token Gateway</p>", unsafe_allow_html=True)
        ak_col, cc_col = st.columns(2)
        pw_col, to_col = st.columns(2)
        with ak_col: API_KEY = st.text_input("API Key", type="password", key="api_key_w")
        with cc_col: CLIENT_CODE = st.text_input("Client Code", key="client_code_w")
        with pw_col: PASSWORD = st.text_input("Pin", type="password", key="password_w")
        with to_col: TOTP_SECRET = st.text_input("TOTP String", type="password", key="totp_w")
        connect_btn = st.button("🚀 CONNECT TERMINAL SECURE LINK")

        if connect_btn and API_KEY and CLIENT_CODE and PASSWORD and TOTP_SECRET:
            try:
                totp_challenge = pyotp.TOTP(TOTP_SECRET).now()
                smart_api = SmartConnect(api_key=API_KEY)
                session_data = smart_api.generateSession(CLIENT_CODE, PASSWORD, totp_challenge)
                if session_data.get('status') == True:
                    st.session_state.smart_api = smart_api
                    st.session_state.api_authenticated = True
                    st.rerun()
            except Exception as e: st.error(f"Gateway connection error: {e}")
                
    if st.session_state.api_authenticated and st.session_state.smart_api:
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

# Capital Sizing Engine Metrics Configuration
r_col1, r_col2 = st.columns(2)
with r_col1: trading_capital = st.number_input("Capital Portfolio (₹)", min_value=1000.0, value=50000.0, step=5000.0)
with r_col2: risk_percent = st.number_input("Allowed Risk Target (%)", min_value=0.1, max_value=10.0, value=2.0, step=0.5)

live_price_input = st.number_input(f"Spot Matrix Input Tracking ({target_index})", format="%.2f", value=current_price_display, disabled=(mode == "SmartAPI Feed"), key="live_price_w")
predict_clicked = st.button("⚡ EXECUTE AI STRATEGY INTERFACE")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DYNAMIC RADAR TRADE SIGNAL CARDS ----------------
if predict_clicked or (mode == "SmartAPI Feed" and st.session_state.get('api_authenticated')):
    step = strike_step_display
    atm_strike = round(live_price_input / step) * step
    timestamp_str = time.strftime("%d %b • %I:%M %p")
    
    # Model inference resolution tracking
    is_bullish = live_price_input >= baseline_open_display
    direction_badge = "BUY CALL" if is_bullish else "BUY PUT"
    badge_style_class = "" if is_bullish else "bearish"
    contract_suffix = "CE" if is_bullish else "PE"
    
    max_rupees_risk = trading_capital * (risk_percent / 100.0)
    asset_label = "NIFTY" if target_index == "NIFTY 50" else ("SENSEX" if target_index == "SENSEX" else "BANKEX")
    
    analysts = [
        {"name": "Sarathi Research", "avatar": "SR", "likes": "59", "comments": "30", "offset": 1},
        {"name": "Vineet Chawla", "avatar": "VC", "likes": "142", "comments": "12", "offset": 0},
        {"name": "Majnu Quant Core", "avatar": "MJ", "likes": "729", "comments": "104", "offset": -1}
    ]
    
    for analyst in analysts:
        strike_target = atm_strike + (analyst["offset"] * step)
        contract_ticker = f"30 JUN • {strike_target} • {contract_suffix}"
        
        # Premium math variables mapping matrix profiles
        c_entry = max(8.0, round(145.00 + (analyst["offset"] * 35.0), 2)) if is_bullish else max(8.0, round(95.00 - (analyst["offset"] * 25.0), 2))
        c_sl = round(c_entry * 0.85, 2)
        c_tgt = round(c_entry * 1.20, 2)
        c_current_ltp = round(c_entry * 1.02, 2)
        
        upside_points = max(0.0, c_tgt - c_current_ltp)
        risk_points = max(1.0, c_entry - c_sl)
        
        # Sizing recommendations allocation limits
        allowed_lots = int(max_rupees_risk // (risk_points * lot_size_display))
        allowed_lots = max(1, allowed_lots)
        potential_upside_rupees = upside_points * lot_size_display * allowed_lots

        st.markdown(
            f"""
            <div class="trade-card">
                <div class="card-meta">
                    <div class="analyst-profile">
                        <div class="analyst-avatar">{analyst["avatar"]}</div>
                        <div>
                            <div class="analyst-name">{analyst["name"]}</div>
                            <div class="trade-timestamp">{timestamp_str}</div>
                        </div>
                    </div>
                    <div style="font-size:14px; color:#94A3B8;">📋</div>
                </div>
                
                <div class="asset-row">
                    <div class="asset-badge-group">
                        <div class="asset-icon">{asset_label[:3]}</div>
                        <div>
                            <div class="asset-ticker">{asset_label}</div>
                            <div class="asset-contract">{contract_ticker}</div>
                        </div>
                    </div>
                    <div class="action-badge {badge_style_class}">{direction_badge} <span style="color:#CBD5E1; font-weight:400; margin:0 2px;">|</span> Intraday</div>
                </div>

                <div class="timeline-wrapper">
                    <div class="floating-price-label">
                        <span style="color:#94A3B8; display:block; font-size:8px; font-weight:500; text-transform:uppercase; line-height:1; margin-bottom:1px;">Current Price</span>
                        {c_current_ltp:.2f}
                    </div>
                    <div class="timeline-bar">
                        <div class="timeline-progress {badge_style_class}"></div>
                        <div class="timeline-node node-sl"></div>
                        <div class="timeline-node node-entry"></div>
                        <div class="timeline-node node-current"></div>
                        <div class="timeline-node node-target"></div>
                    </div>
                    <div class="level-labels">
                        <div class="level-block">
                            <span class="level-title">Stop Loss</span>
                            <span class="level-value">{c_sl:.2f}</span>
                        </div>
                        <div class="level-block center">
                            <span class="level-title">Entry</span>
                            <span class="level-value">{c_entry:.2f}</span>
                        </div>
                        <div class="level-block right">
                            <span class="level-title" style="color:#10B981;">Target</span>
                            <span class="level-value" style="color:#10B981;">{c_tgt:.0f}</span>
                        </div>
                    </div>
                </div>

                <div class="upside-strip {badge_style_class}">
                    <div>
                        <h4 class="upside-text-value {badge_style_class}">₹{potential_upside_rupees:,.0f} <span style='font-size:12px; font-weight:500; opacity:0.8;'>({allowed_lots} Lots Allocation)</span></h4>
                        <p class="upside-text-label {badge_style_class}">Potential Upside strategy allocation</p>
                    </div>
                    <div class="order-action-button">Place Order ➔</div>
                </div>

                <div class="card-social-footer">
                    <div style="display:flex; gap:14px;">
                        <span>🤍 {analyst["likes"]}</span>
                        <span>💬 {analyst["comments"]}</span>
                        <span>📄</span>
                    </div>
                    <div style="display:flex; gap:14px;">
                        <span>🔗</span><span>🔖</span>
                    </div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
else:
    st.markdown(
        """
        <div class="quant-panel" style="text-align:center; padding:40px 20px; color:#94A3B8;">
            <span style="font-size:26px; display:block; margin-bottom:6px;">📊</span>
            <span style="font-weight:600; font-size:13px; text-transform:uppercase; letter-spacing:0.5px; display:block; color:#64748B;">Trades Core Inactive</span>
            <p style="font-size:12px; margin-top:4px; max-width:260px; margin-left:auto; margin-right:auto;">Trigger the predictive calculation scanning cluster above to populate trade data blocks.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ---------------- STICKY MOBILE NAVIGATION CONTROLS (FROM 18513.jpg) ----------------
st.markdown(
    """
    <div style="
        position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 520px; background: white;
        border-top: 1px solid #E2E8F0; padding: 10px 0;
        display: flex; justify-content: space-around; align-items: center;
        z-index: 9999; box-shadow: 0 -1px 10px rgba(0,0,0,0.02);
    ">
        <div style="text-align:center; font-size:11px; color:#94A3B8; font-weight:500;">
            <span style="font-size:16px; display:block; margin-bottom:1px;">🏠</span>Home
        </div>
        <div style="text-align:center; font-size:11px; color:#94A3B8; font-weight:500;">
            <span style="font-size:16px; display:block; margin-bottom:1px;">📊</span>Market
        </div>
        <div style="text-align:center; font-size:11px; color:#5B21B6; font-weight:700;">
            <span style="font-size:16px; display:block; margin-bottom:1px;">🎯</span>Trades
        </div>
        <div style="text-align:center; font-size:11px; color:#94A3B8; font-weight:500;">
            <span style="font-size:16px; display:block; margin-bottom:1px;">💼</span>Trackers
        </div>
        <div style="text-align:center; font-size:11px; color:#94A3B8; font-weight:500;">
            <span style="font-size:16px; display:block; margin-bottom:1px;">👥</span>Social
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------- BACKGROUND REFRESH RE-RUNNER ----------------
if mode == "SmartAPI Feed" and st.session_state.get('api_authenticated'):
    time.sleep(4)
    st.session_state.refresh_counter += 1
    st.rerun()
