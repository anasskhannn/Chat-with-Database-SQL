import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq
from urllib.parse import quote_plus
import pymysql
from api_key import groq_api_key

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLite 3 Database", "Connect to your MySQL Database"]

selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq API Key", type="password")

if not db_uri:
    st.info("Please enter the database information and URI.")

if not api_key:
    st.info("Please add the Groq API key.")

# LLM Model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192", streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        # SQLite setup
        dbfilepath = (Path(__file__).parent / "data/student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))

    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()

        try:
            # Clean and validate host
            mysql_host = mysql_host.strip()
            if '@' in mysql_host:
                raise ValueError("Host cannot contain '@' symbol.")
            
            # Handle host and port
            if ":" in mysql_host:
                host, port = mysql_host.rsplit(":", 1)
                if not port.isdigit():
                    raise ValueError("Port must be numeric.")
            else:
                host = mysql_host
                port = "3306"  # Default MySQL port
            
            # URL encode password to handle special characters
            encoded_password = quote_plus(mysql_password)
            
            # Build MySQL connection string
            connection_string = f"mysql+pymysql://{mysql_user}:{encoded_password}@{host}:{port}/{mysql_db}"
            st.write(f"Connecting to MySQL with connection string: {connection_string}")

            # Create SQLAlchemy engine
            engine = create_engine(connection_string)

            # Test the connection using a simple query:
            with engine.connect() as conn:
                st.write("Successfully connected to MySQL.")
                # We don't need to execute a SELECT query here, we just want to confirm the connection works.

            # Return the database connection wrapped with SQLDatabase
            return SQLDatabase(engine)

        except Exception as e:
            st.error(f"MySQL Connection Error: {str(e)}")
            st.stop()

# Main database connection logic
if db_uri == MYSQL:
    db = configure_db(db_uri=db_uri,
                      mysql_host=mysql_host,
                      mysql_user=mysql_user,
                      mysql_password=mysql_password,
                      mysql_db=mysql_db)
else:
    db = configure_db(db_uri)

# Get schema of the database
schema = db.get_table_names()
st.write("Database Schema:\n", schema)

# Allow the user to preview table contents
selected_table = st.sidebar.selectbox("Select a table to preview its contents", ["None"] + schema)
if selected_table != "None":
    try:
        query = f"SELECT * FROM {selected_table} LIMIT 10"
        preview_data = db.run_query(query)
        st.write(f"Preview of `{selected_table}`:")
        st.write(preview_data)
    except Exception as e:
        st.error(f"Error fetching data from `{selected_table}`: {e}")

# Initialize toolkit and agent for interacting with the database
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)

# Initialize session state for storing chat messages
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Accept user query and process it
user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    # Provide context to the LLM
    query_with_hint = f"""
    You are interacting with a database that contains the following tables: {', '.join(schema)}.
    Use this schema information to answer the user's question accurately.
    The user query is: {user_query}
    """

    try:
        with st.chat_message("assistant"):
            streamlit_callback = StreamlitCallbackHandler(st.container())
            
            # Log the agent's actions for debugging
            st.info("Generating SQL query...")

            # Run the query
            response = agent.run(query_with_hint, callbacks=[streamlit_callback])

            # Display the query and result
            st.write("SQL Query Generated and Executed:")
            st.code(response, language="sql")  # Show query or agent output
            st.session_state.messages.append({"role": "assistant", "content": response})
    except ValueError as ve:
        # Handle parsing issues
        st.error("Parsing issue with the response. The agent may have misunderstood the query.")
        st.exception(ve)
    except Exception as e:
        # Handle general errors
        st.error("An unexpected error occurred while processing your request.")
        st.exception(e)

# Enhanced Debugging Options
if st.sidebar.checkbox("Debugging Mode"):
    st.write("Debugging Information:")
    st.write("Available Schema:")
    st.json(schema)
    st.write("Session Messages:")
    st.json(st.session_state.messages)

