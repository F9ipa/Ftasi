from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import plotly.utils

app = Flask(__name__)

def get_stock_data(symbol, period="1y", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval)
    if df.empty:
        return None, None
    
    # حساب مستويات فيبوناتشي
    max_p = df['High'].max()
    min_p = df['Low'].min()
    diff = max_p - min_p
    fib_levels = {
        "0%": round(max_p, 2),
        "23.6%": round(max_p - 0.236 * diff, 2),
        "38.2%": round(max_p - 0.382 * diff, 2),
        "50%": round(max_p - 0.5 * diff, 2),
        "61.8%": round(max_p - 0.618 * diff, 2),
        "100%": round(min_p, 2)
    }
    
    # استراتيجية السيولة المبسطة (MFI logic)
    df['Price_Chg'] = df['Close'].diff()
    df['Flow'] = df['Price_Chg'] * df['Volume']
    current_flow = "إيجابية" if df['Flow'].iloc[-1] > 0 else "سلبية"
    
    return df, fib_levels, current_flow

@app.route('/', methods=['GET', 'POST'])
def index():
    symbol = request.form.get('symbol', '2222') # أرامكو كافتراضي
    tasi_symbol = "^TASI"
    
    # جلب بيانات السهم المختار
    df, fib, flow_status = get_stock_data(f"{symbol}.SR")
    
    # جلب أسعار السلع والمؤشرات العالمية
    tickers = {
        "TASI": "^TASI",
        "الذهب": "GC=F",
        "برنت": "BZ=F",
        "النفط": "CL=F",
        "الفضة": "SI=F"
    }
    globals_data = {}
    for name, t in tickers.items():
        val = yf.Ticker(t).history(period="1d")['Close']
        globals_data[name] = round(val.iloc[-1], 2) if not val.empty else "N/A"

    # إنشاء الرسم البياني التفاعلي
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graph_json=graph_json, fib=fib, flow=flow_status, globals=globals_data, symbol=symbol)

if __name__ == '__main__':
    app.run(debug=True)
