import sqlite3
from datetime import datetime, timedelta
import os
# Bağlantı
conn = sqlite3.connect("C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\data\\vehicles.db")
cursor = conn.cursor()
# Tablo oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate TEXT NOT NULL,
    model TEXT,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME
)
""")

# Şimdi örnek veriler ekleyelim
now = datetime.now()

'''sample_data = [
    ("34ABC01", "Renault Clio", now - timedelta(hours=1, minutes=30), None),
    ("06XYZ99", "Toyota Corolla", now - timedelta(days=1, hours=5), now - timedelta(days=1, hours=3)),
    ("35QWE12", "Fiat Egea", now - timedelta(hours=6), None),
    ("07RST45", "VW Passat", now - timedelta(days=3, hours=2), now - timedelta(days=3, hours=0)),
    ("16ABC02", "Ford Focus", now - timedelta(hours=10), None),
    ("42XYZ03", "Opel Astra", now - timedelta(minutes=45), None),
]

cursor.executemany("INSERT INTO vehicles (plate, model, entry_time, exit_time) VALUES (?, ?, ?, ?)", sample_data)
'''
conn.commit()
conn.close()
