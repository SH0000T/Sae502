#!/bin/bash

echo "========================================="
echo "TEST COMPLET DU SCANNER AD AVEC EMAIL"
echo "========================================="
echo ""

# Configuration
AD_SERVER="192.168.80.2"
AD_SERVER_FQDN="adsecure.adsecure.local"
AD_DOMAIN="adsecure.local"
AD_USERNAME="Administrateur"
AD_PASSWORD="TC7PII%IUT"
EMAIL_TO="evanchezlui42@gmail.com"

# Nettoyage
AD_SERVER="$(echo -n "$AD_SERVER" | tr -d '\r\n')"
AD_SERVER_FQDN="$(echo -n "$AD_SERVER_FQDN" | tr -d '\r\n')"

echo "Configuration:"
echo "  Server: $AD_SERVER"
echo "  Domain: $AD_DOMAIN"
echo "  Email: $EMAIL_TO"
echo ""

read -p "Lancer le scan avec envoi d'email ? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Test annulé."
    exit 1
fi

echo ""
echo "========================================="
echo "Lancement du scan..."
echo "========================================="

RESPONSE=$(curl -s -X POST http://localhost:5000/api/scans/start \
  -H "Content-Type: application/json" \
  -d "{
    \"ad_server\": \"$AD_SERVER\",
    \"ad_domain\": \"$AD_DOMAIN\",
    \"ad_username\": \"$AD_USERNAME\",
    \"ad_password\": \"$AD_PASSWORD\",
    \"use_ssl\": false,
    \"send_email\": true,
    \"email_to\": \"$EMAIL_TO\"
  }")

echo "$RESPONSE" | jq .

SCAN_ID=$(echo "$RESPONSE" | jq -r '.scan.id // empty')

if [ -z "$SCAN_ID" ]; then
    echo ""
    echo "❌ Erreur: Scan échoué"
    exit 1
fi

echo ""
echo "✅ Scan créé avec l'ID: $SCAN_ID"
echo ""

# Attends un peu pour le traitement
echo "Attente de la fin du scan..."
sleep 5

# Récupère les détails
echo ""
echo "========================================="
echo "Détails du scan:"
echo "========================================="
curl -s http://localhost:5000/api/scans/$SCAN_ID | jq '.scan'

# Télécharge les rapports
echo ""
echo "========================================="
echo "Téléchargement des rapports locaux..."
echo "========================================="

mkdir -p ~/rapports_ad

echo "Téléchargement du rapport TXT..."
curl -s http://localhost:5000/api/scans/$SCAN_ID/download/text -o ~/rapports_ad/rapport_$SCAN_ID.txt
if [ -f ~/rapports_ad/rapport_$SCAN_ID.txt ]; then
    echo "✅ Rapport TXT téléchargé: ~/rapports_ad/rapport_$SCAN_ID.txt"
fi

echo "Téléchargement du rapport CSV..."
curl -s http://localhost:5000/api/scans/$SCAN_ID/download/csv -o ~/rapports_ad/rapport_$SCAN_ID.csv
if [ -f ~/rapports_ad/rapport_$SCAN_ID.csv ]; then
    echo "✅ Rapport CSV téléchargé: ~/rapports_ad/rapport_$SCAN_ID.csv"
fi

echo "Téléchargement du rapport HTML..."
curl -s http://localhost:5000/api/scans/$SCAN_ID/download/html -o ~/rapports_ad/rapport_$SCAN_ID.html
if [ -f ~/rapports_ad/rapport_$SCAN_ID.html ]; then
    echo "✅ Rapport HTML téléchargé: ~/rapports_ad/rapport_$SCAN_ID.html"
fi

echo ""
echo "========================================="
echo "✅ Test terminé !"
echo "========================================="
echo ""
echo "📁 Rapports disponibles dans: ~/rapports_ad/"
echo "📧 Email envoyé à: $EMAIL_TO"
echo ""
echo "Pour voir le rapport texte:"
echo "  cat ~/rapports_ad/rapport_$SCAN_ID.txt"
echo ""
echo "Pour ouvrir le rapport HTML:"
echo "  firefox ~/rapports_ad/rapport_$SCAN_ID.html"
