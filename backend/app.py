from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from models.scan import db
import os

def create_app(config_name='development'):
    """Factory pour créer l'application Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Active CORS
    CORS(app)
    
    # Initialise la base de données
    db.init_app(app)
    
    # Crée les tables
    with app.app_context():
        db.create_all()
    
    # Route de santé
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'ok',
            'message': 'AdSecureCheck API is running',
            'version': '1.0.0'
        }), 200
    
    # Route d'accueil
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': 'Welcome to AdSecureCheck API',
            'endpoints': {
                'health': '/api/health',
                'scans': '/api/scans',
                'scan_details': '/api/scans/<id>',
                'start_scan': '/api/scans/start',
                'stats': '/api/scans/stats'
            }
        }), 200
    
    # Enregistrement des routes
    from routes.scans import scans_bp
    app.register_blueprint(scans_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
