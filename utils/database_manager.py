import sqlite3
import os

class SQLiteManager:
    def __init__(self, db_path="data/student.db"):
        """
        Initialize the SQLiteManager with the specified database path.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        print(f"Connected to database: {self.db_path}")

    def execute_query(self, query, params=()):
        """
        Execute a query on the database.
        :param query: SQL query string.
        :param params: Tuple of parameters for the query.
        :return: Query results if it's a SELECT query, else None.
        """
        if not self.connection:
            raise ConnectionError("No database connection established.")
        
        start_time = time.time()
        self.cursor.execute(query, params)
        end_time = time.time()
        
        print(f"Query executed in {end_time - start_time:.2f} seconds")
        
        if query.strip().upper().startswith("SELECT"):
            return self.cursor.fetchall()
        else:
            self.connection.commit()

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def switch_database(self, new_db_path):
        """
        Switch to a different SQLite database.
        :param new_db_path: Path to the new SQLite database file.
        """
        self.close_connection()
        self.db_path = new_db_path
        self.connect()
        print(f"Switched to database: {new_db_path}")

# Example usage:
if __name__ == "__main__":
    db_manager = SQLiteManager()

    try:
        db_manager.connect()

        # Example query: Create table if not exists
        create_table_query = """
        CREATE TABLE IF NOT EXISTS STUDENT(
            NAME VARCHAR(25),
            CLASS VARCHAR(25),
            SECTION VARCHAR(25),
            MARKS INT
        )
        """
        db_manager.execute_query(create_table_query)

        # Insert example
        insert_query = "INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?)"
        db_manager.execute_query(insert_query, ("Jane Doe", "Data Science", "A", 95))

        # Fetch example
        select_query = "SELECT * FROM STUDENT"
        records = db_manager.execute_query(select_query)
        print("Records:", records)

    finally:
        db_manager.close_connection()
