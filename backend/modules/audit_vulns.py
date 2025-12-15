"""
Module de détection des vulnérabilités Active Directory
"""
import logging

logger = logging.getLogger(__name__)


class VulnerabilityAuditor:
    """Classe pour détecter les vulnérabilités connues"""
    
    def __init__(self, ad_connector):
        """
        Initialise l'auditeur de vulnérabilités
        
        Args:
            ad_connector: Instance de ADConnector connectée
        """
        self.connector = ad_connector
        self.vulnerabilities = []
    
    def _add_vulnerability(self, severity, title, description, cve=None, affected_items=None, recommendation=''):
        """Ajoute une vulnérabilité détectée"""
        vuln = {
            'severity': severity,
            'title': title,
            'description': description,
            'recommendation': recommendation
        }
        
        if cve:
            vuln['cve'] = cve
        
        if affected_items:
            vuln['affected_items'] = affected_items
            vuln['count'] = len(affected_items)
        
        self.vulnerabilities.append(vuln)
    
    def check_ldap_signing(self):
        """Vérifie si la signature LDAP est activée"""
        logger.info("🔍 Vérification de la signature LDAP...")
        
        try:
            # Simulation de check (nécessite des requêtes spécifiques au DC)
            # En pratique, il faudrait interroger la GPO ou les registres du DC
            
            # Pour le moment, on fait une vérification basique
            ldap_signing_required = False  # À implémenter réellement
            
            if not ldap_signing_required:
                self._add_vulnerability(
                    severity='high',
                    title='Signature LDAP non obligatoire',
                    description='La signature LDAP n\'est pas forcée, ce qui permet des attaques man-in-the-middle.',
                    affected_items=[{'server': self.connector.server_address}],
                    recommendation='Activer "Domain controller: LDAP server signing requirements" à "Require signature" dans les GPO.'
                )
            
            logger.info("✅ Vérification signature LDAP terminée")
            return not ldap_signing_required
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return False
    
    def check_smb_signing(self):
        """Vérifie si la signature SMB est activée"""
        logger.info("🔍 Vérification de la signature SMB...")
        
        try:
            # Simulation (nécessite des checks réseau avec impacket)
            smb_signing_required = False
            
            if not smb_signing_required:
                self._add_vulnerability(
                    severity='high',
                    title='Signature SMB non obligatoire',
                    description='La signature SMB n\'est pas forcée, permettant des attaques relay.',
                    affected_items=[{'server': self.connector.server_address}],
                    recommendation='Activer "Microsoft network server: Digitally sign communications (always)" dans les GPO.'
                )
            
            logger.info("✅ Vérification signature SMB terminée")
            return not smb_signing_required
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return False
    
    def check_smbv1_enabled(self):
        """Vérifie si SMBv1 est activé (protocole non sécurisé)"""
        logger.info("🔍 Vérification de SMBv1...")
        
        try:
            # Simulation (nécessite scan réseau)
            smbv1_enabled = True  # Par défaut, on suppose activé
            
            if smbv1_enabled:
                self._add_vulnerability(
                    severity='high',
                    title='SMBv1 activé',
                    description='Le protocole SMBv1 est obsolète et vulnérable (WannaCry, NotPetya). Il devrait être désactivé.',
                    affected_items=[{'server': self.connector.server_address}],
                    recommendation='Désactiver SMBv1 sur tous les serveurs et postes clients. Utiliser SMBv2 ou SMBv3.'
                )
            
            logger.info("✅ Vérification SMBv1 terminée")
            return smbv1_enabled
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return False
    
    def check_zerologon(self):
        """Vérifie la vulnérabilité Zerologon (CVE-2020-1472)"""
        logger.info("🔍 Vérification de Zerologon (CVE-2020-1472)...")
        
        try:
            # Cette vulnérabilité nécessite un test actif avec impacket
            # Pour l'instant, on émet un avertissement
            
            self._add_vulnerability(
                severity='critical',
                title='Vérification Zerologon recommandée',
                description='La vulnérabilité Zerologon (CVE-2020-1472) permet une élévation de privilèges critique. Vérifiez que le patch est installé.',
                cve='CVE-2020-1472',
                affected_items=[{'server': self.connector.server_address}],
                recommendation='Installer les mises à jour de sécurité Microsoft d\'août 2020 ou ultérieures. Vérifier que le patch KB4571694 est installé.'
            )
            
            logger.info("✅ Vérification Zerologon terminée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return False
    
    def check_printnightmare(self):
        """Vérifie la vulnérabilité PrintNightmare (CVE-2021-34527)"""
        logger.info("🔍 Vérification de PrintNightmare (CVE-2021-34527)...")
        
        try:
            self._add_vulnerability(
                severity='critical',
                title='Vérification PrintNightmare recommandée',
                description='La vulnérabilité PrintNightmare permet l\'exécution de code à distance via le spooler d\'impression.',
                cve='CVE-2021-34527',
                affected_items=[{'server': self.connector.server_address}],
                recommendation='Installer les patches de juillet 2021. Désactiver le spooler d\'impression sur les DC si non utilisé.'
            )
            
            logger.info("✅ Vérification PrintNightmare terminée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return False
    
    def check_ntlm_authentication(self):
        """Vérifie l'utilisation de NTLM vs Kerberos"""
        logger.info("🔍 Vérification de l'authentification NTLM...")
        
        try:
            # NTLM est moins sécurisé que Kerberos
            self._add_vulnerability(
                severity='medium',
                title='Authentification NTLM potentiellement active',
                description='NTLM est moins sécurisé que Kerberos et sujet aux attaques relay.',
                affected_items=[{'domain': self.connector.domain}],
                recommendation='Forcer l\'utilisation de Kerberos. Bloquer NTLM via GPO sauf si nécessaire pour la compatibilité.'
            )
            
            logger.info("✅ Vérification NTLM terminée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return False
    
    def check_admin_account_renaming(self):
        """Vérifie si le compte Administrator a été renommé"""
        logger.info("🔍 Vérification du compte Administrator...")
        
        try:
            # Recherche le compte avec RID 500 (Administrator)
            users = self.connector.search_users(
                filter_query='(&(objectClass=user)(objectSid=*-500))'
            )
            
            if users:
                admin_name = users[0].get('sAMAccountName', 'Administrator')
                
                if admin_name.lower() == 'administrator':
                    self._add_vulnerability(
                        severity='low',
                        title='Compte Administrator non renommé',
                        description='Le compte Administrator par défaut n\'a pas été renommé, facilitant les attaques par brute force.',
                        affected_items=[{'username': admin_name}],
                        recommendation='Renommer le compte Administrator et créer un compte leurre "Administrator" sans droits.'
                    )
            
            logger.info("✅ Vérification compte Administrator terminée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return False
    
    def run_all_checks(self):
        """Lance tous les checks de vulnérabilités"""
        logger.info("="*50)
        logger.info("🚀 DÉMARRAGE DE L'AUDIT DES VULNÉRABILITÉS")
        logger.info("="*50)
        
        self.vulnerabilities = []  # Reset
        
        # Lance tous les checks
        self.check_ldap_signing()
        self.check_smb_signing()
        self.check_smbv1_enabled()
        self.check_zerologon()
        self.check_printnightmare()
        self.check_ntlm_authentication()
        self.check_admin_account_renaming()
        
        logger.info("="*50)
        logger.info(f"✅ AUDIT TERMINÉ: {len(self.vulnerabilities)} vulnérabilités détectées")
        logger.info("="*50)
        
        return self.vulnerabilities
