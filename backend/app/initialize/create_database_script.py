import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

print("Creating 'tasks_web_app' database...")

# Connect to PostgreSQL server (to the 'postgres' database)
try:
    # Replace 'your_password' with your actual PostgreSQL password
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="paswd188!!",  # <- UPDATE THIS!
        database="postgres"
    )
    
    # Set autocommit to True for database creation
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Create cursor
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'tasks_web_app'")
    exists = cursor.fetchone()
    
    if exists:
        print("✅ Database 'tasks_web_app' already exists!")
    else:
        # Create the database
        cursor.execute("CREATE DATABASE tasks_web_app")
        print("✅ Database 'tasks_web_app' created successfully!")
    
    # List all databases
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
    databases = [row[0] for row in cursor.fetchall()]
    print(f"📊 Available databases: {databases}")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 Success! You can now run your application.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure PostgreSQL is running")
    print("2. Update the password in this script")
    print("3. Verify connection details are correct")