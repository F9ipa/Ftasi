import requests
from flask import Flask
import os

app = Flask(__name__)

def run_tasi_radar():
    url = "https://scanner.tradingview.com/ksa/scan?label-product=screener-stock"
    payload = {
        "columns": ["name", "description", "close", "SMA20", "SMA50"],
        "filter": [
            {"left": "SMA20", "operation": "greater", "right": "SMA50"}
        ],
        "markets": ["ksa"],
        "range": [0, 50]
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        results = []
        for row in data.get('data', []):
            results.append(f"✅ {row['d'][1]} ({row['d'][0]}) - السعر: {row['d'][2]}")
        return results
    except Exception as e:
        return [f"Error: {str(e)}"]

@app.route('/')
def index():
    stocks = run_tasi_radar()
    return "<br>".join(stocks) if stocks else "لا توجد أسهم تطابق الاستراتيجية حالياً."

if __name__ == "__main__":
    # هذا السطر يخبر Render أن السيرفر جاهز للاستخدام
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
