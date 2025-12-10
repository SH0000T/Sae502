from flask import Blueprint, request, jsonify
from models.scan import db, Scan
from datetime import datetime

scans_bp = Blueprint('scans', __name__)

@scans_bp.route('/scans', methods=['GET'])
def get_scans():
    """Récupère la liste de tous les scans"""
    try:
        scans = Scan.query.order_by(Scan.created_at.desc()).all()
        return jsonify({
            'success': True,
            'count': len(scans),
            'scans': [scan.to_dict() for scan in scans]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scans_bp.route('/scans/<int:scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Récupère les détails d'un scan spécifique"""
    try:
        scan = Scan.query.get(scan_id)
        if not scan:
            return jsonify({
                'success': False,
                'error': 'Scan not found'
            }), 404
        
        result = scan.to_dict()
        result['report_data'] = scan.report_data
        
        return jsonify({
            'success': True,
            'scan': result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scans_bp.route('/scans/start', methods=['POST'])
def start_scan():
    """Lance un nouveau scan"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        ad_server = data.get('ad_server')
        ad_domain = data.get('ad_domain')
        ad_username = data.get('ad_username')
        ad_password = data.get('ad_password')
        
        if not all([ad_server, ad_domain, ad_username, ad_password]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: ad_server, ad_domain, ad_username, ad_password'
            }), 400
        
        # Crée un nouveau scan
        new_scan = Scan(
            ad_server=ad_server,
            ad_domain=ad_domain,
            status='pending'
        )
        
        db.session.add(new_scan)
        db.session.commit()
        
        # TODO: Lancer le scan en arrière-plan (on le fera après)
        # Pour l'instant, on simule juste la création
        
        return jsonify({
            'success': True,
            'message': 'Scan created successfully',
            'scan': new_scan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scans_bp.route('/scans/<int:scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    """Supprime un scan"""
    try:
        scan = Scan.query.get(scan_id)
        if not scan:
            return jsonify({
                'success': False,
                'error': 'Scan not found'
            }), 404
        
        db.session.delete(scan)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Scan deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scans_bp.route('/scans/stats', methods=['GET'])
def get_stats():
    """Récupère les statistiques globales"""
    try:
        total_scans = Scan.query.count()
        completed_scans = Scan.query.filter_by(status='completed').count()
        
        # Calcul des vulnérabilités totales
        scans = Scan.query.filter_by(status='completed').all()
        total_vulns = sum(scan.total_vulnerabilities for scan in scans)
        total_critical = sum(scan.critical_count for scan in scans)
        total_high = sum(scan.high_count for scan in scans)
        total_medium = sum(scan.medium_count for scan in scans)
        total_low = sum(scan.low_count for scan in scans)
        
        # Score de risque moyen
        avg_risk_score = 0
        if completed_scans > 0:
            avg_risk_score = sum(scan.risk_score for scan in scans) // completed_scans
        
        return jsonify({
            'success': True,
            'stats': {
                'total_scans': total_scans,
                'completed_scans': completed_scans,
                'total_vulnerabilities': total_vulns,
                'critical_count': total_critical,
                'high_count': total_high,
                'medium_count': total_medium,
                'low_count': total_low,
                'average_risk_score': avg_risk_score
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
