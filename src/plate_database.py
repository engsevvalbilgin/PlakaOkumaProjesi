from dotenv import load_dotenv
import sqlite3
# .env dosyasını yükle
load_dotenv()
conn = sqlite3.connect('vehicles.db')
cursor = conn.cursor()
class plate_database:
    def saveDatabase(self,plate):
        cursor.execute("INSERT INTO plates (plate) VALUES (?)", (plate,))
        conn.commit()