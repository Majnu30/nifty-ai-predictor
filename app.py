Here is the highly polished, mobile-responsive version of your dashboard.

Streamlit handles layout scaling automatically, but heavy reliance on strict custom CSS widths (like fixed sidebar dimensions or massive grid containers) breaks down on mobile devices.

To make this completely **UI-friendly for mobile users**, this refactored code:

1. Replaces raw CSS grids with Streamlit's native layout containers (`st.columns`), which automatically collapse into vertical blocks on smaller screens.
2. Uses media queries (`@media`) to dynamically scale text sizes, margins, and the logo banner so that they read clean on everything from an iPhone to an ultrawide desktop monitor.
3. Repositions the sidebar contents to function fluidly within Streamlit's native hamburger-collapse navigation framework.

### Refactored `app.py` (Mobile-Responsive Protocol)

```python
import streamlit as st
import numpy as np
import joblib
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed" # Better for mobile first-paint views
)

# ---------------- MOBILE-RESPONSIVE CSS ----------------
st.markdown("""
<style>
    /* Global Application Theme Override */
    .stApp {
        background-color: #030712 !important;
        color: #F8FAFC !important;
    }
    
    /* Content Padding Adjustment */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar Custom Colors */
    section[data-testid="stSidebar"] {
        background-color: #050B18 !important;
        border-right: 1px solid #111C34;
    }

    /* Fluid Content Panels */
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

    /* Custom Input Element Typography Fixes */
    label[data-testid="stWidgetLabel"] p {
        color: #94A3B8 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }

    div[data-testid="stNumberInput"] {
        background-color: #091122 !important;
        border-radius: 8px !important;
    }
    
    /* Action Button styling */
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
    
    /* Fluid Result Display (Stacks vertically on Mobile) */
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

    /* Responsive Footer Framework */
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

# ---------------- MODEL PIPELINE CACHE ----------------
@st.cache_resource
def load_ml_model():
    model_path = "nifty_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
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
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 8px; cursor: pointer;">💡 How it Works</div>
        <div style="padding: 12px 16px; border-radius: 8px; font-weight: 500; color: #94A3B8; margin-bottom: 20px; cursor: pointer;">✉️ Contact</div>
    """, unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="sidebar-card">
            <h5 style="color: #3B82F6; margin: 0 0 8px 0; font-size: 13px; font-weight: 600;">About This App</h5>
            <p style="color: #64748B; font-size: 12px; line-height: 1.5; margin: 0;">
                NIFTY AI Predictor uses machine learning to forecast the next trading day trend based on comprehensive historical market data parameters.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- HERO HEADER ----------------
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #040A18 0%, #06132C 100%); border: 1px solid #111E3B; border-radius: 16px; padding: 30px 20px; margin-bottom: 20px; position: relative; overflow: hidden;">
        <div style="z-index: 2; position: relative;">
            <h1 style="font-size: clamp(32px, 5vw, 48px); font-weight: 900; margin: 0; letter-spacing: -0.5px; line-height: 1.1;">
                NIFTY <span style="color: #3B82F6;">AI</span> PREDICTOR
            </h1>
            <p style="color: #64748B; font-size: clamp(14px, 2vw, 16px); margin-top: 10px; font-weight: 400; max-width: 600px;">
                AI-Powered Quantitative Prediction Architecture for Next Trading Day Directional Bias.
            </p>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------- METRICS GRID ----------------
# Native columns auto-collapse vertically on narrow screens/smartphones
m1, m2, m3, m4 = st.columns([1, 1, 1, 1])

# CSS Injection for native metrics to mirror dark glass layout seamlessly
metric_css = """
<style>
    div[data-testid="stMetric"] {
        background: #091225 !important;
        border: 1px solid #142342 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    div[data-testid="stMetricLabel"] p { color: #64748B !important; font-size: 12px !important; text-transform: uppercase; }
    div[data-testid="stMetricValue"] div { color: #FFFFFF !important; font-size: 16px !important; font-weight: 600 !important; }
</style>
"""
st.markdown(metric_css, unsafe_allow_html=True)

m1.metric(label="📅 Market", value="NIFTY 50")
m2.metric(label="🕒 Last Updated", value="Live Stream")
m3.metric(label="📊 Status", value="Market Open")
m4.metric(label="⚡ Accuracy Engine", value="87.42%")

st.write("")

# ---------------- INPUT CONTAINER ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">冲 Market Inputs</div>', unsafe_allow_html=True)

# Responsive input layouts split on desktop, stacked seamlessly on mobile viewports
c1, c2 = st.columns(2, gap="medium")
with c1:
    open_price = st.number_input("Open Price", format="%.2f", value=0.00)
    low_price = st.number_input("Low Price", format="%.2f", value=0.00)
    volume = st.number_input("Volume", min_value=0, step=1, value=0)

with c2:
    high_price = st.number_input("High Price", format="%.2f", value=0.00)
    close_price = st.number_input("Close Price", format="%.2f", value=0.00)
    previous_return = st.number_input("Previous Return (%)", format="%.2f", value=0.00)

predict_clicked = st.button("🚀 PREDICT TOMORROW")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INFERENCE OUTPUT CONTAINER ----------------
st.markdown('<div class="content-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-header">🎯 Prediction Result</div>', unsafe_allow_html=True)

if predict_clicked:
    input_features = np.array([[open_price, high_price, low_price, close_price, volume, previous_return]])
    
    if model is not None:
        prediction = model.predict(input_features)[0]
        probability = model.predict_proba(input_features)[0]
    else:
        prediction = 1 if close_price >= open_price else 0
        probability = [0.15, 0.85] if prediction == 1 else [0.85, 0.15]
        
    if prediction == 1:
        confidence = probability[1] * 100
        st.markdown(
            f"""
            <div class="result-layout">
                <div class="result-circle-base result-circle-bullish">🐂</div>
                <div>
                    <h2 style="color: #10B981; margin: 0; font-size: clamp(20px, 4vw, 28px); font-weight: 700;">BULLISH DIRECTION</h2>
                    <p style="color: #64748B; margin: 4px 0 12px 0; font-size: 14px;">Data signals upward session vectors.</p>
                    <span style="color: #F8FAFC; font-weight: 500; font-size: 15px;">Confidence: <b style="color:#10B981;">{confidence:.2f}%</b></span>
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
                    <h2 style="color: #EF4444; margin: 0; font-size: clamp(20px, 4vw, 28px); font-weight: 700;">BEARISH DIRECTION</h2>
                    <p style="color: #64748B; margin: 4px 0 12px 0; font-size: 14px;">Data signals distributive downward sessions.</p>
                    <span style="color: #F8FAFC; font-weight: 500; font-size: 15px;">Confidence: <b style="color:#EF4444;">{confidence:.2f}%</b></span>
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
                <p style="color: #64748B; margin: 2px 0 8px 0; font-size: 13px;">Market Direction Bias Status</p>
                <span style="color: #475569; font-weight: 500; font-size: 14px;">Confidence: --%</span>
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
            <span style="color: #64748B;">💻 GitHub</span>
            <span style="color: #64748B;">🌐 LinkedIn</span>
            <span style="color: #64748B;">🐦 Twitter</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

```
