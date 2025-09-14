import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== DATABASE CONNECTION DEBUG ===")
print()

# Check environment variables
print("1. Environment Variables:")
database_url = os.getenv("DATABASE_URL")
print(f"   DATABASE_URL: {database_url}")
print()

# Check if .env file exists
env_file_exists = os.path.exists(".env")
print(f"2. .env file exists: {env_file_exists}")
if env_file_exists:
    print("   Contents of .env file:")
    try:
        with open(".env", "r") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip() and not line.startswith("#"):
                    print(f"   Line {line_num}: {line.strip()}")
    except Exception as e:
        print(f"   Error reading .env: {e}")
print()

# Test different connection strings
print("3. Testing Connections:")

# Test 1: Using environment variable
if database_url:
    print(f"   Testing DATABASE_URL: {database_url}")
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"   ✅ Success! Connected to database: {db_name}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
else:
    print("   No DATABASE_URL found in environment")

print()

# Test 2: Direct connection to postgres database (should always work)
postgres_url = "postgresql://postgres:password@localhost:5432/postgres"
print(f"   Testing connection to 'postgres' database: {postgres_url}")
try:
    engine = create_engine(postgres_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"   ✅ Success! Connected to database: {db_name}")
        
        # List all databases
        result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false"))
        databases = [row[0] for row in result.fetchall()]
        print(f"   📊 Available databases: {databases}")
        
except Exception as e:
    print(f"   ❌ Failed: {e}")
    print("   This means PostgreSQL is not running or password is wrong")

print()

# Test 3: Check if email_categorizer_db exists
print("4. Checking if target database exists:")
try:
    # Connect to postgres database to check if our target database exists
    engine = create_engine("postgresql://postgres:password@localhost:5432/postgres")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'email_categorizer_db'"))
        exists = result.fetchone() is not None
        if exists:
            print("   ✅ 'email_categorizer_db' database exists")
        else:
            print("   ❌ 'email_categorizer_db' database does NOT exist")
            print("   💡 You need to create it first!")
except Exception as e:
    print(f"   ❌ Could not check: {e}")

print()
print("=== NEXT STEPS ===")
print("1. If 'email_categorizer_db' doesn't exist, create it using:")
print("   - pgAdmin GUI, or")
print("   - Command: psql -U postgres -c 'CREATE DATABASE email_categorizer_db;'")
print()
print("2. Update your .env file with correct DATABASE_URL:")
print("   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/email_categorizer_db")
print()
print("3. Replace 'YOUR_PASSWORD' with your actual PostgreSQL password")