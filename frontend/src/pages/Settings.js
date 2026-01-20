import React from 'react';
import { Settings as SettingsIcon } from 'lucide-react';
import './Settings.css';

function Settings() {
  return (
    <div className="settings">
      <div className="settings-header">
        <h2>⚙️ Paramètres</h2>
      </div>

      <div className="settings-content">
        <div className="settings-section">
          <SettingsIcon size={64} color="#cbd5e0" />
          <h3>Paramètres</h3>
          <p>Cette section sera développée prochainement.</p>
          <ul>
            <li>Configuration des notifications</li>
            <li>Gestion des utilisateurs</li>
            <li>Planification des scans automatiques</li>
            <li>Configuration SMTP pour les emails</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Settings;
