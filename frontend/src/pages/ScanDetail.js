import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  Download,
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react';
import apiService from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import './ScanDetail.css';

function ScanDetail() {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSeverity, setSelectedSeverity] = useState('all');

  const fetchScanDetail = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiService.getScan(scanId);
      setScan(response.data.scan);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement du scan');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [scanId]);

  useEffect(() => {
    fetchScanDetail();
  }, [fetchScanDetail]);

  const handleDownload = async (format) => {
    try {
      const response = await apiService.downloadReport(scanId, format);
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `rapport_scan_${scanId}.${format === 'text' ? 'txt' : format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Erreur lors du téléchargement du rapport');
      console.error(err);
    }
  };

  const getRiskColor = (score) => {
    if (score >= 75) return '#e74c3c';
    if (score >= 50) return '#e67e22';
    if (score >= 25) return '#f39c12';
    return '#27ae60';
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle size={20} color="#e74c3c" />;
      case 'high':
        return <AlertTriangle size={20} color="#e67e22" />;
      case 'medium':
        return <Info size={20} color="#f39c12" />;
      case 'low':
        return <CheckCircle size={20} color="#27ae60" />;
      default:
        return null;
    }
  };

  const getSeverityLabel = (severity) => {
    const labels = {
      critical: 'Critique',
      high: 'Élevé',
      medium: 'Moyen',
      low: 'Faible'
    };
    return labels[severity] || severity;
  };

  if (loading) {
    return <LoadingSpinner message="Chargement du scan..." />;
  }

  if (error || !scan) {
    return (
      <div className="error-container">
        <AlertCircle size={48} color="#e74c3c" />
        <p>{error || 'Scan introuvable'}</p>
        <button onClick={() => navigate('/history')} className="btn-back">
          Retour à l'historique
        </button>
      </div>
    );
  }

  const vulnerabilities = scan.report_data?.vulnerabilities || [];
  const filteredVulns = selectedSeverity === 'all' 
    ? vulnerabilities 
    : vulnerabilities.filter(v => v.severity === selectedSeverity);

  return (
    <div className="scan-detail">
      {/* Header */}
      <div className="scan-detail-header">
        <button onClick={() => navigate('/history')} className="btn-back">
          <ArrowLeft size={20} />
          Retour
        </button>
        <h2>Détails du Scan #{scan.id}</h2>
        <div className="header-actions">
          <button onClick={() => handleDownload('text')} className="btn-download">
            <Download size={18} />
            TXT
          </button>
          <button onClick={() => handleDownload('csv')} className="btn-download">
            <Download size={18} />
            CSV
          </button>
          <button onClick={() => handleDownload('html')} className="btn-download">
            <Download size={18} />
            HTML
          </button>
        </div>
      </div>

      {/* Informations du scan */}
      <div className="scan-info-card">
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Domaine</span>
            <span className="info-value">{scan.ad_domain}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Serveur</span>
            <span className="info-value">{scan.ad_server}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Date</span>
            <span className="info-value">
              {new Date(scan.created_at).toLocaleString('fr-FR')}
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Score de risque</span>
            <span 
              className="info-value risk-score" 
              style={{ color: getRiskColor(scan.risk_score) }}
            >
              {scan.risk_score}/100
            </span>
          </div>
        </div>
      </div>

      {/* Statistiques */}
      <div className="stats-cards">
        <div className="stat-card critical">
          <div className="stat-number">{scan.critical_count}</div>
          <div className="stat-label">🔴 Critiques</div>
        </div>
        <div className="stat-card high">
          <div className="stat-number">{scan.high_count}</div>
          <div className="stat-label">🟠 Élevées</div>
        </div>
        <div className="stat-card medium">
          <div className="stat-number">{scan.medium_count}</div>
          <div className="stat-label">🟡 Moyennes</div>
        </div>
        <div className="stat-card low">
          <div className="stat-number">{scan.low_count}</div>
          <div className="stat-label">🟢 Faibles</div>
        </div>
      </div>

      {/* Filtres */}
      <div className="filters">
        <button 
          className={`filter-btn ${selectedSeverity === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('all')}
        >
          Toutes ({vulnerabilities.length})
        </button>
        <button 
          className={`filter-btn ${selectedSeverity === 'critical' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('critical')}
        >
          Critiques ({scan.critical_count})
        </button>
        <button 
          className={`filter-btn ${selectedSeverity === 'high' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('high')}
        >
          Élevées ({scan.high_count})
        </button>
        <button 
          className={`filter-btn ${selectedSeverity === 'medium' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('medium')}
        >
          Moyennes ({scan.medium_count})
        </button>
        <button 
          className={`filter-btn ${selectedSeverity === 'low' ? 'active' : ''}`}
          onClick={() => setSelectedSeverity('low')}
        >
          Faibles ({scan.low_count})
        </button>
      </div>

      {/* Liste des vulnérabilités */}
      <div className="vulnerabilities-list">
        {filteredVulns.length === 0 ? (
          <div className="no-vulns">
            <CheckCircle size={48} color="#27ae60" />
            <p>Aucune vulnérabilité de ce type</p>
          </div>
        ) : (
          filteredVulns.map((vuln, index) => (
            <div key={index} className={`vuln-card severity-${vuln.severity}`}>
              <div className="vuln-header">
                <div className="vuln-title">
                  {getSeverityIcon(vuln.severity)}
                  <h3>{vuln.title}</h3>
                  <span className={`severity-badge ${vuln.severity}`}>
                    {getSeverityLabel(vuln.severity)}
                  </span>
                </div>
              </div>
              
              <div className="vuln-body">
                <p className="vuln-description">{vuln.description}</p>
                
                {vuln.cve && (
                  <div className="vuln-cve">
                    <strong>CVE:</strong> {vuln.cve}
                  </div>
                )}
                
                {vuln.affected_items && vuln.affected_items.length > 0 && (
                  <div className="affected-items">
                    <strong>Éléments affectés ({vuln.count}) :</strong>
                    <ul>
                      {vuln.affected_items.slice(0, 5).map((item, i) => (
                        <li key={i}>
                          {typeof item === 'string' 
                            ? item 
                            : item.username || item.user_dn || item.server || JSON.stringify(item)
                          }
                        </li>
                      ))}
                      {vuln.affected_items.length > 5 && (
                        <li className="more-items">
                          ... et {vuln.affected_items.length - 5} autres
                        </li>
                      )}
                    </ul>
                  </div>
                )}
                
                <div className="vuln-recommendation">
                  <strong>✅ Recommandation :</strong>
                  <p>{vuln.recommendation}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ScanDetail;
