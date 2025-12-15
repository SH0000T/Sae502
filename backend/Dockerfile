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

# Copie la configuration OpenSSL pour activer MD4
COPY openssl.cnf /app/openssl.cnf

# Active MD4 via variable d'environnement
ENV OPENSSL_CONF=/app/openssl.cnf

# Crée le dossier reports
RUN mkdir -p /app/reports

# Expose le port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app.py"]
