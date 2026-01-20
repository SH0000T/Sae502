# Ansible - AdSecureCheck

## 📋 Playbooks disponibles

### Déploiement complet
```bash
cd ~/Sae502/ansible
ansible-playbook playbooks/deploy.yml
```

### Arrêt de l'application
```bash
ansible-playbook playbooks/stop.yml
```

### Redémarrage de l'application
```bash
ansible-playbook playbooks/restart.yml
```

## 🔧 Vérifications

### Test de connectivité
```bash
ansible all -m ping
```

### Vérification de la syntaxe
```bash
ansible-playbook playbooks/deploy.yml --syntax-check
```

### Mode simulation (dry-run)
```bash
ansible-playbook playbooks/deploy.yml --check
```

## 📝 Variables

Les variables sont définies dans `group_vars/all.yml` :
- Ports de l'application
- Credentials base de données
- Configuration pare-feu

## 🔐 Ansible Vault (pour les secrets)

### Créer un fichier vault
```bash
ansible-vault create group_vars/vault.yml
```

### Éditer un fichier vault
```bash
ansible-vault edit group_vars/vault.yml
```

### Utiliser le vault dans un playbook
```bash
ansible-playbook playbooks/deploy.yml --ask-vault-pass
```
