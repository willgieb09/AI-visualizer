from dotenv import load_dotenv, find_dotenv
import os

print("Found .env at:", find_dotenv())

load_dotenv()

print("Loaded key:", os.getenv("GENAI_API_KEY"))
