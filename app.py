import os
from flask import Flask, render_template
import yfinance as yf
import pandas_ta as ta

app = Flask(__name__)

# قائمة الأسهم - يمكنك زيادتها لـ 200 (لاحظ إضافة .SR للسوق السعودي)
SYMBOLS = ["2222.SR", "1120.SR", "7010.SR", "1150.SR", "4030.SR", "AAPL", "NVDA", "TSLA"]

def get_wavetrend_signals(symbol, interval):
    try:
        # جلب البيانات
        period = "2y" if interval == "1mo" else "1y"
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        
        if df.empty or len(df) < 30:
            return False, 0
        
        # معادلة WaveTrend
        ap = (df['High'] + df['Low'] + df['Close']) / 3
        esa = ta.ema(ap, length=10)
        d = ta.ema(abs(ap - esa), length=10)
        ci = (ap - esa) / (0.015 * d)
        wt1 = ta.ema(ci, length=21)
        wt2 = ta.sma(wt1, length=4)
        
        # الشروط: تقاطع إيجابي أو استمرار الإيجابية فوق خط الـ 0
        last_wt1 = wt1.iloc[-1]
        last_wt2 = wt2.iloc[-1]
        prev_wt1 = wt1.iloc[-2]
        prev_wt2 = wt2.iloc[-2]
        
        # شرط التقاطع (Cross Up)
        is_crossing = prev_wt1 <= prev_wt2 and last_wt1 > last_wt2
        # أو شرط الإيجابية العامة (أن يكون الأخضر فوق الأحمر)
        is_bullish = last_wt1 > last_wt2
        
        return is_bullish, round(float(df['Close'].iloc[-1]), 2)
    except:
        return False, 0

@app.route('/')
def index():
    results = []
    for sym in SYMBOLS:
        w_status, price = get_wavetrend_signals(sym, "1wk")
        m_status, _ = get_wavetrend_signals(sym, "1mo")
        
        # إذا كان السهم إيجابي على أي من الفريمين يظهر في القائمة
        if w_status or m_status:
            results.append({
                "symbol": sym,
                "price": price,
                "weekly": "إيجابي ✅" if w_status else "انتظار",
                "monthly": "إيجابي ✅" if m_status else "انتظار"
            })
    return render_template('index.html', stocks=results)

if __name__ == "__main__":
    # Render يتطلب الاستماع على المنفذ المخصص عبر البيئة
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
