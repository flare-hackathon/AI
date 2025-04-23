import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Centralized config for environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_BROKER = os.getenv("REDIS_BROKER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") 

