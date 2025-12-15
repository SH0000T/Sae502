#!/bin/bash

echo "========================================="
echo "TEST COMPLET DU SCANNER AD"
echo "========================================="
echo ""

# ATTENTION: Remplace ces valeurs par ton AD de test réel
AD_SERVER="adsecure.adsecure.local"
AD_DOMAIN="adsecure.local"
AD_USERNAME="Administrateur"
AD_PASSWORD="TC7PII%IUT"

echo "⚠️  IMPORTANT: Modifie les credentials dans le script avant de lancer !"
echo ""
echo "Configuration actuelle:"
echo "  Server: $AD_SERVER"
echo "  Domain: $AD_DOMAIN"
echo "  Username: $AD_USERNAME"
echo ""

read -p "Continuer avec ces paramètres ? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Test annulé. Modifie les variables dans le script."
    exit 1
fi

echo ""
echo "1. Test de l'API health..."
curl -s http://localhost:5000/api/health | jq .

echo ""
echo "========================================="
echo "2. Lancement d'un scan complet..."
echo "========================================="

RESPONSE=$(curl -s -X POST http://localhost:5000/api/scans/start \
  -H "Content-Type: application/json" \
  -d "{
    \"ad_server\": \"$AD_SERVER\",
    \"ad_domain\": \"$AD_DOMAIN\",
    \"ad_username\": \"$AD_USERNAME\",
    \"ad_password\": \"$AD_PASSWORD\",
    \"use_ssl\": false
  }")

echo "$RESPONSE" | jq .

# Extraire l'ID du scan
SCAN_ID=$(echo "$RESPONSE" | jq -r '.scan.id // empty')

if [ -z "$SCAN_ID" ]; then
    echo ""
    echo "❌ Erreur: Impossible de récupérer l'ID du scan"
    echo "Vérifiez les credentials et que l'AD est accessible"
    exit 1
fi

echo ""
echo "✅ Scan créé avec l'ID: $SCAN_ID"

echo ""
echo "========================================="
echo "3. Récupération des détails du scan..."
echo "========================================="

sleep 2

curl -s http://localhost:5000/api/scans/$SCAN_ID | jq .

echo ""
echo "========================================="
echo "4. Statistiques globales..."
echo "========================================="

curl -s http://localhost:5000/api/scans/stats | jq .

echo ""
echo "========================================="
echo "✅ Test terminé !"
echo "========================================="
