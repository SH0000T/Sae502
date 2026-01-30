#!/bin/bash

echo "=================================================="
echo "🚀 AdSecureCheck - Déploiement avec Ansible"
echo "=================================================="
echo ""

# Vérifications
command -v ansible >/dev/null 2>&1 || {
    echo "❌ Ansible non installé. Installation..."
    sudo apt update
    sudo apt install -y ansible
}

command -v git >/dev/null 2>&1 || {
    echo "❌ Git non installé. Installation..."
    sudo apt install -y git
}

# Clone le projet si pas déjà fait
if [ ! -d "$HOME/AdSecureCheck" ]; then
    echo "📥 Clone du projet..."
    git clone https://github.com/SH0000T/Sae502.git "$HOME/AdSecureCheck"
fi

cd "$HOME/AdSecureCheck/ansible"

echo ""
echo "🎯 Lancement du déploiement Ansible..."
echo ""

# Lance le playbook Ansible
ansible-playbook playbooks/deploy.yml

echo ""
echo "=================================================="
echo "✅ DÉPLOIEMENT TERMINÉ"
echo "=================================================="
echo "🌐 Frontend : http://localhost:3000"
echo "🔌 API      : http://localhost:5000"
echo "=================================================="
