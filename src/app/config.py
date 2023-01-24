from pydantic import BaseSettings

class Settings(BaseSettings):
    """Dotenv declaring model for parsing PostgreSQL .env configuration file

    Attributes:
        DATABASE_PORT: An integer with the PostgreSQL port.
        POSTGRES_PASSWORD: A string with the PostgreSQL password.
        POSTGRES_USER: A string with the PostgreSQL username.
        POSTGRES_DB: A string with the PostgreSQL database name.
        POSTGRES_HOST: A string with the PostgreSQL host IP.
        POSTGRES_HOSTNAME: A string with the PostgreSQL resolvable hostname.
    """
    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_HOSTNAME: str

    class Config:
        env_file = './.env'

settings = Settings()