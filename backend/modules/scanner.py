"""
Module principal d'orchestration des scans
"""
from modules.ad_connector import ADConnector
from modules.audit_users import UserAuditor
from modules.audit_vulns import VulnerabilityAuditor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ADScanner:
    """Orchestre tous les audits Active Directory"""
    
    def __init__(self, ad_server, ad_domain, ad_username, ad_password, use_ssl=True):
        """
        Initialise le scanner
        
        Args:
            ad_server (str): Adresse du serveur AD
            ad_domain (str): Nom du domaine
            ad_username (str): Nom d'utilisateur
            ad_password (str): Mot de passe
            use_ssl (bool): Utiliser LDAPS
        """
        self.ad_server = ad_server
        self.ad_domain = ad_domain
        self.connector = ADConnector(ad_server, ad_domain, ad_username, ad_password, use_ssl)
        self.results = {
            'scan_info': {},
            'vulnerabilities': [],
            'statistics': {}
        }
    
    def _calculate_risk_score(self, vulnerabilities):
        """
        Calcule un score de risque (0-100)
        
        Args:
            vulnerabilities (list): Liste des vulnérabilités
        
        Returns:
            int: Score de risque
        """
        score = 0
        
        for vuln in vulnerabilities:
            severity = vuln['severity']
            if severity == 'critical':
                score += 25
            elif severity == 'high':
                score += 15
            elif severity == 'medium':
                score += 7
            elif severity == 'low':
                score += 3
        
        # Limite à 100
        return min(score, 100)
    
    def _count_by_severity(self, vulnerabilities):
        """Compte les vulnérabilités par niveau de criticité"""
        counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for vuln in vulnerabilities:
            severity = vuln['severity']
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def run_full_scan(self):
        """Lance un scan complet de l'AD"""
        logger.info("="*60)
        logger.info("🚀 DÉMARRAGE DU SCAN COMPLET ACTIVE DIRECTORY")
        logger.info("="*60)
        
        start_time = datetime.now()
        
        try:
            # Connexion à l'AD
            logger.info(f"📡 Connexion à {self.ad_server}...")
            self.connector.connect()
            
            # Récupère les infos du domaine
            domain_info = self.connector.get_domain_info()
            
            self.results['scan_info'] = {
                'server': self.ad_server,
                'domain': self.ad_domain,
                'domain_info': domain_info,
                'scan_start': start_time.isoformat(),
                'scan_status': 'running'
            }
            
            # Audit des utilisateurs
            logger.info("\n" + "="*60)
            logger.info("👥 PHASE 1: AUDIT DES UTILISATEURS")
            logger.info("="*60)
            
            user_auditor = UserAuditor(self.connector)
            user_vulns = user_auditor.run_all_checks()
            
            # Audit des vulnérabilités
            logger.info("\n" + "="*60)
            logger.info("🔒 PHASE 2: AUDIT DES VULNÉRABILITÉS")
            logger.info("="*60)
            
            vuln_auditor = VulnerabilityAuditor(self.connector)
            vuln_checks = vuln_auditor.run_all_checks()
            
            # Combine les résultats
            all_vulnerabilities = user_vulns + vuln_checks
            self.results['vulnerabilities'] = all_vulnerabilities
            
            # Calcule les statistiques
            severity_counts = self._count_by_severity(all_vulnerabilities)
            risk_score = self._calculate_risk_score(all_vulnerabilities)
            
            self.results['statistics'] = {
                'total_vulnerabilities': len(all_vulnerabilities),
                'critical_count': severity_counts['critical'],
                'high_count': severity_counts['high'],
                'medium_count': severity_counts['medium'],
                'low_count': severity_counts['low'],
                'risk_score': risk_score
            }
            
            # Fin du scan
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.results['scan_info']['scan_end'] = end_time.isoformat()
            self.results['scan_info']['scan_duration'] = f"{duration:.2f}s"
            self.results['scan_info']['scan_status'] = 'completed'
            
            # Déconnexion
            self.connector.disconnect()
            
            # Résumé
            logger.info("\n" + "="*60)
            logger.info("📊 RÉSUMÉ DU SCAN")
            logger.info("="*60)
            logger.info(f"✅ Scan terminé en {duration:.2f} secondes")
            logger.info(f"📈 Score de risque: {risk_score}/100")
            logger.info(f"🔴 Critique: {severity_counts['critical']}")
            logger.info(f"🟠 Élevé: {severity_counts['high']}")
            logger.info(f"🟡 Moyen: {severity_counts['medium']}")
            logger.info(f"🟢 Faible: {severity_counts['low']}")
            logger.info(f"📝 Total: {len(all_vulnerabilities)} vulnérabilités")
            logger.info("="*60)
            
            return self.results
            
        except Exception as e:
            logger.error(f"❌ ERREUR DURANT LE SCAN: {str(e)}")
            self.results['scan_info']['scan_status'] = 'failed'
            self.results['scan_info']['error'] = str(e)
            
            # Assure la déconnexion
            try:
                self.connector.disconnect()
            except:
                pass
            
            raise
