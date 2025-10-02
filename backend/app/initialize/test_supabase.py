from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_PROD_URL')
print(f"Database URL: {DATABASE_URL}")  # This should now show your connection string

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        print("Connection successful!")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
else:
    print("DATABASE_PROD_URL is still None - check .env file")