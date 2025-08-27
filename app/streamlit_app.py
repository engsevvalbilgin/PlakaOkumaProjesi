import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os

# Veritabanı adı
DB_NAME = 'vehicles.db'


# Veritabanından veri çekme fonksiyonu
# Function to fetch data from the database
def get_vehicles_data_from_db():
    """Veritabanına bağlanır, verileri çeker ve DataFrame olarak döndürür."""
    """Connects to the database, fetches data, and returns it as a DataFrame."""
    conn = None
    try:
        # Veritabanı dosyasının varlığını kontrol et
        # Check if the database file exists
        db_exists = os.path.exists(DB_NAME)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # vehicles tablosunu oluştur (eğer yoksa)
        # Create the vehicles table (if it doesn't exist)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate TEXT NOT NULL,
                model TEXT,
                entry_time TEXT,
                exit_time TEXT
            )
        ''')
        conn.commit()

        # Tabloya örnek veri ekle (sadece ilk çalıştırmada)
        # Add sample data to the table (only on the first run)
        if not db_exists:
            now = datetime.now()
            sample_data = [
                ("34ABC01", "Renault Clio", now - timedelta(hours=1, minutes=23), None),
                ("06XYZ99", "Toyota Corolla", now - timedelta(days=1, hours=2), now - timedelta(days=1, hours=1)),
                ("35QWE12", "Fiat Egea", now - timedelta(hours=6), None),
                ("07RST45", "Volkswagen Passat", now - timedelta(days=3, hours=4), now - timedelta(days=2, hours=20)),
                ("16ABC02", "Ford Focus", now - timedelta(hours=10), None),
                ("42XYZ03", "Opel Astra", now - timedelta(minutes=45), None),
            ]

            cursor.executemany("INSERT INTO vehicles (plate, model, entry_time, exit_time) VALUES (?, ?, ?, ?)",
                               sample_data)
            conn.commit()
            print("Örnek veriler veritabanına eklendi.")
            print("Sample data added to the database.")

        # Tüm veriyi çek ve DataFrame olarak oku
        # Fetch all data and read as a DataFrame
        df = pd.read_sql_query("SELECT * FROM vehicles", conn)

        # Zaman sütunlarını datetime formatına çevir
        # Convert time columns to datetime format
        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['exit_time'] = pd.to_datetime(df['exit_time'])

        return df

    except sqlite3.Error as e:
        st.error(f"Veritabanı hatası: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


# Ana Streamlit uygulama fonksiyonu / Main Streamlit app function
def run_streamlit_app():
    """Etkileşimli Streamlit tabanlı kullanıcı arayüzünü çalıştırır."""
    """Runs the interactive Streamlit-based UI."""

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

    if isinstance(date_range, (tuple, list)):
        start_date, end_date = date_range[0], date_range[1]
    else:
        start_date = date_range
        end_date = date_range

    plate_search = st.sidebar.text_input("Plaka ara (opsiyonel)")

    # DataFrame'e filtreleri uygula / Apply filters to the DataFrame
    filtered = df.copy()
    if mode == "İçerdeki Araçlar":
        filtered = filtered[filtered["exit_time"].isnull()]

    # Tarih aralığı filtresini uygula
    # Apply the date range filter
    if start_date and end_date:
        filtered = filtered[
            (filtered["entry_time"].dt.date >= start_date) &
            (filtered["entry_time"].dt.date <= end_date)
            ]
    elif start_date:
        filtered = filtered[filtered["entry_time"].dt.date == start_date]

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
                        st.markdown(f"**{model}**")
                        st.write(f"Giriş: {fmt(entry)}")
                        if pd.notnull(exit_t):
                            st.write(f"Çıkış: {fmt(exit_t)}")
                            total = exit_t - entry
                            st.write(f"Toplam kalış: **{str(total).split('.')[0]}**")
                        else:
                            now = datetime.now()
                            duration = now - entry
                            st.write(f"İçerde geçen süre: **{str(duration).split('.')[0]}**")

                        btn_key = f"detay_{idx}_{plate}"
                        # Kullanıcı butona bastığında, oturum durumunu güncelle ve detayları göster
                        # When the user clicks the button, update the session state and show details
                        if st.button("Detayları Göster", key=btn_key):
                            st.session_state["selected_plate"] = plate
                st.markdown("---")

    with right_col:
        st.markdown("### Seçilen Araç Detayları")
        selected_plate = st.session_state.get("selected_plate", None)
        if selected_plate is None:
            st.write("Listeden bir araç seçmek için 'Detayları Göster' butonuna basın. 👈")
        else:
            selected_row_data = df[df["plate"] == selected_plate].iloc[0]
            st.markdown(f"#### {selected_row_data['plate']} — {selected_row_data['model']}")
            st.write(f"**Giriş:** {fmt(selected_row_data['entry_time'])}")
            st.write(f"**Çıkış:** {fmt(selected_row_data['exit_time'])}")

            if pd.notnull(selected_row_data['exit_time']):
                total = selected_row_data['exit_time'] - selected_row_data['entry_time']
                st.write(f"**Toplam kalış:** {str(total).split('.')[0]}")
            else:
                now = datetime.now()
                elapsed = now - selected_row_data['entry_time']
                st.write(f"**İçerde geçen süre:** {str(elapsed).split('.')[0]}")

            st.markdown("---")
            st.markdown("<h5 style='color: #333;'>Geçmiş Kayıtlar (örnek)</h5>", unsafe_allow_html=True)
            hist = pd.DataFrame([
                {"action": "Giriş", "time": selected_row_data['entry_time'] - timedelta(days=10)},
                {"action": "Çıkış", "time": selected_row_data['entry_time'] - timedelta(days=10) + timedelta(hours=2)},
                {"action": "Giriş", "time": selected_row_data['entry_time']},
            ])
            st.dataframe(hist.assign(time=lambda d: d['time'].dt.strftime('%Y-%m-%d %H:%M:%S')), hide_index=True)

    # CSV indirme butonu
    st.sidebar.markdown("---")
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Veriyi CSV olarak indir", data=csv, file_name="parking_data.csv", mime="text/csv")
    st.caption("Not: Bu demo, kameradan plaka okuma entegrasyonu içermez. Verinizi gerçek bir kaynaktan alabilirsiniz.")


# Uygulamayı çalıştır / Run the app
if __name__ == '__main__':
    run_streamlit_app()
