import React from 'react';
import { Shield } from 'lucide-react';
import './Navbar.css';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Shield size={32} className="navbar-icon" />
        <h1>AdSecureCheck</h1>
      </div>
      <div className="navbar-info">
        <span className="navbar-subtitle">Automated AD Security Audit</span>
      </div>
    </nav>
  );
}

export default Navbar;
