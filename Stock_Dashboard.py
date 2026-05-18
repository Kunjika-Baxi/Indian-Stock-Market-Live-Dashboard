import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
import os
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
from datetime import datetime, timedelta
import io
from openpyxl import load_workbook
import xgboost as xgb


def dashboard(selected_symbol):
    
    #setting layout of page and fetching data from yfinance 
    s = yf.Ticker(selected_symbol)
    try:
        existing_tickers = pd.read_excel("stock_report.xlsx")['Symbol'].unique()
    except:
        existing_tickers = []

    if selected_symbol in existing_tickers:
    # Backfill for existing tickers
        filter_df = s.history(start="2025-12-04")
    else:
    # 8 months history for new tickers
        today = datetime.today()
        start_date = (today - timedelta(days=240)).strftime("%Y-%m-%d")
        filter_df = s.history(start=start_date, end=today.strftime("%Y-%m-%d"))
    '''---------------------------------------------------------------------------------------------------------------'''


    #Organizing and structuring dataset for analysis
    filter_df.reset_index(inplace=True)
    filter_df['Date']=pd.to_datetime(filter_df['Date'])
    filter_df['Year'] = filter_df['Date'].dt.year
    filter_df['High-Low']=filter_df['High']-filter_df['Low']
    filter_df['Open-Close']=filter_df['Open']-filter_df['Close']
    filter_df['Change Pct']=filter_df['Close'].pct_change()*100
    filter_df['i1']=filter_df['Close'].rolling(window=20).mean() #average 20 day rolling of closing price - Moving Average

    delta=filter_df['Close'].diff()
    gain=delta.clip(lower=0)
    loss=-delta.clip(upper=0)
    avg_gain=gain.rolling(14).mean()
    avg_loss=loss.rolling(14).mean()
    rs=avg_gain/avg_loss
    filter_df['i2']=100-(100/(1+rs)) #Relative Strength Index - meansures overbought/oversold conditions
    
    ema12=filter_df['Close'].ewm(span=12,adjust=False).mean()
    ema26=filter_df['Close'].ewm(span=26,adjust=False).mean()
    filter_df['i3']=ema12-ema26    #Moving average convergence divergence
    '''---------------------------------------------------------------------------------------------------------------'''
    if 'all_results' not in st.session_state:
        st.session_state.all_results = {} # Dictionary: {ticker: dataframe}
    required_cols = ["Date","Open","High","Low","Close","Volume","i1","i2","i3","Change Pct"]
    export_df = filter_df[required_cols].copy()
    export_df['Date'] = export_df['Date'].dt.tz_localize(None)
    export_df['Date'] = export_df['Date'].dt.strftime("%Y-%m-%d")
    st.session_state.all_results[selected_symbol] = export_df
    
    '''---------------------------------------------------------------------------------------------------------------'''
    #calculation for KPI's and Plots
    highest_open=filter_df['Open'].max()
    lowest_close=filter_df['Close'].min()

    yearofp=filter_df.groupby('Year')['Change Pct'].mean()
    maxpyear=yearofp.idxmax()

    avgreturn=filter_df['Change Pct'].mean()
    volatility=filter_df['Change Pct'].std()

    
    #Setting metrices
    col1,col2,col3,col4,col5,col6,col7=st.columns(7)
    #col1
    col1.metric("Highest Open",round(highest_open,2))
    #col2
    col2.metric("Lowest Close",round(lowest_close,2))
    #col3
    col3.metric("Max Profit Year",maxpyear)
    #col4
    col4.metric(
        "Average Daily Return (%)",
        round(avgreturn, 2),
        delta=f"{round(avgreturn*100, 2)}%"
    )
    #col5
    col5.metric(
        "Volatility (%)",
        round(volatility, 2),
        delta=f"{round(volatility, 2)}%"
    )
    #col6
    start_price = filter_df['Close'].iloc[0]
    end_price = filter_df['Close'].iloc[-1]
    n_years = (filter_df['Date'].iloc[-1] - filter_df['Date'].iloc[0]).days / 365
    cagr = (end_price / start_price) ** (1/n_years) - 1
    col6.metric(
        "CAGR(%)",
        round(cagr, 2),
        delta=f"{round(cagr*100, 2)}%"
    )
    #col7
    avg_daily_return = filter_df['Change Pct'].mean()
    risk_free_rate = 0  # assume 0 for simplicity
    sharpe_ratio = (avg_daily_return/volatility)*np.sqrt(252)
    col7.metric("Sharpe Ratio",round(sharpe_ratio,2))

    '''---------------------------------------------------------------------------------------------------------------'''


    #Bullish v/s Bearish

    short_ma = filter_df['Close'].rolling(window=20).mean().iloc[-1]
    long_ma = filter_df['Close'].rolling(window=50).mean().iloc[-1]

    if short_ma > long_ma:
        st.success("Overall Trend: Bullish (prices are expected to rise !!!)")
    else:
        st.error("Overall Trend: Bearish (prices are expected to fall !!!)")
    '''---------------------------------------------------------------------------------------------------------------'''


    #RSI -Relative Strength Index
    latest_rsi = filter_df['i2'].iloc[-1]
    if latest_rsi > 70:
        st.warning("Relative Strength Index (RSI) indicates Overbought")
    elif latest_rsi < 30:
        st.info("Relative Strength Index (RSI) indicates Oversold")
    else:
        st.write("Relative Strength Index (RSI) is Neutral")

    '''---------------------------------------------------------------------------------------------------------------'''


    #Plot 1
    fig_ma = px.line(filter_df,x="Date",y=["Close", "i1"],labels={"value": "Price", "variable": "Legend"},title="Closing Price vs Moving Average")
    st.plotly_chart(fig_ma, use_container_width=True)

    #Plot 2
    fig_candle = go.Figure(data=[go.Candlestick(x=filter_df['Date'],open=filter_df['Open'],high=filter_df['High'],low=filter_df['Low'],
    close=filter_df['Close'])])
    fig_candle.update_layout(title="Candlestick Chart", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig_candle, use_container_width=True)

    '''---------------------------------------------------------------------------------------------------------------'''

    #Download Buttons

    if st.session_state.all_results:
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            for ticker, df in st.session_state.all_results.items():
                # This creates a separate sheet for every ticker in the dictionary
                df.to_excel(writer, sheet_name=ticker[:31], index=False)
        
        st.download_button(
            label="Download Excel (Separate Sheets)",
            data=buffer.getvalue(),
            file_name="stocks_data.xlsx",
            mime="application/vnd.ms-excel"
        )
        
    
    kpi_df = pd.DataFrame({
    "Symbol":[selected_symbol],
    "Highest Open": [highest_open],
    "Lowest Close": [lowest_close],
    "Max Profit Year": [maxpyear],
    "Average Daily Return (%)": [avgreturn],
    "Volatility (%)": [volatility],
    "CAGR (%)": [cagr],
    "Sharpe Ratio": [sharpe_ratio]})
    
    st.download_button(label="Download KPI Summary",data=kpi_df.to_csv(index=False).encode('utf-8'),
    file_name=f"{selected_symbol}_kpi_summary.csv",mime="text/csv")
    '''---------------------------------------------------------------------------------------------------------------'''


def prediction(selected_symbol):
    st.header("Stock Price Prediction")
    company = selected_symbol
    s = yf.Ticker(company)
    df = s.history(period='max')
    df.reset_index(inplace=True)
    df['Change Pct'] = df['Close'].pct_change() * 100
    df['High-Low'] = df['High'] - df['Low']
    df['Open-Close'] = df['Open'] - df['Close']
    df['i1']=df['Close'].rolling(window=20).mean()

    delta=df['Close'].diff()
    gain=delta.clip(lower=0)
    loss=-delta.clip(upper=0)
    avg_gain=gain.rolling(14).mean()
    avg_loss=loss.rolling(14).mean()
    rs=avg_gain/avg_loss
    df['i2']=100-(100/(1+rs)) #Relative Strength Index - meansures overbought/oversold conditions
    
    ema12=df['Close'].ewm(span=12,adjust=False).mean()
    ema26=df['Close'].ewm(span=26,adjust=False).mean()
    df['i3']=ema12-ema26    #Moving average convergence divergence

    # Build full dataset with features + target
    df['Target'] = df['Close'].shift(-1)

    features = ['Change Pct','High-Low','Open-Close','i1','i2','i3','Target']
    df_model = df[features].dropna()   # drop rows where any feature or target is NaN

    X = df_model[['Change Pct','High-Low','Open-Close','i1','i2','i3']]
    y = df_model['Target']


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,random_state=40)
    model = xgb.XGBRegressor(n_estimators=100,max_depth=10,random_state=40,n_jobs=-1,verbosity=1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    st.write("Accuracy:", r2_score(y_test, y_pred)*100," %")
    st.write("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))

    fig_pred = go.Figure()

    # Scatter plot: Actual vs Predicted
    fig_pred.add_trace(go.Scatter(
        x=y_test, y=y_pred, mode='markers',
        name='Predicted vs Actual',
        marker=dict(color='blue', size=6, opacity=0.6)
    ))

    # Add a reference line (perfect prediction)
    fig_pred.add_trace(go.Scatter(
        x=y_test, y=y_test, mode='lines',
        name='Perfect Fit', line=dict(color='red', dash='dash')
    ))

    fig_pred.update_layout(
        title="Actual vs Predicted Closing Prices",
        xaxis_title="Actual Close",
        yaxis_title="Predicted Close",
        template="plotly_white"
    )

    st.plotly_chart(fig_pred, use_container_width=True)

    latest_pred = model.predict([X.iloc[-1]])[0]  #next day close value prediction
    latest_close = df['Close'].iloc[-1]  #actual most recent closing price
    st.write("Actual Recent Closing : ",latest_close)
    if latest_pred > latest_close:
        st.success(f"Predicted next close: {latest_pred:.2f} → Suggestion: BUY TODAY")
    else:
        st.error(f"Predicted next close: {latest_pred:.2f} → Suggestion: SELL TODAY")






