import sqlite3
import time
from pathlib import Path

class SQLiteManager:
    def __init__(self, db_path=None):
        # Ensure that db_path defaults to the correct location
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data/student.db"
        
        self.db_path = db_path
        print(f"Database path is: {self.db_path}")
        
        # Call connect method to establish connection
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the SQLite database"""
        try:
            # Check if the database file exists
            if not self.db_path.exists():
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
            # Establish a connection to the database
            self.connection = sqlite3.connect(self.db_path)
            print(f"Connected to database: {self.db_path}")
        except FileNotFoundError as e:
            print(e)
            self.connection = None
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            self.connection = None

    def execute_query(self, query, params=None):
        """Execute a database query and return results."""
        if self.connection is None:
            raise Exception("No database connection established.")

        try:
            start_time = time.time()

            cursor = self.connection.cursor()
            cursor.execute(query, params or [])
            self.connection.commit()

            execution_time = time.time() - start_time
            print(f"Query executed in {execution_time:.2f} seconds")

            # Fetch and return the result if needed
            return cursor.fetchall()

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return []

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
