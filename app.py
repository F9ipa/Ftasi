import yfinance as yf
import pandas as pd
from flask import Flask, render_template_string, request
import os
import concurrent.futures

app = Flask(__name__)

# القائمة الكاملة لجميع رموز تاسي (TASI)
ALL_TASI = [
    '1010.SR', '1020.SR', '1030.SR', '1050.SR', '1060.SR', '1080.SR', '1111.SR', '1120.SR', '1140.SR', '1150.SR',
    '1180.SR', '1182.SR', '1183.SR', '1201.SR', '1202.SR', '1210.SR', '1211.SR', '1212.SR', '1213.SR', '1214.SR',
    '1301.SR', '1304.SR', '1320.SR', '1321.SR', '1322.SR', '1810.SR', '1830.SR', '1831.SR', '1832.SR', '1833.SR',
    '2001.SR', '2002.SR', '2010.SR', '2020.SR', '2030.SR', '2040.SR', '2050.SR', '2060.SR', '2070.SR', '2080.SR',
    '2081.SR', '2082.SR', '2083.SR', '2090.SR', '2100.SR', '2110.SR', '2120.SR', '2130.SR', '2140.SR', '2150.SR',
    '2160.SR', '2170.SR', '2180.SR', '2190.SR', '2200.SR', '2210.SR', '2220.SR', '2222.SR', '2223.SR', '2230.SR',
    '2240.SR', '2250.SR', '2270.SR', '2280.SR', '2281.SR', '2282.SR', '2283.SR', '2290.SR', '2300.SR', '2310.SR',
    '2320.SR', '2330.SR', '2340.SR', '2350.SR', '2360.SR', '2370.SR', '2380.SR', '2381.SR', '2382.SR', '3001.SR',
    '3002.SR', '3003.SR', '3004.SR', '3005.SR', '3007.SR', '3008.SR', '3010.SR', '3020.SR', '3030.SR', '3040.SR',
    '3050.SR', '3060.SR', '3080.SR', '3090.SR', '3091.SR', '4001.SR', '4002.SR', '4003.SR', '4004.SR', '4005.SR',
    '4006.SR', '4007.SR', '4008.SR', '4009.SR', '4010.SR', '4011.SR', '4012.SR', '4013.SR', '4014.SR', '4015.SR',
    '4020.SR', '4030.SR', '4031.SR', '4040.SR', '4050.SR', '4061.SR', '4071.SR', '4072.SR', '4080.SR', '4081.SR',
    '4082.SR', '4090.SR', '4100.SR', '4110.SR', '4130.SR', '4140.SR', '4141.SR', '4142.SR', '4150.SR', '4160.SR',
    '4161.SR', '4162.SR', '4163.SR', '4164.SR', '4170.SR', '4180.SR', '4190.SR', '4191.SR', '4192.SR', '4200.SR',
    '4210.SR', '4220.SR', '4230.SR', '4240.SR', '4250.SR', '4260.SR', '4270.SR', '4280.SR', '4290.SR', '4291.SR',
    '4292.SR', '4300.SR', '4310.SR', '4320.SR', '4321.SR', '4322.SR', '4323.SR', '4330.SR', '4331.SR', '4332.SR',
    '4333.SR', '4335.SR', '4336.SR', '4340.SR', '4342.SR', '4344.SR', '4345.SR', '4346.SR', '4347.SR', '4348.SR',
    '6001.SR', '6002.SR', '6004.SR', '6010.SR', '6011.SR', '6012.SR', '6013.SR', '6014.SR', '6015.SR', '6020.SR',
    '6040.SR', '6050.SR', '6060.SR', '6070.SR', '6090.SR', '7010.SR', '7020.SR', '7030.SR', '7040.SR', '7201.SR',
    '7202.SR', '7203.SR', '7204.SR', '8010.SR', '8012.SR', '8020.SR', '8030.SR', '8040.SR', '8050.SR', '8060.SR',
    '8070.SR', '8100.SR', '8120.SR', '8150.SR', '8160.SR', '8170.SR', '8180.SR', '8190.SR', '8200.SR', '8210.SR',
    '8230.SR', '8240.SR', '8250.SR', '8260.SR', '8270.SR', '8280.SR', '8300.SR', '8310.SR', '8311.SR', '8312.SR'
]

# تقسيم القائمة آلياً إلى 4 مجموعات
def chunk_list(lst, n):
    size = len(lst) // n + (len(lst) % n > 0)
    return [lst[i:i + size] for i in range(0, len(lst), size)]

CHUNKS = chunk_list(ALL_TASI, 4)

def calculate_wavetrend(df):
    if len(df) < 30: return None
    hl3 = (df['High'] + df['Low'] + df['Close']) / 3
    esa = hl3.ewm(span=10, adjust=False).mean()
    d = (hl3 - esa).abs().ewm(span=10, adjust=False).mean()
    ci = (hl3 - esa) / (0.015 * d)
    wt1 = ci.ewm(span=21, adjust=False).mean()
    wt2 = wt1.rolling(window=4).mean()
    return wt1, wt2

def get_signal(symbol):
    try:
        df = yf.download(symbol, period="3y", interval="1mo", progress=False)
        if df.empty or len(df) < 5: return None
        res = calculate_wavetrend(df)
        if not res: return None
        wt1, wt2 = res
        curr1, prev1, curr2, prev2 = wt1.iloc[-1], wt1.iloc[-2], wt2.iloc[-1], wt2.iloc[-2]
        
        signal = None
        if prev1 <= prev2 and curr1 > curr2: signal = "دخول 🟢"
        elif prev1 >= prev2 and curr1 < curr2: signal = "خروج 🔴"
        
        if signal:
            price = df['Close'].iloc[-1]
            change = ((price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            return {"name": symbol.replace(".SR",""), "price": f"{price:.2f}", "change": f"{change:.2f}", "signal": signal}
    except: return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رادار تاسي WaveTrend</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --accent: #38bdf8; --text: #f8fafc; --success: #22c55e; --danger: #ef4444; }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 900px; margin: auto; }
        .menu { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 30px 0; }
        .btn { background: var(--card); color: var(--accent); padding: 18px; border: 2px solid var(--accent); border-radius: 12px; text-decoration: none; font-weight: bold; transition: 0.3s; font-size: 1.1rem; }
        .btn:hover { background: var(--accent); color: var(--bg); transform: translateY(-3px); }
        .active { background: var(--accent); color: var(--bg); box-shadow: 0 0 15px var(--accent); }
        table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; margin-top: 20px; }
        th, td { padding: 15px; text-align: center; border-bottom: 1px solid #334155; }
        th { background: #334155; color: var(--accent); }
        .buy-row { background: rgba(34, 197, 94, 0.1); color: var(--success); font-weight: bold; }
        .sell-row { background: rgba(239, 68, 68, 0.1); color: var(--danger); font-weight: bold; }
        .loading { color: var(--accent); font-style: italic; margin: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 رادار السوق السعودي (WaveTrend)</h1>
        <p style="color: #94a3b8;">اختر مجموعة لفلترة الأسهم على الفاصل الشهري</p>
        
        <div class="menu">
            <a href="/?part=0" class="btn {{ 'active' if part==0 }}">📦 المجموعة 1 (55 سهم)</a>
            <a href="/?part=1" class="btn {{ 'active' if part==1 }}">📦 المجموعة 2 (55 سهم)</a>
            <a href="/?part=2" class="btn {{ 'active' if part==2 }}">📦 المجموعة 3 (55 سهم)</a>
            <a href="/?part=3" class="btn {{ 'active' if part==3 }}">📦 المجموعة 4 (55 سهم)</a>
        </div>

        {% if stocks is not none %}
            <h2>نتائج المجموعة {{ part + 1 }}</h2>
            <table>
                <thead><tr><th>الرمز</th><th>السعر</th><th>تغير الشهر</th><th>الإشارة</th></tr></thead>
                <tbody>
                    {% for s in stocks %}
                    <tr class="{{ 'buy-row' if 'دخول' in s.signal else 'sell-row' }}">
                        <td>{{ s.name }}</td><td>{{ s.price }}</td><td>{{ s.change }}%</td><td>{{ s.signal }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="4" style="padding:40px; color:#64748b;">لا توجد تقاطعات دخول أو خروج في هذه المجموعة حالياً</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    part = request.args.get('part', type=int)
    stocks = None
    if part is not None and 0 <= part < len(CHUNKS):
        # استخدام 20 خيط متوازي للفحص السريع جداً
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(get_signal, CHUNKS[part]))
        stocks = [r for r in results if r is not None]
    return render_template_string(HTML_TEMPLATE, stocks=stocks, part=part)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
