import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Settings():
    # Database configurations
    DB_HOST: str = os.environ["DB_HOST"]
    DB_PORT: int = os.environ["DB_PORT"]
    DB_USER: str = os.environ["DB_USER"]
    DB_PASSWORD: str = open(os.environ["DB_PASSWORD_FILE"], "r").read().strip()
    DB_NAME: str = os.environ["DB_NAME"]

    # Application configurations
    JWT_SECRET_KEY = open(os.environ["JWT_SECRET_FILE"], "r").read().strip()

# Instantiate the settings
settings = Settings()