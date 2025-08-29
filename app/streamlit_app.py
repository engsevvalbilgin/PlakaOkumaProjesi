import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from plate_database import PlateDatabase
import cv2
import time
from cryptography.fernet import Fernet
load_dotenv()

# Anahtar .env’den alınmalı
FERNET_KEY = os.getenv("FERNET_KEY").encode()
cipher = Fernet(FERNET_KEY)

def get_vehicles_data_from_db():
    conn = None
    try:
        db_exists = os.path.exists(os.environ['DB_NAME'])
        conn = sqlite3.connect(os.environ['DB_NAME'])
        cursor = conn.cursor()

        # Tabloyu oluştur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate TEXT NOT NULL,
                model TEXT,
                entry_time DEFAULT CURRENT_TIMESTAMP NOT NULL,
                exit_time TIMESTAMP
            )
        ''')
        conn.commit()

        # Veriyi çek
        df = pd.read_sql_query("SELECT * FROM vehicles", conn)

        # Plakaları deşifrele
        def decrypt_plate(encrypted_plate):
            try:
                # Eğer veri bytes değilse str'e encode et
                if isinstance(encrypted_plate, str):
                    encrypted_plate = encrypted_plate.encode()
                return cipher.decrypt(encrypted_plate).decode()
            except Exception:
                return encrypted_plate.decode() if isinstance(encrypted_plate, bytes) else encrypted_plate

        df['plate'] = df['plate'].apply(decrypt_plate)

        # Zaman sütunları
        df['entry_time'] = pd.to_datetime(df['entry_time'], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce')
        df['exit_time'] = pd.to_datetime(df['exit_time'], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce')

        df['entry_time_str'] = df['entry_time'].dt.strftime('%Y-%m-%d %H:%M')
        df['exit_time_str'] = df['exit_time'].dt.strftime('%Y-%m-%d %H:%M')

        return df

    except sqlite3.Error as e:
        st.error(f"Veritabanı hatası: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()




# Ana Streamlit uygulama fonksiyonu / Main Streamlit app function
def run_streamlit_app():
    # Veriyi veritabanından yükle / Load data from the database
    df = get_vehicles_data_from_db()

    # Tarihleri biçimlendirmek için yardımcı fonksiyon / Helper function for formatting dates
    def fmt(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(dt) else "-"

    st.set_page_config(page_title="Araç Takip Paneli", layout="wide")
    st.title("Araç Takip Paneli")

    # Seçilen plaka için oturum durumunu başlat (eğer yoksa)
    # Initialize session state for selected plate (if not exists)
    if "selected_plate" not in st.session_state:
        st.session_state["selected_plate"] = None

    # Filtreler için kenar çubuğu / Sidebar for filters
    st.sidebar.header("Filtreler")
    mode = st.sidebar.radio("Görüntüleme modu:", ("İçerdeki Araçlar", "Tüm Geçmiş"))

    min_date = (datetime.now() - timedelta(days=30)).date()
    date_range = st.sidebar.date_input("Gün seç (veya aralık)", value=(min_date, datetime.now().date()))

    # Eğer tek tarih seçildiyse tuple yap

    if isinstance(date_range, (tuple, list))and len(date_range) == 2:
        start_date, end_date = date_range[0], date_range[1]
    else:
        start_date = end_date = date_range

    plate_search = st.sidebar.text_input("Plaka ara (opsiyonel)")

    # DataFrame'e filtreleri uygula / Apply filters to the DataFrame
    filtered = df.copy()
    if mode == "İçerdeki Araçlar":
        filtered = filtered[filtered["exit_time"].isnull()]

    # Tarih aralığı filtresini uygula
    # Apply the date range filter
    if start_date and end_date:
        # start_date ve end_date'i datetime64[ns] yap
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        try:
            filtered = filtered[
                (filtered["entry_time"] >= start_datetime) &
                (filtered["entry_time"] <= end_datetime)
                ]
        except:
            pass
    elif start_date:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = start_datetime + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        try:
            filtered = filtered[
                (filtered["entry_time"] >= start_datetime) &
                (filtered["entry_time"] <= end_datetime)
                ]
        except:
            pass
    if plate_search:
        filtered = filtered[filtered["plate"].str.contains(plate_search, case=False, na=False)]

    filtered = filtered.sort_values(by="entry_time", ascending=False).reset_index(drop=True)

    # Ana içerik düzeni: Sol taraf liste, sağ taraf detaylar için / Main content layout: Left for list, right for details
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.markdown("### Araçlar")

        if filtered.empty:
            st.info("Seçilen filtrelere göre araç bulunamadı.")
        else:
            for idx, row in filtered.iterrows():
                plate = row["plate"]
                model = row["model"]
                entry = row["entry_time"]
                exit_t = row["exit_time"]

                with st.container(border=True):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"""
                                                   <div style="text-align: center; font-size: 1.5em; font-weight: bold; letter-spacing: 1px;">
                                                       {plate}
                                                   </div>
                                               """, unsafe_allow_html=True)
                    with col2:

                        st.write(f"Giriş: {fmt(entry)}")
                        if pd.notnull(exit_t):
                            st.write(f"Çıkış: {fmt(exit_t)}")
                            total = exit_t - entry
                            st.write(f"Toplam kalış: **{str(total).split('.')[0]}**")
                        else:
                            now = datetime.now()
                            duration = now - entry
                            st.write(f"İçerde geçen süre: **{str(duration).split('.')[0]}**")

                        btn_key_detay = f"detay_{idx}_{plate}"
                        btn_key_duzenle = f"duzenle_{idx}_{plate}"

                        # Detayları göster
                        if st.button("Detayları Göster", key=btn_key_detay):
                            st.session_state["selected_plate"] = plate



    with right_col:
        st.markdown("### Seçilen Araç Detayları")
        selected_plate = st.session_state.get("selected_plate", None)
        if selected_plate is None:
            st.write("Listeden bir araç seçmek için 'Detayları Göster' butonuna basın. 👈")
        else:
            # Seçilen aracın tüm kayıtlarını al
            plate_history = df[df["plate"] == selected_plate].sort_values(by="entry_time", ascending=False)
            # Son kayıt detayları
            latest = plate_history.iloc[0]

            st.markdown(f"#### {latest['plate']}")
            st.write(f"**Giriş:** {fmt(latest['entry_time'])}")
            st.write(f"**Çıkış:** {fmt(latest['exit_time'])}")

            if pd.notnull(latest['exit_time']):
                total = latest['exit_time'] - latest['entry_time']
                st.write(f"**Toplam kalış:** {str(total).split('.')[0]}")
            else:
                now = datetime.now()
                elapsed = now - latest['entry_time']
                st.write(f"**İçerde geçen süre:** {str(elapsed).split('.')[0]}")
                # Araç içerideyse Çıkış Ver butonu
                if st.button("Çıkış Ver", key=f"exit_{idx}_{plate}"):
                    # Veritabanını aç
                    db_path = os.environ['DB_NAME']
                    db = PlateDatabase(db_path)
                    db.set_exit_time_by_id(latest['id'])  # artık self doğru şekilde geliyor
                    st.success(f"{selected_plate} için çıkış verildi!")

            st.markdown("---")

            st.markdown(f"#### Tüm Geçmiş Kayıtlar")
            display_df = plate_history[['entry_time_str', 'exit_time_str']].rename(
                columns={'entry_time_str': 'Giriş Zamanı', 'exit_time_str': 'Çıkış Zamanı'}
            )
            st.table(display_df)



#CSV indirme butonu
    # CSV indirme butonu
    st.sidebar.markdown("---")

    # Hangi veriyi indirmek istediğimizi belirle
    if mode == "Tüm Geçmiş":
        csv_df = df.copy()  # tüm geçmişi al
    elif mode == "İçerdeki Araçlar":
        csv_df = df[df["exit_time"].isnull()]  # içerideki araçlar
    else:
        csv_df = filtered.copy()  # filtre varsa filtrelenmiş veriyi al

    # Tarih ve plaka filtrelerini uygula
    if start_date and end_date:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        csv_df = csv_df[
            (csv_df["entry_time"] >= start_datetime) &
            (csv_df["entry_time"] <= end_datetime)
            ]
    if plate_search:
        csv_df = csv_df[csv_df["plate"].str.contains(plate_search, case=False, na=False)]

    # CSV olarak indir
    csv = csv_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Veriyi CSV olarak indir", data=csv, file_name="vehicles.csv", mime="text/csv")


# Uygulamayı çalıştır / Run the app
if __name__ == '__main__':
    run_streamlit_app()
