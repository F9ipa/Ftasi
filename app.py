import os
import requests
from flask import Flask, render_template

app = Flask(__name__)

def get_tasi_data():
    # الرابط الأساسي لفتح الجلسة
    base_url = "https://www.saudiexchange.sa.sa/wps/portal/saudiexchange/ourmarkets/main-market-watch?locale=ar"
    # رابط البيانات (API)
    api_url = "https://www.saudiexchange.sa.sa/wps/portal/saudiexchange/ourmarkets/main-market-watch/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zi_TxNDDwN3A183B39DA0cPZ29PN1C_I0MDQz0w8EKDHAARwP9KGL041EQhd_4cP0oVCv8vY3MfE0NAl3dDRzd3czNdYP0Y_Sj8BtREB6aX5CRmZueH6UfVpSZXFpS7K_p55GcnpOfm5pXkllclpOfp5-fV1QCACv9R_E!/p0/IZ7_5PFC1PS0G0HT90A6A3866T30G1=CZ6_5PFC1PS0G0HT90A6A3866T30G4=NJlistCompanies=/"

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
        "Referer": base_url
    }

    try:
        session = requests.Session()
        # الخطوة 1: زيارة الصفحة الرئيسية للحصول على الكوكيز
        session.get(base_url, headers=headers, timeout=15)
        
        # الخطوة 2: طلب البيانات باستخدام نفس الجلسة
        response = session.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        stocks = data.get('recs', [])
        print(f"تم جلب {len(stocks)} شركة بنجاح")
        return stocks
    except Exception as e:
        print(f"فشل جلب البيانات: {e}")
        return []

@app.route('/')
def index():
    stocks = get_tasi_data()
    return render_template('index.html', stocks=stocks)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
