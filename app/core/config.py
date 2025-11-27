"""
Módulo de configuración de la aplicación.

Este módulo define las configuraciones principales de la aplicación, incluyendo la configuración
de la base de datos y la seguridad. Utiliza Pydantic para cargar las configuraciones desde
variables de entorno, asegurando flexibilidad y facilidad de uso en diferentes entornos
(desarrollo, pruebas, producción).
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Clase que define las configuraciones principales de la aplicación.

    Atributos:
        DATABASE_URL (str): URL de conexión a la base de datos. Debe ser proporcionada como
            una variable de entorno.
        SECRET_KEY (str): Clave secreta utilizada para firmar y verificar tokens JWT.
        ALGORITHM (str): Algoritmo utilizado para la codificación de los tokens JWT.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Tiempo de expiración de los tokens de acceso en minutos.
    """

    # --- Configuración de Base de Datos ---
    # Pydantic buscará una variable de entorno llamada DATABASE_URL.
    # Como no tiene valor por defecto, si no la encuentra, lanzará error.
    # Esto asegura que siempre se proporcione una URL válida para la base de datos.
    DATABASE_URL: str

    # --- Configuración de Seguridad ---
    # SECRET_KEY: Clave secreta utilizada para firmar y verificar tokens JWT.
    # ALGORITHM: Algoritmo utilizado para la codificación de los tokens JWT.
    # ACCESS_TOKEN_EXPIRE_MINUTES: Tiempo de expiración de los tokens de acceso en minutos.
    # Nota: En producción, es importante configurar SECRET_KEY como una variable de entorno segura.
    SECRET_KEY: str = "tu_secreto_super_seguro_cambialo_en_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5

    class Config:
        """
        Configuración adicional para Pydantic.

        Atributos:
            case_sensitive (bool): Hace que las variables de entorno sean sensibles a mayúsculas y minúsculas.
        """
        # Configuración adicional para Pydantic.
        case_sensitive = True

# Instanciamos la clase Settings una sola vez para evitar múltiples inicializaciones.
# Esto permite acceder a las configuraciones de manera centralizada en toda la aplicación.
settings = Settings()
