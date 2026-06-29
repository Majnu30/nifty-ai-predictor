import streamlit as st
import numpy as np
import joblib

# Page Config
st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="centered"
)

# Load Model
model = joblib.load("nifty_model.pkl")

# Header
st.title("📈 NIFTY AI Predictor")
st.caption("AI-powered prediction of the next trading day's market direction")

st.divider()

# Inputs
open_price = st.number_input("📊 Open Price", format="%.2f")
high_price = st.number_input("📈 High Price", format="%.2f")
low_price = st.number_input("📉 Low Price", format="%.2f")
close_price = st.number_input("💰 Close Price", format="%.2f")
volume = st.number_input("🔄 Volume", min_value=0)
previous_return = st.number_input(
    "📌 Previous Return (%)",
    format="%.2f"
)

# Predict Button
if st.button("🚀 Predict Tomorrow", use_container_width=True):

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

    st.divider()
    st.subheader("🎯 Prediction Result")

    if prediction == 1:
        confidence = probability[1] * 100
        st.success(f"📈 Market may move UP\n\nConfidence: {confidence:.2f}%")
    else:
        confidence = probability[0] * 100
        st.error(f"📉 Market may move DOWN\n\nConfidence: {confidence:.2f}%")

    st.progress(confidence / 100)

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align:center; color:gray;'>
        <h4>Designed by <span style='color:#3B82F6;'>MAJNU</span></h4>
    </div>
    """,
    unsafe_allow_html=True
)
