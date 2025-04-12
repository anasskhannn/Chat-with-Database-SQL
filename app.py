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
import pandas as pd
from datetime import datetime
import os
import plotly.express as px
from langchain.callbacks.base import BaseCallbackHandler
import io
import gzip
import json

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

def get_available_databases(base_path="database/local"):
    project_root = Path(__file__).parent
    search_path = project_root / base_path
    db_files = []
    for ext in ['.db', '.sqlite', '.sqlite3']:
        db_files.extend(list(search_path.glob(f"*{ext}")))
    return [db.relative_to(project_root) for db in db_files]

@st.cache_resource
def configure_sqlite_db(selected_db):
    if not selected_db:
        st.error("No database selected")
        st.stop()
    dbfilepath = (Path(__file__).parent / selected_db).absolute()
    creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
    try:
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    except Exception as e:
        st.error(f"SQLite Connection Error: {str(e)}")
        st.stop()

@st.cache_resource
def configure_mysql_db(mysql_host, mysql_user, mysql_password, mysql_db):
    if not (mysql_host and mysql_user and mysql_password and mysql_db):
        st.error("Please provide all MySQL connection details.")
        st.stop()
    try:
        mysql_host = mysql_host.strip()
        if '@' in mysql_host:
            raise ValueError("Host cannot contain '@' symbol.")
        host, port = (mysql_host.rsplit(":", 1) if ":" in mysql_host else (mysql_host, "3306"))
        if not port.isdigit():
            raise ValueError("Port must be numeric.")
        encoded_password = quote_plus(mysql_password)
        connection_string = f"mysql+pymysql://{mysql_user}:{encoded_password}@{host}:{port}/{mysql_db}"
        engine = create_engine(connection_string)
        with engine.connect():
            pass
        return SQLDatabase(engine)
    except Exception as e:
        st.error(f"MySQL Connection Error: {str(e)}")
        st.stop()

# Initialize session state for database tracking
if "last_db" not in st.session_state:
    st.session_state["last_db"] = None

radio_opt = ["Use SQLite 3 Database", "Connect to your MySQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)
db_uri = MYSQL if selected_opt == radio_opt[1] else LOCALDB

if db_uri == MYSQL:
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
    current_db = f"mysql:{mysql_host}:{mysql_user}:{mysql_db}"
else:
    available_dbs = get_available_databases()
    if not available_dbs:
        st.error("No SQLite databases found!")
        st.stop()
    selected_db = st.sidebar.selectbox(
        "Select SQLite Database",
        options=available_dbs,
        format_func=lambda x: x.name
    )
    current_db = str(selected_db)

# Clear chat history if database changes
if st.session_state["last_db"] != current_db:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state["chat_history"] = []
    st.session_state["last_db"] = current_db

# API Key Handling
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input(label="Groq API Key ", type="password")
if not api_key:
    st.warning("Please provide a Groq API key via environment variable (GROQ_API_KEY) or input.")
    st.stop()

llm = ChatGroq(groq_api_key=api_key, model_name="Llama-3.3-70b-versatile", temperature=0.0, top_p=0.9)

# Configure database
if db_uri == MYSQL:
    db = configure_mysql_db(mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_sqlite_db(selected_db)

# Show connection success and table names
try:
    table_names = db.get_table_names()
    if not table_names:
        st.error("No tables found in the database.")
        st.stop()
    st.success("Successfully connected to the database!", icon="✅")
    st.markdown("**Available Tables**:")
    for table in table_names:
        st.markdown(f"- {table}")
except Exception as e:
    st.error(f"Error retrieving table names: {str(e)}")
    st.stop()

class SQLCaptureCallback(BaseCallbackHandler):
    def __init__(self):
        self.last_query = None

    def on_tool_start(self, serialized, input_str, **kwargs):
        if serialized.get('name') == 'sql_db_query':
            self.last_query = input_str

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)

def format_query_for_agent(user_query, schema):
    prompt = f"""
You are a SQL expert assisting with querying a database. The database schema includes tables: {', '.join(schema)}.

Instructions:
- Generate accurate SQL queries based on the user's question.
- Return results in a clear, tabular format if applicable.
- If the query might return no results, explain why.
- If the question is ambiguous, ask for clarification within the response.
- Avoid modifying the database (no INSERT, UPDATE, DELETE).
- Use LIMIT for large tables unless specified otherwise.

User Question: {user_query}

Provide the SQL query and a formatted answer.
"""
    return prompt

def validate_query(query):
    if not query:
        return False, "Empty query."
    if "SELECT *" in query.upper() and "WHERE" not in query.upper():
        return False, "Avoid SELECT * without WHERE for large tables."
    return True, ""

def display_query_result(response, query, user_query):
    try:
        if query and "SELECT" in query.upper() and any(keyword in user_query.lower() for keyword in ["visualize", "chart", "graph", "plot"]):
            result = db.run(query)
            if result:
                df = pd.DataFrame(eval(result) if isinstance(result, str) else result)
                st.dataframe(df)
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                if len(numeric_cols) > 0:
                    st.write("**Visualization**:")
                    fig = px.bar(df, x=df.columns[0], y=numeric_cols[0])
                    st.plotly_chart(fig)
        elif query and "SELECT" in query.upper():
            result = db.run(query)
            if result:
                df = pd.DataFrame(eval(result) if isinstance(result, str) else result)
                st.dataframe(df)
    except Exception as e:
        st.warning(f"Could not process result: {str(e)}")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

st.sidebar.subheader("Query History")
if st.session_state.chat_history:
    for idx, entry in enumerate(st.session_state.chat_history):
        with st.sidebar.expander(f"{entry['timestamp']}: {entry['user_query'][:30]}..."):
            st.write(f"**Query**: {entry['user_query']}")
            st.write(f"**SQL**: {entry['sql_query']}")
            st.write(f"**Response**: {entry['response'][:100]}...")
else:
    st.sidebar.info("No queries yet.")

user_query = st.chat_input(placeholder="Ask anything from the database")
if user_query:
    formatted_query = format_query_for_agent(user_query, table_names)
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)
    with st.chat_message("assistant"):
        sql_callback = SQLCaptureCallback()
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(formatted_query, callbacks=[streamlit_callback, sql_callback])
        query = sql_callback.last_query
        if query:
            is_valid, message = validate_query(query)
            if not is_valid:
                st.error(f"Query rejected: {message}")
                st.stop()
            st.write("**Generated SQL Query**:")
            st.code(query, language="sql")
        else:
            st.warning("No SQL query was generated for this request.")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
        display_query_result(response, query, user_query)
        st.session_state.chat_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_query": user_query,
            "sql_query": query or "N/A",
            "response": response[:500] + ("..." if len(response) > 500 else "")
        })

def to_csv_gz(chat_history):
    df = pd.DataFrame(chat_history)
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
        f.write(df.to_csv(index=False).encode())
    return buffer.getvalue()

def to_json(chat_history):
    return json.dumps(chat_history, ensure_ascii=False).encode()

csv_gz_data = to_csv_gz(st.session_state.chat_history)
json_data = to_json(st.session_state.chat_history)

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="Download Chat History as CSV (Compressed)",
        data=csv_gz_data,
        file_name="chat_history.csv.gz",
        mime="application/gzip"
    )
with col2:
    st.download_button(
        label="Download Chat History as JSON",
        data=json_data,
        file_name="chat_history.json",
        mime="application/json"
    )