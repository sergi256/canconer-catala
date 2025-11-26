FROM python:3.11-alpine

LABEL maintainer="Sergi"
LABEL description="Cançoner Català - Bibliografia database"

WORKDIR /app

# Dependències del sistema
RUN apk add --no-cache gcc musl-dev linux-headers

# Dependències Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar estructura del projecte
COPY app.py .
COPY config.py .
COPY backend/ ./backend/
COPY db/ ./db/

# Usuari no-root
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

# Port
EXPOSE 5000

# Variables d'entorn
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Executar
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]