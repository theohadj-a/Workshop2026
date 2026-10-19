FROM python:3.13-slim

# Variables d'environnement standard
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Durcissement de sécurité : création d'un utilisateur non-root
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source applicatif
COPY app/ ./app/

# Création du dossier pour la base SQLite et attribution des permissions
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Bascule vers l'utilisateur non privilégié
USER appuser

EXPOSE 8000

# Contrôle de santé Docker
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; sys_exit = 0 if urllib.request.urlopen('http://localhost:8000/health').getcode() == 200 else 1; exit(sys_exit)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
