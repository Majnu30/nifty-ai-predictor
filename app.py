
import streamlit as st
import numpy as np
import joblib
import yfinance as yf

# Load your model (Make sure 'models/nifty_model.pkl' exists in your Colab file explorer!)
try:
    model = joblib.load("models/nifty_model.pkl")
except:
    # Fallback if the folder structure is different in Colab
    model = joblib.load("nifty_model.pkl")

st.title("NIFTY AI Predictor")

mode = st.radio("Select Input Mode", ["Manual Input", "Live Market Data"])

open_price, high_price, low_price, close_price, volume, previous_return = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

if mode == "Live Market Data":
    st.subheader("Fetching Real-Time Data...")
    try:
        nifty = yf.Ticker("^NSEI")
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
            
            st.info(
                f"**Live Data Loaded (Index: NIFTY 50)**\n"
                f"* **Open:** {open_price:,.2f}\n"
                f"* **High:** {high_price:,.2f}\n"
                f"* **Low:** {low_price:,.2f}\n"
                f"* **Close:** {close_price:,.2f}\n"
                f"* **Volume:** {volume:,.0f}\n"
                f"* **Calculated Day Return:** {previous_return:.2f}%"
            )
        else:
            st.warning("Insufficient data fetched.")
    except Exception as e:
        st.error(f"Error fetching live data: {e}")

if mode == "Manual Input":
    open_price = st.number_input("Open", value=open_price)
    high_price = st.number_input("High", value=high_price)
    low_price = st.number_input("Low", value=low_price)
    close_price = st.number_input("Close", value=close_price)
    volume = st.number_input("Volume", value=volume)
    previous_return = st.number_input("Previous Return (%)", value=previous_return)

if st.button("Predict Next Movement"):
    data = np.array([[open_price, high_price, low_price, close_price, volume, previous_return]])
    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0]

    st.write("---")
    if prediction == 1:
        st.success(f"UP 📈\nConfidence: {probability[1]*100:.2f}%")
    else:
        st.error(f"DOWN 📉\nConfidence: {probability[0]*100:.2f}%")
