import os
from datetime import timedelta

class Config:
    """Configuration de base"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://admin:ChangeMe123!@localhost:5432/adsecurecheck'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Reports
    REPORTS_DIR = '/app/reports'
    
    # Active Directory (à configurer par l'utilisateur)
    AD_SERVER = os.getenv('AD_SERVER', '')
    AD_DOMAIN = os.getenv('AD_DOMAIN', '')
    AD_USE_SSL = os.getenv('AD_USE_SSL', 'true').lower() == 'true'

class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
