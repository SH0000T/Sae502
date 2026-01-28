#!/bin/bash

#######################################
# AdSecureCheck - Installation Auto
# Version: 1.0
#######################################

set -e  # Arrête si erreur

echo "=================================================="
echo "🚀 AdSecureCheck - Installation Automatique"
echo "=================================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR="$HOME/AdSecureCheck"
AD_SERVER="192.168.80.2"
AD_DOMAIN="adsecure.local"
AD_USERNAME="Administrateur"
AD_PASSWORD="TC7PII%IUT"
EMAIL="evanchezlui42@gmail.com"

#######################################
# 1. Installation des dépendances
#######################################
echo -e "${YELLOW}📦 [1/7] Installation des dépendances système...${NC}"

sudo apt update -qq
sudo apt install -y git curl wget docker.io docker-compose nodejs npm ansible python3-pip jq > /dev/null 2>&1

# Ajoute l'utilisateur au groupe docker
sudo usermod -aG docker $USER

echo -e "${GREEN}✅ Dépendances installées${NC}"

#######################################
# 2. Clone du projet
#######################################
echo -e "${YELLOW}📥 [2/7] Clone du projet...${NC}"

if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Le dossier existe déjà. Suppression..."
    rm -rf "$PROJECT_DIR"
fi

git clone https://github.com/SH0000T/Sae502.git "$PROJECT_DIR" > /dev/null 2>&1
cd "$PROJECT_DIR"

echo -e "${GREEN}✅ Projet cloné${NC}"

#######################################
# 3. Configuration automatique
#######################################
echo -e "${YELLOW}⚙️  [3/7] Configuration automatique...${NC}"

# Créer le fichier .env pour le frontend
cat > frontend/.env << ENVEOF
REACT_APP_API_URL=http://localhost:5000/api
ENVEOF

# Configuration Ansible pour localhost
cat > ansible/inventory/hosts.yml << ANSIBLEEOF
all:
  children:
    production:
      hosts:
        adsecure-server:
          ansible_host: localhost
          ansible_connection: local
          ansible_user: $USER
ANSIBLEEOF

echo -e "${GREEN}✅ Configuration terminée${NC}"

#######################################
# 4. Démarrage Docker
#######################################
echo -e "${YELLOW}🐳 [4/7] Démarrage des conteneurs Docker...${NC}"

# Redémarre Docker si nécessaire
sudo systemctl start docker > /dev/null 2>&1

# Arrête les anciens conteneurs
docker compose down > /dev/null 2>&1 || true

# Lance backend et base de données
docker compose up -d backend database > /dev/null 2>&1

# Attente du démarrage
echo "⏳ Attente du démarrage des services (30s)..."
sleep 30

echo -e "${GREEN}✅ Conteneurs démarrés${NC}"

#######################################
# 5. Installation frontend
#######################################
echo -e "${YELLOW}🎨 [5/7] Installation du frontend...${NC}"

cd "$PROJECT_DIR/frontend"
npm install > /dev/null 2>&1

# Lance le frontend en arrière-plan
nohup npm start > /dev/null 2>&1 &
FRONTEND_PID=$!

echo "⏳ Attente du démarrage du frontend (20s)..."
sleep 20

echo -e "${GREEN}✅ Frontend démarré (PID: $FRONTEND_PID)${NC}"

#######################################
# 6. Tests de connectivité
#######################################
echo -e "${YELLOW}🧪 [6/7] Tests de connectivité...${NC}"

cd "$PROJECT_DIR"

# Test API
echo "  🔍 Test de l'API..."
API_HEALTH=$(curl -s http://localhost:5000/api/health | jq -r '.status')

if [ "$API_HEALTH" = "ok" ]; then
    echo -e "  ${GREEN}✅ API Backend : OK${NC}"
else
    echo -e "  ${RED}❌ API Backend : ERREUR${NC}"
    exit 1
fi

# Test connexion AD
echo "  🔍 Test de connexion Active Directory..."
AD_TEST=$(curl -s -X POST http://localhost:5000/api/ad/test-connection \
  -H "Content-Type: application/json" \
  -d "{
    \"ad_server\": \"$AD_SERVER\",
    \"ad_domain\": \"$AD_DOMAIN\",
    \"ad_username\": \"$AD_USERNAME\",
    \"ad_password\": \"$AD_PASSWORD\",
    \"use_ssl\": false
  }" | jq -r '.success')

if [ "$AD_TEST" = "true" ]; then
    echo -e "  ${GREEN}✅ Connexion AD : OK${NC}"
else
    echo -e "  ${YELLOW}⚠️  Connexion AD : Échec (vérifiez vos credentials)${NC}"
fi

# Test frontend
sleep 5
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)

if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "  ${GREEN}✅ Frontend : OK${NC}"
else
    echo -e "  ${YELLOW}⚠️  Frontend : En cours de démarrage...${NC}"
fi

echo -e "${GREEN}✅ Tests terminés${NC}"

#######################################
# 7. Lancement du scan automatique
#######################################
echo -e "${YELLOW}🚀 [7/7] Lancement du scan automatique...${NC}"

SCAN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/scans/start \
  -H "Content-Type: application/json" \
  -d "{
    \"ad_server\": \"$AD_SERVER\",
    \"ad_domain\": \"$AD_DOMAIN\",
    \"ad_username\": \"$AD_USERNAME\",
    \"ad_password\": \"$AD_PASSWORD\",
    \"use_ssl\": false,
    \"send_email\": true,
    \"email_to\": \"$EMAIL\"
  }")

SCAN_ID=$(echo "$SCAN_RESPONSE" | jq -r '.scan.id')

if [ "$SCAN_ID" != "null" ]; then
    echo -e "${GREEN}✅ Scan lancé avec succès (ID: $SCAN_ID)${NC}"
    echo "⏳ Le scan prend 2-5 minutes..."
else
    echo -e "${RED}❌ Erreur lors du lancement du scan${NC}"
    echo "$SCAN_RESPONSE" | jq '.'
fi

#######################################
# 8. Résumé final
#######################################
echo ""
echo "=================================================="
echo -e "${GREEN}✅ INSTALLATION TERMINÉE AVEC SUCCÈS !${NC}"
echo "=================================================="
echo ""
echo "📊 Informations d'accès :"
echo "  🌐 Frontend : http://localhost:3000"
echo "  🔌 API      : http://localhost:5000"
echo "  📧 Email    : $EMAIL"
echo ""
echo "📋 Commandes utiles :"
echo "  • Voir les conteneurs : docker ps"
echo "  • Logs backend        : docker logs adsecure-backend"
echo "  • Arrêter tout        : cd $PROJECT_DIR && ./stop.sh"
echo ""
echo "📂 Projet installé dans : $PROJECT_DIR"
echo ""
echo "=================================================="

# Sauvegarde du PID du frontend
echo "$FRONTEND_PID" > "$PROJECT_DIR/.frontend.pid"

