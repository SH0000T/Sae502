#!/bin/bash

echo "🛑 Arrêt d'AdSecureCheck..."

# Arrête Docker
docker compose down

# Arrête le frontend
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null
    rm .frontend.pid
    echo "✅ Frontend arrêté"
fi

echo "✅ Tous les services sont arrêtés"
