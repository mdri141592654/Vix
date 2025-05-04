import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "yfinance", "pandas", "numpy", "requests"])

import yfinance as yf
import pandas as pd
import numpy as np
import json

# CM_Williams_Vix_Fix Berechnung
def calculate_vix_fix(df, pd_period=22, bbl=20, mult=2.0, lb=50, ph=0.85):
    df = df.copy()
    df["wvf"] = ((df["High"].rolling(window=pd_period).max() - df["Close"]) /
                 df["High"].rolling(window=pd_period).max()) * 100

    midline = df["wvf"].rolling(window=bbl).mean()
    sdev = df["wvf"].rolling(window=bbl).std()
    upperBand = midline + sdev * mult
    df["green_bar"] = df["wvf"] >= upperBand

    return df

# Liste der S&P500 und DAX Ticker (vereinfachte Demo)
sp500_tickers = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]  # Kürzen für Test
dax_tickers = ["SAP.DE", "SIE.DE", "BAYN.DE", "ALV.DE", "DTE.DE"]

all_tickers = sp500_tickers + dax_tickers
results = []

for ticker in all_tickers:
    try:
        data = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if len(data) < 22:
            continue
        df = calculate_vix_fix(data)
        if df["green_bar"].iloc[-1]:
            results.append(ticker)
    except Exception as e:
        print(f"{ticker} Fehler: {e}")

# Als JSON-Datei speichern
with open("vixfix_green.json", "w") as f:
    json.dump(results, f)

print("Fertig! Ergebnisse in vixfix_green.json gespeichert.")
