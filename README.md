
SQLite database ==================================
# Navigate to your backend directory
cd backend

# Open the SQLite database
sqlite3 email_categorizer.db

# View tables
.tables

# View schema of a specific table
.schema users

# Run a query
SELECT * FROM users;

# Exit SQLite
.exit