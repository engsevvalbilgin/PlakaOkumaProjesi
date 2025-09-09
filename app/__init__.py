import os
import sqlite3
from dotenv import load_dotenv
load_dotenv()

conn = sqlite3.connect(os.environ['DB_NAME'])
cursor = conn.cursor()
cursor.execute("SELECT * FROM vehicles WHERE id=?", (5,))
print("Kayıt kontrol:", cursor.fetchall())
