import pandas as pd
import numpy as np

def calculate_wavetrend(df, n1=10, n2=21):
    # ap = hlc3 (Average Price)
    ap = (df['high'] + df['low'] + df['close']) / 3
    
    # esa = ema(ap, n1)
    esa = ap.ewm(span=n1, adjust=False).mean()
    
    # d = ema(abs(ap - esa), n1)
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    
    # ci = (ap - esa) / (0.015 * d)
    ci = (ap - esa) / (0.015 * d)
    
    # wt1 = tci = ema(ci, n2)
    wt1 = ci.ewm(span=n2, adjust=False).mean()
    
    # wt2 = sma(wt1, 4)
    wt2 = wt1.rolling(window=4).mean()
    
    return wt1, wt2
