"""Standalone script to recreate the database without importing app code."""
import os
from pathlib import Path
import sqlite3

# Remove old database
db_path = Path("ai_desk.db")
if db_path.exists():
    db_path.unlink()
    print("✓ Removed old database")

# Create new database with schema
db_path.touch()
conn = sqlite3.connect("ai_desk.db")
cursor = conn.cursor()

# Create tables directly
cursor.execute("""
    CREATE TABLE user (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        email VARCHAR NOT NULL UNIQUE,
        username VARCHAR NOT NULL UNIQUE,
        full_name VARCHAR NOT NULL,
        hashed_password VARCHAR NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
""")
print("✓ Created user table")

cursor.execute("""
    CREATE TABLE chatsession (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title VARCHAR NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES user(id)
    )
""")
print("✓ Created chatsession table")

cursor.execute("""
    CREATE TABLE message (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        content VARCHAR NOT NULL,
        sender VARCHAR NOT NULL,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES chatsession(id)
    )
""")
print("✓ Created message table")

# Create a test user
cursor.execute("""
    INSERT INTO user (email, username, full_name, hashed_password)
    VALUES (?, ?, ?, ?)
""", ("test@example.com", "testuser", "Test User", "test_password_hash"))
print("✓ Created test user")

conn.commit()
conn.close()

print("\n✅ Database recreated successfully!")
