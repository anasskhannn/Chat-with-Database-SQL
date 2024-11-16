import streamlit as st
from utils.database_manager import SQLiteManager
from utils.model_handler import ModelHandler

# Initialize SQLiteManager
db_manager = SQLiteManager()  # Create SQLite manager instance
model_handler = ModelHandler()  # Create ModelHandler instance


# Streamlit app interface
st.title("Chat with Database")

query = st.text_input("Enter your query:")

if query:
    result, execution_time = model_handler.process_query(query)
    st.write("Query Results:", result)
    st.write(f"Response Time: {execution_time:.2f} seconds")

# Assuming db_manager is already initialized

result, response_time, sql_query, explanation = model_handler.process_and_execute_with_explanation(
    db_manager=db_manager,
    natural_language_query=query
)

if result is not None:
    st.write(f"**Query Result:** {result}")
    st.write(f"**SQL Query Generated:** {sql_query}")
    st.write(f"**Explanation:** {explanation}")
    st.write(f"**Response Time:** {response_time:.2f} seconds")
else:
    st.error("There was an issue processing the query.")



    

# Sidebar for database switching
st.sidebar.title("Database Management")
db_path = st.sidebar.text_input("Database Path", value="data/student.db")


# User input
user_input = st.text_input("Ask your question in natural language:")

if st.button("Submit"):
    if user_input.strip():
        result, response_time, sql_query = model_handler.process_and_execute_with_explanation(db_manager, user_input)
        if result is not None:
            st.write("**Generated SQL Query:**", sql_query)
            st.write("**Query Result:**")
            st.table(result)
            st.write(f"**Response Time:** {response_time:.2f} seconds")
        else:
            st.error("Error executing query.")
    else:
        st.warning("Please enter a valid question.")

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
