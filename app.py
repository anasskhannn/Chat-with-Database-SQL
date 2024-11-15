import streamlit as st
from config.api_key import Config
from config.database import DatabaseConfig
from agents.sql_agent import create_sql_agent_instance
from langchain_groq import ChatGroq
from demo import groq_api_key
import sqlite3

# Streamlit app setup
st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

# Database choice
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"
radio_opt = ["Use SQLLite 3 Database", "Connect to your MySQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=radio_opt)

# Database and API Key Setup
db_uri = LOCALDB if radio_opt.index(selected_opt) == 0 else MYSQL
mysql_host = st.sidebar.text_input("MySQL Host")
mysql_user = st.sidebar.text_input("MySQL User")
mysql_password = st.sidebar.text_input("MySQL password", type="password")
mysql_db = st.sidebar.text_input("MySQL database")
api_key = st.sidebar.text_input(label="GRoq API Key", type="password")

if not api_key:
    st.info("Please add the Groq API key")

# Initialize Groq API
config = Config()
groq_api_key = config.groq_api_key
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192", streaming=True)

# Configure database
db = DatabaseConfig.configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)

# Create SQL Agent
agent = create_sql_agent_instance(db, llm)

# Chat Logic
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        response = agent.run(user_query)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
