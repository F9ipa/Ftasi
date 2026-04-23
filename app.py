import requests
import json

def run_tasi_radar():
    url = "https://scanner.tradingview.com/ksa/scan?label-product=screener-stock"
    
    # إعداد "الطلب" لفلترة التقاطع مباشرة من خوادم TradingView
    payload = {
        "columns": ["logoid", "name", "close", "change", "SMA20", "SMA50", "description"],
        "filter": [
            {
                "left": "SMA20",
                "operation": "greater",
                "right": "SMA50"
            }
        ],
        "ignore_unknown_fields": False,
        "markets": ["ksa"],
        "options": {"lang": "ar"},
        "range": [0, 150], # يجلب أول 150 شركة تنطبق عليها الاستراتيجية
        "sort": {
            "sortBy": "change",
            "sortOrder": "desc"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        stocks = data.get('data', [])
        
        print(f"--- رادار الأسهم السعودية (تقاطع 20/50) ---")
        print(f"تم العثور على {len(stocks)} شركة تنطبق عليها الاستراتيجية:\n")
        
        for item in stocks:
            # d[1] = الاسم، d[2] = الإغلاق، d[4] = متوسط 20، d[5] = متوسط 50
            name = item['d'][1]
            description = item['d'][6]
            close = item['d'][2]
            sma20 = item['d'][4]
            sma50 = item['d'][5]
            
            print(f"الشركة: {description} ({name})")
            print(f"   الإغلاق: {close}")
            print(f"   SMA20: {sma20:.2f} | SMA50: {sma50:.2f}")
            print("-" * 30)
            
    except Exception as e:
        print(f"حدث خطأ أثناء جلب البيانات: {e}")

if __name__ == "__main__":
    run_tasi_radar()
