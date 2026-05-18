import yfinance as yf
import pandas as pd
import streamlit as st
import requests
import io
import Stock_Dashboard
from streamlit_marquee import streamlit_marquee
st.set_page_config(page_title="NSE/BSE Live Dashboard", layout="wide")
st.title("Indian Stock Market Live Dashboard")

st.markdown(
    """
    <div style="
        background-color:#FFFDE7;
        color:#000000;
        font-size:15px;
        line-height:20px;
        width:100%;
        padding:8px;
        text-align:center;
        font-weight:bold;">
        ⚠️ Disclaimer: For awareness use only.  
        Investments in securities markets are subject to market risks.  
        Review your goals before investing.
    </div>
    """,
    unsafe_allow_html=True
)

def fetch_tickers(exchange, index_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    if exchange == "NSE":
        urls = {
            "Nifty 50": "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
            "Nifty Bank": "https://archives.nseindia.com/content/indices/ind_niftybanklist.csv",
            "Nifty Midcap 100": "https://archives.nseindia.com/content/indices/ind_niftymidcap100list.csv",
            "Nifty Smallcap 100": "https://archives.nseindia.com/content/indices/ind_niftysmallcap100list.csv"
        }
        try:
            resp = requests.get(urls[index_name], headers=headers)
            df = pd.read_csv(io.StringIO(resp.text))
            return (df['Symbol'] + ".NS").tolist()
        except:
            st.warning("Could not fetch NSE tickers")
            return []
    else: 
        bse_data = {
            "SENSEX": ["500325.BO", "532540.BO", "500180.BO", "532174.BO", "500209.BO"],
            "BSE 100": ["500325.BO", "532540.BO", "500124.BO", "532898.BO"]
        }
        return bse_data.get(index_name, [])

# Sidebar toggle
mode = st.sidebar.radio("Choose Mode:", ["Dashboard", "Prediction"],key="mode_selector")

if mode == "Dashboard":
    exchange = st.selectbox("Select Exchange : ", ["NSE", "BSE"])
    if exchange == 'NSE':
        index_options = ['Nifty 50','Nifty Bank','Nifty Midcap 100','Nifty Smallcap 100']
    else:
        index_options = ['SENSEX','BSE 100']

    subcat = st.selectbox("Select Index : ", index_options)
    ticker_list = fetch_tickers(exchange, subcat)

    if ticker_list:
        selected_ticker = st.selectbox("Select Company", ticker_list)
        Stock_Dashboard.dashboard(selected_ticker)

elif mode == "Prediction":
    exchange = st.selectbox("Select Exchange for Prediction : ", ["NSE"])
    if exchange == 'NSE':
        index_options = ['Nifty 50','Nifty Bank','Nifty Midcap 100','Nifty Smallcap 100']
    
    subcat = st.selectbox("Select Index for Prediction : ", index_options)
    ticker_list = fetch_tickers(exchange, subcat)

    if ticker_list:
        selected_ticker = st.selectbox("Select Company", ticker_list)
        Stock_Dashboard.prediction(selected_ticker)
