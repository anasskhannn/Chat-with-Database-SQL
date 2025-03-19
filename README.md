This is the complete project chat with database in natural language using llm and ai agents.


# Milestones
- [x] Create a chat with sqlite connection with local db. 
- [x] Create a connection with mysql database.
- [x] Create option to download chat history.
- [x] Better Response quality for Easy Understanding of answer.
- [ ] Add context of previous to answer similar queries to reduce computation.
    - [ ] By adding a memory to local storage and retrieve the response of similar queries from there.

- [ ] Better UI
- [ ] Make the code base modular for readability and easy modifications.


# Modifications

- [ ] To remove double answers from natural language output
- [ ] To change location of download button 
- [ ] To make model better


## Structure Of the Code Base
```
D:.
|   .env
|   .gitignore
|   api_key.py
|   app.py
|   docker-compose.yml
|   README.md
|   requirements.txt
|   structure.txt
|           
+---data
|   |   README.md
|   |   
|   +---data_source
|   |   |   |   local_source
|   |   |   |   |   test.sql
|   |   |   |   mysql_source    
|   |   |   |   |   test.sql
|   |           
|   +---local
|   |       test.db
|   |       
|   +---my_sql
|   |   |   my_sql_databases.db 
```