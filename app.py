# ---------------- ANGEL ONE CONFIGURATION ENTRY ----------------
if mode == "AngelOne Live Stream":
    st.markdown('<div class="content-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">🔐 Secure SmartAPI Gateway Terminal</div>', unsafe_allow_html=True)
    
    ak_col, cc_col, pw_col, to_col = st.columns(4)
    with ak_col:
        API_KEY = st.text_input("SmartAPI Key", type="password", help="Get this from your SmartAPI developer profile panel")
    with cc_col:
        CLIENT_CODE = st.text_input("Client ID / Code", help="Your Angel One login User ID")
    with pw_col:
        PASSWORD = st.text_input("Mpin / Password", type="password")
    with to_col:
        TOTP_SECRET = st.text_input("TOTP Token String", type="password", help="The secret key string from standard safety apps")
        
    st.markdown('</div>', unsafe_allow_html=True)

    if API_KEY and CLIENT_CODE and PASSWORD and TOTP_SECRET:
        try:
            # --- STATIC IP PROXY CONFIGURATION START ---
            # Paste the proxy URL you got from QuotaGuard here
            PROXY_URL = "http://username:password@static.quotaguard.com:9293" 
            
            # Injecting proxy configuration into the system runtime environment
            os.environ["HTTP_PROXY"] = PROXY_URL
            os.environ["HTTPS_PROXY"] = PROXY_URL
            # --- STATIC IP PROXY CONFIGURATION END ---

            # Now, when SmartConnect connects, it routes through your static proxy IP!
            smart_conn = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            session_data = smart_conn.generateSession(CLIENT_CODE, PASSWORD, totp)
            
            if session_data.get('status'):
                api_authenticated = True
                
                token_map = {"NIFTY 50": "26000", "SENSEX": "1", "BANKEX": "12"}
                exchange_map = {"NIFTY 50": "NSE", "SENSEX": "BSE", "BANKEX": "BSE"}
                symbol_map = {"NIFTY 50": "Nifty 50", "SENSEX": "SENSEX", "BANKEX": "BANKEX"}
                
                quote_response = smart_conn.getOHLC(
                    exchange=exchange_map[target_index], 
                    tradingsymbol=symbol_map[target_index], 
                    symboltoken=token_map[target_index]
                )
                
                if quote_response.get('status') and 'data' in quote_response:
                    live_data = quote_response['data']
                    open_price = float(live_data.get('open', 0))
                    high_price = float(live_data.get('high', 0))
                    low_price = float(live_data.get('low', 0))
                    close_price = float(live_data.get('close', 0))
                    volume = float(live_data.get('volume', 0))
                    previous_return = ((close_price - open_price) / open_price) * 100 if open_price > 0 else 0.0
                else:
                    st.error(f"OHLC data request failed: {quote_response.get('message', 'Invalid response format')}")
            else:
                st.error(f"Login Rejected: {session_data.get('message', 'Check client parameters or TOTP configuration')}")
        except Exception as api_err:
            st.error(f"Failed to authenticate connection stream to AngelOne Gateway: {api_err}")
    else:
        st.info("Awaiting input keys inside the Secure Gateway panel above to pull real-time data ticks.")
