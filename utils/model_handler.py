import time
import os
from groq import Groq

class ModelHandler:
    def __init__(self):
        """
        Initialize the LLM client and model configuration.
        """
        self.llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "llama3-8b-8192"

    def process_and_execute_with_explanation(self, db_manager, natural_language_query):
        try:
            # Generate SQL query from natural language input
            llm_response = self.llm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an assistant that generates SQL queries."},
                    {"role": "user", "content": f"Generate a SQL query for: {natural_language_query}"}
                ],
                model=self.model_name,
            )
            sql_query = llm_response.choices[0].message.content.strip()

            # Record response time and execute the query
            start_time = time.time()
            results = db_manager.execute_query(sql_query)
            response_time = time.time() - start_time

            # Generate explanation for the SQL query
            explanation_response = self.llm_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an assistant that explains SQL query generation."},
                    {"role": "user", "content": f"Explain how the SQL query was generated for: {natural_language_query}"}
                ],
                model=self.model_name,
            )
            explanation = explanation_response.choices[0].message.content.strip()

            # Return exactly 4 values
            return results, response_time, sql_query, explanation

        except Exception as e:
            print(f"Error during query processing: {e}")
            return None, None, None, None