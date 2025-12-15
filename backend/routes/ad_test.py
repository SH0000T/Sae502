from flask import Blueprint, request, jsonify
from modules.ad_connector import ADConnector
import logging

ad_test_bp = Blueprint('ad_test', __name__)
logger = logging.getLogger(__name__)

@ad_test_bp.route('/ad/test-connection', methods=['POST'])
def test_ad_connection():
    """Teste la connexion à Active Directory"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['ad_server', 'ad_domain', 'ad_username', 'ad_password']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(required_fields)}'
            }), 400
        
        # Crée le connecteur
        connector = ADConnector(
            server=data['ad_server'],
            domain=data['ad_domain'],
            username=data['ad_username'],
            password=data['ad_password'],
            use_ssl=data.get('use_ssl', True)
        )
        
        # Test de connexion
        result = connector.test_connection()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Connection successful',
                'domain_info': result['domain_info']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error testing AD connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ad_test_bp.route('/ad/users', methods=['POST'])
def get_ad_users():
    """Récupère la liste des utilisateurs AD"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['ad_server', 'ad_domain', 'ad_username', 'ad_password']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(required_fields)}'
            }), 400
        
        # Crée le connecteur
        connector = ADConnector(
            server=data['ad_server'],
            domain=data['ad_domain'],
            username=data['ad_username'],
            password=data['ad_password'],
            use_ssl=data.get('use_ssl', True)
        )
        
        # Connexion et recherche
        connector.connect()
        users = connector.search_users()
        connector.disconnect()
        
        return jsonify({
            'success': True,
            'count': len(users),
            'users': users[:10]  # Limite à 10 pour le test
        }), 200
            
    except Exception as e:
        logger.error(f"Error fetching AD users: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ad_test_bp.route('/ad/privileged-users', methods=['POST'])
def get_privileged_users():
    """Récupère les utilisateurs privilégiés"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['ad_server', 'ad_domain', 'ad_username', 'ad_password']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(required_fields)}'
            }), 400
        
        # Crée le connecteur
        connector = ADConnector(
            server=data['ad_server'],
            domain=data['ad_domain'],
            username=data['ad_username'],
            password=data['ad_password'],
            use_ssl=data.get('use_ssl', True)
        )
        
        # Connexion et recherche
        connector.connect()
        privileged = connector.get_privileged_users()
        connector.disconnect()
        
        return jsonify({
            'success': True,
            'count': len(privileged),
            'privileged_users': privileged
        }), 200
            
    except Exception as e:
        logger.error(f"Error fetching privileged users: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
