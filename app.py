import streamlit as st
import yfinance as ticker  # لسحب بيانات السوق السعودي
import pandas as pd

st.set_page_config(page_title="TASI Dashboard", layout="wide")

st.title("📊 لوحة متابعة السوق السعودي (TASI)")

# إدخال رمز السهم (مثلاً 1120 للراجحي)
stock_symbol = st.sidebar.text_input("أدخل رمز السهم (مثال: 1120)", "2222")
full_symbol = f"{stock_symbol}.SR"

# جلب البيانات
data = ticker.download(full_symbol, period="1mo", interval="1d")

if not data.empty:
    st.subheader(f"أداء السهم {stock_symbol} خلال الشهر الماضي")
    st.line_chart(data['Close'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("آخر سعر إغلاق", f"{data['Close'][-1]:.2f} ريال")
    with col2:
        change = data['Close'][-1] - data['Close'][0]
        st.metric("التغير الشهري", f"{change:.2f} ريال", delta=f"{change:.2f}")
else:
    st.error("لم يتم العثور على بيانات، تأكد من رمز السهم.")
