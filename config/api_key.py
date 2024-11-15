from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """Configuration class to load environment variables and settings."""

    @property
    def groq_api_key(self):
        """Get the Groq API key from environment variables."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing from the environment variables.")
        return api_key
