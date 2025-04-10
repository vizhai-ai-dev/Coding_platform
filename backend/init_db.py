#!/usr/bin/env python3
"""
Database initialization script.
Run this script to create the database tables.
"""

from database.db import engine
from database.models import Base
from sqlalchemy import inspect
import sqlite3

def add_column_if_not_exists(conn, table_name, column_name, column_type):
    """Add a column to a table if it doesn't exist"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        print(f"Added column {column_name} to table {table_name}")

def main():
    # Create tables
    inspector = inspect(engine)
    if not inspector.has_table("problems"):
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    else:
        print("Database tables already exist, checking for migrations...")
        
        # Add any missing columns (for migrations)
        conn = sqlite3.connect('coding_platform.db')
        add_column_if_not_exists(conn, 'problems', 'starter_code', 'TEXT')
        conn.commit()
        conn.close()
        
        print("Database migration completed!")

if __name__ == "__main__":
    main() 