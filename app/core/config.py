from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Configuración de Base de Datos (Lo que ya tenías) ---
    # Pydantic buscará una variable de entorno llamada DATABASE_URL.
    # Como no tiene valor por defecto, si no la encuentra, lanzará error (¡Bien!).
    DATABASE_URL: str

    # --- Configuración de Seguridad (Lo nuevo) ---
    # Estas sí tienen valor por defecto, así que si no existen en las env vars, usará estos valores.
    # En producción, deberías pasar SECRET_KEY también por variable de entorno.
    SECRET_KEY: str = "tu_secreto_super_seguro_cambialo_en_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True


# Instanciamos la clase una sola vez
settings = Settings()
