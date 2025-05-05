import os
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def load_tickers():
    with open("tickers/dax_tickers.json", "r") as f:
        dax = json.load(f)
    with open("tickers/sp500_tickers.json", "r") as f:
        sp500 = json.load(f)
    return dax, sp500

def cm_williams_vix_fix(df):
    lowest = df['Low'].rolling(window=22).min()
    highest_close = df['Close'].rolling(window=22).max()
    vixfix = (highest_close - df['Low']) / highest_close * 100
    df['vixfix_green'] = (vixfix > vixfix.shift(1)) & (vixfix > 20)
    return df

def get_current_price(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1h")
        return round(data['Close'].iloc[-1], 2)
    except:
        return None

def analyze():
    dax, sp500 = load_tickers()
    tickers = [(symbol, 'DAX') for symbol in dax] + [(symbol, 'S&P500') for symbol in sp500]

    results = []
    for symbol, index in tickers:
        try:
            df = yf.download(symbol, period="5d", interval="1h", auto_adjust=True)
            if df.empty or len(df) < 22:
                continue

            df = cm_williams_vix_fix(df)
            if df['vixfix_green'].iloc[-1]:
                current_price = get_current_price(symbol)
                results.append({
                    "symbol": symbol,
                    "index": index,
                    "price": current_price
                })
        except Exception as e:
            continue

    os.makedirs("static", exist_ok=True)
    with open("static/results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    analyze()
