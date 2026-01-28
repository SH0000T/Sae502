#!/bin/bash

echo "🔄 Redémarrage d'AdSecureCheck..."

# Arrête tout
./stop.sh

# Attend 5 secondes
sleep 5

# Relance
docker compose up -d backend database
cd frontend && nohup npm start > /dev/null 2>&1 &

echo "✅ Services redémarrés"
echo "🌐 Frontend : http://localhost:3000"
echo "🔌 API      : http://localhost:5000"
