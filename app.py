import yfinance as yf
import pandas as pd
from flask import Flask, render_template, request
import os
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def calculate_wavetrend(df):
    if len(df) < 40: return None, None
    ap = (df['High'] + df['Low'] + df['Close']) / 3
    esa = ap.ewm(span=10, adjust=False).mean()
    d = abs(ap - esa).ewm(span=10, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d)
    wt1 = ci.ewm(span=21, adjust=False).mean()
    wt2 = wt1.rolling(window=4).mean()
    return wt1, wt2

def scan_single_stock(t, interval):
    """وظيفة لفحص سهم واحد فقط، سيتم استدعاؤها بالتوازي"""
    try:
        data = yf.download(t, period="1y", interval=interval, progress=False, threads=False)
        if len(data) < 10: return None
        
        wt1, wt2 = calculate_wavetrend(data)
        if wt1 is None or pd.isna(wt1.iloc[-1]): return None
        
        w1_now, w2_now = wt1.iloc[-1], wt2.iloc[-1]
        w1_prev, w2_prev = wt1.iloc[-2], wt2.iloc[-2]
        
        symbol = t.split('.')[0]
        if w1_prev <= w2_prev and w1_now > w2_now:
            return ('pos', symbol)
        elif w1_prev >= w2_prev and w1_now < w2_now:
            return ('neg', symbol)
    except:
        pass
    return None

def get_all_signals(interval):
    try:
        with open('stocks.txt', 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
    except:
        return [], []

    pos_signals, neg_signals = [], []
    
    # استخدام ThreadPoolExecutor لتشغيل الفحص بالتوازي (15 خيط معالجة)
    with ThreadPoolExecutor(max_workers=15) as executor:
        results = list(executor.map(lambda t: scan_single_stock(t, interval), tickers))
    
    # تصنيف النتائج
    for res in results:
        if res:
            if res[0] == 'pos': pos_signals.append(res[1])
            else: neg_signals.append(res[1])
            
    return pos_signals, neg_signals

@app.route('/')
def index():
    interval = request.args.get('interval', '1d')
    pos, neg = get_all_signals(interval)
    return render_template('index.html', pos=pos, neg=neg, interval=interval)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
