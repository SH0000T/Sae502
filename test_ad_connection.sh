#!/bin/bash

echo "========================================="
echo "Test de connexion Active Directory"
echo "========================================="
echo ""

# Remplace ces valeurs par ton AD de test
AD_SERVER="ad.itsimvan.local"
AD_DOMAIN="itsimvan.local"
AD_USERNAME="Administrateur"
AD_PASSWORD="Sim3vanZlp42300"

echo "1. Test de connexion basique..."
curl -X POST http://localhost:5000/api/ad/test-connection \
  -H "Content-Type: application/json" \
  -d "{
    \"ad_server\": \"$AD_SERVER\",
    \"ad_domain\": \"$AD_DOMAIN\",
    \"ad_username\": \"$AD_USERNAME\",
    \"ad_password\": \"$AD_PASSWORD\",
    \"use_ssl\": false
  }" | jq .

echo ""
echo "========================================="
