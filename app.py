import os
import time
from flask import Flask, render_template, jsonify
import yfinance as yf

app = Flask(__name__)

# مخزن مؤقت لضمان سرعة الاستجابة
data_store = {'stocks': [], 'last_update': 0}

def load_tasi_symbols():
    try:
        path = os.path.join(os.path.dirname(__file__), 'tasi.txt')
        with open(path, 'r') as f:
            return [f"{line.strip()}.SR" for line in f if line.strip()]
    except:
        return ["2222.SR", "1120.SR"]

@app.route('/api/data')
def get_stock_data():
    global data_store
    # إذا تم التحديث قبل أقل من 5 دقائق، ارجع البيانات المخزنة فوراً
    if data_store['stocks'] and (time.time() - data_store['last_update'] < 300):
        return jsonify(data_store['stocks'])

    symbols = load_tasi_symbols()
    try:
        # جلب جماعي سريع جداً
        df = yf.download(' '.join(symbols), period="1d", interval="1m", group_by='ticker', threads=True, progress=False)
        
        updated_list = []
        for sym in symbols:
            try:
                if sym in df and not df[sym].empty:
                    last_price = float(df[sym]['Close'].iloc[-1])
                    open_price = float(df[sym]['Open'].iloc[0])
                    change = last_price - open_price
                    updated_list.append({
                        's': sym.replace('.SR', ''),
                        'p': round(last_price, 2),
                        'c': round(change, 2),
                        'pc': round((change/open_price)*100, 2)
                    })
            except: continue
        
        if updated_list:
            data_store['stocks'] = sorted(updated_list, key=lambda x: x['pc'], reverse=True)
            data_store['last_update'] = time.time()
            
        return jsonify(data_store['stocks'])
    except Exception as e:
        return jsonify(data_store['stocks']) # ارجع آخر بيانات ناجحة في حال الفشل

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
