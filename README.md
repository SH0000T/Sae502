📋 Table des Matières

- Présentation
- Fonctionnalités
- Architecture
- Prérequis
- Installation Rapide
- Installation Détaillée
- Utilisation
- Déploiement avec Ansible
- API Documentation
- Maintenance
- Troubleshooting
- Contribution
- License


🎯 Présentation
AdSecureCheck est une solution automatisée d'audit de sécurité pour Active Directory. Elle permet de scanner n'importe quel environnement AD, d'identifier les vulnérabilités et mauvaises configurations, et de générer des rapports détaillés avec des recommandations de remédiation.
Pourquoi AdSecureCheck ?
Les entreprises manquent souvent d'outils automatisés pour évaluer en continu la posture de sécurité de leur Active Directory. Les audits manuels sont :

⏰ Chronophages
❌ Sujets à erreur
📊 Difficiles à suivre dans le temps

AdSecureCheck résout ces problèmes en automatisant complètement le processus d'audit.

✨ Fonctionnalités
Scanner de Vulnérabilités

✅ Détection des comptes avec mots de passe faibles ou expirés
✅ Identification des comptes inactifs ou obsolètes
✅ Vérification des privilèges excessifs (Domain Admin, Enterprise Admin)
✅ Détection des GPO mal configurées
✅ Analyse des délégations dangereuses
✅ Vérification des protocoles non sécurisés (LDAP non signé, SMBv1)
✅ Détection des vulnérabilités connues (PrintNightmare, Zerologon, etc.)

Génération de Rapports

📄 Rapport TXT : Texte détaillé avec tous les détails
📊 Rapport CSV : Export pour analyse Excel
🌐 Rapport HTML : Dashboard interactif visuel
📧 Envoi automatique par email avec pièces jointes

Interface Web

📊 Dashboard de visualisation des résultats
🕒 Historique des scans
📈 Graphiques de tendance de la posture de sécurité
⚙️ Gestion des configurations de scan
💾 Téléchargement des rapports


🏗️ Architecture
AdSecureCheck/
├── backend/                    # API Flask + Modules d'audit
│   ├── app.py                 # Point d'entrée API
│   ├── config.py              # Configuration
│   ├── models/                # Modèles de données
│   │   └── scan.py
│   ├── routes/                # Routes API REST
│   │   ├── scans.py
│   │   └── ad_test.py
│   ├── modules/               # Modules d'audit
│   │   ├── ad_connector.py   # Connexion LDAP
│   │   ├── audit_users.py    # Audit utilisateurs
│   │   ├── audit_vulns.py    # Détection vulnérabilités
│   │   ├── scanner.py        # Orchestrateur principal
│   │   ├── report_generator.py  # Génération rapports
│   │   └── email_sender.py   # Envoi emails
│   └── requirements.txt       # Dépendances Python
│
├── frontend/                   # Interface React
│   ├── src/
│   │   ├── components/        # Composants réutilisables
│   │   ├── pages/            # Pages de l'application
│   │   └── services/         # Services API
│   └── package.json
│
├── ansible/                    # Automatisation déploiement
│   ├── playbooks/
│   │   ├── deploy.yml        # Déploiement complet
│   │   ├── stop.yml          # Arrêt
│   │   └── restart.yml       # Redémarrage
│   ├── roles/
│   │   ├── common/           # Packages de base
│   │   ├── docker/           # Installation Docker
│   │   ├── firewall/         # Configuration UFW
│   │   └── app/              # Déploiement application
│   └── inventory/
│       └── hosts.yml
│
├── docker-compose.yml          # Orchestration conteneurs
├── .gitignore
└── README.md
Stack Technique
Backend

Python 3.11+
Flask (API REST)
PostgreSQL 15
Libraries : ldap3, impacket, pywinrm

Frontend

React.js 18
Recharts (graphiques)
Axios (requêtes API)
Lucide React (icônes)

Infrastructure

Docker & Docker Compose
Ansible (automatisation)
Nginx (serveur web)


📦 Prérequis
Système d'exploitation

Debian 11/12 ou Ubuntu 20.04/22.04 LTS
4 Go RAM minimum
20 Go d'espace disque

Logiciels requis

Docker & Docker Compose
Python 3.11+
Node.js 20+
Ansible 2.9+
Git


🚀 Installation Rapide
Option 1 : Déploiement Automatisé avec Ansible (Recommandé)
bash# 1. Clone le projet
git clone https://github.com/SH0000T/Sae502.git
cd Sae502

# 2. Lance le déploiement complet
cd ansible
ansible-playbook playbooks/deploy.yml

# 3. Accède à l'application
# Frontend: http://localhost
# API: http://localhost:5000
C'est tout ! 🎉 L'application est déployée et prête à l'emploi.

📖 Installation Détaillée
Étape 1 : Installation des dépendances système
bash# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des outils de base
sudo apt install -y curl wget git vim build-essential

# Installation de Python 3.11+
sudo apt install -y python3 python3-pip python3-venv

# Installation de Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Vérification des versions
python3 --version
node --version
npm --version
Étape 2 : Installation de Docker
bash# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajout de l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Redémarrage de la session (ou déconnexion/reconnexion)
newgrp docker

# Vérification
docker --version
docker compose version
Étape 3 : Installation d'Ansible
bashsudo apt install -y ansible

# Vérification
ansible --version
Étape 4 : Clone du projet
bash# Clone depuis GitHub
git clone https://github.com/SH0000T/Sae502.git
cd Sae502

# Configuration Git (si nécessaire)
git config user.name "Ton Nom"
git config user.email "ton.email@exemple.com"
Étape 5 : Configuration du pare-feu
bash# Installation et configuration d'UFW
sudo apt install -y ufw

# Autorisation des ports nécessaires
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 5000/tcp  # API (dev)

# Activation
sudo ufw enable

# Vérification
sudo ufw status verbose
Étape 6 : Lancement avec Docker Compose
bashcd ~/Sae502

# Build et lancement des conteneurs
docker compose up -d --build

# Attente du démarrage (30 secondes)
sleep 30

# Vérification des conteneurs
docker ps

# Vérification des logs
docker logs adsecure-backend
docker logs adsecure-db
Étape 7 : Lancement du Frontend (mode dev)
bashcd ~/Sae502/frontend

# Installation des dépendances
npm install

# Lancement du serveur de développement
npm start
```

Le frontend sera accessible sur **http://localhost:3000**

---

## 📱 Utilisation

### 1. Accéder à l'interface web

Ouvre ton navigateur et va sur :
- **Frontend** : http://localhost:3000 (mode dev) ou http://localhost (production)
- **API** : http://localhost:5000/api/health

### 2. Lancer un scan

1. **Clique sur "Nouveau Scan"** dans le menu

2. **Remplis le formulaire** :
```
   Serveur AD : 192.168.80.2 (ou FQDN de ton DC)
   Domaine : example.local
   Username : Administrateur
   Password : ********
   SSL : Décoché (ou coché si LDAPS configuré)
```

3. **Teste la connexion** (optionnel mais recommandé)

4. **Lance le scan** - Le scan prend entre 2 et 10 minutes selon la taille de l'AD

5. **Consulte les résultats**
   - Visualise les vulnérabilités par criticité
   - Télécharge les rapports (TXT, CSV, HTML)
   - Vérifie ton email pour les rapports

### 3. Consulter l'historique

- Clique sur **"Historique"** dans le menu
- Visualise tous les scans effectués
- Clique sur l'icône 👁️ pour voir les détails
- Télécharge les rapports avec le bouton 💾

### 4. Dashboard

- Vue d'ensemble de la sécurité
- Statistiques globales
- Graphiques de répartition des vulnérabilités
- Scans récents

---

## 🤖 Déploiement avec Ansible

### Structure Ansible
```
ansible/
├── ansible.cfg           # Configuration Ansible
├── inventory/
│   └── hosts.yml        # Serveurs cibles
├── group_vars/
│   └── all.yml          # Variables globales
├── playbooks/
│   ├── deploy.yml       # Déploiement complet
│   ├── stop.yml         # Arrêt de l'application
│   └── restart.yml      # Redémarrage
└── roles/
    ├── common/          # Packages de base
    ├── docker/          # Installation Docker
    ├── firewall/        # Configuration UFW
    └── app/             # Déploiement de l'app
Commandes Ansible
Déploiement complet
bashcd ~/Sae502/ansible

# Test de connectivité
ansible all -m ping

# Vérification de la syntaxe
ansible-playbook playbooks/deploy.yml --syntax-check

# Simulation (dry-run)
ansible-playbook playbooks/deploy.yml --check

# Déploiement réel
ansible-playbook playbooks/deploy.yml
Arrêt de l'application
bashcd ~/Sae502/ansible
ansible-playbook playbooks/stop.yml
Redémarrage de l'application
bashcd ~/Sae502/ansible
ansible-playbook playbooks/restart.yml
Configuration de l'inventaire
Édite ansible/inventory/hosts.yml :
yamlall:
  children:
    production:
      hosts:
        adsecure-server:
          ansible_host: localhost
          ansible_connection: local
          ansible_user: ton_utilisateur
Variables personnalisables
Édite ansible/group_vars/all.yml :
yaml# Ports de l'application
api_port: 5000
frontend_port: 80
db_port: 5432

# Base de données
postgres_db: adsecurecheck
postgres_user: admin
postgres_password: ChangeMe123!

# Email (optionnel)
email_user: ton.email@gmail.com
email_password: ""  # À définir

📚 API Documentation
Endpoints disponibles
Health Check
bashGET /api/health
Réponse :
json{
  "status": "ok",
  "message": "AdSecureCheck API is running",
  "version": "1.0.0"
}
Test de connexion AD
bashPOST /api/ad/test-connection
Content-Type: application/json

{
  "ad_server": "dc01.example.com",
  "ad_domain": "example.local",
  "ad_username": "admin",
  "ad_password": "password",
  "use_ssl": false
}
Lancer un scan
bashPOST /api/scans/start
Content-Type: application/json

{
  "ad_server": "dc01.example.com",
  "ad_domain": "example.local",
  "ad_username": "admin",
  "ad_password": "password",
  "use_ssl": false,
  "send_email": true,
  "email_to": "user@example.com"
}
Liste des scans
bashGET /api/scans
Détails d'un scan
bashGET /api/scans/<scan_id>
Statistiques globales
bashGET /api/scans/stats
Télécharger un rapport
bashGET /api/scans/<scan_id>/download/<format>
# format: text, csv, html
Supprimer un scan
bashDELETE /api/scans/<scan_id>

🔧 Maintenance
Vérifier l'état des services
bash# Conteneurs Docker
docker ps -a

# Logs du backend
docker logs adsecure-backend --tail 50

# Logs de la base de données
docker logs adsecure-db --tail 20

# Logs du frontend
docker logs adsecure-frontend --tail 50
Redémarrer les services
bashcd ~/Sae502

# Redémarrage complet
docker compose restart

# Redémarrage d'un service spécifique
docker compose restart backend
docker compose restart database
Sauvegarder la base de données
bash# Backup
docker exec adsecure-db pg_dump -U admin adsecurecheck > backup_$(date +%Y%m%d).sql

# Restauration
cat backup_20240121.sql | docker exec -i adsecure-db psql -U admin -d adsecurecheck
Nettoyer Docker
bash# Arrêter et supprimer tous les conteneurs
docker compose down

# Supprimer les images inutilisées
docker system prune -a

# Rebuild complet
docker compose build --no-cache
docker compose up -d
Mettre à jour le projet
bashcd ~/Sae502

# Pull les dernières modifications
git pull origin main

# Rebuild et redémarrage
docker compose down
docker compose build --no-cache
docker compose up -d

🐛 Troubleshooting
Problème : Le backend ne démarre pas
Solution :
bash# Vérifier les logs
docker logs adsecure-backend

# Vérifier la connexion à la base de données
docker exec -it adsecure-db psql -U admin -d adsecurecheck

# Redémarrer
docker compose restart backend
Problème : Le frontend ne s'affiche pas
Solution :
bash# Vérifier les logs
docker logs adsecure-frontend

# Vérifier le build React
cd ~/Sae502/frontend
npm install
npm run build

# Lancer en mode dev
npm start
Problème : Connexion AD échouée
Vérifications :

Le serveur AD est-il accessible ? ping dc01.example.com
Le port LDAP est-il ouvert ? telnet dc01.example.com 389
Les credentials sont-ils corrects ?
Le pare-feu bloque-t-il la connexion ?

Solution :
bash# Teste la connexion depuis le conteneur
docker exec -it adsecure-backend python3 -c "
from modules.ad_connector import ADConnector
connector = ADConnector('dc01.example.com', 'example.local', 'admin', 'password', False)
result = connector.test_connection()
print(result)
"
Problème : Erreur "Port already in use"
Solution :
bash# Identifier le processus utilisant le port
sudo lsof -i :5000
sudo lsof -i :80

# Arrêter le processus
sudo kill -9 <PID>

# Ou changer le port dans docker-compose.yml
Problème : Email non envoyé
Vérifications :

Le App Password Gmail est-il configuré ?
La validation en 2 étapes est-elle activée ?
Les variables d'environnement sont-elles correctes ?

Solution :
bash# Édite le fichier email_sender.py
nano backend/modules/email_sender.py

# Vérifie les credentials
EMAIL_USER = "ton.email@gmail.com"
EMAIL_PASSWORD = "ton_app_password"

# Redémarre le backend
docker compose restart backend
Problème : Ansible échoue avec "sudo password required"
Solution :
bash# Configure sudo sans mot de passe
echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/$USER
sudo chmod 0440 /etc/sudoers.d/$USER

# Ou lance avec --ask-become-pass
ansible-playbook playbooks/deploy.yml --ask-become-pass

🔐 Sécurité
Bonnes pratiques

Changer les mots de passe par défaut

bash   # Édite docker-compose.yml
   nano docker-compose.yml
   
   # Change POSTGRES_PASSWORD
   # Change SECRET_KEY

Utiliser LDAPS

Configure le certificat SSL sur ton AD
Active use_ssl: true dans les scans


Restreindre l'accès réseau

bash   # Limite l'API au localhost en production
   # Édite docker-compose.yml
   ports:
     - "127.0.0.1:5000:5000"  # Au lieu de "5000:5000"

Sauvegardes régulières

bash   # Automatise les backups
   crontab -e
   
   # Ajoute :
   0 2 * * * docker exec adsecure-db pg_dump -U admin adsecurecheck > /backup/adsecure_$(date +\%Y\%m\%d).sql

Mettre à jour régulièrement

bash   cd ~/Sae502
   git pull origin main
   docker compose build --no-cache
   docker compose up -d

👥 Contribution
Les contributions sont les bienvenues !

Fork le projet
Crée une branche (git checkout -b feature/AmazingFeature)
Commit tes changements (git commit -m 'Add some AmazingFeature')
Push sur la branche (git push origin feature/AmazingFeature)
Ouvre une Pull Request


📄 License
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

👤 Auteur
Projet SAE 502 - Audit Active Directory

GitHub: @SH0000T
Email: evanchezlui42@gmail.com


🙏 Remerciements

Flask - Framework Web Python
React - Framework Frontend
ldap3 - Client LDAP Python
Recharts - Graphiques React
Docker - Conteneurisation
Ansible - Automatisation
