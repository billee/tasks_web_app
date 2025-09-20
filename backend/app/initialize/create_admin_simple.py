"""
==============================================================================
                          CREATE ADMIN USER SCRIPT
==============================================================================

This script creates an admin user in your PostgreSQL database.
It automatically detects whether to use local or production database based on
the --production flag.

SETUP REQUIRED:
1. Make sure your .env file contains:
   DATABASE_URL=postgresql://postgres:password@localhost:5432/your_local_db
   DATABASE_PROD_URL=postgresql://user:pass@host:5432/your_prod_db

2. Install required packages:
   pip install sqlalchemy passlib python-dotenv psycopg2-binary

USAGE:
------
For LOCAL development database:
   python create_admin_simple.py "Admin Name" "admin@email.com" "password123"

For PRODUCTION database:
   python create_admin_simple.py "Admin Name" "admin@email.com" "password123" --production

⚠️  IMPORTANT: 
- Without --production flag = Uses DATABASE_URL (local database)
- With --production flag = Uses DATABASE_PROD_URL (production database)

EXAMPLES:
---------
# Create admin in LOCAL database
python create_admin_simple.py "John Smith" "john@company.com" "mySecurePass123"

# Create admin in PRODUCTION database  
python create_admin_simple.py "John Smith" "john@company.com" "mySecurePass123" --production

The script will clearly show which database it's connecting to when you run it.

==============================================================================
"""




import sys
import os
import warnings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from dotenv import load_dotenv

# Suppress BCrypt warnings
warnings.filterwarnings("ignore", message=".*bcrypt.*")
warnings.filterwarnings("ignore", message=".*trapped.*")

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

def parse_arguments():
    """Parse command line arguments and return production flag and other args"""
    is_production = False
    args = []
    
    for arg in sys.argv[1:]:  # Skip script name
        if arg == "--production":
            is_production = True
            print("🔍 Found --production flag")
        else:
            args.append(arg)
    
    return is_production, args

def get_database_url(is_production=False):
    """
    Get database URL based on production flag
    - If --production flag: use DATABASE_PROD_URL
    - If no flag (default): use DATABASE_URL
    """
    
    if is_production:
        print("🌐 Production mode - using DATABASE_PROD_URL")
        prod_url = os.getenv("DATABASE_PROD_URL")
        if not prod_url:
            print("🚨 DATABASE_PROD_URL not found in environment variables!")
            print("Make sure DATABASE_PROD_URL is set in your .env or Render environment")
            sys.exit(1)
        return prod_url
    
    # Default to local development database
    print("🏠 Development mode - using DATABASE_URL")
    dev_url = os.getenv("DATABASE_URL")
    if not dev_url:
        print("🚨 DATABASE_URL not found in environment variables!")
        print("Make sure DATABASE_URL is set in your .env file")
        sys.exit(1)
    return dev_url

# Parse arguments FIRST
is_production, parsed_args = parse_arguments()

# Get the appropriate database URL based on the flag
SQLALCHEMY_DATABASE_URL = get_database_url(is_production)

print(is_production)
print()
print(SQLALCHEMY_DATABASE_URL)



# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_users_table_if_not_exists(db):
    """Create the users table if it doesn't exist with all required columns"""
    try:
        # Create the table with all columns including name (PostgreSQL syntax)
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.commit()
        print("✅ Users table created/verified successfully!")
    except Exception as e:
        print(f"❌ Error creating users table: {e}")
        raise

def create_admin_user(name, email, password):
    db = SessionLocal()


    try:
        # Create the users table if it doesn't exist
        create_users_table_if_not_exists(db)
        
        # Check if user already exists
        result = db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
        existing_user = result.fetchone()
        
        if existing_user:
            print("User already exists")
            return
        
        # Create new user
        hashed_password = pwd_context.hash(password)
        
        db.execute(
            text(
                "INSERT INTO users (name, email, hashed_password, is_active, is_admin, created_by, created_at) "
                "VALUES (:name, :email, :hashed_password, :is_active, :is_admin, :created_by, CURRENT_TIMESTAMP)"
            ),
            {
                "name": name,
                "email": email,
                "hashed_password": hashed_password,
                "is_active": True,
                "is_admin": True,
                "created_by": "system"
            }
        )
        
        db.commit()
        print(f"🎉 Admin user {name} ({email}) created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    if len(parsed_args) != 3:
        print("Usage: python create_admin_simple.py <name> <email> <password> [--production]")
        print("Examples:")
        print("  Local:      python create_admin_simple.py 'John Admin' 'john@company.com' 'mypassword123'")
        print("  Production: python create_admin_simple.py 'John Admin' 'john@company.com' 'mypassword123' --production")
        sys.exit(1)
    
    name = parsed_args[0]
    email = parsed_args[1]
    password = parsed_args[2]
    
    print(f"Creating admin user: {name} ({email})")
    create_admin_user(name, email, password)