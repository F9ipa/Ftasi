import yfinance as yf
import pandas as pd
import pandas_ta as ta
from flask import Flask, render_template

app = Flask(__name__)

# قائمة ببعض أسهم السوق السعودي (يمكنك توسيع القائمة)
SYMBOLS = ["2222.SR", "1120.SR", "1150.SR", "2010.SR", "7010.SR"] # أرامكو، الراجحي، الإنماء، سابك، STC

def calculate_wavetrend(df, n1=10, n2=21):
    ap = (df['High'] + df['Low'] + df['Close']) / 3
    esa = ta.ema(ap, length=n1)
    d = ta.ema(abs(ap - esa), length=n1)
    ci = (ap - esa) / (0.015 * d)
    wt1 = ta.ema(ci, length=n2)
    wt2 = ta.sma(wt1, length=4)
    return wt1, wt2

def get_signals(interval):
    positive_cross = []
    negative_cross = []
    
    for symbol in SYMBOLS:
        try:
            df = yf.download(symbol, period="1y", interval=interval)
            if len(df) < 30: continue
            
            wt1, wt2 = calculate_wavetrend(df)
            
            # فحص التقاطع في آخر شمعة
            if wt1.iloc[-2] <= wt2.iloc[-2] and wt1.iloc[-1] > wt2.iloc[-1]:
                positive_cross.append(symbol)
            elif wt1.iloc[-2] >= wt2.iloc[-2] and wt1.iloc[-1] < wt2.iloc[-1]:
                negative_cross.append(symbol)
        except:
            continue
            
    return positive_cross, negative_cross

@app.route('/')
def index():
    # هنا نقوم بالفحص للفواصل المختلفة (تبسيطاً سنعرض اليومي)
    # يمكنك تكرار العملية للفواصل: 1mo, 1wk, 1d, 4h
    pos, neg = get_signals("1d")
    return render_template('index.html', pos=pos, neg=neg)

if __name__ == "__main__":
    app.run(debug=True)
