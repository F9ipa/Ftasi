def get_signals():
    # رموز احتياطية تظهر دائماً حتى لو فشل قراءة الملف
    symbols = ["2222.SR", "1120.SR", "6040.SR", "^TASI"]
    
    try:
        # تحديد المسار بشكل دقيق
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, 'symbols.txt')
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                # قراءة الملف وتنظيف الرموز من أي فراغات
                file_symbols = [line.strip() for line in f.readlines() if line.strip()]
                if file_symbols:
                    symbols = file_symbols
    except Exception as e:
        print(f"Error reading symbols.txt: {e}")

    results = []
    for symbol in symbols:
        try:
            # جلب البيانات (أسبوعي)
            data = yf.download(symbol, period="2y", interval="1wk", progress=False, timeout=15)
            
            if data is None or data.empty or len(data) < 20:
                continue

            ha_data = get_heikin_ashi(data)
            wt1, wt2 = calculate_wavetrend(ha_data)
            
            c_wt1, c_wt2 = float(wt1.iloc[-1]), float(wt2.iloc[-1])
            p_wt1, p_wt2 = float(wt1.iloc[-2]), float(wt2.iloc[-2])

            signal, color = "انتظار", "#95a5a6"
            if p_wt1 <= p_wt2 and c_wt1 > c_wt2:
                signal, color = "#089981" # أخضر تريدنج فيو
            elif p_wt1 >= p_wt2 and c_wt1 < c_wt2:
                signal, color = "#f23645" # أحمر تريدنج فيو

            results.append({
                'symbol': symbol, 
                'wt1': round(c_wt1, 2), 
                'wt2': round(c_wt2, 2), 
                'signal': "إيجابي" if "089981" in color else "سلبي" if "f23645" in color else "انتظار", 
                'color': color
            })
        except:
            continue
            
    return results
