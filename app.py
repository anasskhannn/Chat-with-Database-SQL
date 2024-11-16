import streamlit as st
from utils.database_manager import SQLiteManager

# Initialize SQLiteManager
db_manager = SQLiteManager()

# Sidebar for database switching
st.sidebar.title("Database Management")
db_path = st.sidebar.text_input("Database Path", value="data/student.db")

# Switch database
if st.sidebar.button("Switch Database"):
    try:
        db_manager.switch_database(db_path)
        st.sidebar.success(f"Switched to database: {db_path}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# Example query execution
if st.button("Show Records"):
    try:
        records = db_manager.execute_query("SELECT * FROM STUDENT")
        st.write(records)
    except Exception as e:
        st.error(f"Error: {e}")
