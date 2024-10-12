import os

class Settings:
    def __init__(self):
        # Database configurations
        self.DB_HOST: str = os.getenv("DB_HOST")
        self.DB_PORT: int = int(os.getenv("DB_PORT", "0"))
        self.DB_USER: str = os.getenv("DB_USER")
        self.DB_PASSWORD: str = os.getenv("DB_PASSWORD")
        self.DB_NAME: str = os.getenv("DB_NAME")
        
        # Application configurations
        self.JWT_SECRET_KEY: str = os.getenv("JWT_SECRET")

# Instantiate the settings
settings = Settings()