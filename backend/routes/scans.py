from flask import Blueprint, request, jsonify
from models.scan import db, Scan
from modules.scanner import ADScanner
from datetime import datetime
import logging

scans_bp = Blueprint('scans', __name__)
logger = logging.getLogger(__name__)

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
        use_ssl = data.get('use_ssl', False)
        
        if not all([ad_server, ad_domain, ad_username, ad_password]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: ad_server, ad_domain, ad_username, ad_password'
            }), 400
        
        # Crée un nouveau scan
        new_scan = Scan(
            ad_server=ad_server,
            ad_domain=ad_domain,
            status='running'
        )
        
        db.session.add(new_scan)
        db.session.commit()
        
        try:
            # Lance le scan
            logger.info(f"🚀 Démarrage du scan #{new_scan.id}...")
            
            scanner = ADScanner(
                ad_server=ad_server,
                ad_domain=ad_domain,
                ad_username=ad_username,
                ad_password=ad_password,
                use_ssl=use_ssl
            )
            
            results = scanner.run_full_scan()
            
            # Met à jour le scan avec les résultats
            new_scan.status = 'completed'
            new_scan.completed_at = datetime.utcnow()
            new_scan.report_data = results
            new_scan.total_vulnerabilities = results['statistics']['total_vulnerabilities']
            new_scan.critical_count = results['statistics']['critical_count']
            new_scan.high_count = results['statistics']['high_count']
            new_scan.medium_count = results['statistics']['medium_count']
            new_scan.low_count = results['statistics']['low_count']
            new_scan.risk_score = results['statistics']['risk_score']
            
            db.session.commit()
            
            logger.info(f"✅ Scan #{new_scan.id} terminé avec succès")
            
            return jsonify({
                'success': True,
                'message': 'Scan completed successfully',
                'scan': new_scan.to_dict(),
                'results': results
            }), 201
            
        except Exception as scan_error:
            # Met à jour le statut en échec
            new_scan.status = 'failed'
            new_scan.completed_at = datetime.utcnow()
            new_scan.report_data = {'error': str(scan_error)}
            db.session.commit()
            
            logger.error(f"❌ Scan #{new_scan.id} échoué: {str(scan_error)}")
            
            return jsonify({
                'success': False,
                'error': f'Scan failed: {str(scan_error)}',
                'scan_id': new_scan.id
            }), 500
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Erreur lors de la création du scan: {str(e)}")
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
        failed_scans = Scan.query.filter_by(status='failed').count()
        running_scans = Scan.query.filter_by(status='running').count()
        
        # Calcul des vulnérabilités totales
        scans = Scan.query.filter_by(status='completed').all()
        total_vulns = sum(scan.total_vulnerabilities for scan in scans) if scans else 0
        total_critical = sum(scan.critical_count for scan in scans) if scans else 0
        total_high = sum(scan.high_count for scan in scans) if scans else 0
        total_medium = sum(scan.medium_count for scan in scans) if scans else 0
        total_low = sum(scan.low_count for scan in scans) if scans else 0
        
        # Score de risque moyen
        avg_risk_score = 0
        if completed_scans > 0:
            avg_risk_score = sum(scan.risk_score for scan in scans) // completed_scans
        
        return jsonify({
            'success': True,
            'stats': {
                'total_scans': total_scans,
                'completed_scans': completed_scans,
                'failed_scans': failed_scans,
                'running_scans': running_scans,
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
