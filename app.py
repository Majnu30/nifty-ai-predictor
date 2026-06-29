import streamlit as st
import numpy as np
import joblib

st.set_page_config(
    page_title="NIFTY AI Predictor",
    page_icon="📈",
    layout="wide"
)

model = joblib.load("nifty_model.pkl")

st.title("📈 NIFTY AI Predictor")
st.caption("AI-powered prediction of the next trading day's market direction")

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Market Inputs")

    c1, c2 = st.columns(2)

    with c1:
        open_price = st.number_input(
            "Open Price",
            min_value=0.0,
            format="%.2f"
        )

        low_price = st.number_input(
            "Low Price",
            min_value=0.0,
            format="%.2f"
        )

        volume = st.number_input(
            "Volume",
            min_value=0,
            step=1000
        )

    with c2:
        high_price = st.number_input(
            "High Price",
            min_value=0.0,
            format="%.2f"
        )

        close_price = st.number_input(
            "Close Price",
            min_value=0.0,
            format="%.2f"
        )

        previous_return = st.number_input(
            "Previous Return (%)",
            format="%.2f"
        )

    predict = st.button(
        "🚀 Predict Tomorrow",
        use_container_width=True
    )

with col2:
    st.subheader("Today's Summary")

    st.metric("Open", f"{open_price:,.2f}")
    st.metric("Close", f"{close_price:,.2f}")
    st.metric("Previous Return", f"{previous_return:.2f}%")

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
    st.subheader("Prediction Result")

    c1, c2 = st.columns(2)

    if prediction == 1:
        with c1:
            st.success("📈 BULLISH")

        with c2:
            st.metric(
                "Confidence",
                f"{probability[1]*100:.2f}%"
            )
    else:
        with c1:
            st.error("📉 BEARISH")

        with c2:
            st.metric(
                "Confidence",
                f"{probability[0]*100:.2f}%"
            )
