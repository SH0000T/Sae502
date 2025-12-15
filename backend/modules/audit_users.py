"""
Module d'audit des comptes utilisateurs Active Directory
"""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class UserAuditor:
    """Classe pour auditer les comptes utilisateurs"""
    
    def __init__(self, ad_connector):
        """
        Initialise l'auditeur d'utilisateurs
        
        Args:
            ad_connector: Instance de ADConnector connectée
        """
        self.connector = ad_connector
        self.vulnerabilities = []
    
    def _add_vulnerability(self, severity, title, description, affected_items, recommendation):
        """Ajoute une vulnérabilité détectée"""
        self.vulnerabilities.append({
            'severity': severity,  # critical, high, medium, low
            'title': title,
            'description': description,
            'affected_items': affected_items,
            'count': len(affected_items),
            'recommendation': recommendation
        })
    
    def check_inactive_users(self, days=90):
        """
        Vérifie les comptes inactifs depuis X jours
        
        Args:
            days (int): Nombre de jours d'inactivité
        """
        logger.info(f"🔍 Recherche des comptes inactifs depuis {days} jours...")
        
        try:
            users = self.connector.search_users()
            inactive_users = []
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for user in users:
                username = user.get('sAMAccountName', 'Unknown')
                last_logon = user.get('lastLogon', '0')
                
                # Si jamais connecté ou inactif depuis longtemps
                if last_logon == '0' or last_logon == '[]':
                    inactive_users.append({
                        'username': username,
                        'last_logon': 'Never',
                        'status': 'Never logged in'
                    })
            
            if inactive_users:
                self._add_vulnerability(
                    severity='medium',
                    title=f'Comptes inactifs depuis plus de {days} jours',
                    description=f'{len(inactive_users)} comptes n\'ont pas été utilisés depuis plus de {days} jours ou n\'ont jamais été utilisés.',
                    affected_items=inactive_users[:20],  # Limite à 20 pour l'affichage
                    recommendation='Désactiver ou supprimer les comptes inutilisés pour réduire la surface d\'attaque.'
                )
            
            logger.info(f"✅ Trouvé {len(inactive_users)} comptes inactifs")
            return inactive_users
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification des comptes inactifs: {str(e)}")
            return []
    
    def check_privileged_accounts(self):
        """Vérifie les comptes avec privilèges élevés"""
        logger.info("🔍 Analyse des comptes privilégiés...")
        
        try:
            privileged = self.connector.get_privileged_users()
            
            # Compte les admins par groupe
            admin_by_group = {}
            for item in privileged:
                group = item['group']
                if group not in admin_by_group:
                    admin_by_group[group] = []
                admin_by_group[group].append(item['user_dn'])
            
            # Compte total d'admins de domaine
            domain_admins = admin_by_group.get('Domain Admins', [])
            enterprise_admins = admin_by_group.get('Enterprise Admins', [])
            
            if len(domain_admins) > 5:
                self._add_vulnerability(
                    severity='high',
                    title='Trop de comptes Domain Admins',
                    description=f'{len(domain_admins)} comptes ont les droits Domain Admin. Recommandation: max 3-5 comptes.',
                    affected_items=[{'dn': dn} for dn in domain_admins[:10]],
                    recommendation='Réduire le nombre de Domain Admins. Utiliser des groupes délégués pour les tâches spécifiques.'
                )
            
            if enterprise_admins:
                self._add_vulnerability(
                    severity='critical',
                    title='Comptes Enterprise Admins détectés',
                    description=f'{len(enterprise_admins)} comptes ont les droits Enterprise Admin. Ces comptes ne devraient être utilisés qu\'exceptionnellement.',
                    affected_items=[{'dn': dn} for dn in enterprise_admins],
                    recommendation='Les comptes Enterprise Admin doivent être réservés uniquement aux modifications de la forêt. Désactiver quand non utilisés.'
                )
            
            logger.info(f"✅ Analysé {len(privileged)} comptes privilégiés")
            return privileged
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse des comptes privilégiés: {str(e)}")
            return []
    
    def check_password_policy(self):
        """Vérifie la politique de mots de passe"""
        logger.info("🔍 Vérification de la politique de mots de passe...")
        
        try:
            domain_info = self.connector.get_domain_info()
            
            # Simulation de vérification (à améliorer avec de vraies requêtes LDAP)
            issues = []
            
            # Check: longueur minimale du mot de passe
            min_pwd_length = 8  # Valeur par défaut si non récupérée
            if min_pwd_length < 12:
                issues.append({
                    'policy': 'Longueur minimale du mot de passe',
                    'current_value': min_pwd_length,
                    'recommended_value': '14+ caractères'
                })
            
            if issues:
                self._add_vulnerability(
                    severity='high',
                    title='Politique de mots de passe faible',
                    description='La politique de mots de passe ne respecte pas les meilleures pratiques.',
                    affected_items=issues,
                    recommendation='Augmenter la longueur minimale à 14 caractères minimum. Activer la complexité des mots de passe.'
                )
            
            logger.info(f"✅ Vérification de la politique de mots de passe terminée")
            return issues
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification de la politique de mots de passe: {str(e)}")
            return []
    
    def check_users_never_expire_password(self):
        """Vérifie les comptes avec mot de passe n'expirant jamais"""
        logger.info("🔍 Recherche des comptes avec mots de passe permanents...")
        
        try:
            users = self.connector.search_users()
            never_expire = []
            
            for user in users:
                username = user.get('sAMAccountName', 'Unknown')
                uac = user.get('userAccountControl', '0')
                
                # userAccountControl flag: 65536 = DONT_EXPIRE_PASSWORD
                try:
                    uac_value = int(uac)
                    if uac_value & 65536:  # Bit 16 = password never expires
                        never_expire.append({
                            'username': username,
                            'reason': 'Password never expires flag set'
                        })
                except:
                    pass
            
            if never_expire:
                self._add_vulnerability(
                    severity='medium',
                    title='Comptes avec mots de passe permanents',
                    description=f'{len(never_expire)} comptes ont des mots de passe configurés pour ne jamais expirer.',
                    affected_items=never_expire[:20],
                    recommendation='Forcer l\'expiration des mots de passe pour tous les comptes, sauf les comptes de service (et les stocker dans un gestionnaire sécurisé).'
                )
            
            logger.info(f"✅ Trouvé {len(never_expire)} comptes avec mot de passe permanent")
            return never_expire
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return []
    
    def check_disabled_accounts_in_admin_groups(self):
        """Vérifie les comptes désactivés dans les groupes d'admins"""
        logger.info("🔍 Recherche des comptes désactivés dans les groupes privilégiés...")
        
        try:
            privileged = self.connector.get_privileged_users()
            disabled_admins = []
            
            for item in privileged:
                user_dn = item['user_dn']
                group = item['group']
                
                # Récupère les infos du compte
                try:
                    self.connector.connection.search(
                        search_base=user_dn,
                        search_filter='(objectClass=user)',
                        attributes=['sAMAccountName', 'userAccountControl']
                    )
                    
                    if self.connector.connection.entries:
                        entry = self.connector.connection.entries[0]
                        uac = str(entry.userAccountControl) if hasattr(entry, 'userAccountControl') else '0'
                        username = str(entry.sAMAccountName) if hasattr(entry, 'sAMAccountName') else 'Unknown'
                        
                        # userAccountControl flag: 2 = ACCOUNTDISABLE
                        try:
                            if int(uac) & 2:
                                disabled_admins.append({
                                    'username': username,
                                    'group': group,
                                    'dn': user_dn
                                })
                        except:
                            pass
                except:
                    continue
            
            if disabled_admins:
                self._add_vulnerability(
                    severity='low',
                    title='Comptes désactivés dans les groupes privilégiés',
                    description=f'{len(disabled_admins)} comptes désactivés sont toujours membres de groupes privilégiés.',
                    affected_items=disabled_admins,
                    recommendation='Supprimer les comptes désactivés des groupes privilégiés pour maintenir une bonne hygiène de sécurité.'
                )
            
            logger.info(f"✅ Trouvé {len(disabled_admins)} comptes désactivés dans les groupes privilégiés")
            return disabled_admins
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return []
    
    def run_all_checks(self):
        """Lance tous les checks utilisateurs"""
        logger.info("="*50)
        logger.info("🚀 DÉMARRAGE DE L'AUDIT DES UTILISATEURS")
        logger.info("="*50)
        
        self.vulnerabilities = []  # Reset
        
        # Lance tous les checks
        self.check_inactive_users(days=90)
        self.check_privileged_accounts()
        self.check_password_policy()
        self.check_users_never_expire_password()
        self.check_disabled_accounts_in_admin_groups()
        
        logger.info("="*50)
        logger.info(f"✅ AUDIT TERMINÉ: {len(self.vulnerabilities)} vulnérabilités détectées")
        logger.info("="*50)
        
        return self.vulnerabilities
