import streamlit as st
import requests
import pandas as pd
import time

def fetch_data_safe():
    # الرابط الدولي للسكرينر
    url = "https://scanner.tradingview.com/saudi/scan"
    
    # Headers احترافية وشاملة لتجنب حظر سيرفرات Render
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Origin": "https://www.tradingview.com",
        "Referer": "https://www.tradingview.com/"
    }
    
    payload = {
        "filter": [{"left": "type", "operation": "in_range", "right": ["stock", "dr", "fund"]}],
        "markets": ["saudi"],
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name", "description", "close", "change", "RSI", "EMA20"],
        "sort": {"sortBy": "change", "sortOrder": "desc"},
        "range": [0, 150]
    }

    try:
        # زيادة timeout لـ 30 ثانية لأن سيرفرات Render المجانية قد تكون بطيئة في الاتصال
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # إذا أعاد السيرفر خطأ 403 (حظر) أو غيره
        if response.status_code != 200:
            st.error(f"رفض السيرفر الطلب (Error {response.status_code}). جرب تحديث الصفحة بعد قليل.")
            return None
            
        return response.json()
    except requests.exceptions.Timeout:
        st.error("انتهى وقت المحاولة (Timeout). السيرفر استغرق وقتاً طويلاً للرد.")
    except Exception as e:
        st.error(f"حدث خطأ غير متوقع: {e}")
    return None

# --- بقية كود Streamlit (الواجهة والعداد) ---
