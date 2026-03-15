import os

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ESSENTIAL_DAILY_LIMIT = 2
