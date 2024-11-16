from utils.model_handler import ModelHandler

# Initialize the ModelHandler
model_handler = ModelHandler()

# Test natural language input
user_input = "Show me all students who scored more than 80 marks in the database."
sql_query = model_handler.process_query(user_input)

print("Generated SQL Query:", sql_query)
