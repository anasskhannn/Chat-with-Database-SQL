🚀 SQL Chat App
Query your SQLite or MySQL databases with natural language using this sleek Streamlit app, powered by LangChain 🗄️

---

## Features

Available Now ✅

- [x] 🗄️ Connect to SQLite or MySQL databases.

- [x] 💬 Query databases using natural language (e.g., "Show all customers").

- [x] 📊 Visualize results with interactive bar charts (triggered by "visualize" or "chart").

- [x] 📜 View and download query history as CSV.gz or JSON.

- [x] 🖥️ User-friendly UI with database selection and query history sidebar.

---

## Coming Soon 🔜


- [ ] 📋 Query suggestions based on table names.

- [ ] 🔍 Advanced query validation (e.g., limit JOINs, subqueries).

- [ ] ⚡ Query caching for faster responses.

- [ ] 🧠 Context memory for follow-up queries.

- [ ] 💾 Session persistence (save history across sessions).

- [ ] 🧩 Modular codebase for easier maintenance.

## 🛠️ Setup
1. Clone the Repository
```
git clone https://github.com/anasskhannn/Chat-with-Database-SQL
cd Chat-with-Database-SQL
```

2. Install Dependencies
pip install streamlit langchain langchain-groq sqlalchemy pymysql pandas plotly

3. Set Up a Database

- SQLite 🗃️:
Place `.db`, `.sqlite`, or `.sqlite3` files in database/local/.


- MySQL 🐬:
Use a local MySQL server or run a
Docker container:
```
docker run -d -p 3306:3306 --name mysql-container \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=mydb \
  mysql:latest
```
    Connection Details:
    Host: localhost
    User: root
    Password: root
    Database: mydb

4. Get a Groq API Key 🔑

Sign up at GROQ CLoud for a Groq API key.
Set it as GROQ_API_KEY or enter it in the app.

5. Run the App 🎉
`streamlit run app.py`

---
## 📖 Usage

- Open the app (http://localhost:8501).
- In the sidebar:
    1. Choose SQLite or MySQL.
    2. For SQLite, select a database file.
    3. For MySQL, enter host, user, password, and database.
    4. Input your Groq API key (if not set).


Type a query (e.g., "List all orders" or "Visualize sales").
View results, SQL code, and charts.
Check query history or download as CSV.gz or JSON.

### 💡 Tips

Ensure SQLite files are readable and MySQL credentials are valid.

Use "visualize" or "chart" for bar charts (requires numeric data).

Stop Docker MySQL with:
`docker stop mysql-container`

---

## 🛠️ Tech Stack

Python 🐍: Core language.
Streamlit 🌐: Web app framework.
LangChain 🔗: Natural language to SQL.
Groq 🤖: Llama-3.3-70b model.
SQLAlchemy 🗄️: Database connectivity.
MySQL/SQLite 🗃️: Database engines.
Pandas 📋: Data handling.
Plotly 📊: Visualizations.
Docker 🐳: MySQL containerization.

---

## Structure Of the Code Base
```
├── Chat-with-Database-SQL
|   .env
|   .gitignore
|   api_key.py
|   app.py
|   docker-compose.yml
|   README.md
|   requirements.txt
|   structure.txt
|           
+---database
|   |   
|   +---local
|   |       test.db
|   +---my_sql
|   |       my_sql_databases.db 
+---data_source
|   |   README.md
|   |   |   local_source
|   |   |   |   test.sql
|   |   |   mysql_source    
|   |   |   |   test.sql
```
--- 
Made with Love ❤️ by [Mohd Anas Khan](https://github.com/anasskhannn)