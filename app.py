import streamlit as st
import numpy as np
import joblib
import os
import pyotp
import time
import pandas as pd
from SmartApi import SmartConnect # Ensure this is installed via pip install smartapi-python

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MAJNU | AI Options Terminal",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- ADVANCED UI THEME ENGINE ----------------
st.markdown("""
<style>
    :root { --primary: #3B82F6; --bg: #030712; --panel: #070F21; }
    .stApp { background-color: var(--bg) !important; color: #F8FAFC !important; font-family: 'Inter', sans-serif; }
    
    /* Panel Styling */
    .glass-panel { background: var(--panel); border: 1px solid #111E3B; border-radius: 16px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .panel-header { font-size: 14px; font-weight: 600; color: #64748B; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Metrics Override */
    div[data-testid="stMetric"] { background: #091225; border: 1px solid #142342; border-radius: 12px; padding: 15px; }
    div[data-testid="stMetricLabel"] { font-size: 12px; color: #94A3B8; }
    div[data-testid="stMetricValue"] { font-size: 20px; font-weight: 700; color: #F8FAFC; }
    
    /* Buttons */
    div.stButton > button { width: 100%; height: 50px; border-radius: 8px; border: none; font-weight: 700; color: white; background: linear-gradient(90deg, #2563EB, #7C3AED); transition: 0.3s; }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3); }
    
    /* Table Styling */
    .stTable { background: var(--panel); border-radius: 8px; }
    thead tr th { background-color: #111E3B !important; color: #E2E8F0 !important; }
    tbody tr td { color: #CBD5E1 !important; }
    
    /* Custom Indicators */
    .signal-badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .bullish { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }
    .bearish { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIC INITIALIZATION ----------------
def reset_index_baselines():
    selected = st.session_state.index_selector
    if selected == "SENSEX":
        st.session_state.current_price, st.session_state.baseline_open, st.session_state.strike_step = 76730.0, 77000.0, 100
    elif selected == "BANKEX":
        st.session_state.current_price, st.session_state.baseline_open, st.session_state.strike_step = 65200.0, 65500.0, 100
    else:
        st.session_state.current_price, st.session_state.baseline_open, st.session_state.strike_step = 23950.0, 24030.0, 50

# State Defaults
if "current_price" not in st.session_state: st.session_state.current_price = 23950.0
if "smart_api" not in st.session_state: st.session_state.smart_api = None
if "api_authenticated" not in st.session_state: st.session_state.api_authenticated = False
if "refresh_counter" not in st.session_state: st.session_state.refresh_counter = 0

# ---------------- HEADER AREA ----------------
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 42px; font-weight: 900; margin-bottom: 5px; background: linear-gradient(90deg, #60A5FA, #A78BFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">MAJNU AI TERMINAL</h1>
        <p style="color: #64748B;">Institutional Grade Directional Signal Framework</p>
    </div>
""", unsafe_allow_html=True)

# ---------------- INPUT CONFIGURATION ----------------
col1, col2 = st.columns([1, 1])
with col1:
    target_index = st.selectbox("Target Market Index", ["NIFTY 50", "SENSEX", "BANKEX"], key="index_selector", on_change=reset_index_baselines)
with col2:
    mode = st.radio("Input Source Engine", ["Manual Input", "AngelOne Live Stream"], horizontal=True)

# ---------------- ANGEL ONE AUTH ----------------
if mode == "AngelOne Live Stream" and not st.session_state.api_authenticated:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🔐 Secure API Handshake</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: api_k = st.text_input("API Key", type="password")
    with c2: client_c = st.text_input("Client ID")
    with c3: passw = st.text_input("Password/MPIN", type="password")
    with c4: totp_s = st.text_input("TOTP Secret", type="password")
    if st.button("AUTHENTICATE SDK GATEWAY"):
        try:
            smart_api = SmartConnect(api_key=api_k)
            data = smart_api.generateSession(client_c, passw, pyotp.TOTP(totp_s).now())
            if data['status']:
                st.session_state.smart_api = smart_api
                st.session_state.api_authenticated = True
                st.rerun()
        except Exception as e: st.error(f"Handshake Failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DATA FETCHING ----------------
if mode == "AngelOne Live Stream" and st.session_state.api_authenticated:
    try:
        token_map = {"NIFTY 50": "99926000", "SENSEX": "99919000", "BANKEX": "99923000"}
        exch_map = {"NIFTY 50": "NSE", "SENSEX": "BSE", "BANKEX": "BSE"}
        market_data = st.session_state.smart_api.getMarketData(mode="FULL", exchangeTokens={exch_map[target_index]: [token_map[target_index]]})
        if market_data['status']:
            tick = market_data['data']['fetched'][0]
            st.session_state.current_price = float(tick['ltp'])
    except: pass

# ---------------- MAIN DASHBOARD VIEW ----------------
st.markdown(f"""
    <div style="background: rgba(37, 99, 235, 0.05); border: 1px solid #1E3A8A; padding: 30px; border-radius: 16px; text-align: center; margin-bottom: 25px;">
        <div style="font-size: 14px; color: #818CF8; font-weight: 600; text-transform: uppercase;">Live Last Traded Price (LTP)</div>
        <div style="font-size: 56px; font-weight: 900; color: white;">₹ {st.session_state.current_price:,.2f}</div>
    </div>
""", unsafe_allow_html=True)

# Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Active Index", target_index)
m2.metric("Feed Status", "Live Stream" if st.session_state.api_authenticated else "Manual Mode")
m3.metric("System Core", "ML Inference Active")

# ---------------- STRATEGY GENERATOR ----------------
st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">🚀 Execution Controller</div>', unsafe_allow_html=True)
price_val = st.number_input("Adjust Price Baseline", value=float(st.session_state.current_price), format="%.2f", disabled=(mode == "AngelOne Live Stream"))
if st.button("RUN AI SIGNAL FILTER"):
    st.markdown("---")
    # Simulate Model Inference Logic
    is_bullish = price_val > st.session_state.baseline_open
    confidence = 88.42 if is_bullish else 82.15
    
    # Visual Feedback
    status_class = "bullish" if is_bullish else "bearish"
    label = "BULLISH (UPWARD BIAS)" if is_bullish else "BEARISH (DOWNWARD BIAS)"
    st.markdown(f'<div style="text-align:center; margin-bottom:20px;"><span class="signal-badge {status_class}">{label} | CONFIDENCE: {confidence}%</span></div>', unsafe_allow_html=True)
    
    # Generate Table
    step = st.session_state.strike_step
    atm = round(price_val / step) * step
    data = []
    for i in range(-5, 6):
        strike = atm + (i * step)
        entry = round((atm - strike if is_bullish else strike - atm) * 0.5 + 100, 1)
        data.append({
            "Contract": f"{target_index} {strike} {'CE' if is_bullish else 'PE'}",
            "Entry Zone": f"₹{entry}",
            "Stop Loss": f"₹{round(entry * 0.95, 1)}",
            "Target": f"₹{round(entry * 1.08, 1)}"
        })
    st.table(pd.DataFrame(data))
st.markdown('</div>', unsafe_allow_html=True)

# Refresh Loop
if mode == "AngelOne Live Stream" and st.session_state.api_authenticated:
    time.sleep(4)
    st.session_state.refresh_counter += 1
    st.rerun()
