import streamlit as st
import numpy as np
import joblib
from PIL import Image

st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

model = joblib.load("nifty_model.pkl")

st.markdown("""
<style>
.stApp{
    background:#020617;
    color:white;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:#040b1d;
    border-right:1px solid #0f172a;
}

/* Cards */
.card{
    background:rgba(9,15,40,0.8);
    border:1px solid #1e293b;
    border-radius:20px;
    padding:20px;
    box-shadow:0px 0px 20px rgba(59,130,246,0.15);
}

/* Metric cards */
.metric{
    background:#071122;
    border:1px solid #1e293b;
    border-radius:18px;
    padding:18px;
    text-align:center;
}

/* Predict Button */
div.stButton > button{
    width:100%;
    height:65px;
    border:none;
    border-radius:16px;
    font-size:24px;
    font-weight:bold;
    color:white;
    background:linear-gradient(
        90deg,
        #2563eb,
        #9333ea
    );
}

/* Inputs */
.stNumberInput input{
    background:#071122;
    color:white;
    border-radius:12px;
}

/* Footer */
.footer{
    background:#030712;
    border:1px solid #1e293b;
    border-radius:25px;
    padding:30px;
    margin-top:40px;
}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR ===================

with st.sidebar:
    logo = Image.open("assets/majnu_logo.png")
    st.image(logo)

    st.markdown("## 🏠 Home")
    st.markdown("## 📈 Predict")
    st.markdown("## ℹ️ About")
    st.markdown("## 💡 How It Works")
    st.markdown("## ✉️ Contact")

    st.markdown("---")

    st.info(
        """
        **About This App**

        NIFTY AI Predictor uses machine learning
        to forecast the next trading day.
        """
    )

# ================= HEADER ===================

left, right = st.columns([1.2,1])

with left:
    st.markdown("""
    <h1 style='font-size:70px;'>
    NIFTY <span style='color:#3b82f6'>
    AI</span><br>
    PREDICTOR
    </h1>
    """, unsafe_allow_html=True)

    st.markdown(
        "### AI-Powered Prediction for Next Day Market Direction"
    )

with right:
    banner = Image.open("assets/banner.png")
    st.image(banner)

# ================= METRICS ===================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="metric">
        📅<br>
        <h4>NIFTY 50</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="metric">
        🕒<br>
        <h4>Live</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="metric">
        📊<br>
        <h4>Market Open</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        """
        <div class="metric">
        🤖<br>
        <h4>87.42%</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# ================= INPUT CARD ===================

st.markdown(
    "<div class='card'>",
    unsafe_allow_html=True
)

st.subheader("📈 Market Inputs")

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

predict = st.button(
    "🚀 PREDICT TOMORROW"
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)

# ================= RESULT CARD ===================

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

    st.markdown(
        "<div class='card'>",
        unsafe_allow_html=True
    )

    st.subheader("🎯 Prediction Result")

    if prediction == 1:
        st.success("📈 Market Direction : BULLISH")
        confidence = probability[1] * 100
    else:
        st.error("📉 Market Direction : BEARISH")
        confidence = probability[0] * 100

    st.progress(confidence / 100)
    st.write(f"Confidence : {confidence:.2f}%")

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

# ================= FOOTER ===================

st.markdown("""
<div class="footer">

<h4>Designed by</h4>

<h1 style="
background:linear-gradient(
90deg,#2563eb,#a855f7);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
font-size:70px;
margin-top:-10px;
">
MAJNU
</h1>

<h3>Code. Create. Conquer.</h3>

</div>
""", unsafe_allow_html=True)
