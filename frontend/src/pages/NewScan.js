import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  PlayCircle, 
  Server, 
  Globe, 
  User, 
  Lock,
  Mail,
  AlertCircle,
  CheckCircle,
  Loader
} from 'lucide-react';
import apiService from '../services/api';
import './NewScan.css';

function NewScan() {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    ad_server: '',
    ad_domain: '',
    ad_username: '',
    ad_password: '',
    use_ssl: false,
    send_email: true,
    email_to: 'evanchezlui42@gmail.com'
  });

  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleTestConnection = async (e) => {
    e.preventDefault();
    
    if (!formData.ad_server || !formData.ad_domain || !formData.ad_username || !formData.ad_password) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setTesting(true);
    setTestResult(null);
    setError(null);

    try {
      const response = await apiService.testADConnection({
        ad_server: formData.ad_server,
        ad_domain: formData.ad_domain,
        ad_username: formData.ad_username,
        ad_password: formData.ad_password,
        use_ssl: formData.use_ssl
      });

      if (response.data.success) {
        setTestResult({
          success: true,
          message: 'Connexion réussie !',
          domain_info: response.data.domain_info
        });
      } else {
        setTestResult({
          success: false,
          message: response.data.error || 'Échec de la connexion'
        });
      }
    } catch (err) {
      setTestResult({
        success: false,
        message: err.response?.data?.error || 'Erreur lors du test de connexion'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.ad_server || !formData.ad_domain || !formData.ad_username || !formData.ad_password) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.startScan(formData);
      
      if (response.data.success) {
        // Redirige vers la page de détail du scan
        navigate(`/scan/${response.data.scan.id}`);
      } else {
        setError(response.data.error || 'Erreur lors du lancement du scan');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du lancement du scan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="new-scan">
      <div className="new-scan-header">
        <h2>🚀 Lancer un Nouveau Scan</h2>
        <p>Configurez les paramètres de connexion à votre Active Directory</p>
      </div>

      <div className="new-scan-container">
        <form onSubmit={handleSubmit} className="scan-form">
          
          {/* Configuration AD */}
          <div className="form-section">
            <h3>📡 Configuration Active Directory</h3>
            
            <div className="form-group">
              <label htmlFor="ad_server">
                <Server size={18} />
                Serveur AD (IP ou FQDN) *
              </label>
              <input
                type="text"
                id="ad_server"
                name="ad_server"
                value={formData.ad_server}
                onChange={handleChange}
                placeholder="192.168.80.2 ou dc01.example.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="ad_domain">
                <Globe size={18} />
                Domaine *
              </label>
              <input
                type="text"
                id="ad_domain"
                name="ad_domain"
                value={formData.ad_domain}
                onChange={handleChange}
                placeholder="example.local"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="ad_username">
                <User size={18} />
                Nom d'utilisateur *
              </label>
              <input
                type="text"
                id="ad_username"
                name="ad_username"
                value={formData.ad_username}
                onChange={handleChange}
                placeholder="Administrateur"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="ad_password">
                <Lock size={18} />
                Mot de passe *
              </label>
              <input
                type="password"
                id="ad_password"
                name="ad_password"
                value={formData.ad_password}
                onChange={handleChange}
                placeholder="••••••••"
                required
              />
            </div>

            <div className="form-group-checkbox">
              <input
                type="checkbox"
                id="use_ssl"
                name="use_ssl"
                checked={formData.use_ssl}
                onChange={handleChange}
              />
              <label htmlFor="use_ssl">
                Utiliser LDAPS (SSL/TLS)
              </label>
            </div>
          </div>

          {/* Configuration Email */}
          <div className="form-section">
            <h3>📧 Configuration Email</h3>
            
            <div className="form-group-checkbox">
              <input
                type="checkbox"
                id="send_email"
                name="send_email"
                checked={formData.send_email}
                onChange={handleChange}
              />
              <label htmlFor="send_email">
                Envoyer le rapport par email
              </label>
            </div>

            {formData.send_email && (
              <div className="form-group">
                <label htmlFor="email_to">
                  <Mail size={18} />
                  Adresse email
                </label>
                <input
                  type="email"
                  id="email_to"
                  name="email_to"
                  value={formData.email_to}
                  onChange={handleChange}
                  placeholder="votre.email@exemple.com"
                />
              </div>
            )}
          </div>

          {/* Test de connexion */}
          <div className="form-actions">
            <button
              type="button"
              onClick={handleTestConnection}
              className="btn-test"
              disabled={testing || loading}
            >
              {testing ? (
                <>
                  <Loader size={18} className="spinning" />
                  Test en cours...
                </>
              ) : (
                <>
                  <CheckCircle size={18} />
                  Tester la connexion
                </>
              )}
            </button>

            <button
              type="submit"
              className="btn-submit"
              disabled={loading || testing}
            >
              {loading ? (
                <>
                  <Loader size={18} className="spinning" />
                  Scan en cours...
                </>
              ) : (
                <>
                  <PlayCircle size={18} />
                  Lancer le scan
                </>
              )}
            </button>
          </div>

          {/* Résultat du test */}
          {testResult && (
            <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
              {testResult.success ? (
                <>
                  <CheckCircle size={24} />
                  <div>
                    <strong>✓ {testResult.message}</strong>
                    {testResult.domain_info && (
                      <p>Domaine: {testResult.domain_info.domain_name}</p>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <AlertCircle size={24} />
                  <div>
                    <strong>✗ {testResult.message}</strong>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Erreur */}
          {error && (
            <div className="error-message">
              <AlertCircle size={24} />
              <span>{error}</span>
            </div>
          )}
        </form>

        {/* Informations d'aide */}
        <div className="scan-info">
          <h3>ℹ️ Informations</h3>
          
          <div className="info-section">
            <h4>Prérequis</h4>
            <ul>
              <li>Accès réseau au contrôleur de domaine</li>
              <li>Compte avec droits de lecture sur l'AD</li>
              <li>Port LDAP (389) ou LDAPS (636) ouvert</li>
            </ul>
          </div>

          <div className="info-section">
            <h4>Détails du scan</h4>
            <ul>
              <li>✓ Analyse des comptes utilisateurs</li>
              <li>✓ Détection des privilèges excessifs</li>
              <li>✓ Vérification des politiques de sécurité</li>
              <li>✓ Recherche de vulnérabilités connues</li>
              <li>✓ Génération de rapports détaillés</li>
            </ul>
          </div>

          <div className="info-section">
            <h4>Durée estimée</h4>
            <p>Entre 2 et 10 minutes selon la taille de l'AD</p>
          </div>

          <div className="info-section warning">
            <h4>⚠️ Attention</h4>
            <p>Les credentials ne sont jamais stockés. Ils sont utilisés uniquement pour la durée du scan.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default NewScan;
