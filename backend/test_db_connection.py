import psycopg2
from sqlalchemy import create_engine

# Test different connection scenarios
test_configs = [
    # Test 1: Your current config
    {
        "name": "Current config (tasks_web_app db)",
        "url": "postgresql://postgres:paswd188!!@localhost:5432/tasks_web_app"
    },
    # Test 2: Default postgres database
    {
        "name": "Default postgres database", 
        "url": "postgresql://postgres:paswd188!!@localhost:5432/postgres"
    },
    # Test 3: Empty password
    {
        "name": "Empty password",
        "url": "postgresql://postgres:@localhost:5432/postgres"
    }
]

def test_connection(config):
    print(f"\nTesting: {config['name']}")
    print(f"URL: {config['url']}")
    
    try:
        engine = create_engine(config['url'])
        connection = engine.connect()
        print("✅ CONNECTION SUCCESSFUL!")
        
        # Try to execute a simple query
        result = connection.execute("SELECT version();")
        version = result.fetchone()[0]
        print(f"PostgreSQL version: {version[:50]}...")
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")
        return False

if __name__ == "__main__":
    print("Testing PostgreSQL connections...")
    
    successful_config = None
    for config in test_configs:
        if test_connection(config):
            successful_config = config
            break
    
    if successful_config:
        print(f"\n🎉 SUCCESS! Use this configuration:")
        print(f"DATABASE_URL = \"{successful_config['url']}\"")
    else:
        print("\n❌ None of the test configurations worked.")
        print("You need to either:")
        print("1. Reset your PostgreSQL password")
        print("2. Create the 'tasks_web_app' database")
        print("3. Check what credentials you use in pgAdmin4")