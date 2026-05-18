# Indian Stock Market Live Dashboard

A Streamlit-based interactive dashboard for **NSE/BSE stock analysis and prediction**.  
This project fetches live market data, computes key performance indicators (KPIs), visualizes trends, and applies machine learning (XGBoost) for predictive modeling.

---

## Features

### Dashboard
- Fetch tickers from NSE/BSE indices (Nifty 50, Bank, Midcap, Smallcap, Sensex, BSE 100).
- KPIs: Highest Open, Lowest Close, Max Profit Year, Average Daily Return, Volatility, CAGR, Sharpe Ratio.
- Trend analysis: Bullish vs Bearish signals.
- RSI (Relative Strength Index) and MACD (Moving Average Convergence Divergence).
- Interactive plots: Moving Average line chart, Candlestick chart.
- Export options: Multi-sheet Excel download & KPI summary CSV.

### Prediction
- Historical data fetched via `yfinance`.
- Feature engineering: Change %, High-Low, Open-Close, Moving Average, RSI, MACD.
- XGBoost regression model for next-day closing price prediction.
- Evaluation metrics: R², RMSE.
- Visualizations: Actual vs Predicted scatter plot.
- Trend indication (Predict Next Day's Closing Price)

---

## Tech Stack

- **Frontend:** Streamlit  
- **Data:** yfinance, requests, pandas  
- **Visualization:** Plotly (Express & Graph Objects)  
- **Machine Learning:** scikit-learn, XGBoost  
- **Export:** openpyxl for Excel integration  

---

## Project Structure

 main.py                   # Entry point with dashboard/prediction mode toggle
  ├── Stock_Dashboard.py   # Core logic for dashboard & prediction
  ├── stock_report.xlsx    # Optional file for existing tickers
  └── requirements.txt     # Dependencies

  
---

## Installation & Usage

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kunjika-Baxi/Indian-Stock-Market-Live-Dashboard.git
   cd Indian-Stock-Market-Live-Dashboard

2. **Install Dependencies**
   pip install -r requirements.txt
   
3. **Run the app**
   streamlit run main.py

