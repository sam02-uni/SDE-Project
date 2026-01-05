# Base image
FROM python:3.11-slim

# Imposta cartella di lavoro
WORKDIR /app

# Copia solo requirements e installa dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NOTA: non copio il codice. Lo montiamo tramite volume in docker-compose

# Comando per partire con reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]