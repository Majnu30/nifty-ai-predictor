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

# ---------------- BRAND THEME & RESPONSIVE CSS TERMINAL ----------------
st.markdown("""
<style>
    .stApp { background-color: #F3F4F6 !important; color: #1F2937 !important; }
    .block-container { padding-top: 0rem; padding-bottom: 5rem; max-width: 600px; margin: 0 auto; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    /* Top Purple App Header from 18513.jpg */
    .app-header {
        background-color: #5B21B6;
        color: white;
        padding: 20px 16px;
        margin: 0 -16px 15px -16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .app-title { font-size: 22px; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 8px; }
    
    /* Segmented Navigation Tab Controls */
    .tab-container {
        display: flex;
        background: white;
        margin: 0 -16px 15px -16px;
        border-bottom: 1px solid #E5E7EB;
    }
    .nav-tab {
        flex: 1;
        text-align: center;
        padding: 14px 0;
        font-size: 15px;
        font-weight: 600;
        color: #9CA3AF;
        cursor: pointer;
    }
    .nav-tab.active {
        color: #5B21B6;
        border-bottom: 3px solid #5B21B6;
    }

    /* Functional Configuration Wrapper Panel */
    .quant-panel { 
        background: white; 
        border: 1px solid #E5E7EB; 
        border-radius: 16px; 
        padding: 20px; 
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    label[data-testid="stWidgetLabel"] p { color: #4B5563 !important; font-weight: 600 !important; font-size: 13px !important; }
    div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div { background-color: #F9FAFB !important; color: #1F2937 !important; border: 1px solid #D1D5DB !important; }
    div[data-testid="stRadio"] > label { display: none; }

    /* Tactical Action Buttons */
    div.stButton > button { width: 100%; height: 50px; border-radius: 12px; border: none; color: white; font-size: 15px; font-weight: 700; background: #5B21B6; transition: all 0.2s; }
    div.stButton > button:hover { background: #4C1D95; transform: translateY(-1px); }

    /* Premium Dynamic Call Option Card Layout (Mirroring 18513.jpg) */
    .trade-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .card-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #F3F4F6;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }
    .analyst-profile { display: flex; align-items: center; gap: 8px; }
    .analyst-avatar { width: 32px; height: 32px; background: #E0E7FF; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #4F46E5; font-size: 14px; }
    .analyst-name { font-size: 14px; font-weight: 600; color: #374151; }
    .trade-timestamp { font-size: 12px; color: #6B7280; }
    
    .asset-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }
    .asset-badge-group { display: flex; align-items: center; gap: 10px; }
    .asset-icon { width: 36px; height: 36px; background: #FF5722; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 11px; }
    .asset-ticker { font-size: 16px; font-weight: 700; color: #111827; margin: 0; }
    .asset-contract { font-size: 12px; color: #6B7280; margin: 2px 0 0 0; }
    .action-badge { font-size: 13px; font-weight: 700; color: #10B981; text-transform: uppercase; }

    /* Timeline Tracking Indicator Slider Layout */
    .timeline-wrapper { margin: 24px 0 20px 0; position: relative; }
    .timeline-bar { height: 4px; background: #E5E7EB; border-radius: 2px; position: relative; }
    .timeline-progress { height: 4px; background: #10B981; position: absolute; left: 33%; width: 25%; }
    .timeline-node { width: 10px; height: 10px; background: #D1D5DB; border-radius: 50%; position: absolute; top: -3px; }
    .node-sl { left: 0%; }
    .node-entry { left: 33%; }
    .node-current { left: 58%; background: #111827; width: 12px; height: 12px; top: -4px; }
    .node-target { right: 0%; background: #D1D5DB; }
    
    .floating-price-label {
        position: absolute;
        top: -32px;
        left: 58%;
        transform: translateX(-50%);
        background: white;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        padding: 2px 6px;
        font-size: 11px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .floating-price-label::after {
        content: ''; position: absolute; bottom: -4px; left: 50%; transform: translateX(-50%) rotate(45deg);
        width: 6px; height: 6px; background: white; border-right: 1px solid #D1D5DB; border-bottom: 1px solid #D1D5DB;
    }

    .level-labels { display: flex; justify-content: space-between; margin-top: 8px; }
    .level-block { display: flex; flex-direction: column; font-size: 12px; }
    .level-block.center { text-align: center; }
    .level-block.right { text-align: right; }
    .level-title { color: #9CA3AF; font-weight: 500; }
    .level-value { color: #374151; font-weight: 600; margin-top: 2px; }

    /* Potential Upside Dynamic Strip Card Block */
    .upside-strip {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 12px;
        padding: 12px 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 14px;
    }
    .upside-text-value { color: #065F46; font-size: 15px; font-weight: 700; margin: 0; }
    .upside-text-label { color: #047857; font-size: 12px; font-weight: 600; margin: 2px 0 0 0; }
    .order-action-button { background: #EEF2F6; color: #4338CA; font-weight: 700; font-size: 13px; padding: 8px 14px; border-radius: 8px; display: flex; align-items: center; gap: 4px; cursor: pointer; border: 1px solid #E2E8F0; }

    /* Social Card Interaction Footer */
    .card-social-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid #F3F4F6;
        color: #9CA3AF;
        font-size: 13px;
    }
    .social-left-group { display: flex; gap: 16px; }
    .social-icon-item { display: flex; align-items: center; gap: 5px; cursor: pointer; }
    .social-icon-item:hover { color: #4B5563; }
</style>
""", unsafe_allow_html=True)

# ---------------- APPLICATION HEADER TOPBAR (FROM 18513.jpg) ----------------
st.markdown(
    """
    <div class="app-header">
        <div class="app-title">Trades <span style="font-size:15px; opacity:0.7;">ⓘ</span></div>
        <div style="display:flex; gap:18px; font-size:18px; opacity:0.9;">
            <span>🔍</span><span>📋</span><span>🔔</span>
            <span style="background:#4C1D95; border-radius:50%; width:24px; height:24px; display:inline-block; text-align:center; font-size:12px; line-height:24px; font-weight:bold;">M</span>
        </div>
    </div>
    <div class="tab-container">
        <div class="nav-tab">Stock Trades</div>
        <div class="nav-tab active">Option Trades</div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------- CONTROL ARCHITECTURE CONFIG PANE ----------------
st.markdown('<div class="quant-panel">', unsafe_allow_html=True)
st.markdown("<p style='color:#374151; font-size:14px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px;'>Quant Configuration Controls</p>", unsafe_allow_html=True)

c_sel1, c_sel2 = st.columns([1, 1])
with c_sel1:
    target_index = st.selectbox("Market Target Index", ["NIFTY 50", "SENSEX", "BANKEX"], key="index_selector", on_change=reset_index_baselines)
with c_sel2:
    mode = st.radio("Input Source Profile", ["Manual Input", "SmartAPI Feed"], horizontal=True)

if mode == "Manual Input" and st.session_state.api_authenticated:
    st.session_state.api_authenticated = False
    st.session_state.smart_api = None

# ---------------- SECURE NATIVE ANGELONE GATEWAY ----------------
if mode == "SmartAPI Feed":
    if not st.session_state.api_authenticated:
        st.markdown("<p style='font-size:13px; font-weight:600; margin-top:10px;'>🔐 Access Terminal Token Link</p>", unsafe_allow_html=True)
        ak_col, cc_col = st.columns(2)
        pw_col, to_col = st.columns(2)
        with ak_col: API_KEY = st.text_input("SmartAPI Key", type="password", key="api_key_w")
        with cc_col: CLIENT_CODE = st.text_input("Client ID", key="client_code_w")
        with pw_col: PASSWORD = st.text_input("Mpin", type="password", key="password_w")
        with to_col: TOTP_SECRET = st.text_input("TOTP String", type="password", key="totp_w")
        connect_btn = st.button("🚀 SYNC GATEWAY INTERFACE")

        if connect_btn and API_KEY and CLIENT_CODE and PASSWORD and TOTP_SECRET:
            try:
                totp_challenge = pyotp.TOTP(TOTP_SECRET).now()
                smart_api = SmartConnect(api_key=API_KEY)
                session_data = smart_api.generateSession(CLIENT_CODE, PASSWORD, totp_challenge)
                if session_data.get('status') == True:
                    st.session_state.smart_api = smart_api
                    st.session_state.api_authenticated = True
                    st.rerun()
            except Exception as e: st.error(f"Link Connection Fault: {e}")
                
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

live_price_input = st.number_input(f"Target Value Spot Tracking Base ({target_index})", format="%.2f", value=current_price_display, disabled=(mode == "SmartAPI Feed"), key="live_price_w")
predict_clicked = st.button("⚡ PARSE EXPERT INTRA-DAY TRADE CALLS")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- HIGH-FIDELITY TRADE CALL MATRIX (FROM 18513.jpg) ----------------
if predict_clicked or (mode == "SmartAPI Feed" and st.session_state.get('api_authenticated')):
    step = strike_step_display
    atm_strike = round(live_price_input / step) * step
    
    # Static parameters matching the structure displayed in 18513.jpg
    timestamp_str = time.strftime("%d %b • %I:%M %p")
    
    # 3 Strategy instances mimicking diverse quantitative analyst signals
    analysts = [
        {"name": "Sarathi Research", "avatar": "SR", "likes": "59", "comments": "30", "offset": 1},
        {"name": "Vineet Chawla", "avatar": "VC", "likes": "142", "comments": "12", "offset": 0},
        {"name": "Majnu Quant Core", "avatar": "MJ", "likes": "388", "comments": "94", "offset": -1}
    ]
    
    for analyst in analysts:
        c_strike = atm_strike + (analyst["offset"] * step)
        
        # Exact premium arithmetic matching trade risk tracking models
        c_entry = max(5.0, round(9.50 + (analyst["offset"] * 12.0), 2))
        c_sl = max(0.05, round(c_entry - 9.45, 2))
        c_tgt = round(c_entry + 17.50, 2)
        c_current_ltp = max(0.10, round(c_entry - 7.80, 2))
        
        # Position sizing rules per lot allocation calculations
        upside_points = max(0.0, c_tgt - c_current_ltp)
        potential_upside_rupees = upside_points * lot_size_display
        percentage_upside = (upside_points / c_current_ltp) * 100
        
        # Clean asset identifier definition string formatting
        asset_label = "NIFTY" if target_index == "NIFTY 50" else ("SENSEX" if target_index == "SENSEX" else "BANKEX")
        contract_ticker = f"30 JUN · {c_strike} · CE"

        # Structural high fidelity card rendering injection block
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
                    <div style="font-size:16px; color:#9CA3AF; cursor:pointer;">🔔</div>
                </div>
                
                <div class="asset-row">
                    <div class="asset-badge-group">
                        <div class="asset-icon">{asset_label[:3]}</div>
                        <div>
                            <div class="asset-ticker">{asset_label}</div>
                            <div class="asset-contract">{contract_ticker}</div>
                        </div>
                    </div>
                    <div class="action-badge">BUY CALL <span style="color:#D1D5DB; font-weight:normal;">|</span> Intraday</div>
                </div>

                <!-- Custom Slider / Timeline Level Plotting Component -->
                <div class="timeline-wrapper">
                    <div class="floating-price-label">
                        <span style="color:#9CA3AF; display:block; font-size:9px; font-weight:500; text-transform:uppercase; line-height:1;">Current Price</span>
                        {c_current_ltp:.2f}
                    </div>
                    <div class="timeline-bar">
                        <div class="timeline-progress"></div>
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

                <!-- Potential Upside Strip Block -->
                <div class="upside-strip">
                    <div>
                        <h4 class="upside-text-value">₹{potential_upside_rupees:,.0f} ({percentage_upside:.2f}%)</h4>
                        <p class="upside-text-label">Potential Upside per lot</p>
                    </div>
                    <div class="order-action-button">
                        Place Order <span style="font-size:11px; margin-left:2px;">➔</span>
                    </div>
                </div>

                <!-- Social Footer Interactivity -->
                <div class="card-social-footer">
                    <div class="social-left-group">
                        <div class="social-icon-item">🤍 {analyst["likes"]}</div>
                        <div class="social-icon-item">💬 {analyst["comments"]}</div>
                        <div class="social-icon-item">📄</div>
                    </div>
                    <div style="display:flex; gap:16px;">
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
        <div class="quant-panel" style="text-align:center; padding:40px 20px; color:#9CA3AF;">
            <span style="font-size:28px; display:block; margin-bottom:8px;">📊</span>
            <span style="font-weight:600; font-size:14px; text-transform:uppercase; letter-spacing:0.5px; display:block; color:#6B7280;">Filtered Signals Offline</span>
            <p style="font-size:12px; margin-top:4px; max-width:280px; margin-left:auto; margin-right:auto;">Trigger the directional scanner above to generate professional execution cards and custom order targets.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ---------------- APPLICATION PERSISTENT BOTTOM NAVIGATION BAR ----------------
st.markdown(
    """
    <div style="
        position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
        width: 100%; max-width: 600px; background: white;
        border-top: 1px solid #E5E7EB; padding: 8px 0;
        display: flex; justify-content: space-around; align-items: center;
        z-index: 9999; box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    ">
        <div style="text-align:center; font-size:11px; color:#9CA3AF; font-weight:500; cursor:pointer;">
            <span style="font-size:18px; display:block;">🏠</span>Home
        </div>
        <div style="text-align:center; font-size:11px; color:#9CA3AF; font-weight:500; cursor:pointer;">
            <span style="font-size:18px; display:block;">📊</span>Market
        </div>
        <div style="text-align:center; font-size:11px; color:#5B21B6; font-weight:700; cursor:pointer;">
            <span style="font-size:18px; display:block;">🎯</span>Trades
        </div>
        <div style="text-align:center; font-size:11px; color:#9CA3AF; font-weight:500; cursor:pointer;">
            <span style="font-size:18px; display:block;">💼</span>Trackers
        </div>
        <div style="text-align:center; font-size:11px; color:#9CA3AF; font-weight:500; cursor:pointer;">
            <span style="font-size:18px; display:block;">👥</span>Social
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------- SYNC LIVE TICKERS LOOP RE-RUNNER ----------------
if mode == "SmartAPI Feed" and st.session_state.get('api_authenticated'):
    time.sleep(4)
    st.session_state.refresh_counter += 1
    st.rerun()
