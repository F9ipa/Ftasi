import streamlit as st
import requests
import pandas as pd
import time

# 1. إعدادات الصفحة واللغة
st.set_page_config(page_title="TASI Radar Pro", layout="wide")
st.markdown("""<style> .main { text-align: right; direction: rtl; } </style>""", unsafe_allow_html=True)

st.title("🚀 رادار السوق السعودي الاحترافي")
st.write("فحص فني شامل لجميع شركات تاسي - الفاصل اليومي")

def get_market_data():
    # الرابط الرسمي للمحرك (تجنب روابط الصفحات العادية)
    url = "https://scanner.tradingview.com/saudi/scan"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    
    # الطلب الفني الدقيق
    payload = {
        "filter": [{"left": "type", "operation": "in_range", "right": ["stock", "dr", "fund"]}],
        "options": {"lang": "ar"},
        "markets": ["saudi"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name", "description", "close", "change", "RSI", "EMA20", "EMA50", "volume"],
        "sort": {"sortBy": "change", "sortOrder": "desc"},
        "range": [0, 250]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        response.raise_for_status() # سيكشف أي خطأ 404 أو 403 فوراً
        return response.json()
    except Exception as e:
        st.error(f"⚠️ فشل الاتصال: تأكد من الرابط أو الشبكة. (التفاصيل: {e})")
        return None

# 2. واجهة المستخدم والتفاعل
if st.button('إطلاق الرادار ⚡'):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # عداد احترافي
    for i in range(1, 101):
        if i == 40:
            json_data = get_market_data()
        
        progress_bar.progress(i)
        status_text.text(f"جاري المسح الذكي... {i}%")
        time.sleep(0.01)

    if json_data and 'data' in json_data:
        # معالجة البيانات وتحويلها لجدول
        rows = []
        for item in json_data['data']:
            d = item['d']
            rows.append({
                "الرمز": item['s'].split(':')[1],
                "الشركة": d[1],
                "السعر": d[2],
                "تغيير %": round(d[3], 2),
                "RSI": round(d[4], 2) if d[4] else 0,
                "الاتجاه": "🟢 صاعد" if d[2] > d[5] else "🔴 هابط",
                "EMA20": d[5],
                "السيولة": f"{d[7]:,.0f}"
            })
        
        df = pd.DataFrame(rows)
        
        # عرض النتائج بصورة منظمة
        st.success(f"✅ تم تحليل {len(df)} شركة بنجاح")
        
        # إضافة فلتر سريع داخل الويب
        positive_only = st.checkbox("إظهار الشركات الإيجابية فقط (فوق EMA20)")
        if positive_only:
            df = df[df['الاتجاه'] == "🟢 صاعد"]
            
        st.dataframe(df.style.background_gradient(subset=['RSI'], cmap='RdYlGn_r'), use_container_width=True)
