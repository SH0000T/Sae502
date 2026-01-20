import React, { useState, useEffect } from 'react';
import { 
  AlertCircle, 
  Shield, 
  TrendingUp, 
  Activity,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import apiService from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentScans, setRecentScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Récupère les stats et les scans récents
      const [statsRes, scansRes] = await Promise.all([
        apiService.getStats(),
        apiService.getScans()
      ]);

      setStats(statsRes.data.stats);
      setRecentScans(scansRes.data.scans.slice(0, 5));
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des données');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Chargement du dashboard..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <AlertCircle size={48} color="#e74c3c" />
        <p>{error}</p>
        <button onClick={fetchDashboardData} className="btn-retry">Réessayer</button>
      </div>
    );
  }

  // Données pour le graphique en camembert
  const vulnData = [
    { name: 'Critiques', value: stats?.critical_count || 0, color: '#e74c3c' },
    { name: 'Élevées', value: stats?.high_count || 0, color: '#e67e22' },
    { name: 'Moyennes', value: stats?.medium_count || 0, color: '#f39c12' },
    { name: 'Faibles', value: stats?.low_count || 0, color: '#27ae60' }
  ];

  // Couleur du score de risque
  const getRiskColor = (score) => {
    if (score >= 75) return '#e74c3c';
    if (score >= 50) return '#e67e22';
    if (score >= 25) return '#f39c12';
    return '#27ae60';
  };

  const riskScore = stats?.average_risk_score || 0;
  const riskColor = getRiskColor(riskScore);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>📊 Dashboard de Sécurité</h2>
        <button onClick={fetchDashboardData} className="btn-refresh">
          🔄 Actualiser
        </button>
      </div>

      {/* Cards de statistiques */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#667eea' }}>
            <Shield size={32} />
          </div>
          <div className="stat-content">
            <h3>{stats?.total_scans || 0}</h3>
            <p>Scans Totaux</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: riskColor }}>
            <TrendingUp size={32} />
          </div>
          <div className="stat-content">
            <h3>{riskScore}/100</h3>
            <p>Score de Risque Moyen</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#e74c3c' }}>
            <AlertCircle size={32} />
          </div>
          <div className="stat-content">
            <h3>{stats?.total_vulnerabilities || 0}</h3>
            <p>Vulnérabilités Totales</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#27ae60' }}>
            <CheckCircle size={32} />
          </div>
          <div className="stat-content">
            <h3>{stats?.completed_scans || 0}</h3>
            <p>Scans Complétés</p>
          </div>
        </div>
      </div>

      {/* Graphiques */}
      <div className="charts-grid">
        {/* Graphique en camembert */}
        <div className="chart-card">
          <h3>🎯 Répartition des Vulnérabilités</h3>
          {stats?.total_vulnerabilities > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={vulnData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {vulnData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">
              <p>Aucune donnée disponible</p>
            </div>
          )}
        </div>

        {/* Détails des vulnérabilités */}
        <div className="chart-card">
          <h3>📈 Détails par Criticité</h3>
          <div className="vuln-details">
            <div className="vuln-item" style={{ borderLeftColor: '#e74c3c' }}>
              <div className="vuln-label">
                <AlertTriangle size={20} color="#e74c3c" />
                <span>Critiques</span>
              </div>
              <span className="vuln-count">{stats?.critical_count || 0}</span>
            </div>
            
            <div className="vuln-item" style={{ borderLeftColor: '#e67e22' }}>
              <div className="vuln-label">
                <AlertTriangle size={20} color="#e67e22" />
                <span>Élevées</span>
              </div>
              <span className="vuln-count">{stats?.high_count || 0}</span>
            </div>
            
            <div className="vuln-item" style={{ borderLeftColor: '#f39c12' }}>
              <div className="vuln-label">
                <Activity size={20} color="#f39c12" />
                <span>Moyennes</span>
              </div>
              <span className="vuln-count">{stats?.medium_count || 0}</span>
            </div>
            
            <div className="vuln-item" style={{ borderLeftColor: '#27ae60' }}>
              <div className="vuln-label">
                <CheckCircle size={20} color="#27ae60" />
                <span>Faibles</span>
              </div>
              <span className="vuln-count">{stats?.low_count || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Scans récents */}
      <div className="recent-scans">
        <h3>📋 Scans Récents</h3>
        {recentScans.length > 0 ? (
          <div className="scans-list">
            {recentScans.map((scan) => (
              <div key={scan.id} className="scan-item">
                <div className="scan-info">
                  <span className="scan-domain">{scan.ad_domain}</span>
                  <span className="scan-date">
                    {new Date(scan.created_at).toLocaleString('fr-FR')}
                  </span>
                </div>
                <div className="scan-stats">
                  <span className={`scan-status status-${scan.status}`}>
                    {scan.status === 'completed' ? '✓' : scan.status === 'failed' ? '✗' : '⋯'}
                  </span>
                  <span className="scan-risk" style={{ color: getRiskColor(scan.risk_score) }}>
                    Score: {scan.risk_score}/100
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-data">
            <p>Aucun scan disponible</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
