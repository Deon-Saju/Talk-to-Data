import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "data/olist.db"
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.8-flash")
MAX_ROWS = 50