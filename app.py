import streamlit as st
import numpy as np
import joblib

model = joblib.load("nifty_model.pkl")

st.title("NIFTY AI Predictor")

open_price = st.number_input("Open")
high_price = st.number_input("High")
low_price = st.number_input("Low")
close_price = st.number_input("Close")
volume = st.number_input("Volume")
previous_return = st.number_input("Previous Return (%)")

if st.button("Predict"):

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

    if prediction == 1:
        st.success(
            f"UP 📈\nConfidence: {probability[1] * 100:.2f}%"
        )
    else:
        st.error(
            f"DOWN 📉\nConfidence: {probability[0] * 100:.2f}%"
        )
