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

    def encrypt_plate(self, plate: str) :
        encrypted_data = cipher.encrypt(plate.encode()).decode()
        return encrypted_data

    def decrypt_plate(self, encrypted_plate: str) -> str:
        try:
            return cipher.decrypt(encrypted_plate.encode()).decode()
        except Exception:
            return encrypted_plate

    def record_plate_event(self, plate: str):
        now = datetime.now()
        encrypted_plate = self.encrypt_plate(plate)

        # Aktif kayıtları al ve deşifre et
        self.cursor.execute("SELECT id, plate, entry_time, exit_time FROM vehicles ORDER BY id DESC")
        all_records = self.cursor.fetchall()

        # 1. Araç çıkışıyla yeni kayıt arasında 3 saniye kuralı
        if all_records:
            last_id, last_plate_enc, last_entry_time, last_exit_time = all_records[0]
            try:
                last_entry_dt = datetime.strptime(last_entry_time, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                last_entry_dt = datetime.strptime(last_entry_time, "%Y-%m-%d %H:%M:%S")
            if last_exit_time:
                try:
                    last_exit_dt = datetime.strptime(last_exit_time, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    last_exit_dt = datetime.strptime(last_exit_time, "%Y-%m-%d %H:%M:%S")
                if (now - last_exit_dt).total_seconds() < 3:
                    return  # 3 sn geçmeden yeni kayıt yapılmaz

        # Aynı plaka içeride mi kontrol et
        self.cursor.execute("SELECT id, plate, entry_time, exit_time FROM vehicles WHERE exit_time IS NULL")
        active_records = self.cursor.fetchall()
        for record in active_records:
            record_id, enc_plate, entry_time, exit_time = record
            try:
                entry_time_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                entry_time_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")

            if exit_time is None:
                # 2. Giriş-çıkış arasında minimum 3 saniye
                if (now - entry_time_dt).total_seconds() < 3:
                    return
                else:
                    # 3 sn geçtiyse çıkış ver
                    self.cursor.execute(
                        "UPDATE vehicles SET exit_time = ? WHERE id = ?",
                        (now, record_id)
                    )
                    self.conn.commit()
                return

        # 3. Farklı araçların girişleri arasında 3 saniye kuralı
        for record in all_records:
            record_id, enc_plate, entry_time, exit_time = record
            try:
                entry_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                entry_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
            if (now - entry_dt).total_seconds() < 3:
                return  # 3 sn geçmeden başka araç kaydı yapılmaz

        # Yeni giriş kaydı oluştur
        self.cursor.execute(
            "INSERT INTO vehicles (plate, entry_time) VALUES (?, ?)",
            (encrypted_plate, now)
        )
        self.conn.commit()

    '''def record_plate_event(self, plate: str):
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

'''
    def set_exit_time_by_id(self, vehicle_id: int):
        '''print(vehicle_id)'''
        vehicle_id = int(vehicle_id)
        now = datetime.now()
        self.cursor.execute("SELECT id, plate, exit_time FROM vehicles WHERE id=?", (vehicle_id,))
        rows = self.cursor.fetchall()
        '''print("Veritabanında bu ID ile kayıt:", rows)'''
        self.cursor.execute(
            "UPDATE vehicles SET exit_time = ? WHERE id = ?",
            (now, vehicle_id)
        )
        '''print("Güncellenen satır sayısı:", self.cursor.rowcount)'''
        self.conn.commit()

    def set_exit_time(self, plate: str):
        print(plate)
        encrypted_plate = self.encrypt_plate(plate)
        '''print(encrypted_plate)'''
        now = datetime.now()
        self.cursor.execute(
            "UPDATE vehicles SET exit_time = ? WHERE plate = ? AND exit_time IS NULL",
            (now, encrypted_plate)
        )
        print(self.cursor.rowcount)
        self.conn.commit()

    '''
    def set_exit_time_by_id(self, vehicle_id: int):
    now = datetime.now()
    self.cursor.execute(
        "UPDATE vehicles SET exit_time = ? WHERE id = ? AND exit_time IS NULL",
        (now, vehicle_id)
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
'''

    def get_vehicles_data_from_db(self):
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