import os


class Settings:
    # Database configurations
    DB_HOST: str = os.environ["DB_HOST"]
    DB_PORT: int = os.environ["DB_PORT"]
    DB_USER: str = os.environ["DB_USER"]
    DB_PASSWORD: str = os.environ["DB_PASSWORD"]
    DB_NAME: str = os.environ["DB_NAME"]

    # Application configurations
    JWT_SECRET_KEY = os.environ["JWT_SECRET"]


# Instantiate the settings
settings = Settings()
