from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_URL = os.getenv("API_URL")
STUDENT_URL = os.getenv("STUDENT_URL")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")