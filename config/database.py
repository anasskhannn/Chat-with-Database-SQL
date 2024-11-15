from sqlalchemy import create_engine
import sqlite3
from langchain.sql_database import SQLDatabase

class DatabaseConfig:
    """Handles database connection logic."""

    @staticmethod
    def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
        if db_uri == "USE_LOCALDB":
            dbfilepath = "student.db"  # Path to your local SQLite DB
            creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
            return SQLDatabase(create_engine("sqlite:///", creator=creator))
        elif db_uri == "USE_MYSQL":
            if not (mysql_host and mysql_user and mysql_password and mysql_db):
                raise ValueError("Please provide all MySQL connection details.")
            return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
        else:
            raise ValueError("Invalid database URI provided.")
