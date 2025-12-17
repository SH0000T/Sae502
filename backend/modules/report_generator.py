"""
Module de génération de rapports détaillés
"""
import json
import csv
from datetime import datetime
from io import StringIO
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Génère des rapports dans différents formats"""
    
    def __init__(self, scan_results):
        """
        Initialise le générateur de rapports
        
        Args:
            scan_results (dict): Résultats complets du scan
        """
        self.results = scan_results
        self.vulnerabilities = scan_results.get('vulnerabilities', [])
        self.stats = scan_results.get('statistics', {})
        self.scan_info = scan_results.get('scan_info', {})
    
    def _format_severity_emoji(self, severity):
        """Retourne l'emoji correspondant à la criticité"""
        emojis = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        return emojis.get(severity, '⚪')
    
    def _format_affected_items_detailed(self, vuln):
        """
        Formate les éléments affectés de manière détaillée et lisible
        
        Args:
            vuln (dict): Vulnérabilité
        
        Returns:
            list: Liste de chaînes formatées
        """
        affected = vuln.get('affected_items', [])
        details = []
        
        if not affected:
            return ['Aucun élément spécifique identifié']
        
        for item in affected[:10]:  # Limite à 10 pour la lisibilité
            if isinstance(item, dict):
                # Format selon le type de vulnérabilité
                if 'username' in item:
                    user = item['username']
                    status = item.get('status', item.get('reason', 'N/A'))
                    last_logon = item.get('last_logon', 'N/A')
                    group = item.get('group', '')
                    
                    if group:
                        details.append(f"  • Utilisateur: {user} | Groupe: {group}")
                    elif last_logon:
                        details.append(f"  • Utilisateur: {user} | Dernière connexion: {last_logon} | Statut: {status}")
                    else:
                        details.append(f"  • Utilisateur: {user} | Statut: {status}")
                
                elif 'user_dn' in item:
                    dn = item['user_dn']
                    group = item.get('group', 'N/A')
                    # Extrait le CN du DN
                    cn = dn.split(',')[0].replace('CN=', '')
                    details.append(f"  • Utilisateur: {cn} | Groupe privilégié: {group}")
                
                elif 'policy' in item:
                    policy = item['policy']
                    current = item.get('current_value', 'N/A')
                    recommended = item.get('recommended_value', 'N/A')
                    details.append(f"  • Politique: {policy}")
                    details.append(f"    Valeur actuelle: {current}")
                    details.append(f"    Valeur recommandée: {recommended}")
                
                elif 'server' in item:
                    server = item['server']
                    details.append(f"  • Serveur: {server}")
                
                elif 'dn' in item:
                    dn = item['dn']
                    cn = dn.split(',')[0].replace('CN=', '')
                    details.append(f"  • DN: {cn}")
                
                else:
                    # Format générique
                    details.append(f"  • {json.dumps(item, indent=4)}")
            else:
                details.append(f"  • {str(item)}")
        
        if len(affected) > 10:
            details.append(f"  ... et {len(affected) - 10} autres éléments")
        
        return details
    
    def generate_text_report(self):
        """Génère un rapport texte formaté"""
        lines = []
        lines.append("=" * 80)
        lines.append("RAPPORT D'AUDIT DE SÉCURITÉ ACTIVE DIRECTORY")
        lines.append("=" * 80)
        lines.append("")
        
        # Informations du scan
        lines.append("📊 INFORMATIONS DU SCAN")
        lines.append("-" * 80)
        lines.append(f"Serveur AD: {self.scan_info.get('server', 'N/A')}")
        lines.append(f"Domaine: {self.scan_info.get('domain', 'N/A')}")
        lines.append(f"Date du scan: {self.scan_info.get('scan_start', 'N/A')}")
        lines.append(f"Durée: {self.scan_info.get('scan_duration', 'N/A')}")
        lines.append(f"Statut: {self.scan_info.get('scan_status', 'N/A')}")
        lines.append("")
        
        # Statistiques
        lines.append("📈 RÉSUMÉ DES VULNÉRABILITÉS")
        lines.append("-" * 80)
        lines.append(f"Score de risque global: {self.stats.get('risk_score', 0)}/100")
        lines.append(f"Total de vulnérabilités: {self.stats.get('total_vulnerabilities', 0)}")
        lines.append(f"  🔴 Critiques: {self.stats.get('critical_count', 0)}")
        lines.append(f"  🟠 Élevées: {self.stats.get('high_count', 0)}")
        lines.append(f"  🟡 Moyennes: {self.stats.get('medium_count', 0)}")
        lines.append(f"  🟢 Faibles: {self.stats.get('low_count', 0)}")
        lines.append("")
        
        # Détail des vulnérabilités par criticité
        for severity in ['critical', 'high', 'medium', 'low']:
            vulns_by_severity = [v for v in self.vulnerabilities if v['severity'] == severity]
            
            if not vulns_by_severity:
                continue
            
            emoji = self._format_severity_emoji(severity)
            severity_name = severity.upper()
            
            lines.append("")
            lines.append("=" * 80)
            lines.append(f"{emoji} VULNÉRABILITÉS {severity_name} ({len(vulns_by_severity)})")
            lines.append("=" * 80)
            
            for i, vuln in enumerate(vulns_by_severity, 1):
                lines.append("")
                lines.append(f"[{severity_name} #{i}] {vuln['title']}")
                lines.append("-" * 80)
                lines.append(f"Description: {vuln['description']}")
                
                if vuln.get('cve'):
                    lines.append(f"CVE: {vuln['cve']}")
                
                count = vuln.get('count', 0)
                if count > 0:
                    lines.append(f"Nombre d'éléments affectés: {count}")
                
                # Détails des éléments affectés
                lines.append("")
                lines.append("Éléments affectés:")
                affected_details = self._format_affected_items_detailed(vuln)
                lines.extend(affected_details)
                
                lines.append("")
                lines.append("✅ Recommandation:")
                lines.append(f"  {vuln['recommendation']}")
                lines.append("")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("FIN DU RAPPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_csv_report(self):
        """Génère un rapport CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # En-tête
        writer.writerow([
            'Criticité',
            'Titre',
            'Description',
            'CVE',
            'Nombre affecté',
            'Éléments affectés',
            'Recommandation'
        ])
        
        # Lignes
        for vuln in self.vulnerabilities:
            affected_items = vuln.get('affected_items', [])
            affected_str = '; '.join([
                str(item) if not isinstance(item, dict) else 
                f"{item.get('username', item.get('user_dn', item.get('server', json.dumps(item))))}"
                for item in affected_items[:5]
            ])
            
            if len(affected_items) > 5:
                affected_str += f" ... et {len(affected_items) - 5} autres"
            
            writer.writerow([
                vuln['severity'].upper(),
                vuln['title'],
                vuln['description'],
                vuln.get('cve', 'N/A'),
                vuln.get('count', 0),
                affected_str,
                vuln['recommendation']
            ])
        
        return output.getvalue()
    
    def generate_html_summary(self):
        """Génère un résumé HTML simple"""
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .critical {{ color: #e74c3c; }}
                .high {{ color: #e67e22; }}
                .medium {{ color: #f39c12; }}
                .low {{ color: #27ae60; }}
                .stats {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
                .vuln {{ border-left: 4px solid #3498db; padding: 10px; margin: 10px 0; background: #f8f9fa; }}
                .recommendation {{ background: #d4edda; padding: 10px; margin-top: 10px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>🔐 Rapport d'Audit Active Directory</h1>
            
            <div class="stats">
                <h2>📊 Résumé</h2>
                <p><strong>Serveur:</strong> {self.scan_info.get('server', 'N/A')}</p>
                <p><strong>Domaine:</strong> {self.scan_info.get('domain', 'N/A')}</p>
                <p><strong>Date:</strong> {self.scan_info.get('scan_start', 'N/A')}</p>
                <p><strong>Score de risque:</strong> {self.stats.get('risk_score', 0)}/100</p>
                <p><strong>Vulnérabilités totales:</strong> {self.stats.get('total_vulnerabilities', 0)}</p>
                <ul>
                    <li class="critical">🔴 Critiques: {self.stats.get('critical_count', 0)}</li>
                    <li class="high">🟠 Élevées: {self.stats.get('high_count', 0)}</li>
                    <li class="medium">🟡 Moyennes: {self.stats.get('medium_count', 0)}</li>
                    <li class="low">🟢 Faibles: {self.stats.get('low_count', 0)}</li>
                </ul>
            </div>
            
            <h2>🔍 Détails des vulnérabilités</h2>
        """
        
        for vuln in self.vulnerabilities:
            severity_class = vuln['severity']
            emoji = self._format_severity_emoji(vuln['severity'])
            
            html += f"""
            <div class="vuln {severity_class}">
                <h3>{emoji} {vuln['title']}</h3>
                <p><strong>Criticité:</strong> <span class="{severity_class}">{vuln['severity'].upper()}</span></p>
                <p>{vuln['description']}</p>
                <p><strong>Éléments affectés:</strong> {vuln.get('count', 0)}</p>
                <div class="recommendation">
                    <strong>✅ Recommandation:</strong> {vuln['recommendation']}
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
