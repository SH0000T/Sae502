FROM python:3.11-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les dépendances
COPY requirements.txt .

# Installe les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    krb5-user \
    && rm -rf /var/lib/apt/lists/*

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de l'application
COPY . .

# Crée le dossier reports
RUN mkdir -p /app/reports

# Expose le port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app.py"]
