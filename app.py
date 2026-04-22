import pandas as pd
import yfinance as yf
import pandas_ta as ta
from flask import Flask, render_template
import os

app = Flask(__name__)

def calculate_wavetrend(df, n1=10, n2=21):
    # حساب hlc3
    ap = (df['High'] + df['Low'] + df['Close']) / 3
    esa = ta.ema(ap, length=n1)
    d = ta.ema(abs(ap - esa), length=n1)
    ci = (ap - esa) / (0.015 * d)
    wt1 = ta.ema(ci, length=n2)
    wt2 = ta.sma(wt1, length=4)
    return wt1, wt2

def get_signals():
    # قراءة الرموز من الملف
    with open('symbols.txt', 'r') as f:
        symbols = [line.strip() for line in f.readlines()]
    
    results = []
    for symbol in symbols:
        try:
            data = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if data.empty: continue
            
            wt1, wt2 = calculate_wavetrend(data)
            
            last_wt1 = wt1.iloc[-1]
            last_wt2 = wt2.iloc[-1]
            prev_wt1 = wt1.iloc[-2]
            prev_wt2 = wt2.iloc[-2]

            # تحديد حالة التقاطع
            signal = "None"
            if prev_wt1 <= prev_wt2 and last_wt1 > last_wt2:
                signal = "Buy (Green Dot)"
            elif prev_wt1 >= prev_wt2 and last_wt1 < last_wt2:
                signal = "Sell (Red Dot)"

            results.append({
                'symbol': symbol,
                'wt1': round(last_wt1, 2),
                'wt2': round(last_wt2, 2),
                'signal': signal
            })
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            
    return results

@app.route('/')
def index():
    stocks = get_signals()
    return render_template('index.html', stocks=stocks)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
