# 🚀 AdSecureCheck - Démarrage Rapide

## Installation en 1 commande
```bash
curl -sSL https://raw.githubusercontent.com/SH0000T/Sae502/main/install.sh | bash
```

Ou depuis le projet cloné :
```bash
./install.sh
```

## Accès

- **Frontend** : http://localhost:3000
- **API** : http://localhost:5000/api/health

## Commandes
```bash
# Arrêter
./stop.sh

# Redémarrer
./restart.sh

# Logs
docker logs adsecure-backend
```

## Configuration

Édite les variables dans `install.sh` :
```bash
AD_SERVER="ton_serveur"
AD_DOMAIN="ton_domaine"
AD_USERNAME="ton_user"
AD_PASSWORD="ton_mdp"
```

C'est tout ! 🎉
