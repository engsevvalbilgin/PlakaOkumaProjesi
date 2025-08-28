# app.py (Ana Streamlit Uygulaması)
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os
from dotenv import load_dotenv
import sys

# .env dosyasındaki değişkenleri yükle
load_dotenv()


# PlateDatabase sınıfının bulunduğu dizini sys.path'e ekle
# Assuming plate_database.py is in the same directory or a known path
# If plate_database.py is in a 'src' folder next to app.py, this path setup is needed.
# For simplicity in a single file scenario, we'll include PlateDatabase class directly.
# If you have it in a separate file, make sure it's importable.
# sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
# from plate_database import PlateDatabase


# PlateDatabase sınıfını doğrudan buraya dahil ediyoruz
# Including PlateDatabase class directly here for a single file solution
class PlateDatabase:
    """
    A class to manage vehicle plate entry and exit events in an SQLite database.
    It includes a debounce mechanism to prevent rapid duplicate entries.
    """

    def __init__(self, db_path):
        """
        Initializes the database connection and creates the 'vehicles' table if it doesn't exist.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Creates the 'vehicles' table with 'plate', 'model', 'entry_time', and 'exit_time' columns.
        'entry_time' and 'exit_time' are defined as DATETIME.
        'entry_time' defaults to the current timestamp when a new record is inserted.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate TEXT NOT NULL,
                model TEXT,
                entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                exit_time DATETIME
            )
        """)
        self.conn.commit()

    def record_plate_event(self, plate):
        """
        Records an entry or exit event for a given plate with a 3-second debounce for both entry and exit.
        """
        now = datetime.now()

        # En son kaydı al
        self.cursor.execute(
            "SELECT entry_time, exit_time FROM vehicles WHERE plate = ? ORDER BY id DESC LIMIT 1",
            (plate,)
        )
        last_record = self.cursor.fetchone()

        if last_record:
            # last_event_time_str doğrudan string formatında gelebilir, kontrol edelim
            last_event_time_str = last_record[1] if last_record[1] else last_record[0]
            # Datetime'a dönüştürme formatı, SQLite'ın DATETIME varsayılan formatına göre ayarlandı
            try:
                last_event_time = datetime.strptime(str(last_event_time_str), "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                last_event_time = datetime.strptime(str(last_event_time_str), "%Y-%m-%d %H:%M:%S")

            # 3 saniyeden kısa süre önceyse kaydı atla
            if (now - last_event_time) < timedelta(seconds=3):
                # print(f"Plaka {plate} çok kısa süre önce görüldü. İşlem atlandı. ⛔")
                return

        # Debounce süresi geçti, aktif kaydı kontrol et
        self.cursor.execute(
            "SELECT * FROM vehicles WHERE plate = ? AND exit_time IS NULL",
            (plate,)
        )
        active_record = self.cursor.fetchone()

        if active_record:
            # Araç çıkış yaptı
            self.cursor.execute(
                "UPDATE vehicles SET exit_time = ? WHERE plate = ? AND exit_time IS NULL",
                (now, plate)
            )
            print(f"Araç çıkış yaptı: {plate} 🚗💨")
        else:
            # Yeni giriş kaydı oluştur
            self.cursor.execute(
                "INSERT INTO vehicles (plate, entry_time) VALUES (?, ?)",
                (plate, now)
            )
            print(f"Araç giriş yaptı: {plate} 🅿️")

        self.conn.commit()

    def set_exit_time(self, plate: str):  # self parametresi eklendi
        """Verilen plaka için exit_time sütununu günceller."""
        now = datetime.now()

        self.cursor.execute(
            "UPDATE vehicles SET exit_time = ? WHERE plate = ? AND exit_time IS NULL",
            (now, plate)
        )





    def update_data_by_id(self, vehicle_id, new_plate, new_model):
        """
        Verilen id'ye göre plaka ve model bilgisini günceller.
        """
        try:
            self.cursor.execute("""
                UPDATE vehicles
                SET plate = ?, model = ?
                WHERE id = ?
            """, (new_plate.strip().upper(), new_model.strip(), vehicle_id))
            self.conn.commit()
            print(f"Kayıt güncellendi: ID={vehicle_id}, Yeni Plaka='{new_plate}', Yeni Model='{new_model}'")
        except sqlite3.Error as e:
            print(f"Veritabanı güncelleme hatası: {e}")

    def __del__(self):
        """
        Closes the database connection when the object is garbage collected.
        """
        self.conn.close()


# Veritabanından araç verilerini çeken yardımcı fonksiyon
def get_vehicles_data_from_db():
    try:
        db_path = os.environ.get('DB_NAME', 'vehicles.db')  # Varsayılan değer ekledik
        db = PlateDatabase(db_path)  # PlateDatabase örneği oluşturuldu

        df = pd.read_sql_query("SELECT * FROM vehicles", db.conn)  # Bağlantıyı db nesnesinden al

        # Zaman sütunlarını datetime formatına çevir
        # SQLite DATETIME formatı için uygun dönüştürme
        df['entry_time'] = pd.to_datetime(df['entry_time'], errors='coerce')
        df['exit_time'] = pd.to_datetime(df['exit_time'], errors='coerce')

        # string formatına çevir
        df['entry_time_str'] = df['entry_time'].dt.strftime('%Y-%m-%d %H:%M')
        df['exit_time_str'] = df['exit_time'].dt.strftime('%Y-%m-%d %H:%M')
        return df

    except Exception as e:
        st.error(f"Veritabanı hatası: {e}")
        return pd.DataFrame()


# Ana Streamlit uygulama fonksiyonu / Main Streamlit app function
def run_streamlit_app():
    # Veriyi veritabanından yükle / Load data from the database
    df = get_vehicles_data_from_db()

    # Tarihleri biçimlendirmek için yardımcı fonksiyon / Helper function for formatting dates
    def fmt(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(dt) else "-"

    st.set_page_config(page_title="Araç Takip Paneli", layout="wide")
    st.title("Araç Takip Paneli")

    # Seçilen plaka ve düzenleme modunu oturum durumuna ekle
    # Initialize session state for selected plate (if not exists) and editing_id
    if "selected_plate" not in st.session_state:
        st.session_state["selected_plate"] = None
    if "editing_id" not in st.session_state:
        st.session_state["editing_id"] = None

    # Filtreler için kenar çubuğu / Sidebar for filters
    st.sidebar.header("Filtreler")
    mode = st.sidebar.radio("Görüntüleme modu:", ("İçerdeki Araçlar", "Tüm Geçmiş"))

    min_date = (datetime.now() - timedelta(days=30)).date()
    date_range = st.sidebar.date_input("Gün seç (veya aralık)", value=(min_date, datetime.now().date()))

    # Eğer tek tarih seçildiyse tuple yap
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
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
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        try:
            filtered = filtered[
                (filtered["entry_time"] >= start_datetime) &
                (filtered["entry_time"] <= end_datetime)
                ]
        except Exception as e:
            st.warning(f"Tarih filtresi uygulanırken hata oluştu: {e}")
            pass
    elif start_date:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = start_datetime + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        try:
            filtered = filtered[
                (filtered["entry_time"] >= start_datetime) &
                (filtered["entry_time"] <= end_datetime)
                ]
        except Exception as e:
            st.warning(f"Tarih filtresi uygulanırken hata oluştu: {e}")
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
                # Her aracın benzersiz ID'sini alıyoruz
                current_id = row['id']
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
                        st.markdown(f"**{model if model else 'Belirtilmemiş'}**")
                        st.write(f"Giriş: {fmt(entry)}")
                        if pd.notnull(exit_t):
                            st.write(f"Çıkış: {fmt(exit_t)}")
                            total = exit_t - entry
                            st.write(f"Toplam kalış: **{str(total).split('.')[0]}**")
                        else:
                            now = datetime.now()
                            duration = now - entry
                            st.write(f"İçerde geçen süre: **{str(duration).split('.')[0]}**")

                        btn_key_detay = f"detay_{current_id}"
                        btn_key_duzenle = f"duzenle_{current_id}"

                        # Detayları göster
                        if st.button("Detayları Göster", key=btn_key_detay):
                            st.session_state["selected_plate"] = plate
                            st.session_state["editing_id"] = None  # Detay gösterirken düzenleme modundan çık
                            st.rerun()

                        # Düzenle butonu
                        if st.button("Düzenle", key=btn_key_duzenle):
                            st.session_state["editing_id"] = current_id
                            st.session_state["selected_plate"] = None
                            st.rerun()

                        if st.session_state["editing_id"] == current_id:
                            st.markdown("---")
                            with st.form(key=f"form_{current_id}"):
                                new_plate = st.text_input(f"Plaka ({current_id}):", value=plate,
                                                          key=f"input_plate_{current_id}")
                                new_model = st.text_input(f"Model ({current_id}):", value=model if model else '',
                                                          key=f"input_model_{current_id}")
                                submit_btn = st.form_submit_button("Kaydet Değişiklikler")
                                if submit_btn:
                                    db_path = os.environ.get('DB_NAME', 'vehicles.db')
                                    db = PlateDatabase(db_path)
                                    db.update_data_by_id(current_id, new_plate, new_model)
                                    st.success(f"ID: {current_id} için kayıt güncellendi!")
                                    st.session_state["editing_id"] = None
                                    st.rerun()

    with right_col:
        st.markdown("### Seçilen Araç Detayları")
        selected_plate = st.session_state.get("selected_plate", None)
        if selected_plate is None:
            st.write("Listeden bir araç seçmek için 'Detayları Göster' butonuna basın. 👈")
        else:
            # Seçilen aracın tüm kayıtlarını al
            plate_history = df[df["plate"] == selected_plate].sort_values(by="entry_time", ascending=False)

            if not plate_history.empty:
                # En son kayıt detayları
                latest = plate_history.iloc[0]

                st.markdown(f"#### {latest['plate']} — {latest['model'] if latest['model'] else 'Belirtilmemiş'}")
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
                    selected_plate=st.session_state["selected_plate"]
                    if st.button("Çıkış Ver", key=f"exit_details_{selected_plate}"):  # Anahtar benzersiz olmalı
                        try:
                            db_path = os.environ.get('DB_NAME', 'vehicles.db')
                            db = PlateDatabase(db_path)
                            db.set_exit_time(selected_plate)
                            st.success(f"{selected_plate} için çıkış verildi!")
                            st.session_state["selected_plate"] = None  # Çıkış verildikten sonra detay modundan çık
                            st.rerun()
                        except Exception as e:
                            st.error(f"Çıkış verme hatası: {e}")
            else:
                st.info(f"'{selected_plate}' plakasına ait detay bulunamadı.")

            st.markdown("---")

            st.markdown(f"#### Tüm Geçmiş Kayıtlar")
            display_df = plate_history[['entry_time_str', 'exit_time_str']].rename(
                columns={'entry_time_str': 'Giriş Zamanı', 'exit_time_str': 'Çıkış Zamanı'}
            )
            st.table(display_df)

    # CSV indirme butonu
    st.sidebar.markdown("---")

    # Hangi veriyi indirmek istediğimizi belirle
    csv_df = filtered.copy()  # Filtrelenmiş veriyi direkt kullanıyoruz

    # CSV olarak indir
    csv = csv_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Veriyi CSV olarak indir", data=csv, file_name="vehicles.csv", mime="text/csv")


# Uygulamayı çalıştır / Run the app
if __name__ == '__main__':
    run_streamlit_app()