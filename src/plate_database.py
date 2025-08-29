import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

# Şifreleme için Fernet
FERNET_KEY = os.getenv("FERNET_KEY").encode()
cipher = Fernet(FERNET_KEY)


# PlateDatabase sınıfı
class PlateDatabase:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
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

    def encrypt_plate(self, plate: str) -> str:
        return cipher.encrypt(plate.encode()).decode()

    def decrypt_plate(self, encrypted_plate: str) -> str:
        try:
            return cipher.decrypt(encrypted_plate.encode()).decode()
        except Exception:
            return encrypted_plate

    def record_plate_event(self, plate: str):
        """
        Araç giriş/çıkış kaydı yapar.
        Aynı plaka ard arda kaydedilmez, şifrelenmiş olsa da deşifre ederek kontrol eder.
        """
        now = datetime.now()
        encrypted_plate = self.encrypt_plate(plate)

        # Aktif kayıtları al ve deşifre et
        self.cursor.execute("SELECT id, plate, entry_time, exit_time FROM vehicles WHERE exit_time IS NULL")
        active_records = self.cursor.fetchall()

        # Aynı plaka içeride mi kontrol et
        for record in active_records:
            record_id, enc_plate, entry_time, exit_time = record
            try:
                entry_time_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                entry_time_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")

            if exit_time is None:
                # Araç içerideyse, girişten bu yana 3 saniyeden azsa kaydetme
                if (now - entry_time_dt).total_seconds() < 3:
                    return
                else:
                    # 3 saniye geçtiyse çıkış ver
                    self.cursor.execute(
                        "UPDATE vehicles SET exit_time = ? WHERE id = ?",
                        (now, record_id)
                    )
                    self.conn.commit()

                return

        # Yoksa yeni giriş kaydı oluştur
        self.cursor.execute(
            "INSERT INTO vehicles (plate, entry_time) VALUES (?, ?)",
            (encrypted_plate, now)
        )
        self.conn.commit()

    def set_exit_time(self, plate: str):
        encrypted_plate = self.encrypt_plate(plate)
        now = datetime.now()
        self.cursor.execute(
            "UPDATE vehicles SET exit_time = ? WHERE plate = ? AND exit_time IS NULL",
            (now, encrypted_plate)
        )
        self.conn.commit()

    def update_data_by_id(self, vehicle_id, new_plate, new_model):
        encrypted_plate = self.encrypt_plate(new_plate.strip().upper())
        try:
            self.cursor.execute("""
                UPDATE vehicles
                SET plate = ?, model = ?
                WHERE id = ?
            """, (encrypted_plate, new_model.strip(), vehicle_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Veritabanı güncelleme hatası: {e}")

    def __del__(self):
        self.conn.close()


# Veritabanından araç verilerini çeken fonksiyon
def get_vehicles_data_from_db():
    try:
        db_path = os.environ.get('DB_NAME', 'vehicles.db')
        db = PlateDatabase(db_path)

        df = pd.read_sql_query("SELECT * FROM vehicles", db.conn)

        # Plakaları deşifrele
        df['plate'] = df['plate'].apply(db.decrypt_plate)

        # Zaman sütunları
        df['entry_time'] = pd.to_datetime(df['entry_time'], errors='coerce')
        df['exit_time'] = pd.to_datetime(df['exit_time'], errors='coerce')

        df['entry_time_str'] = df['entry_time'].dt.strftime('%Y-%m-%d %H:%M')
        df['exit_time_str'] = df['exit_time'].dt.strftime('%Y-%m-%d %H:%M')
        return df

    except Exception as e:
        st.error(f"Veritabanı hatası: {e}")
        return pd.DataFrame()