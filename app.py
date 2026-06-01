import streamlit as st
import pandas as pd
from openai import OpenAI

# 1. HOCANIN İSTEDİĞİ ENTEGRASYON BİLGİLERİ (OpenAI ve Google Sheets)
# Satın aldığın 5 dolarlık yeni keyi buraya yapıştır

CSV_LINK = "https://docs.google.com/spreadsheets/d/1Os_zg6Su07LifEX0TUcAPsSHMhfWYPClGfW4a-EXiwo/export?format=csv"

# OpenAI İstemcisini Başlatma
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2. UYGULAMA BAŞLIĞI VE ARAYÜZÜ
st.set_page_config(page_title="AI Seyahat Planlayıcısı", page_icon="🗺️", layout="wide")
st.title("🗺️ AI ile Seyahatimi Planlıyorum")
st.write("---")

# Yan panel (Sidebar) Tasarımı
st.sidebar.header("✈️ Seyahat Parametreleri")
sehir = st.sidebar.text_input("Gitmek İstediğiniz Şehir:", "Paris")
gun = st.sidebar.number_input("Kalınacak Gün Sayısı:", min_value=1, max_value=15, value=3)
butce = st.sidebar.selectbox("Bütçe Segmenti Seçin:", ["Ekonomik", "Orta Seviye", "Lüks/Premium"])
ilgiler = st.sidebar.multiselect("İlgi Alanları:", ["Tarih/Kültür", "Doğa", "Gastronomi", "Alışveriş"], default=["Tarih/Kültür", "Gastronomi"])

# 3. BUTONA BASILDIĞINDA ÇALIŞACAK MOTOR
if st.sidebar.button("Canlı AI Planı Oluştur", type="primary"):
    ilgi_metni = ", ".join(ilgiler)
    
    # Sekmeleri Oluşturma (Tab Yapısı)
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Günlük Rota", "💰 Harcama Tahmini", "🚌 Ulaşım Rehberi (Google Sheets)", "🍔 Yemek Önerileri"])
    
    # A) GOOGLE SHEETS ENTEGRASYONU (15 PUAN)
    with tab3:
        st.subheader("🚌 Yerel Ulaşım ve Altyapı Bilgileri")
        try:
            df = pd.read_csv(CSV_LINK)
            sehir_veri = df[df['Sehir'].str.upper() == sehir.strip().upper()]
            if not sehir_veri.empty:
                st.info(f"📍 *Aranan Şehir:* {sehir_veri.iloc[0]['Sehir']}")
                st.markdown(f"💳 *Önerilen Ulaşım Kartı:* {sehir_veri.iloc[0]['Kart_Adi']}")
                st.markdown(f"💵 *Kart Ücreti / Depozito:* {sehir_veri.iloc[0]['Kart_Fiyati']}")
                st.markdown(f"✈️ *Havalimanı Transfer Seçeneği:* {sehir_veri.iloc[0]['Havalani_Transfer']}")
                st.success(f"💡 *Önemli Seyahat Tüyosu:* {sehir_veri.iloc[0]['Tuyolar']}")
            else:
                st.warning("Girdiğiniz şehir Google Sheets veri tabanında bulunamadı. Genel ulaşım tüyolarını kontrol edin.")
        except Exception as e:
            st.error(f"Google Sheets bağlantı hatası: {e}")

    # B) GERÇEK AI PROMPTLARI VE ÇAĞRILARI (20 PUAN)
    with st.spinner("🔄 OpenAI canlı sunucularına bağlanılıyor, verileriniz işleniyor..."):
        try:
            # 1. Rota İsteği
            response_rota = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Bana {sehir} şehri için {gun} günlük, ilgi alanları {ilgi_metni} olan detaylı bir seyahat rotası yaz. Maddeler halinde olsun, emojiler kullan. Markdown kod bloğu içine alma."}]
            )
            with tab1:
                st.subheader(f"🗺️ {sehir} Günlük Rota Planı")
                st.write(response_rota.choices[0].message.content)
                
            # 2. Bütçe İsteği
            response_harcama = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Bana {sehir} şehri için {gun} günlük, {butce} bütçesine uygun tahmini harcama listesi çıkar. Konaklama, yemek ve aktiviteleri ayrı ayrı para birimleriyle belirt."}]
            )
            with tab2:
                st.subheader(f"💰 {butce} Segment Harcama Analizi")
                st.write(response_harcama.choices[0].message.content)
                
            # 3. Yemek İsteği
            response_yemek = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"{sehir} şehrinde {butce} bütçesine uygun, mutlaka gidilmesi gereken 3 gerçek restoran ismi listele. Yanına o bütçeye uygun meşhur yemeklerini yaz."}]
            )
            with tab4:
                st.subheader(f"🍔 {butce} Segmenti Mekan Önerileri")
                st.write(response_yemek.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Yapay zeka motoru bağlantı hatası: {e}")
            
