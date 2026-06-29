import streamlit as st
import numpy as np
import joblib
import yfinance as yf
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- THEME & RESPONSIVE UI CSS ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #030712 !important;
        color: #F8FAFC !important;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    section[data-testid="stSidebar"] {
        background-color: #050B18 !important;
        border-right: 1px solid #111C34;
    }

    .content-panel {
        background: #070F21;
        border: 1px solid #111E3B;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    @media (min-width: 768px) {
        .content-panel { padding: 30px; }
    }
    
    .panel-header {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }

    label[data-testid="stWidgetLabel"] p {
        color: #94A3B8 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }

    div[data-testid="stNumberInput"] {
        background-color: #091122 !important;
        border-radius: 8px !important;
    }
    
    /* Segmented Control / Radio Overrides */
    div[data-testid="stRadio"] > label {
        display: none;
    }
    
    div.stButton > button {
        width: 100%;
        height: 52px;
        border-radius: 10px;
        border: none;
        color: white;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 1px;
        background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%);
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25);
        transition: all 0.3s ease;
        margin-top: 10px;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(90deg, #1D4ED8 0%, #6D28D9 100%);
        transform: translateY(-1px);
    }
    
    .responsive-header {
        background: linear-gradient(135deg, #040A18 0%, #06132C 100%); 
        border: 1px solid #111E3B; 
        border-radius: 16px; 
        padding: 30px 20px; 
        margin-bottom: 20px; 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
        gap: 20px;
    }

    @media (min-width: 768px) {
        .responsive-header {
            flex-direction: row;
            align-items: center;
            padding: 40px;
        }
    }

    .result-layout {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 20px;
        padding: 10px 0;
    }
    
    @media (min-width: 576px) {
        .result-layout {
            flex-direction: row;
            text-align: left;
            gap: 35px;
        }
    }
    
    .result-circle-base {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        flex-shrink: 0;
    }

    .result-circle-placeholder { border: 2px dashed #1E293B; color: #475569; }
    .result-circle-bullish { border: 3px solid #10B981; background: rgba(16, 185, 129, 0.05); box-shadow: 0 0 15px rgba(16, 185, 129, 0.2); }
    .result-circle-bearish { border: 3px solid #EF4444; background: rgba(239, 68, 68, 0.05); box-shadow: 0 0 15px rgba(239, 68, 68, 0.2); }

    .sidebar-card {
        background: #070F21;
        border: 1px solid #111E3B;
        border-radius: 12px;
        padding: 16px;
        margin-top: 20px;
    }

    .footer-panel {
        background: linear-gradient(90deg, #050B18 0%, #081226 100%);
        border: 1px solid #111E3B;
        border-radius: 16px;
        padding: 30px 20px;
        margin-top: 40px;
        text-align: center;
    }
    
    @media (min-width: 768px) {
        .footer-panel {
            text-align: left;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 40px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SAFE MODEL RESILIENCY LOADING ----------------
@st.cache_resource
def load_ml_model():
    for path in ["models/nifty_model.pkl", "nifty_model.pkl"]:
        if os.path.exists(path):
            return joblib.load(path)
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
    
    st.markdown("<p style='color:#475569; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Navigation</p>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%); padding: 12px 16px; border-radius: 8px; font-weight: 600; color: white; margin-bottom: 8px; cursor: pointer;">🏠 Home</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 8px; cursor: pointer;">📈 Predict</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 8px; cursor: pointer;">ℹ️ About</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 20px; cursor: pointer;">✉️ Contact</div>
    """, unsafe_allow_html=True)

# ---------------- HERO HEADER WITH MAJNU LOGO ASIDE ----------------
st.markdown(
    """
    <div class="responsive-header">
        <div>
            <h1 style="font-size: clamp(32px, 5vw, 48px); font-weight: 900; margin: 0; letter-spacing: -0.5px; line-height: 1.1;">
                NIFTY <span style="color: #3B82F6;">AI</span> PREDICTOR
            </h1>
            <p style="color: #64748B; font-size: clamp(14px, 2vw, 16px); margin-top: 10px; font-weight: 400; max-width: 600px;">
                AI-Powered Quantitative Prediction Architecture for Next Trading Day Directional Bias.
            </p>
        </div>
        <div style="background: rgba(30, 41, 59, 0.3); border: 1px solid #1E293B; padding: 15px 25px; border-radius: 12px; min-width: 160px; text-align: center;">
            <h3 style="color: #FFFFFF; font-size: 22px; font-weight: 900; margin: 0; letter-spacing: 3px;">
                M<span style="color: #3B82F6;">A</span>JNU
            </h3>
            <span style="color: #3B82F6; font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; display: block; margin-top: 2px;">
                OFFICIAL ENGINE
            </span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------- DATA SOURCE SELECTION ----------------
st.markdown("<p style='color:#94A3B8; font-size:14px; font-weight:500; margin-bottom:8px;'>Data Intake Strategy</p>", unsafe_allow_html=True)
mode = st.radio("Select Input Mode", ["Manual Input", "Live Market Data"], horizontal=True)

# Initializing feature variables
open_price, high_price, low_price, close_price, volume, previous_return = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

# ---------------- YAHOO FINANCE LIVE FEED FETCHING ----------------
if mode == "Live Market Data":
    try:
        nifty = yf.Ticker("^NSEI")
        # Fetch data to safely calculate the latest records
        df = nifty.history(period="5d")
        
        if len(df) >= 2:
            latest_row = df.iloc[-1]
            prior_close = df.iloc[-2]['Close']
            
            open_price = float(latest_row['Open'])
            high_price = float(latest_row['High'])
            low_price = float(latest_row['Low'])
            close_price = float(latest_row['Close'])
            volume = float(latest_row['Volume'])
            previous_return = ((close_price - prior_close) / prior_close) * 100
        else:
            st.warning("Insufficient sequential ticker iterations returned from backend APIs.")
    except Exception as e:
        st.error(f"Failed to resolve quantitative data stream: {e}")

# ---------------- METRICS HUD STATUS DISPLAY ----------------
m1, m2, m3, m4 = st.columns([1, 1, 1, 1])
metric_css = """
<style>
    div[data-testid="stMetric"] { background: #091225 !important; border: 1px solid #142342 !important; border-radius: 12px !important; padding: 12px 16px !important; }
    div[data-testid="stMetricLabel"] p { color: #64748B !important; font-size: 12px !important; text-transform: uppercase; }
    div[data-testid="stMetricValue"] div { color: #FFFFFF !important; font-size: 16px !important; font-weight: 600 !important; }
</style>
"""
st.markdown(metric_css, unsafe_allow_html=True)

m1.metric(label="📅 Target Index", value="NIFTY 50")
m2.metric(label="🕒 Feed Source", value="Yahoo Finance" if mode == "Live Market Data" else "Manual Matrix")
m3.metric(label="📊 Pipeline Status", value="Synchronized" if mode == "Live Market Data" else "Awaiting Input")
m4.metric(label="⚡ Engine Core", value="ML Inference Ready" if model else "Simulated Mode")

st.write("")

# ---------------- MAIN PANEL INPUT CONTROLS ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">📊 Dynamic Matrix Tuning</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="medium")

with c1:
    open_price = st.number_input("Open Price (₹)", format="%.2f", value=open_price, disabled=(mode == "Live Market Data"))
    low_price = st.number_input("Low Price (₹)", format="%.2f", value=low_price, disabled=(mode == "Live Market Data"))
    volume = st.number_input("Trading Volume", format="%.2f", value=volume, disabled=(mode == "Live Market Data"))

with c2:
    high_price = st.number_input("High Price (₹)", format="%.2f", value=high_price, disabled=(mode == "Live Market Data"))
    close_price = st.number_input("Close Price (₹)", format="%.2f", value=close_price, disabled=(mode == "Live Market Data"))
    previous_return = st.number_input("Previous Session Return (%)", format="%.2f", value=previous_return, disabled=(mode == "Live Market Data"))

predict_clicked = st.button("🚀 EXECUTE PREDICTION MATRIX")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INFERENCE CALCULATION BLOCK ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">🎯 Inference Pipeline Output</div>', unsafe_allow_html=True)

if predict_clicked:
    # EXACT layout of 6 features to perfectly match your current nifty_model.pkl
    data_array = np.array([[open_price, high_price, low_price, close_price, volume, previous_return]])
    
    if model is not None:
        prediction = model.predict(data_array)[0]
        probability = model.predict_proba(data_array)[0]
    else:
        # Graceful validation mock fallback configuration if model file isn't found
        prediction = 1 if close_price >= open_price else 0
        probability = [0.18, 0.82] if prediction == 1 else [0.82, 0.18]
        
    if prediction == 1:
        confidence = probability[1] * 100
        st.markdown(
            f"""
            <div class="result-layout">
                <div class="result-circle-base result-circle-bullish">🐂</div>
                <div>
                    <h2 style="color: #10B981; margin: 0; font-size: clamp(20px, 4vw, 28px); font-weight: 700;">PROJECTION VECTOR: BULLISH (UP)</h2>
                    <p style="color: #64748B; margin: 4px 0 12px 0; font-size: 14px;">Inference models capture structural support trends shifting upward.</p>
                    <span style="color: #F8FAFC; font-weight: 500; font-size: 15px;">Confidence Threshold: <b style="color:#10B981;">{confidence:.2f}%</b></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        confidence = probability[0] * 100
        st.markdown(
            f"""
            <div class="result-layout">
                <div class="result-circle-base result-circle-bearish">🐻</div>
                <div>
                    <h2 style="color: #EF4444; margin: 0; font-size: clamp(20px, 4vw, 28px); font-weight: 700;">PROJECTION VECTOR: BEARISH (DOWN)</h2>
                    <p style="color: #64748B; margin: 4px 0 12px 0; font-size: 14px;">Inference models capture overhead resistance distributions building momentum.</p>
                    <span style="color: #F8FAFC; font-weight: 500; font-size: 15px;">Confidence Threshold: <b style="color:#EF4444;">{confidence:.2f}%</b></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.progress(confidence / 100)
else:
    st.markdown(
        """
        <div class="result-layout">
            <div class="result-circle-base result-circle-placeholder">---</div>
            <div>
                <h2 style="color: #475569; margin: 0; font-size: 24px; font-weight: 700;">--</h2>
                <p style="color: #64748B; margin: 2px 0 8px 0; font-size: 13px;">Awaiting prediction runtime trigger initialization.</p>
                <span style="color: #475569; font-weight: 500; font-size: 14px;">Confidence Threshold: --%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.progress(0.0)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BRAND FOOTER BANNER ----------------
st.markdown(
    """
    <div class="footer-panel">
        <div>
            <p style="color: #475569; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin: 0 0 5px 0;">
                Designed By
            </p>
            <h1 style="
                font-size: clamp(40px, 6vw, 56px);
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
            <span style="color: #64748B; cursor: pointer;">💻 GitHub</span>
            <span style="color: #64748B; cursor: pointer;">🌐 LinkedIn</span>
            <span style="color: #64748B; cursor: pointer;">🐦 Twitter</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
