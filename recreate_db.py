"""Script to recreate the database."""
import os
from sqlmodel import SQLModel, create_engine, Session
from app.models import ChatSession, Message, User

# Create engine directly
DATABASE_URL = "sqlite:///ai_desk.db"
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},
)

def recreate_db():
    """Drop all tables and recreate them."""
    # Drop all tables
    SQLModel.metadata.drop_all(engine)
    print("✓ Dropped all existing tables")
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("✓ Created all tables")
    
    # Create a test user
    with Session(engine) as session:
        test_user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="test_password_hash"
        )
        session.add(test_user)
        session.commit()
        print(f"✓ Created test user: {test_user.username}")
    
    print("\n✅ Database recreated successfully!")

if __name__ == "__main__":
    recreate_db()
