# test_neon.py
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_PROD_URL')
print(f"Testing: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print("Neon connection successful!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")