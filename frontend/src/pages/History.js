import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  History as HistoryIcon,
  Eye,
  Trash2,
  Download,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import apiService from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import './History.css';

function History() {
  const navigate = useNavigate();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchScans();
  }, []);

  const fetchScans = async () => {
    try {
      setLoading(true);
      const response = await apiService.getScans();
      setScans(response.data.scans);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement de l\'historique');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (scanId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce scan ?')) {
      return;
    }

    try {
      await apiService.deleteScan(scanId);
      setScans(scans.filter(s => s.id !== scanId));
    } catch (err) {
      alert('Erreur lors de la suppression du scan');
      console.error(err);
    }
  };

  const handleDownload = async (scanId, format) => {
    try {
      const response = await apiService.downloadReport(scanId, format);
      
      // Crée un lien de téléchargement
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={20} color="#27ae60" />;
      case 'failed':
        return <AlertCircle size={20} color="#e74c3c" />;
      case 'running':
        return <Clock size={20} color="#3498db" />;
      default:
        return <Clock size={20} color="#95a5a6" />;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed':
        return 'Terminé';
      case 'failed':
        return 'Échoué';
      case 'running':
        return 'En cours';
      default:
        return 'En attente';
    }
  };

  if (loading) {
    return <LoadingSpinner message="Chargement de l'historique..." />;
  }

  return (
    <div className="history">
      <div className="history-header">
        <h2>📋 Historique des Scans</h2>
        <button onClick={fetchScans} className="btn-refresh">
          🔄 Actualiser
        </button>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={24} />
          <span>{error}</span>
        </div>
      )}

      {scans.length === 0 ? (
        <div className="no-scans">
          <HistoryIcon size={64} color="#cbd5e0" />
          <h3>Aucun scan disponible</h3>
          <p>Lancez votre premier scan pour commencer</p>
          <button 
            onClick={() => navigate('/new-scan')} 
            className="btn-new-scan"
          >
            Nouveau Scan
          </button>
        </div>
      ) : (
        <div className="scans-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Domaine</th>
                <th>Serveur</th>
                <th>Date</th>
                <th>Statut</th>
                <th>Score de Risque</th>
                <th>Vulnérabilités</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan) => (
                <tr key={scan.id}>
                  <td>#{scan.id}</td>
                  <td className="scan-domain">{scan.ad_domain}</td>
                  <td>{scan.ad_server}</td>
                  <td>{new Date(scan.created_at).toLocaleString('fr-FR')}</td>
                  <td>
                    <span className={`status-badge status-${scan.status}`}>
                      {getStatusIcon(scan.status)}
                      {getStatusLabel(scan.status)}
                    </span>
                  </td>
                  <td>
                    <span 
                      className="risk-score"
                      style={{ color: getRiskColor(scan.risk_score) }}
                    >
                      {scan.risk_score}/100
                    </span>
                  </td>
                  <td>
                    <div className="vuln-summary">
                      {scan.critical_count > 0 && (
                        <span className="vuln-badge critical">
                          🔴 {scan.critical_count}
                        </span>
                      )}
                      {scan.high_count > 0 && (
                        <span className="vuln-badge high">
                          🟠 {scan.high_count}
                        </span>
                      )}
                      {scan.medium_count > 0 && (
                        <span className="vuln-badge medium">
                          🟡 {scan.medium_count}
                        </span>
                      )}
                      {scan.low_count > 0 && (
                        <span className="vuln-badge low">
                          🟢 {scan.low_count}
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        onClick={() => navigate(`/scan/${scan.id}`)}
                        className="btn-action btn-view"
                        title="Voir les détails"
                      >
                        <Eye size={18} />
                      </button>
                      
                      {scan.status === 'completed' && (
                        <div className="dropdown">
                          <button className="btn-action btn-download" title="Télécharger">
                            <Download size={18} />
                          </button>
                          <div className="dropdown-content">
                            <button onClick={() => handleDownload(scan.id, 'text')}>
                              📄 TXT
                            </button>
                            <button onClick={() => handleDownload(scan.id, 'csv')}>
                              📊 CSV
                            </button>
                            <button onClick={() => handleDownload(scan.id, 'html')}>
                              🌐 HTML
                            </button>
                          </div>
                        </div>
                      )}
                      
                      <button
                        onClick={() => handleDelete(scan.id)}
                        className="btn-action btn-delete"
                        title="Supprimer"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default History;
