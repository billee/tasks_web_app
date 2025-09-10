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

# Database URL - make sure this matches your actual database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./email_categorizer.db"

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_users_table_if_not_exists(db):
    """Create the users table if it doesn't exist and ensure it has all required columns"""
    try:
        # First, create the table if it doesn't exist
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Check if 'name' column exists, if not add it
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'name' not in columns:
            print("Adding missing 'name' column to users table...")
            db.execute(text("ALTER TABLE users ADD COLUMN name TEXT"))
        
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
                "INSERT INTO users (name, email, hashed_password, is_active, is_admin, created_by) "
                "VALUES (:name, :email, :hashed_password, :is_active, :is_admin, :created_by)"
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