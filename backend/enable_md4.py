"""
Script pour activer MD4 dans OpenSSL (nécessaire pour NTLM)
"""
import ssl
import hashlib

def enable_legacy_algorithms():
    """Active les algorithmes legacy d'OpenSSL"""
    try:
        # Essaie de créer un hash MD4 pour vérifier si c'est activé
        hashlib.new('md4')
        print("✅ MD4 déjà activé")
        return True
    except ValueError:
        print("⚠️ MD4 désactivé, tentative d'activation...")
        
        # Configure OpenSSL pour accepter les algorithmes legacy
        import os
        os.environ['OPENSSL_CONF'] = '/app/openssl.cnf'
        
        return False

if __name__ == "__main__":
    enable_legacy_algorithms()
