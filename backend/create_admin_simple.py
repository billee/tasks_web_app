import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

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

def create_admin_user(email, password):
    db = SessionLocal()
    
    try:
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
                "INSERT INTO users (email, hashed_password, is_active, is_admin, created_by) "
                "VALUES (:email, :hashed_password, :is_active, :is_admin, :created_by)"
            ),
            {
                "email": email,
                "hashed_password": hashed_password,
                "is_active": True,
                "is_admin": True,
                "created_by": "system"
            }
        )
        
        db.commit()
        print(f"Admin user {email} created successfully!")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_admin_simple.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    create_admin_user(email, password)