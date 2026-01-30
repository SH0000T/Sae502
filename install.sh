#!/bin/bash

#######################################
# AdSecureCheck - Installation Auto
# Version: 1.4 (Debian-safe, interactif)
#######################################

set -e

echo "=================================================="
echo "🚀 AdSecureCheck - Installation Automatique"
echo "=================================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Variables par défaut
PROJECT_DIR="$HOME/AdSecureCheck"
AD_SERVER="192.168.80.2"
AD_DOMAIN="adsecure.local"
AD_USERNAME="Administrateur"
AD_PASSWORD="TC7PII%IUT"
EMAIL="evanchezlui42@gmail.com"

#######################################
# Demande interactive des infos AD
#######################################
read -p "Adresse du serveur AD [$AD_SERVER]: " input
[ ! -z "$input" ] && AD_SERVER="$input"

read -p "Domaine AD [$AD_DOMAIN]: " input
[ ! -z "$input" ] && AD_DOMAIN="$input"

read -p "Utilisateur AD [$AD_USERNAME]: " input
[ ! -z "$input" ] && AD_USERNAME="$input"

read -s -p "Mot de passe AD [$AD_PASSWORD]: " input
echo
[ ! -z "$input" ] && AD_PASSWORD="$input"

read -p "Email pour notification [$EMAIL]: " input
[ ! -z "$input" ] && EMAIL="$input"

echo -e "${GREEN}✅ Informations AD enregistrées${NC}"

#######################################
# 0. Réparation dpkg
#######################################
echo -e "${YELLOW}🛠️  Vérification dpkg...${NC}"

sudo dpkg --configure -a || true
sudo apt --fix-broken install -y || true

echo -e "${GREEN}✅ dpkg OK${NC}"

#######################################
# 1. Dépendances système
#######################################
echo -e "${YELLOW}📦 [1/7] Installation des dépendances...${NC}"

sudo apt update

sudo apt install -y \
  git curl wget jq \
  docker.io \
  docker-compose \
  nodejs npm \
  ansible python3-pip

# Docker
sudo systemctl enable docker
sudo systemctl start docker

echo -e "${GREEN}✅ Dépendances installées${NC}"

#######################################
# Détection docker compose
#######################################
if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="sudo docker-compose"
elif docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="sudo docker compose"
else
  echo -e "${RED}❌ Docker Compose introuvable${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Docker Compose détecté : $COMPOSE_CMD${NC}"

#######################################
# 2. Clone du projet
#######################################
echo -e "${YELLOW}📥 [2/7] Clone du projet...${NC}"

if [ -d "$PROJECT_DIR" ]; then
  rm -rf "$PROJECT_DIR"
fi

git clone https://github.com/SH0000T/Sae502.git "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo -e "${GREEN}✅ Projet cloné${NC}"

#######################################
# 3. Configuration
#######################################
echo -e "${YELLOW}⚙️  [3/7] Configuration automatique...${NC}"

cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:5000/api
EOF

mkdir -p ansible/inventory
cat > ansible/inventory/hosts.yml << EOF
all:
  hosts:
    localhost:
      ansible_connection: local
EOF

echo -e "${GREEN}✅ Configuration OK${NC}"

#######################################
# 4. Docker backend + DB
#######################################
echo -e "${YELLOW}🐳 [4/7] Démarrage Docker...${NC}"

$COMPOSE_CMD down || true
$COMPOSE_CMD up -d backend database

echo "⏳ Attente services (30s)..."
sleep 30

echo -e "${GREEN}✅ Conteneurs démarrés${NC}"

#######################################
# 5. Frontend
#######################################
echo -e "${YELLOW}🎨 [5/7] Installation frontend...${NC}"

cd frontend
npm install
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 20

echo -e "${GREEN}✅ Frontend lancé (PID $FRONTEND_PID)${NC}"

#######################################
# 6. Tests
#######################################
echo -e "${YELLOW}🧪 [6/7] Tests...${NC}"

cd "$PROJECT_DIR"

API_HEALTH=$(curl -s http://localhost:5000/api/health | jq -r '.status')

if [ "$API_HEALTH" != "ok" ]; then
  echo -e "${RED}❌ API KO${NC}"
  exit 1
fi
echo -e "${GREEN}✅ API OK${NC}"

#######################################
# 7. Scan automatique
#######################################
echo -e "${YELLOW}🚀 [7/7] Lancement du scan...${NC}"

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
  echo -e "${GREEN}✅ Scan lancé (ID $SCAN_ID)${NC}"
else
  echo -e "${RED}❌ Erreur scan${NC}"
  echo "$SCAN_RESPONSE"
fi

#######################################
# FIN
#######################################
echo ""
echo "=================================================="
echo -e "${GREEN}✅ INSTALLATION TERMINÉE${NC}"
echo "=================================================="
echo "🌐 Frontend : http://localhost:3000"
echo "🔌 API      : http://localhost:5000"
echo "📂 Projet   : $PROJECT_DIR"
echo "=================================================="

echo "$FRONTEND_PID" > "$PROJECT_DIR/.frontend.pid"
