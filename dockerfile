# ── Dockerfile — Puente Lógico SAS BIC ────────────────────────────────────
# Imagen base: Python 3.11 liviana (slim reduce el tamaño de la imagen ~60%)
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y activa logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Cloud Run inyecta la variable PORT (por defecto 8080)
ENV PORT=8080

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero solo requirements.txt para aprovechar el cache de Docker:
# Si el código cambia pero las dependencias no, Docker no reinstala todo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Creamos el directorio de configuración de Streamlit
RUN mkdir -p /app/.streamlit

# Exponemos el puerto (documentación, Cloud Run usa la variable PORT)
EXPOSE 8080

# Comando de inicio:
# --server.port        usa la variable PORT de Cloud Run
# --server.address     escucha en todas las interfaces (requerido en contenedor)
# --server.headless    desactiva el prompt de email de Streamlit
# --server.enableCORS  permite que Cloud Run enrute correctamente
CMD streamlit run main.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
