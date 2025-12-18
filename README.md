# Social Security PDF Analyzer (IA-NAVANTIA)

## Descripción
API diseñada para automatizar el análisis de documentos PDF relacionados con cálculos de pensión de la Seguridad Social. Utilizando la tecnología de OpenAI, esta herramienta extrae información estructurada crítica para procesos de jubilación.

## Características Principales
- **Análisis de Jubilación Anticipada Voluntaria**:
  - Extracción de modalidad de jubilación.
  - Fechas relevantes (fecha de jubilación anticipada).
  - Cálculo de meses de anticipación.
  - Identificación del coeficiente reductor.
  - Extracción del importe de la pensión (14 pagas).

- **Análisis de Jubilación Parcial**:
  - Extracción de modalidad.
  - Importe de la pensión.
  - Fecha de jubilación parcial.
  - Porcentaje de reducción de jornada.

- **Arquitectura Robusta**: Construida sobre FastAPI para un alto rendimiento y fácil documentación.

## Estructura del Proyecto
```
IA_SERVICIOS/
├── app/
│   ├── api/            # Definición de rutas y endpoints
│   ├── application/    # Lógica de negocio y casos de uso
│   ├── domain/         # Modelos de datos y entidades
│   ├── infrastructure/ # Integraciones (Cliente OpenAI)
│   └── main.py         # Punto de entrada de la aplicación
├── requirements.txt    # Dependencias de Python
└── gunicorn.conf.py    # Configuración del servidor de producción
```

## Requisitos Previos
- Python 3.8 o superior
- Una clave de API de OpenAI válida

## Instalación

1. **Clonar el repositorio** (si aplica) o navegar al directorio del proyecto.

2. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv venv
   # En Linux/Mac:
   source venv/bin/activate
   # En Windows:
   venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

Crea un archivo `.env` en la raíz del proyecto basándote en el siguiente ejemplo:

```env
OPENAI_API_KEY=sk-tu-clave-api-aqui
OPENAI_MODEL=gpt-5-nano # Opcional, modelo por defecto
```

## Ejecución

### Servidor de Desarrollo
Para ejecutar la aplicación localmente con recarga automática:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Servidor de Producción (Gunicorn)
Para despliegues en producción utilizando Gunicorn:
```bash
gunicorn -c gunicorn.conf.py app.main:app
```

## Uso de la API

La API expone los siguientes endpoints principales:

- **Jubilación Anticipada**:
  - `POST /api/jubilacion/anticipada`
  - Body: `multipart/form-data` con el archivo PDF.

- **Jubilación Parcial**:
  - `POST /api/jubilacion/parcial`
  - Body: `multipart/form-data` con el archivo PDF.

### Documentación Interactiva
FastAPI genera automáticamente documentación interactiva. Una vez que el servidor esté en ejecución, puedes consultarla en:
- Swagger UI: `/ia_servicios/docs` (Dependiendo de tu configuración de proxy/host)

## Tecnologías Utilizadas
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno y rápido.
- [Uvicorn](https://www.uvicorn.org/) - Servidor ASGI.
- [OpenAI](https://github.com/openai/openai-python) - Cliente para modelos GPT.
- [Pydantic](https://docs.pydantic.dev/) - Validación de datos.
