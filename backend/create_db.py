"""
Database initialization script for Retail Analytics Platform
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_database():
    """Create the retail_analytics database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="password",  # Change this to your PostgreSQL password
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'retail_analytics'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('CREATE DATABASE retail_analytics')
            print("✅ Database 'retail_analytics' created successfully!")
        else:
            print("ℹ️ Database 'retail_analytics' already exists.")
            
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        print("📝 Make sure PostgreSQL is running and credentials are correct")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
