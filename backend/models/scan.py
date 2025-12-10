from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Scan(db.Model):
    """Modèle pour stocker les scans"""
    
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, running, completed, failed
    
    # Informations sur la cible
    ad_server = db.Column(db.String(255), nullable=False)
    ad_domain = db.Column(db.String(255), nullable=False)
    
    # Résultats
    total_vulnerabilities = db.Column(db.Integer, default=0)
    critical_count = db.Column(db.Integer, default=0)
    high_count = db.Column(db.Integer, default=0)
    medium_count = db.Column(db.Integer, default=0)
    low_count = db.Column(db.Integer, default=0)
    
    # Score de risque (0-100)
    risk_score = db.Column(db.Integer, default=0)
    
    # Rapport JSON complet
    report_data = db.Column(db.JSON, nullable=True)
    
    # Chemin vers le rapport HTML
    report_path = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<Scan {self.id} - {self.status}>'
    
    def to_dict(self):
        """Convertit le scan en dictionnaire"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'ad_server': self.ad_server,
            'ad_domain': self.ad_domain,
            'total_vulnerabilities': self.total_vulnerabilities,
            'critical_count': self.critical_count,
            'high_count': self.high_count,
            'medium_count': self.medium_count,
            'low_count': self.low_count,
            'risk_score': self.risk_score,
            'report_path': self.report_path
        }
