import pandas as pd
import yfinance as yf
from flask import Flask, render_template
import os

app = Flask(__name__)

# دالة حساب مؤشر WaveTrend بناءً على معادلة LazyBear
def calculate_wavetrend(df, n1=10, n2=21):
    # hlc3 هو متوسط (الأعلى + الأدنى + الإغلاق)
    ap = (df['High'] + df['Low'] + df['Close']) / 3
    
    # حساب EMA للأسعار (esa)
    esa = ap.ewm(span=n1, adjust=False).mean()
    
    # حساب EMA للانحراف المطلق (d)
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    
    # حساب معامل القناة (ci)
    ci = (ap - esa) / (0.015 * d)
    
    # الخط الأخضر (wt1) هو EMA للـ ci
    wt1 = ci.ewm(span=n2, adjust=False).mean()
    
    # الخط الأحمر (wt2) هو SMA لـ wt1 بطول 4
    wt2 = wt1.rolling(window=4).mean()
    
    return wt1, wt2

def get_signals():
    # التأكد من وجود ملف الرموز أو إنشاء واحد افتراضي للتجربة
    if not os.path.exists('symbols.txt'):
        with open('symbols.txt', 'w') as f:
            f.write("6040.SR\n1120.SR\n2222.SR") # أمثلة: تبوك، الراجحي، أرامكو

    with open('symbols.txt', 'r') as f:
        symbols = [line.strip() for line in f.readlines() if line.strip()]
    
    results = []
    for symbol in symbols:
        try:
            # جلب بيانات آخر 30 يوم بفواصل يومية
            data = yf.download(symbol, period="1mo", interval="1d", progress=False)
            if data.empty or len(data) < 25: 
                continue
            
            wt1, wt2 = calculate_wavetrend(data)
            
            # الحصول على آخر قيمتين لتحديد التقاطع
            curr_wt1 = float(wt1.iloc[-1])
            curr_wt2 = float(wt2.iloc[-1])
            prev_wt1 = float(wt1.iloc[-2])
            prev_wt2 = float(wt2.iloc[-2])

            # منطق الإشارات (النقاط السوداء في TradingView)
            signal = "انتظار"
            color = "black"
            
            if prev_wt1 <= prev_wt2 and curr_wt1 > curr_wt2:
                signal = "دخول (تقاطع إيجابي)"
                color = "green"
            elif prev_wt1 >= prev_wt2 and curr_wt1 < curr_wt2:
                signal = "خروج (تقاطع سلبي)"
                color = "red"

            results.append({
                'symbol': symbol,
                'wt1': round(curr_wt1, 2),
                'wt2': round(curr_wt2, 2),
                'signal': signal,
                'color': color
            })
        except Exception as e:
            print(f"خطأ في السهم {symbol}: {e}")
            
    return results

@app.route('/')
def index():
    stocks_data = get_signals()
    return render_template('index.html', stocks=stocks_data)

if __name__ == "__main__":
    # استخدام المنفذ الذي يحدده Render أو 5000 محلياً
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
