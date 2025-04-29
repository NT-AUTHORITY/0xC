"""
Database initialization script for the 0xC Chat application.

This script creates the database tables and optionally adds some sample data.
"""

import os
from app import create_app
from database import db
from models import User, Message

def init_db(with_sample_data=False):
    """Initialize the database and optionally add sample data."""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        print("Database tables created successfully.")
        
        # Add sample data if requested
        if with_sample_data:
            add_sample_data()
            print("Sample data added successfully.")

def add_sample_data():
    """Add sample users and messages to the database."""
    # Check if we already have users
    if db.session.query(User).count() > 0:
        print("Sample data already exists. Skipping.")
        return
    
    # Create sample users
    admin = User.register("admin", "admin123", "admin@example.com")
    user1 = User.register("user1", "password123", "user1@example.com")
    user2 = User.register("user2", "password123", "user2@example.com")
    
    # Create sample messages
    Message.add(admin.id, "Welcome to 0xC Chat!")
    Message.add(user1.id, "Hello, world!")
    Message.add(user2.id, "This is a test message.")
    Message.add(admin.id, "Feel free to explore the API.")
    
    print(f"Created {db.session.query(User).count()} sample users.")
    print(f"Created {db.session.query(Message).count()} sample messages.")

if __name__ == "__main__":
    # Check if we should add sample data
    sample_data = os.environ.get("SAMPLE_DATA", "0") == "1"
    
    # Initialize the database
    init_db(with_sample_data=sample_data)
