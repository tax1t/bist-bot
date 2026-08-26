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
    # BİST-100 ve ana hacimli hisseleri kapsayan genişletilmiş havuz
    hisseler = [
        "THYAO.IS", "TUPRS.IS", "EREGL.IS", "KCHOL.IS", "GARAN.IS", 
        "AKBNK.IS", "ISCTR.IS", "YKBNK.IS", "ASELS.IS", "BIMAS.IS",
        "SAHOL.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", "KRDMD.IS",
        "PGSUS.IS", "TOASO.IS", "FROTO.IS", "ARCLK.IS", "ENKAI.IS",
        "MGROS.IS", "TCELL.IS", "TTKOM.IS", "SISE.IS", "BIMAS.IS",
        "ENJSA.IS", "ODAS.IS", "BERA.IS", "OYAKC.IS", "ASTOR.IS",
        "KONTR.IS", "GESAN.IS", "ALARK.IS", "HEKTS.IS", "GUBRF.IS"
    ]
    
    print(f"🔍 Toplam {len(hisseler)} hisse filtreleniyor...")
    bulunan_fırsatlar = []
    
    for hisse in hisseler:
        try:
            ticker = yf.Ticker(hisse)
            veri = ticker.history(period="1y", interval="1d") # Trend için 1 yıllık veri
            
            if len(veri) < 200:
                continue
                
            # 1. Trend Filtresi (200 Günlük Hareketli Ortalama - Batan çöp hisseleri eler)
            veri['SMA_200'] = veri['Close'].rolling(window=200).mean()
            
            # 2. Bollinger ve RSI Hesaplama
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
            
            # GELİŞMİŞ FİLTRELİ DİP KURALI:
            # - Fiyat Bollinger alt bandına değecek
            # - RSI aşırı satışta olacak (<38)
            # - Fiyat 200 günlük ortalamanın üstünde olacak (Yani genel trendi yükseliş olan sağlam hisse)
            if (son_dusuk <= bollinger_alt) and (son_rsi < 38) and (son_kapanis > sma_200):
                bulunan_fırsatlar.append(
                    f"📌 *{hisse}*\n"
                    f"💰 Fiyat: `{son_kapanis:.2f} TL` | 📉 Alt Bant: `{bollinger_alt:.2f} TL` | 📊 RSI: `{son_rsi:.2f}`\n"
                )
                
            time.sleep(0.3)
                
        except Exception as e:
            pass
            
    if bulunan_fırsatlar:
        rapor = "🚨 *BİST AKILLI DİP FIRSATLARI RAPORU* 🚨\n\n" + "\n".join(bulunan_fırsatlar) + "\n⚠️ _Kriter: Trend üstü sağlam hisse dipte!_"
        telegram_mesaj_gonder(rapor)
    else:
        print("🔍 Tarama bitti. Sağlam trendde olup dip yapan hisse bulunamadı.")

if __name__ == "__main__":
    borsa_taramasi_yap()
