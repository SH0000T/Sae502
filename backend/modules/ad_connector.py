"""
Module de connexion à Active Directory via LDAP/LDAPS
"""
from ldap3 import Server, Connection, ALL, NTLM, Tls, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError
import ssl
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ADConnector:
    """Classe pour gérer la connexion à Active Directory"""
    
    def __init__(self, server, domain, username, password, use_ssl=True):
        """
        Initialise la connexion AD
        
        Args:
            server (str): Adresse du serveur AD (ex: dc01.example.com)
            domain (str): Nom du domaine (ex: example.com)
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            use_ssl (bool): Utiliser LDAPS (recommandé)
        """
        self.server_address = server
        self.domain = domain
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.connection = None
        self.base_dn = self._get_base_dn()
        
    def _get_base_dn(self):
        """Génère le Base DN à partir du domaine"""
        parts = self.domain.split('.')
        return ','.join([f'DC={part}' for part in parts])
    
    def connect(self):
        """Établit la connexion à l'AD"""
        try:
            # Configuration du serveur
            port = 636 if self.use_ssl else 389
            
            if self.use_ssl:
                # Configuration TLS pour LDAPS
                tls = Tls(validate=ssl.CERT_NONE)  # En prod, valider le certificat
                server = Server(
                    self.server_address,
                    port=port,
                    use_ssl=True,
                    tls=tls,
                    get_info=ALL
                )
            else:
                server = Server(
                    self.server_address,
                    port=port,
                    get_info=ALL
                )
            
            # Format du username pour NTLM
            user = f'{self.domain}\\{self.username}'
            
            # Connexion avec authentification NTLM
            self.connection = Connection(
                server,
                user=user,
                password=self.password,
                authentication=NTLM,
                auto_bind=True
            )
            
            logger.info(f"✅ Connexion réussie à {self.server_address}")
            return True
            
        except LDAPBindError as e:
            logger.error(f"❌ Erreur d'authentification: {str(e)}")
            raise Exception(f"Authentication failed: Invalid credentials")
        except LDAPException as e:
            logger.error(f"❌ Erreur LDAP: {str(e)}")
            raise Exception(f"LDAP connection failed: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Erreur de connexion: {str(e)}")
            raise Exception(f"Connection failed: {str(e)}")
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.connection:
            self.connection.unbind()
            logger.info("Connexion fermée")
    
    def test_connection(self):
        """Test simple de connexion"""
        try:
            self.connect()
            info = self.get_domain_info()
            self.disconnect()
            return {
                'success': True,
                'message': 'Connection successful',
                'domain_info': info
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_domain_info(self):
        """Récupère les informations du domaine"""
        if not self.connection:
            raise Exception("Not connected to AD")
        
        try:
            # Recherche les informations du domaine
            self.connection.search(
                search_base=self.base_dn,
                search_filter='(objectClass=domain)',
                search_scope=SUBTREE,
                attributes=['name', 'distinguishedName', 'whenCreated', 'minPwdLength', 'maxPwdAge']
            )
            
            if self.connection.entries:
                entry = self.connection.entries[0]
                return {
                    'domain_name': str(entry.name) if hasattr(entry, 'name') else self.domain,
                    'distinguished_name': str(entry.distinguishedName),
                    'base_dn': self.base_dn
                }
            
            return {
                'domain_name': self.domain,
                'base_dn': self.base_dn
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du domaine: {str(e)}")
            return {
                'domain_name': self.domain,
                'base_dn': self.base_dn
            }
    
    def search_users(self, filter_query='(objectClass=user)', attributes=None):
        """
        Recherche des utilisateurs dans l'AD
        
        Args:
            filter_query (str): Filtre LDAP
            attributes (list): Liste des attributs à récupérer
        
        Returns:
            list: Liste des utilisateurs trouvés
        """
        if not self.connection:
            raise Exception("Not connected to AD")
        
        if attributes is None:
            attributes = [
                'sAMAccountName', 'userPrincipalName', 'displayName',
                'memberOf', 'whenCreated', 'lastLogon', 'pwdLastSet',
                'userAccountControl', 'adminCount'
            ]
        
        try:
            self.connection.search(
                search_base=self.base_dn,
                search_filter=filter_query,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            users = []
            for entry in self.connection.entries:
                user = {}
                for attr in attributes:
                    if hasattr(entry, attr):
                        user[attr] = str(getattr(entry, attr))
                users.append(user)
            
            logger.info(f"Trouvé {len(users)} utilisateurs")
            return users
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'utilisateurs: {str(e)}")
            raise
    
    def search_groups(self, filter_query='(objectClass=group)', attributes=None):
        """
        Recherche des groupes dans l'AD
        
        Args:
            filter_query (str): Filtre LDAP
            attributes (list): Liste des attributs à récupérer
        
        Returns:
            list: Liste des groupes trouvés
        """
        if not self.connection:
            raise Exception("Not connected to AD")
        
        if attributes is None:
            attributes = ['sAMAccountName', 'distinguishedName', 'member', 'whenCreated']
        
        try:
            self.connection.search(
                search_base=self.base_dn,
                search_filter=filter_query,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            groups = []
            for entry in self.connection.entries:
                group = {}
                for attr in attributes:
                    if hasattr(entry, attr):
                        group[attr] = str(getattr(entry, attr))
                groups.append(group)
            
            logger.info(f"Trouvé {len(groups)} groupes")
            return groups
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de groupes: {str(e)}")
            raise
    
    def get_privileged_users(self):
        """Récupère les utilisateurs avec des privilèges élevés"""
        if not self.connection:
            raise Exception("Not connected to AD")
        
        privileged_groups = [
            'Domain Admins',
            'Enterprise Admins',
            'Schema Admins',
            'Administrators',
            'Account Operators',
            'Backup Operators',
            'Server Operators',
            'Print Operators'
        ]
        
        privileged_users = []
        
        for group_name in privileged_groups:
            try:
                # Recherche le groupe
                self.connection.search(
                    search_base=self.base_dn,
                    search_filter=f'(&(objectClass=group)(sAMAccountName={group_name}))',
                    search_scope=SUBTREE,
                    attributes=['member']
                )
                
                if self.connection.entries:
                    group = self.connection.entries[0]
                    if hasattr(group, 'member'):
                        members = group.member.values if hasattr(group.member, 'values') else [str(group.member)]
                        for member_dn in members:
                            privileged_users.append({
                                'user_dn': str(member_dn),
                                'group': group_name
                            })
            except Exception as e:
                logger.warning(f"Erreur lors de la recherche du groupe {group_name}: {str(e)}")
                continue
        
        logger.info(f"Trouvé {len(privileged_users)} utilisateurs privilégiés")
        return privileged_users
