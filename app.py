import streamlit as st
import numpy as np
import joblib

st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide"
)

model = joblib.load("nifty_model.pkl")

# ---------- CSS ----------
st.markdown("""
<style>

.stApp {
    background-color: #0B1120;
}

.main-title {
    font-size: 55px;
    font-weight: 700;
    color: white;
    margin-bottom: 0px;
}

.subtitle {
    color: #94A3B8;
    font-size: 18px;
}

.card {
    background: #111827;
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #1E293B;
}

.metric-card {
    background: #111827;
    padding: 20px;
    border-radius: 20px;
    text-align: center;
    border: 1px solid #1E293B;
}

div.stButton > button {
    width: 100%;
    height: 60px;
    border-radius: 15px;
    border: none;
    background: linear-gradient(
        90deg,
        #2563EB,
        #7C3AED
    );
    color: white;
    font-size: 20px;
    font-weight: bold;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
left, right = st.columns([2, 1])

with left:
    st.markdown(
        "<div class='main-title'>NIFTY AI Predictor</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>AI-powered prediction of the next trading day's market direction</div>",
        unsafe_allow_html=True
    )

with right:
    st.markdown("""
    <div class='card' style='text-align:center'>
        <h1 style='font-size:70px'>📈</h1>
        <h4 style='color:#60A5FA'>
        Bull vs Bear Market
        </h4>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------- METRICS ----------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Market", "NIFTY 50")

with m2:
    st.metric("Model", "Random Forest")

with m3:
    st.metric("Status", "Ready")

with m4:
    st.metric("Accuracy", "87.4%")

st.write("")

# ---------- INPUT SECTION ----------
st.markdown("## Market Inputs")

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

predict = st.button(
    "🚀 Predict Tomorrow"
)

# ---------- PREDICTION ----------
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

    if prediction == 1:
        confidence = probability[1] * 100

        st.success(
            f"📈 Prediction: BULLISH\n\nConfidence: {confidence:.2f}%"
        )

    else:
        confidence = probability[0] * 100

        st.error(
            f"📉 Prediction: BEARISH\n\nConfidence: {confidence:.2f}%"
        )

    st.progress(confidence / 100)

# ---------- FOOTER ----------
st.write("")
st.divider()

st.markdown(
    """
    <div style='text-align:center'>
        <h4 style='color:#94A3B8'>
        Designed by
        </h4>

        <h1 style='
        color:#60A5FA;
        font-size:45px;
        margin-top:-10px;'>
        MAJNU
        </h1>

        <p style='color:#64748B'>
        AI • Finance • Innovation
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
