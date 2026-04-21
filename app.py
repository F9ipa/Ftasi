import os
from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

# قائمة الأسهم المختارة - تأكد من صحة الرموز
WATCHLIST = ["6040", "2222", "1120", "1150", "2010", "2280", "4030"]

def calculate_wavetrend(df, n1=10, n2=21):
    try:
        # حساب hlc3
        ap = (df['High'] + df['Low'] + df['Close']) / 3
        # حساب متوسط القناة
        esa = ap.ewm(span=n1, adjust=False).mean()
        # حساب الانحراف المتوسط
        d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
        # حساب مؤشر القناة
        ci = (ap - esa) / (0.015 * d)
        # حساب الموجات (WaveTrend)
        wt1 = ci.ewm(span=n2, adjust=False).mean()
        wt2 = wt1.rolling(window=4).mean()
        return wt1, wt2
    except Exception:
        return pd.Series(), pd.Series()

def analyze_market():
    results = []
    for symbol in WATCHLIST:
        try:
            ticker = f"{symbol}.SR"
            df = yf.download(ticker, period="60d", interval="1d", progress=False)
            
            if df.empty or len(df) < 30:
                continue

            wt1_series, wt2_series = calculate_wavetrend(df)
            if wt1_series.empty: continue

            last_wt1 = round(float(wt1_series.iloc[-1]), 2)
            last_wt2 = round(float(wt2_series.iloc[-1]), 2)
            prev_wt1 = wt1_series.iloc[-2]
            prev_wt2 = wt2_series.iloc[-2]

            bullish_cross = (prev_wt1 < prev_wt2) and (last_wt1 > last_wt2)
            bearish_cross = (prev_wt1 > prev_wt2) and (last_wt1 < last_wt2)

            decision = "انتظار"
            color = "secondary"
            logic = "استمرار الحركة"

            if bullish_cross and last_wt1 < -53:
                decision = "دخول ذهبي"
                color = "success"
                logic = f"تقاطع صاعد من قاع ({last_wt1})"
            elif last_wt1 < -60:
                decision = "منطقة ارتداد"
                color = "info"
                logic = "تشبع بيعي حاد"
            elif bearish_cross and last_wt1 > 53:
                decision = "جني ربح"
                color = "danger"
                logic = f"تقاطع هابط من قمة ({last_wt1})"
            elif last_wt1 > 60:
                decision = "تضخم"
                color = "warning"
                logic = "تشبع شرائي - حذر"

            results.append({
                "symbol": symbol,
                "price": round(float(df['Close'].iloc[-1]), 2),
                "wt1": last_wt1,
                "decision": decision,
                "color": color,
                "logic": logic
            })
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            continue
    return results

@app.route('/')
def index():
    try:
        # جلب البيانات العالمية بحذر لتجنب تعليق الصفحة
        commodities = {}
        world_tickers = {"برنت": "BZ=F", "الذهب": "GC=F", "تاسي": "^TASI"}
        for name, sym in world_tickers.items():
            try:
                t_info = yf.Ticker(sym).history(period="1d")
                if not t_info.empty:
                    commodities[name] = round(t_info['Close'].iloc[-1], 2)
                else:
                    commodities[name] = "---"
            except:
                commodities[name] = "خطأ"
        
        market_data = analyze_market()
        return render_template('index.html', results=market_data, commodities=commodities)
    except Exception as e:
        return f"خطأ في النظام: {str(e)}"

if __name__ == '__main__':
    # استخدام بورت متغير ليتوافق مع Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
