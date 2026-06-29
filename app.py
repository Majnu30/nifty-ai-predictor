import streamlit as st
import numpy as np
import joblib

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
    background: linear-gradient(180deg,#020617,#030b1f);
    color:white;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:#040B1D;
    border-right:1px solid #1E293B;
}

/* Cards */
.card{
    background:rgba(10,20,40,0.7);
    border:1px solid #1E293B;
    border-radius:20px;
    padding:25px;
    box-shadow:0 0 20px rgba(59,130,246,0.15);
}

/* Metrics */
.metric-card{
    background:#071122;
    border:1px solid #1E293B;
    border-radius:18px;
    padding:20px;
    text-align:center;
}

/* Predict Button */
div.stButton > button{
    width:100%;
    height:65px;
    border:none;
    border-radius:15px;
    color:white;
    font-size:22px;
    font-weight:700;
    background:linear-gradient(
        90deg,
        #2563EB,
        #9333EA
    );
}

/* Footer */
.footer{
    border:1px solid #1E293B;
    border-radius:25px;
    padding:35px;
    margin-top:40px;
    background:rgba(8,15,35,0.8);
}

</style>
""", unsafe_allow_html=True)
with st.sidebar:

    st.markdown("""
    <h1 style='text-align:center;
    color:#3B82F6;
    font-size:55px'>
    Ⓜ
    </h1>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align:center'>MAJNU</h2>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 🏠 Home")
    st.markdown("### 📈 Predict")
    st.markdown("### ℹ️ About")
    st.markdown("### 💡 How It Works")
    st.markdown("### ✉️ Contact")

    st.markdown("---")

    st.info(
        """
        **About This App**

        Predicts the next trading day's
        market direction using
        Machine Learning.
        """
    )
    
left, right = st.columns([1.2,1])

with left:

    st.markdown("""
    <h1 style='font-size:65px'>
    NIFTY
    <span style='color:#3B82F6'>
    AI
    </span><br>
    PREDICTOR
    </h1>
    """, unsafe_allow_html=True)

    st.markdown(
        "### AI-Powered Prediction for Next Day Market Direction"
    )

with right:

    st.markdown("""
    <div style="
    border-radius:25px;
    padding:40px;
    text-align:center;
    background:
    linear-gradient(
    135deg,
    #071122,
    #0F172A
    );">

    <h1 style='font-size:90px'>
    🐂 ⚔️ 🐻
    </h1>

    <h3 style='color:#60A5FA'>
    Bull vs Bear Market
    </h3>

    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "📅 Market",
        "NIFTY 50"
    )

with c2:
    st.metric(
        "🕒 Last Updated",
        "Live"
    )

with c3:
    st.metric(
        "📊 Status",
        "Market Open"
    )

with c4:
    st.metric(
        "🤖 Model Accuracy",
        "87.42%"
    )
    st.markdown("## 📈 Market Inputs")

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

    st.markdown("---")
    st.subheader("🎯 Prediction Result")

    if prediction == 1:

        confidence = probability[1] * 100

        st.success(
            "📈 Market Direction : BULLISH"
        )

    else:

        confidence = probability[0] * 100

        st.error(
            "📉 Market Direction : BEARISH"
        )

    st.progress(
        confidence / 100
    )

    st.write(
        f"Confidence : {confidence:.2f}%"
    )

    st.markdown("""
<div class='footer'>

<h4>Designed by</h4>

<h1 style="
font-size:70px;
background:linear-gradient(
90deg,
#3B82F6,
#A855F7
);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
">

MAJNU

</h1>

<h3 style='color:#60A5FA'>
Code. Create. Conquer.
</h3>

</div>
""", unsafe_allow_html=True)
    
