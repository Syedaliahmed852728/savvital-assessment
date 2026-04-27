from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROVIDER = "groq"  # "groq" or "ollama"


#  Paste your api key in the .env file as GROQ_API_KEY if chose 'groq' as provider
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "NONE")
GROQ_MODEL = "llama-3.1-8b-instant"  # set the model of your choice


OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"  # set the model name you have in your local Ollama instance


# llm basic parameters
TEMPERATURE = 0.0  # Low = more consistent, deterministic output
# (responses will be same for same input every time)
MAX_TOKENS = 1000  # Enough for structured JSON response
TIMEOUT = 60  # Seconds before request times out
MAX_RETRIES = 3  # Number of times to retry LLM call if it fails

# file paths
OUTPUT_FILE = SCREENSHOTS_DIR = os.path.join(BASE_DIR, "sample_output.json")
EVIDENCE_FILE = os.path.join(BASE_DIR, "evidence_log.docx")
CLIENTS_FILE = os.path.join(BASE_DIR, "clients.json")
