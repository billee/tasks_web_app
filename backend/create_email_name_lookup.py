"""
==============================================================================
                          CREATE EMAIL-NAME LOOKUP TABLE SCRIPT
==============================================================================

This script creates an email_name_lookup table in your PostgreSQL database.
It automatically detects whether to use local or production database based on
the --production flag.

SETUP REQUIRED:
1. Make sure your .env file contains:
   DATABASE_URL=postgresql://postgres:password@localhost:5432/your_local_db
   DATABASE_PROD_URL=postgresql://user:pass@host:5432/your_prod_db

2. Install required packages:
   pip install sqlalchemy python-dotenv psycopg2-binary

USAGE:
------
For LOCAL development database:
   python create_email_name_lookup.py

For PRODUCTION database:
   python create_email_name_lookup.py --production

⚠️  IMPORTANT: 
- Without --production flag = Uses DATABASE_URL (local database)
- With --production flag = Uses DATABASE_PROD_URL (production database)

EXAMPLES:
---------
# Create table in LOCAL database
python create_email_name_lookup.py

# Create table in PRODUCTION database  
python create_email_name_lookup.py --production

The script will clearly show which database it's connecting to when you run it.

==============================================================================
"""

import sys
import os
import warnings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore")

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

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_email_name_lookup_table(db):
    """Create the email_name_lookup table if it doesn't exist"""
    try:
        # Create the table with all required columns (PostgreSQL syntax)
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS email_name_lookup (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.commit()
        print("✅ Email-Name Lookup table created/verified successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating email_name_lookup table: {e}")
        db.rollback()
        return False

def main():
    db = SessionLocal()
    
    try:
        # Create the email_name_lookup table
        success = create_email_name_lookup_table(db)
        
        if success:
            print("🎉 Table creation completed successfully!")
        else:
            print("❌ Table creation failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        db.close()

if __name__ == "__main__":
    # Check if any unexpected arguments were provided
    if len(parsed_args) > 0:
        print("Usage: python create_email_name_lookup.py [--production]")
        print("Examples:")
        print("  Local:      python create_email_name_lookup.py")
        print("  Production: python create_email_name_lookup.py --production")
        sys.exit(1)
    
    main()