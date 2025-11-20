from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Pydantic leerá esto de las variables de entorno de Docker automáticamente
    DATABASE_URL: str

    class Config:
        case_sensitive = True

settings = Settings()
