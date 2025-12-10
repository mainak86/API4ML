"""Script to recreate the database from SQLModel definitions."""
import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

# Set up database
DATABASE_URL = "sqlite:///ai_desk.db"
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

def recreate_db():
    """Drop all tables and recreate from models."""
    # Remove old database file
    db_path = Path("ai_desk.db")
    if db_path.exists():
        db_path.unlink()
        print("✓ Removed old database")
    
    # Import models to register them with SQLModel
    try:
        from app.models import ChatSession, Message
        from app.models.user import User
        print("✓ Imported models successfully")
    except Exception as e:
        print(f"⚠ Error importing models: {e}")
        print("⚠ Falling back to manual table creation")
        return manual_recreate_db()
    
    # Create engine
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    # Drop all tables
    SQLModel.metadata.drop_all(engine)
    print("✓ Dropped all existing tables")
    
    # Create all tables from models
    SQLModel.metadata.create_all(engine)
    print("✓ Created all tables from models")
    
    # Create a test user
    with Session(engine) as session:
        test_user = User(
            email="test@example.com",
            username="testuser",
            firstname="Test",
            lastname="User",
            hashed_password="test_password_hash"
        )
        session.add(test_user)
        session.commit()
        print(f"✓ Created test user: {test_user.username}")
    
    print("\n✅ Database recreated successfully from models!")


def manual_recreate_db():
    """Fallback: Create database with manual SQL."""
    import sqlite3
    
    db_path = Path("ai_desk.db")
    if db_path.exists():
        db_path.unlink()
        print("✓ Removed old database")
    
    db_path.touch()
    conn = sqlite3.connect("ai_desk.db")
    cursor = conn.cursor()
    
    # Create tables manually
    cursor.execute("""
        CREATE TABLE user (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            email VARCHAR NOT NULL UNIQUE,
            username VARCHAR NOT NULL UNIQUE,
            firstname VARCHAR NOT NULL,
            lastname VARCHAR NOT NULL,
            hashed_password VARCHAR NOT NULL,
            user_role VARCHAR DEFAULT 'user',
            created_at VARCHAR DEFAULT '',
            is_active BOOLEAN NOT NULL DEFAULT 1,
            locked BOOLEAN NOT NULL DEFAULT 0,
            failed_login_attempts INTEGER DEFAULT 0
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
        INSERT INTO user (email, username, firstname, lastname, hashed_password)
        VALUES (?, ?, ?, ?, ?)
    """, ("test@example.com", "testuser", "Test", "User", "test_password_hash"))
    print("✓ Created test user")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database recreated successfully (manual)!")


if __name__ == "__main__":
    recreate_db()
