import os
from dotenv import load_dotenv
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MONGODB_SETTINGS = {
        'db': 'meetAppDb',
        'host':os.environ.get('DATABASE_URL') 
    }
