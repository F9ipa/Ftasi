import os, time, threading
from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# مخزن البيانات المطور
data_store = {
    'signals': [], 
    'last_update': 0, 
    'is_loading': False,
    'progress': 0,
    'total_companies': 0  # عدد الشركات الكلي في الملف
}

def load_tasi_symbols():
    try:
        path = os.path.join(os.path.dirname(__file__), 'tasi.txt')
        if not os.path.exists(path):
            return ["2222.SR"] 
        with open(path, 'r') as f:
            lines = [f"{line.strip()}.SR" for line in f if line.strip()]
            data_store['total_companies'] = len(lines) # حفظ العدد الكلي
            return lines
    except: 
        return ["2222.SR"]

def background_scan():
    global data_store
    while True:
        try:
            data_store['is_loading'] = True
            symbols = load_tasi_symbols()
            all_opportunities = []
            
            chunk_size = 40
            for i in range(0, len(symbols), chunk_size):
                chunk = symbols[i:i + chunk_size]
                
                # تحميل البيانات بنظام المجموعات
                df = yf.download(' '.join(chunk), period="100d", interval="1d", group_by='ticker', threads=True, progress=False)
                
                for sym in chunk:
                    try:
                        if isinstance(df.columns, pd.MultiIndex):
                            if sym not in df.columns.levels[0] or df[sym].empty: continue
                            s_data = df[sym].dropna()
                        else:
                            s_data = df.dropna()

                        if len(s_data) < 50: continue

                        close_prices = s_data['Close']
                        sma20 = close_prices.rolling(window=20).mean()
                        sma50 = close_prices.rolling(window=50).mean()
                        
                        last_p = float(close_prices.iloc[-1])
                        curr_20 = float(sma20.iloc[-1])
                        curr_50 = float(sma50.iloc[-1])
                        
                        # استراتيجية التقاطعات
                        if curr_20 > curr_50 and last_p > curr_20:
                            prev_close = float(close_prices.iloc[-2])
                            pc = ((last_p - prev_close) / prev_close) * 100
                            
                            all_opportunities.append({
                                's': sym.replace('.SR', ''),
                                'p': round(last_p, 2),
                                'pc': round(pc, 2)
                            })
                    except: continue
                
                # تحديث تدريجي للنتائج
                data_store['signals'] = sorted(all_opportunities, key=lambda x: x['pc'], reverse=True)
                data_store['last_update'] = time.time()
                data_store['progress'] = i + len(chunk) # عدد الشركات التي تم فحصها حتى الآن

            data_store['is_loading'] = False
        except Exception as e:
            print(f"Error: {e}")
            data_store['is_loading'] = False
        
        time.sleep(600)

threading.Thread(target=background_scan, daemon=True).start()

@app.route('/api/data')
def get_signals():
    return jsonify({
        'stocks': data_store['signals'], 
        'count': len(data_store['signals']),
        'loading': data_store['is_loading'],
        'progress': data_store['progress'],
        'total': data_store['total_companies']
    })

@app.route('/')
def index(): return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
