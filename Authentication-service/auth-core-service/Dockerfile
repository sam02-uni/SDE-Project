#  Base image
FROM python:3.11-slim

#  Imposta working directory
WORKDIR /app

#  Copia requirements e installa dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#  Copia tutto il codice
COPY . .

#Comando di avvio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
