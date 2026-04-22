import os
import requests
from flask import Flask, render_template

app = Flask(__name__)

# الرابط الرسمي المباشر لبيانات شركات السوق الرئيسية
TADAWUL_URL = "https://www.saudiexchange.sa.sa/wps/portal/saudiexchange/ourmarkets/main-market-watch/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zi_TxNDDwN3A183B39DA0cPZ29PN1C_I0MDQz0w8EKDHAARwP9KGL041EQhd_4cP0oVCv8vY3MfE0NAl3dDRzd3czNdYP0Y_Sj8BtREB6aX5CRmZueH6UfVpSZXFpS7K_p55GcnpOfm5pXkllclpOfp5-fV1QCACv9R_E!/p0/IZ7_5PFC1PS0G0HT90A6A3866T30G1=CZ6_5PFC1PS0G0HT90A6A3866T30G4=NJlistCompanies=/"

def get_tasi_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.saudiexchange.sa.sa/"
    }
    try:
        response = requests.get(TADAWUL_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get('recs', [])
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

@app.route('/')
def index():
    stocks = get_tasi_data()
    return render_template('index.html', stocks=stocks)

if __name__ == "__main__":
    # Render يمرر المنفذ عبر متغير بيئة يسمى PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
