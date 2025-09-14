import sys
import os
import warnings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Suppress BCrypt warnings
warnings.filterwarnings("ignore", message=".*bcrypt.*")
warnings.filterwarnings("ignore", message=".*trapped.*")

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Database URL - PostgreSQL connection
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:paswd188!!@localhost:5432/tasks_web_app"

# Create engine (removed SQLite-specific connect_args)
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
        print("Users table created/verified successfully!")
    except Exception as e:
        print(f"Error creating users table: {e}")
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
        print(f"Admin user {name} ({email}) created successfully!")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin_simple.py <name> <email> <password>")
        sys.exit(1)
    
    name = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    create_admin_user(name, email, password)