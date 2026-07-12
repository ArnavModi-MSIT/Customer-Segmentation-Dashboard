import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "username": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "olist_project"),
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")