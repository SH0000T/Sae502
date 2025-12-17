#!/bin/bash

echo "========================================="
echo "Test de connexion Active Directory"
echo "========================================="
echo ""

# Configuration : IP et FQDN
AD_SERVER="192.168.80.2"
AD_SERVER_FQDN="adsecure.adsecure.local"
AD_DOMAIN="adsecure.local"
AD_USERNAME="Administrateur"
AD_PASSWORD="TC7PII%IUT"

# Nettoyage / normalisation du host (supprime CR/LF invisibles)
AD_SERVER="$(echo -n "$AD_SERVER" | tr -d '\r\n')"
AD_SERVER_FQDN="$(echo -n "$AD_SERVER_FQDN" | tr -d '\r\n')"

# Résolution IP si on a mis un FQDN (utile pour affichage)
AD_SERVER_IP="$(getent hosts "$AD_SERVER" | awk '{print $1}')"
if [ -z "$AD_SERVER_IP" ] && [[ "$AD_SERVER" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  AD_SERVER_IP="$AD_SERVER"
fi

if [ -n "$AD_SERVER_IP" ]; then
  echo "Resolved server -> $AD_SERVER_IP"
fi

echo "⚠️  IMPORTANT: Modifie les credentials dans le script avant de lancer !"
echo ""
echo "Configuration actuelle:"
echo "  Server (used first): $AD_SERVER"
echo "  Server (FQDN): $AD_SERVER_FQDN"
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

# Fonction pour tester la connexion
test_connection() {
  local server_val="$1"
  echo ""
  echo "-> Test de connexion avec le serveur: $server_val"
  
  RESPONSE=$(curl -s -X POST http://localhost:5000/api/ad/test-connection \
    -H "Content-Type: application/json" \
    -d "{
      \"ad_server\": \"$server_val\",
      \"ad_domain\": \"$AD_DOMAIN\",
      \"ad_username\": \"$AD_USERNAME\",
      \"ad_password\": \"$AD_PASSWORD\",
      \"use_ssl\": false
    }")
  
  echo "$RESPONSE" | jq .
  
  # Vérifie si la connexion a réussi
  SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
  echo "$SUCCESS"
}

echo ""
echo "========================================="
echo "1. Test de connexion basique..."
echo "========================================="

# 1) Tentative avec AD_SERVER (par défaut l'IP)
RESULT=$(test_connection "$AD_SERVER")

# Vérifie le succès
if echo "$RESULT" | grep -q "true"; then
  echo ""
  echo "✅ Connexion réussie avec: $AD_SERVER"
  CONNECTION_SUCCESS=true
else
  CONNECTION_SUCCESS=false
  
  # 2) Si échec et qu'on a un FQDN différent, retenter avec le FQDN
  if [ -n "$AD_SERVER_FQDN" ] && [ "$AD_SERVER_FQDN" != "$AD_SERVER" ]; then
    echo ""
    echo "Réessai avec le FQDN : $AD_SERVER_FQDN"
    RESULT=$(test_connection "$AD_SERVER_FQDN")
    
    if echo "$RESULT" | grep -q "true"; then
      echo ""
      echo "✅ Connexion réussie avec: $AD_SERVER_FQDN"
      CONNECTION_SUCCESS=true
    fi
  fi
fi

if [ "$CONNECTION_SUCCESS" = false ]; then
  echo ""
  echo "❌ Erreur: Impossible de se connecter à l'AD"
  echo "Vérifiez les credentials et que l'AD est accessible"
  exit 1
fi

echo ""
echo "========================================="
echo "✅ Test de connexion terminé avec succès !"
echo "========================================="
