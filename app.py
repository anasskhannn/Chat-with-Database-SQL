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
import io
import pandas as pd

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
        dbfilepath = (Path(__file__).parent / "data/student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))

    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()

        try:
            mysql_host = mysql_host.strip()
            if '@' in mysql_host:
                raise ValueError("Host cannot contain '@' symbol.")
            if ":" in mysql_host:
                host, port = mysql_host.rsplit(":", 1)
                if not port.isdigit():
                    raise ValueError("Port must be numeric.")
            else:
                host = mysql_host
                port = "3306"  

            encoded_password = quote_plus(mysql_password)
            connection_string = f"mysql+pymysql://{mysql_user}:{encoded_password}@{host}:{port}/{mysql_db}"

            engine = create_engine(connection_string)
            with engine.connect() as conn:
                st.write("Successfully connected to MySQL.")
            return SQLDatabase(engine)
        except Exception as e:
            st.error(f"MySQL Connection Error: {str(e)}")
            st.stop()

if db_uri == MYSQL:
    db = configure_db(db_uri=db_uri,
                      mysql_host=mysql_host,
                      mysql_user=mysql_user,
                      mysql_password=mysql_password,
                      mysql_db=mysql_db)
else:
    db = configure_db(db_uri)

schema = db.get_table_names()
st.write("Database Schema:\n", schema)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent (
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True 
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    # Store query history
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    st.session_state.query_history.append({"query": user_query, "result": ""})

    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    # Process and run the query with schema hint
    schema_hint = f"Database schema includes tables: {', '.join(schema)}."
    query_with_hint = f"{schema_hint}\nAnswer the question: {user_query}"
    
    response = agent.run(query_with_hint)

    # Store the result
    st.session_state.query_history[-1]["result"] = response

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.write(response)

    # CSV export
    if len(st.session_state.query_history) > 0:
        last_result = pd.DataFrame([st.session_state.query_history[-1]["result"]])  
        csv_data = last_result.to_csv(index=False)
        st.download_button(
            label="Download Last Query Results as CSV",
            data=csv_data,
            file_name="query_result.csv",
            mime="text/csv"
        )
