import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "yfinance", "pandas", "numpy", "requests"])

import yfinance as yf
import pandas as pd
import numpy as np
import json

def calculate_vix_fix(df, pd_period=22, bbl=20, mult=2.0, lb=50, ph=0.85, pl=1.01):
    df = df.copy()

    # WVF-Berechnung
    highest_close = df['Close'].rolling(window=pd_period).max()
    df['wvf'] = ((highest_close - df['Low']) / highest_close) * 100

    # Bollinger Bands
    midline = df['wvf'].rolling(window=bbl).mean()
    sdev = df['wvf'].rolling(window=bbl).std()
    upperBand = midline + sdev * mult

    # Range High
    rangeHigh = df['wvf'].rolling(window=lb).max() * ph

    # Bedingung für grünen Balken
    df['green_bar'] = (df['wvf'] >= upperBand) | (df['wvf'] >= rangeHigh)

    return df

# Liste der S&P500 und DAX Ticker (Demo)
sp500_tickers = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]
dax_tickers = ["SAP.DE", "SIE.DE", "BAYN.DE", "ALV.DE", "DTE.DE"]

all_tickers = sp500_tickers + dax_tickers
results = []

for ticker in all_tickers:
    try:
        data = yf.download(ticker, period="1y", interval="1h", progress=False)
        if len(data) < 60:
            continue
        df = calculate_vix_fix(data)
        if df["green_bar"].iloc[-1]:
            results.append(ticker)
    except Exception as e:
        print(f"{ticker} Fehler: {e}")

