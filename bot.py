import pandas as pd
import yfinance as yf
import numpy as np
import requests
import time

TOKEN = "8613256232:AAE515o_XgWtMdy9JbTyB0a6FAAeF6ZlDn4"
CHAT_ID = "8541001320"

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Hata: {e}")

def borsa_taramasi_yap():
    hisseler = [
        "THYAO.IS", "TUPRS.IS", "EREGL.IS", "KCHOL.IS", "GARAN.IS", 
        "AKBNK.IS", "ISCTR.IS", "YKBNK.IS", "ASELS.IS", "BIMAS.IS",
        "SAHOL.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", "KRDMD.IS",
        "PGSUS.IS", "TOASO.IS", "FROTO.IS", "ARCLK.IS", "ENKAI.IS",
        "MGROS.IS", "TCELL.IS", "TTKOM.IS", "SISE.IS", 
        "ENJSA.IS", "ODAS.IS", "BERA.IS", "OYAKC.IS", "ASTOR.IS",
        "KONTR.IS", "GESAN.IS", "ALARK.IS", "GUBRF.IS"
    ]
    
    print(f"🔍 Toplam {len(hisseler)} hisse filtreleniyor...")
    bulunan_fırsatlar = []
    
    for hisse in hisseler:
        try:
            ticker = yf.Ticker(hisse)
            veri = ticker.history(period="1y", interval="1d")
            
            if len(veri) < 200:
                continue
                
            veri['SMA_200'] = veri['Close'].rolling(window=200).mean()
            veri['SMA_20'] = veri['Close'].rolling(window=20).mean()
            veri['STD'] = veri['Close'].rolling(window=20).std()
            veri['Bollinger_Lower'] = veri['SMA_20'] - (veri['STD'] * 2.0)
            
            delta = veri['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            veri['RSI'] = 100 - (100 / (1 + rs))
            
            son_kapanis = veri['Close'].iloc[-1]
            son_dusuk = veri['Low'].iloc[-1]
            bollinger_alt = veri['Bollinger_Lower'].iloc[-1]
            son_rsi = veri['RSI'].iloc[-1]
            sma_200 = veri['SMA_200'].iloc[-1]
            
            if (son_dusuk <= bollinger_alt) and (son_rsi < 38) and (son_kapanis > sma_200):
                bulunan_fırsatlar.append(
                    f"📌 *{hisse}*\n"
                    f"💰 Fiyat: `{son_kapanis:.2f} TL` | 📉 Alt Bant: `{bollinger_alt:.2f} TL` | 📊 RSI: `{son_rsi:.2f}`\n"
                )
                
            time.sleep(0.3)
                
        except Exception as e:
            pass
            
    # SONUÇLARI BİLDİR (Artık fırsat olmasa bile Telegram'a bilgi atacak)
    if bulunan_fırsatlar:
        rapor = "🚨 *BİST AKILLI DİP FIRSATLARI RAPORU* 🚨\n\n" + "\n".join(bulunan_fırsatlar) + "\n⚠️ _Kriter: Trend üstü sağlam hisse dipte!_"
        telegram_mesaj_gonder(rapor)
    else:
        telegram_mesaj_gonder("🔍 *BİST Günlük Tarama Tamamlandı*\n\nBugün kriterlere uyan (trend üstü + dipte) fırsat bulunamadı. Piyasayı takip etmeye devam ediyoruz! ☕")

if __name__ == "__main__":
    borsa_taramasi_yap()
