"""
Module d'envoi d'emails avec rapports en pièce jointe
Compatible Gmail (SMTP + App Password)
"""

import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)


class EmailSender:
    """Classe pour envoyer des emails avec rapports"""

    def __init__(self):
        # Configuration SMTP Gmail
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587

        # Variables d'environnement (OBLIGATOIRES)
        self.from_email = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASSWORD')

        if not self.from_email or not self.password:
            logger.error("❌ EMAIL_USER ou EMAIL_PASSWORD non définis")
            raise RuntimeError(
                "Variables d'environnement EMAIL_USER / EMAIL_PASSWORD manquantes"
            )

    def send_report(self, to_email, scan_results, text_report, csv_report, html_report):
        """
        Envoie le rapport par email

        Args:
            to_email (str): Adresse email du destinataire
            scan_results (dict): Résultats du scan
            text_report (str): Rapport texte
            csv_report (str): Rapport CSV
            html_report (str): Rapport HTML

        Returns:
            bool: True si envoyé, False sinon
        """

        try:
            logger.info(f"📧 Préparation de l'email pour {to_email}")

            # Création du message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = (
                f"[AdSecureCheck] Rapport d'audit AD - "
                f"{scan_results['scan_info']['domain']}"
            )

            stats = scan_results['statistics']
            scan_info = scan_results['scan_info']

            body = f"""
Bonjour,

Voici le rapport d'audit de sécurité Active Directory.

📊 RÉSUMÉ DU SCAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Serveur : {scan_info.get('server', 'N/A')}
Domaine : {scan_info.get('domain', 'N/A')}
Date    : {scan_info.get('scan_start', 'N/A')}
Durée   : {scan_info.get('scan_duration', 'N/A')}

Score de risque : {stats.get('risk_score', 'N/A')}/100

Vulnérabilités détectées :
  🔴 Critiques : {stats.get('critical_count', 0)}
  🟠 Élevées   : {stats.get('high_count', 0)}
  🟡 Moyennes  : {stats.get('medium_count', 0)}
  🟢 Faibles   : {stats.get('low_count', 0)}

Total : {stats.get('total_vulnerabilities', 0)} vulnérabilités

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 Pièces jointes :
  • rapport_complet.txt
  • rapport_vulnerabilites.csv
  • rapport_resume.html

Cordialement,
AdSecureCheck - Automated Security Audit
            """

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # ---------- PJ TEXTE ----------
            part_txt = MIMEBase('application', 'octet-stream')
            part_txt.set_payload(text_report.encode('utf-8'))
            encoders.encode_base64(part_txt)
            part_txt.add_header(
                'Content-Disposition',
                'attachment',
                filename="rapport_complet.txt"
            )
            msg.attach(part_txt)

            # ---------- PJ CSV ----------
            part_csv = MIMEBase('application', 'octet-stream')
            part_csv.set_payload(csv_report.encode('utf-8'))
            encoders.encode_base64(part_csv)
            part_csv.add_header(
                'Content-Disposition',
                'attachment',
                filename="rapport_vulnerabilites.csv"
            )
            msg.attach(part_csv)

            # ---------- PJ HTML ----------
            part_html = MIMEText(html_report, 'html', 'utf-8')
            part_html.add_header(
                'Content-Disposition',
                'attachment',
                filename="rapport_resume.html"
            )
            msg.attach(part_html)

            # ---------- ENVOI SMTP ----------
            logger.info("📤 Connexion au serveur SMTP Gmail")

            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()

            logger.info(f"🔐 Authentification SMTP : {self.from_email}")
            server.login(self.from_email, self.password)

            logger.info("📨 Envoi de l'email")
            server.send_message(msg)
            server.quit()

            logger.info(f"✅ Email envoyé avec succès à {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error("❌ Erreur d'authentification SMTP")
            logger.error(str(e))
            logger.error("➡️ Vérifie l'App Password Gmail")
            return False

        except smtplib.SMTPException as e:
            logger.error("❌ Erreur SMTP")
            logger.error(str(e))
            return False

        except Exception as e:
            logger.error("❌ Erreur inattendue lors de l'envoi de l'email")
            logger.exception(e)
            return False
