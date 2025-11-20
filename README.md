rpa_orchestrator/
│
├── app/                  # Todo tu código fuente de Python vive aquí
│   ├── __init__.py
│   ├── main.py           # Punto de entrada de la app
│   ├── api/              # Aquí van los Endpoints (Rutas)
│   │   └── v1/           # Versionado de API (importante para el futuro)
│   ├── core/             # Configuraciones generales (Variables de entorno, seguridad)
│   ├── db/               # Conexión a base de datos
│   ├── models/           # Modelos de la Base de Datos (Tablas)
│   ├── schemas/          # Esquemas de Pydantic (Validación de datos entrada/salida)
│   └── services/         # Lógica de negocio (Aquí va la magia, no en los endpoints)
│
├── tests/                # Tests unitarios e integración
├── .gitignore
├── requirements.txt      # Dependencias de Python
├── Dockerfile            # La receta para construir tu imagen de Python
└── docker-compose.yml    # Orquestación de servicios (App + Base de Datos)