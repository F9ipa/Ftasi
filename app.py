import yfinance as yf
import pandas as pd
import pandas_ta as ta
from flask import Flask, render_template, request

app = Flask(__name__)

# دالة حساب WaveTrend
def get_wavetrend(df):
    if len(df) < 40: return pd.Series(), pd.Series()
    # معادلة hlc3
    ap = (df['High'] + df['Low'] + df['Close']) / 3
    # قناة الـ EMA
    esa = ta.ema(ap, length=10)
    d = ta.ema(abs(ap - esa), length=10)
    ci = (ap - esa) / (0.015 * d)
    wt1 = ta.ema(ci, length=21)
    wt2 = ta.sma(wt1, length=4)
    return wt1, wt2

def check_signals(interval):
    # قائمة تجريبية لبعض الشركات القيادية (يمكنك زيادتها)
    # ملاحظة: فحص كل السوق (200+ سهم) على Render المجاني قد يستغرق وقتاً
    tickers = ["2222.SR", "1120.SR", "1150.SR", "2010.SR", "7010.SR", "4030.SR", "1180.SR"] 
    
    pos_signals = []
    neg_signals = []
    
    for t in tickers:
        try:
            data = yf.download(t, period="2y", interval=interval, progress=False)
            wt1, wt2 = get_wavetrend(data)
            
            if wt1.empty or wt2.empty: continue
            
            # فحص التقاطع في آخر شمعتين
            current_wt1 = wt1.iloc[-1]
            current_wt2 = wt2.iloc[-1]
            prev_wt1 = wt1.iloc[-2]
            prev_wt2 = wt2.iloc[-2]
            
            # تقاطع إيجابي (wt1 يخترق wt2 للأعلى)
            if prev_wt1 <= prev_wt2 and current_wt1 > current_wt2:
                pos_signals.append(t.replace(".SR", ""))
            # تقاطع سلبي (wt1 يكسر wt2 للأسفل)
            elif prev_wt1 >= prev_wt2 and current_wt1 < current_wt2:
                neg_signals.append(t.replace(".SR", ""))
        except:
            continue
    return pos_signals, neg_signals

@app.route('/')
def index():
    # الفاصل الافتراضي "يومي"
    interval = request.args.get('interval', '1d')
    pos, neg = check_signals(interval)
    return render_template('index.html', pos=pos, neg=neg, interval=interval)

if __name__ == "__main__":
    app.run()
