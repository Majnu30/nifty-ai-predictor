import streamlit as st
import numpy as np
import joblib
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- THEME & CSS ----------------
st.markdown("""
<style>
    /* Global App Background */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Container Padding */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 5rem;
        max-width: 1200px;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    div[data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-size: 14px !important;
        font-weight: 500;
    }
    
    div[data-testid="stMetricValue"] div {
        color: #F1F5F9 !important;
        font-size: 24px !important;
        font-weight: 600;
    }
    
    /* Action Button styling */
    div.stButton > button {
        width: 100%;
        height: 56px;
        border-radius: 12px;
        border: none;
        color: white;
        font-size: 18px;
        font-weight: 600;
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
        margin-top: 20px;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }

    /* Custom Input Labels */
    label[data-testid="stWidgetLabel"] p {
        color: #CBD5E1 !important;
        font-weight: 500;
    }
    
    /* Prediction Cards */
    .result-card {
        padding: 30px;
        border-radius: 16px;
        margin-top: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .bullish-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.05) 100%);
        border-color: rgba(16, 185, 129, 0.3);
    }
    .bearish-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.05) 100%);
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    /* Footer Styling */
    .footer-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 30px;
        margin-top: 80px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL (SAFE LOAD) ----------------
@st.cache_resource
def load_prediction_model():
    model_path = "nifty_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

model = load_prediction_model()

# ---------------- HEADER AREA ----------------
header_left, header_right = st.columns([3, 1])

with header_left:
    st.markdown(
        """
        <h1 style='font-size: 52px; font-weight: 800; letter-spacing: -1px; margin-bottom: 5px; line-height: 1.1;'>
            NIFTY <span style='background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>AI</span> PREDICTOR
        </h1>
        <p style='color: #94A3B8; font-size: 18px; font-weight: 400; margin-top: 0;'>
            Predicting next-day market direction using advanced machine learning architectures.
        </p>
        """, 
        unsafe_allow_html=True
    )

with header_right:
    st.markdown(
        """
        <div style="text-align: right; padding-top: 10px;">
            <span style="font-size: 14px; background: rgba(59, 130, 246, 0.1); color: #60A5FA; padding: 6px 16px; border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.2); font-weight: 600;">
                Active Environment
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.write("---")

# ---------------- SYSTEM METRICS ----------------
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Market Index", value="NIFTY 50")
m2.metric(label="Data Stream", value="Live Sync")
m3.metric(label="System Engine", value="Ready")
m4.metric(label="Model Core", value="Scikit-Learn Inference" if model else "Demo Mode")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- INPUT FORM SECTION ----------------
st.markdown("<h3 style='font-size:22px; font-weight:600; color:#F1F5F9; margin-bottom:20px;'>📊 Market Input Metrics</h3>", unsafe_allow_html=True)

# 3 Column configuration for a well-balanced form
row1_col1, row1_col2, row1_col3 = st.columns(3)
row2_col1, row2_col2, row2_col3 = st.columns(3)

with row1_col1:
    open_price = st.number_input("Open Price (₹)", format="%.2f", value=22000.00)
with row1_col2:
    high_price = st.number_input("High Price (₹)", format="%.2f", value=22150.00)
with row1_col3:
    low_price = st.number_input("Low Price (₹)", format="%.2f", value=21950.00)

with row2_col1:
    close_price = st.number_input("Close Price (₹)", format="%.2f", value=22100.00)
with row2_col2:
    volume = st.number_input("Volume Traded", min_value=0, step=1000, value=250000)
with row2_col3:
    previous_return = st.number_input("Previous Daily Return (%)", format="%.2f", value=0.45)

# ---------------- ENGINE PREDICTION ----------------
predict_btn = st.button("🚀 EXECUTE ML PREDICTION ENGINE")

if predict_btn:
    # Feature engineering verification structure
    features = np.array([[open_price, high_price, low_price, close_price, volume, previous_return]])
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:22px; font-weight:600; color:#F1F5F9;'>🎯 Inference Output</h3>", unsafe_allow_html=True)
    
    if model is not None:
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
    else:
        # Graceful fallback mock if model pickle is missing
        st.warning("`nifty_model.pkl` structural binary not detected. Running simulated inference visualization.")
        prediction = 1 if close_price >= open_price else 0
        probability = [0.22, 0.78] if prediction == 1 else [0.78, 0.22]

    # Render results dynamically based on direction
    if prediction == 1:
        confidence = probability[1] * 100
        st.markdown(
            f"""
            <div class="result-card bullish-card">
                <h2 style="color: #10B981; margin: 0 0 10px 0; font-size: 28px; display: flex; align-items: center; gap: 10px;">
                    📈 MARKET BIAS: BULLISH
                </h2>
                <p style="color: #A7F3D0; margin: 0 0 15px 0; font-size: 16px;">
                    The model projects systemic upward momentum for the upcoming session.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.progress(confidence / 100)
        st.markdown(f"<p style='color:#10B981; font-weight:600; margin-top:5px;'>Confidence Threshold: {confidence:.2f}%</p>", unsafe_allow_html=True)
        
    else:
        confidence = probability[0] * 100
        st.markdown(
            f"""
            <div class="result-card bearish-card">
                <h2 style="color: #EF4444; margin: 0 0 10px 0; font-size: 28px; display: flex; align-items: center; gap: 10px;">
                    📉 MARKET BIAS: BEARISH
                </h2>
                <p style="color: #FCA5A5; margin: 0 0 15px 0; font-size: 16px;">
                    The model projects systemic downward exposure or selling pressure for the upcoming session.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        # Custom color trick for progress bar logic using markdown styling injection if needed, 
        # but native progress bar stays functional.
        st.progress(confidence / 100)
        st.markdown(f"<p style='color:#EF4444; font-weight:600; margin-top:5px;'>Confidence Threshold: {confidence:.2f}%</p>", unsafe_allow_html=True)

# ---------------- FOOTER BRANDING ----------------
st.markdown(
    """
    <div class="footer-card">
        <p style="color: #64748B; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px;">
            Engineered By
        </p>
        <h1 style="
            font-size: 48px;
            font-weight: 900;
            margin: 0;
            background: linear-gradient(90deg, #3B82F6 0%, #A855F7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 12px;
            padding-left: 12px;
        ">
            MAJNU
        </h1>
        <p style="color: #475569; font-size: 14px; margin-top: 10px; font-weight: 500;">
            Code • Create • Conquer
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
