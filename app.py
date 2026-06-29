import streamlit as st
import numpy as np
import joblib

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide"
)

# ---------------- LOAD MODEL ----------------
model = joblib.load("nifty_model.pkl")

# ---------------- CSS ----------------
st.markdown("""
<style>

.stApp {
    background-color: #050A18;
    color: white;
}

.block-container {
    padding-top: 2rem;
}

div[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #1E293B;
    padding: 20px;
    border-radius: 18px;
}

div.stButton > button {
    width: 100%;
    height: 65px;
    border-radius: 15px;
    border: none;
    color: white;
    font-size: 22px;
    font-weight: bold;
    background: linear-gradient(
        90deg,
        #2563EB,
        #9333EA
    );
}

.footer-card {
    background: #111827;
    border: 1px solid #1E293B;
    border-radius: 25px;
    padding: 40px;
    margin-top: 50px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
left, right = st.columns([2, 1])

with left:
    st.markdown(
        """
        <h1 style='font-size:60px; margin-bottom:0;'>
            NIFTY
            <span style='color:#3B82F6;'>
            AI
            </span>
            <br>
            PREDICTOR
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='color:#94A3B8; font-size:20px;'>
        AI-powered prediction for next day market direction
        </p>
        """,
        unsafe_allow_html=True
    )

with right:
    st.markdown(
        """
        <div style="
            background:#111827;
            border-radius:20px;
            padding:35px;
            text-align:center;
            border:1px solid #1E293B;
        ">
            <h1 style='font-size:80px;'>📈</h1>
            <h3 style='color:#60A5FA;'>
                Bull vs Bear Market
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# ---------------- METRICS ----------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📅 Market", "NIFTY 50")

with c2:
    st.metric("🕒 Updated", "Live")

with c3:
    st.metric("📊 Status", "Ready")

with c4:
    st.metric("🤖 Model", "AI Enabled")

st.write("")
st.subheader("📈 Market Inputs")

# ---------------- INPUTS ----------------
c1, c2 = st.columns(2)

with c1:
    open_price = st.number_input(
        "Open Price",
        format="%.2f"
    )

    low_price = st.number_input(
        "Low Price",
        format="%.2f"
    )

    volume = st.number_input(
        "Volume",
        min_value=0
    )

with c2:
    high_price = st.number_input(
        "High Price",
        format="%.2f"
    )

    close_price = st.number_input(
        "Close Price",
        format="%.2f"
    )

    previous_return = st.number_input(
        "Previous Return (%)",
        format="%.2f"
    )

st.write("")

# ---------------- PREDICT BUTTON ----------------
predict = st.button(
    "🚀 PREDICT TOMORROW"
)

# ---------------- PREDICTION ----------------
if predict:

    data = np.array([[
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        previous_return
    ]])

    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0]

    st.write("")
    st.subheader("🎯 Prediction Result")

    if prediction == 1:
        confidence = probability[1] * 100

        st.success(
            f"📈 Market Direction: BULLISH"
        )

    else:
        confidence = probability[0] * 100

        st.error(
            f"📉 Market Direction: BEARISH"
        )

    st.progress(confidence / 100)

    st.write(
        f"Confidence: {confidence:.2f}%"
    )

)
