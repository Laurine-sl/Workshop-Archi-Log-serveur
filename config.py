import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    API_URL = os.getenv('API_URL')
    PORT = int(os.getenv('PORT'))
    SECRET_TOKEN = os.getenv('SECRET_TOKEN')