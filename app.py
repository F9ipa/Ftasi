import requests
from flask import Flask, render_template_string
import os

app = Flask(__name__)

def get_tasi_data():
    url = "https://scanner.tradingview.com/ksa/scan?label-product=screener-stock"
    payload = {
        "columns": ["name", "description", "close", "change", "SMA20", "SMA50", "volume"],
        "filter": [
            {"left": "SMA20", "operation": "greater", "right": "SMA50"},
            {"left": "type", "operation": "equal", "right": "stock"}
        ],
        "markets": ["ksa"],
        "options": {"lang": "ar"},
        "range": [0, 100],
        "sort": {"sortBy": "change", "sortOrder": "desc"}
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json().get('data', [])
    except:
        return []

# قالب الصفحة (HTML + CSS للـ Dark Mode)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رادار الأسهم السعودية</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --accent-color: #38bdf8;
            --success-color: #22c55e;
            --border-color: #334155;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 900px; margin: auto; }
        header { 
            text-align: center; 
            padding: 20px 0;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 30px;
        }
        h1 { color: var(--accent-color); margin: 0; font-size: 1.5rem; }
        .stats { font-size: 0.9rem; color: #94a3b8; margin-top: 10px; }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }
        th, td {
            padding: 15px;
            text-align: right;
            border-bottom: 1px solid var(--border-color);
        }
        th { background-color: #334155; color: var(--accent-color); font-weight: 600; }
        tr:hover { background-color: #2d3748; }
        
        .badge {
            background: #064e3b;
            color: #4ade80;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .price { font-weight: bold; color: #f1f5f9; }
        .change-pos { color: var(--success-color); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 رادار الأسهم السعودية (TASI)</h1>
            <p class="stats">استراتيجية تقاطع المتوسطات: SMA20 > SMA50</p>
        </header>
        
        <table>
            <thead>
                <tr>
                    <th>الشركة</th>
                    <th>الرمز</th>
                    <th>السعر</th>
                    <th>التغيير</th>
                    <th>الحالة</th>
                </tr>
            </thead>
            <tbody>
                {% for row in stocks %}
                <tr>
                    <td>{{ row['d'][1] }}</td>
                    <td><span style="color: #94a3b8;">{{ row['d'][0] }}</span></td>
                    <td class="price">{{ row['d'][2] }}</td>
                    <td class="change-pos">{{ "%.2f"|format(row['d'][3]) }}%</td>
                    <td><span class="badge">تقاطع إيجابي</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <footer style="text-align:center; margin-top:30px; color:#64748b; font-size:0.8rem;">
            يتم التحديث تلقائياً عند إعادة تحميل الصفحة
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    stocks = get_tasi_data()
    return render_template_string(HTML_TEMPLATE, stocks=stocks)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
