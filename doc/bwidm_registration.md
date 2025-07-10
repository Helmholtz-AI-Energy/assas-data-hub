# bwIDM (Baden-Württemberg Identity Management) OAuth/OIDC Registration and Setup Guide

This guide explains how to register your application with bwIDM (Baden-Württemberg Identity Management), understand the OpenID Connect (OIDC) flow, and integrate it with the ASSAS Data Hub for institutional authentication.

## Table of Contents

1. [bwIDM Registration Process](#bwidm-registration-process)
2. [OpenID Connect Flow Explanation](#openid-connect-flow-explanation)
3. [AARC Entitlements and Role Mapping](#aarc-entitlements-and-role-mapping)
4. [Security Features](#security-features)
5. [Code Implementation Details](#code-implementation-details)
6. [Testing and Debugging](#testing-and-debugging)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

## bwIDM Registration Process

### Step 1: Request bwIDM Client Registration

bwIDM uses a formal registration process for production applications.

#### Development/Testing Registration

1. **Contact bwIDM Support:**
   - Email: `bwidm-support@kit.edu`
   - Subject: "OIDC Client Registration Request - ASSAS Data Hub"

2. **Provide Application Details:**
   ```
   Application Name: ASSAS Data Hub
   Description: Research data management platform for atmospheric science
   Organization: Your Institution/Department
   Contact Person: Your Name <your.email@institution.edu>
   
   Technical Details:
   - Redirect URIs: https://yourdomain.com/auth/callback/bwidm
   - Application Type: Web Application
   - Grant Types: authorization_code
   - Response Types: code
   - Scopes: openid profile email eduperson_entitlement
   - Token Endpoint Auth Method: client_secret_post
   ```

#### Production Registration

1. **Formal Application Process:**
   - Submit through official bwIDM registration portal
   - Provide institutional backing/approval
   - Security review process
   - Data protection compliance

2. **Required Documentation:**
   - Application architecture diagram
   - Data processing description
   - Privacy policy
   - Terms of service
   - Security measures documentation

### Step 2: bwIDM Client Credentials

After approval, you'll receive:

```json
{
  "client_id": "your-bwidm-client-id",
  "client_secret": "your-bwidm-client-secret",
  "issuer": "https://login.bwidm.de/auth/realms/bw",
  "authorization_endpoint": "https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/auth",
  "token_endpoint": "https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/token",
  "userinfo_endpoint": "https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/userinfo",
  "jwks_uri": "https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/certs",
  "end_session_endpoint": "https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/logout"
}
```

### Step 3: Environment Configuration

```bash
# bwIDM Configuration
BWIDM_CLIENT_ID=your_bwidm_client_id
BWIDM_CLIENT_SECRET=your_bwidm_client_secret
BWIDM_DISCOVERY_URL=https://login.bwidm.de/auth/realms/bw/.well-known/openid_configuration

# Flask Configuration
SECRET_KEY=your-production-secret-key-very-long-and-random
FLASK_ENV=production
```

## OpenID Connect Flow Explanation

bwIDM uses OpenID Connect (OIDC), which is OAuth 2.0 + identity layer. It provides both authentication (who the user is) and authorization (what they can access).

### Complete OIDC Flow Diagram

```
User Browser    Your App         bwIDM           Home Institution
     |             |               |                     |
     |------------>|               |                     |  1. User clicks "Login with bwIDM"
     |             |               |                     |
     |             |-------------->|                     |  2. Redirect to bwIDM authorization
     |<---------------------------|                     |     URL with client_id, state, nonce
     |             |               |                     |
     |             |               |-------------------->|  3. bwIDM redirects to user's institution
     |<-------------------------------------------------|     (KIT, Uni Stuttgart, etc.)
     |             |               |                     |
     |  [User logs in at home institution]                |
     |             |               |                     |
     |------------>|<--------------|<--------------------|  4. Institution redirects back via bwIDM
     |             |               |                     |     with authorization code
     |             |               |                     |
     |             |-------------->|                     |  5. Exchange code for tokens
     |             |<--------------|                     |     (access_token + id_token)
     |             |               |                     |
     |             |-------------->|                     |  6. Get additional user info
     |             |<--------------|                     |
     |             |               |                     |
     |<------------|               |                     |  7. Create session & redirect to app
```

### Step-by-Step Process

#### Step 1: Authorization Request

**User Action:** Clicks "Sign in with bwIDM"  
**Your App:** `/auth/login/bwidm`

```python
# Generate CSRF protection state and OIDC nonce
state = secrets.token_urlsafe(32)
nonce = secrets.token_urlsafe(32)
session['oauth_state_bwidm'] = state
session['oidc_nonce_bwidm'] = nonce

# Create bwIDM authorization URL
authorization_url = "https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/auth?" + urlencode({
    'client_id': 'your_bwidm_client_id',
    'redirect_uri': 'https://yourdomain.com/auth/callback/bwidm',
    'scope': 'openid profile email eduperson_entitlement',
    'response_type': 'code',
    'state': state,
    'nonce': nonce,
    'prompt': 'login'  # Force fresh authentication
})
```

#### Step 2: Institution Selection and Authentication

**What the user sees:**
1. **bwIDM Institution Selection:**
   ```
   Please select your home institution:
   
   [🏛️] Karlsruhe Institute of Technology (KIT)
   [🏛️] University of Stuttgart  
   [🏛️] University of Freiburg
   [🏛️] University of Heidelberg
   [🏛️] University of Mannheim
   [...] More institutions
   
   [Continue]
   ```

2. **Home Institution Login:**
   - User is redirected to their institution's login page
   - Enters institutional credentials (e.g., KIT account)
   - May require 2FA/MFA depending on institution policy

3. **Consent Screen (if required):**
   ```
   ASSAS Data Hub requests access to:
   ✓ Your basic profile information
   ✓ Your email address
   ✓ Your institutional affiliations
   
   [Allow] [Deny]
   ```

#### Step 3: Authorization Response

**If approved**, bwIDM redirects to:
```
https://yourdomain.com/auth/callback/bwidm?
    code=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...&
    state=HN-jWMzV1S_j7oAGZ-hJJ46KyjT_mYoE_LLEIJGlnr4&
    session_state=abc123-def456-789xyz
```

**If denied or error:**
```
https://yourdomain.com/auth/callback/bwidm?
    error=access_denied&
    error_description=User denied access&
    state=HN-jWMzV1S_j7oAGZ-hJJ46KyjT_mYoE_LLEIJGlnr4
```

#### Step 4: Token Exchange

**Your app's server-to-server request:**

```python
token_data = {
    'grant_type': 'authorization_code',
    'client_id': 'your_bwidm_client_id',
    'client_secret': 'your_bwidm_client_secret',
    'code': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'redirect_uri': 'https://yourdomain.com/auth/callback/bwidm',
}

response = requests.post(
    'https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/token',
    data=token_data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
```

**bwIDM's token response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGSjg2R2NGM2pTYk5US2N5WkNCZGhQSGtudy1RSVRzdHQ1NTJfRmVjM0JnIn0...",
  "expires_in": 3600,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGSjg2R2NGM2pTYk5US2N5WkNCZGhQSGtudy1RSVRzdHQ1NTJfRmVjM0JnIn0...",
  "token_type": "Bearer",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGSjg2R2NGM2pTYk5US2N5WkNCZGhQSGtudy1RSVRzdHQ1NTJfRmVjM0JnIn0...",
  "not-before-policy": 0,
  "session_state": "abc123-def456-789xyz",
  "scope": "openid profile email eduperson_entitlement"
}
```

#### Step 5: Decode and Validate ID Token

The `id_token` is a JWT containing user identity information:

```python
import jwt
from cryptography.hazmat.primitives import serialization

# Get public keys for token verification
jwks_response = requests.get('https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/certs')
jwks = jwks_response.json()

# Decode and verify ID token
id_token_payload = jwt.decode(
    id_token,
    options={"verify_signature": True, "verify_aud": True, "verify_iss": True},
    audience=client_id,
    issuer="https://login.bwidm.de/auth/realms/bw",
    algorithms=["RS256"]
)
```

**Decoded ID Token payload:**
```json
{
  "exp": 1673456789,
  "iat": 1673453189,
  "auth_time": 1673453189,
  "jti": "abc123-def456-789xyz",
  "iss": "https://login.bwidm.de/auth/realms/bw",
  "aud": "your_bwidm_client_id",
  "sub": "f:12345678-abcd-1234-efgh-123456789abc:john.doe@kit.edu",
  "typ": "ID",
  "azp": "your_bwidm_client_id",
  "nonce": "HN-jWMzV1S_j7oAGZ-hJJ46KyjT_mYoE_LLEIJGlnr4",
  "session_state": "abc123-def456-789xyz",
  "given_name": "John",
  "family_name": "Doe",
  "preferred_username": "john.doe@kit.edu",
  "name": "John Doe",
  "email": "john.doe@kit.edu",
  "email_verified": true,
  "eduperson_entitlement": [
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:admin",
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:researchers",
    "urn:mace:dir:entitlement:common-lib-terms"
  ]
}
```

#### Step 6: Get Additional User Information

```python
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

userinfo_response = requests.get(
    'https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/userinfo',
    headers=headers
)
```

**UserInfo response:**
```json
{
  "sub": "f:12345678-abcd-1234-efgh-123456789abc:john.doe@kit.edu",
  "name": "John Doe",
  "given_name": "John",
  "family_name": "Doe",
  "preferred_username": "john.doe@kit.edu",
  "email": "john.doe@kit.edu",
  "email_verified": true,
  "eduperson_entitlement": [
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:admin",
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:researchers"
  ],
  "eduperson_scoped_affiliation": [
    "employee@kit.edu",
    "member@kit.edu"
  ],
  "schac_home_organization": "kit.edu",
  "eduperson_principal_name": "john.doe@kit.edu"
}
```

## AARC Entitlements and Role Mapping

### Understanding AARC Entitlements

AARC (Authentication and Authorisation for Research and Collaboration) defines a standard for group memberships and entitlements in research infrastructures.

#### Entitlement Format

```
urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:admin
└─┬─┘ └──┬──┘ └────┬────┘ └─┬─┘ └─┬─┘ └──────┬──────┘ └─┬─┘
  │      │         │        │     │           │          │
scheme namespace authority group service   resource    role
```

**Components:**
- **scheme**: Always `urn`
- **namespace**: `geant` for GÉANT services
- **authority**: `helmholtz.de` for Helmholtz Association
- **group**: `HIFIS` for Helmholtz Federated IT Services
- **service**: `ASSAS-Data-Hub` for your specific application
- **resource**: Optional sub-resource
- **role**: `admin`, `writer`, `reader`, `viewer`

#### Example Entitlements

```python
EXAMPLE_ENTITLEMENTS = [
    # Administrative access
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:admin",
    
    # Data management roles
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:data-manager",
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:researcher",
    
    # Institution-specific groups
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:KIT:local-admin",
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:UniStuttgart:researcher",
    
    # Project-specific access
    "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:Project-ATMO:member",
    
    # Generic academic entitlements
    "urn:mace:dir:entitlement:common-lib-terms"
]
```

### Role Mapping Implementation

```python
class BWIDMRoleProcessor:
    """Process bwIDM user data and AARC entitlements."""
    
    ASSAS_GROUP_PREFIX = "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub"
    
    @staticmethod
    def parse_entitlements(entitlements: List[str]) -> Dict[str, List[str]]:
        """Parse AARC entitlements into structured format."""
        parsed = {
            'assas_roles': [],
            'institutions': [],
            'projects': [],
            'other_entitlements': []
        }
        
        for entitlement in entitlements:
            if entitlement.startswith(BWIDMRoleProcessor.ASSAS_GROUP_PREFIX):
                # Parse ASSAS-specific entitlement
                parts = entitlement.replace(BWIDMRoleProcessor.ASSAS_GROUP_PREFIX + ":", "").split(":")
                
                if len(parts) == 1:
                    # Direct role: urn:...:ASSAS-Data-Hub:admin
                    parsed['assas_roles'].append(parts[0])
                elif len(parts) == 2:
                    # Institution role: urn:...:ASSAS-Data-Hub:KIT:admin
                    institution, role = parts
                    parsed['institutions'].append({
                        'institution': institution,
                        'role': role
                    })
                elif len(parts) >= 3:
                    # Project role: urn:...:ASSAS-Data-Hub:Project-ATMO:member
                    if parts[0].startswith('Project-'):
                        parsed['projects'].append({
                            'project': parts[0],
                            'role': ':'.join(parts[1:])
                        })
            else:
                parsed['other_entitlements'].append(entitlement)
        
        return parsed
    
    @staticmethod
    def get_user_roles(entitlements: List[str], user_info: Dict) -> List[str]:
        """Extract user roles from AARC entitlements."""
        parsed = BWIDMRoleProcessor.parse_entitlements(entitlements)
        roles = set()
        
        # Direct ASSAS roles
        for role in parsed['assas_roles']:
            if role in ['admin', 'writer', 'reader', 'viewer']:
                roles.add(role)
        
        # Institution-based roles
        for inst in parsed['institutions']:
            if inst['role'] in ['admin', 'writer', 'reader', 'viewer']:
                roles.add(inst['role'])
        
        # Fallback: determine role from institution
        email = user_info.get('email', '')
        if '@kit.edu' in email or '@uni-stuttgart.de' in email:
            roles.add('researcher')
        
        # Default role if none found
        if not roles:
            roles.add('viewer')
        
        return list(roles)
    
    @staticmethod
    def get_highest_role(roles: List[str]) -> str:
        """Get the highest privilege role."""
        role_hierarchy = ['admin', 'writer', 'reader', 'viewer']
        
        for role in role_hierarchy:
            if role in roles:
                return role
        
        return 'viewer'
```

## Security Features

### 1. ID Token Validation

```python
def validate_id_token(id_token: str, nonce: str, client_id: str) -> Dict:
    """Validate and decode OIDC ID token."""
    
    # Get public keys from bwIDM
    jwks_response = requests.get(
        'https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/certs'
    )
    jwks = jwks_response.json()
    
    # Verify token signature and claims
    try:
        payload = jwt.decode(
            id_token,
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True
            },
            audience=client_id,
            issuer="https://login.bwidm.de/auth/realms/bw",
            algorithms=["RS256"],
            jwks_client=PyJWKClient("https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/certs")
        )
        
        # Verify nonce to prevent replay attacks
        if payload.get('nonce') != nonce:
            raise ValueError("Nonce mismatch")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise ValueError("ID token has expired")
    except jwt.InvalidAudienceError:
        raise ValueError("Invalid audience")
    except jwt.InvalidIssuerError:
        raise ValueError("Invalid issuer")
    except jwt.InvalidSignatureError:
        raise ValueError("Invalid signature")
```

### 2. Session Security

```python
def create_bwidm_session(user_info: Dict, id_token_payload: Dict) -> None:
    """Create secure session for bwIDM user."""
    
    entitlements = user_info.get('eduperson_entitlement', [])
    roles = BWIDMRoleProcessor.get_user_roles(entitlements, user_info)
    
    session.permanent = True
    session['user'] = {
        'id': id_token_payload.get('sub'),
        'username': user_info.get('preferred_username'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'given_name': user_info.get('given_name'),
        'family_name': user_info.get('family_name'),
        'provider': 'bwidm',
        'authenticated': True,
        'roles': roles,
        'highest_role': BWIDMRoleProcessor.get_highest_role(roles),
        'institution': user_info.get('schac_home_organization'),
        'entitlements': entitlements,
        'affiliations': user_info.get('eduperson_scoped_affiliation', []),
        'auth_time': id_token_payload.get('auth_time'),
        'session_id': id_token_payload.get('session_state'),
    }
```

### 3. Token Management

```python
class TokenManager:
    """Manage OIDC tokens securely."""
    
    @staticmethod
    def store_tokens(access_token: str, refresh_token: str, expires_in: int) -> None:
        """Store tokens securely in session."""
        session['tokens'] = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': time.time() + expires_in,
            'token_type': 'Bearer'
        }
    
    @staticmethod
    def get_valid_access_token() -> Optional[str]:
        """Get valid access token, refresh if needed."""
        tokens = session.get('tokens', {})
        
        if not tokens:
            return None
        
        # Check if token is expired
        if time.time() >= tokens.get('expires_at', 0):
            # Try to refresh token
            if tokens.get('refresh_token'):
                return TokenManager.refresh_access_token()
            else:
                return None
        
        return tokens.get('access_token')
    
    @staticmethod
    def refresh_access_token() -> Optional[str]:
        """Refresh access token using refresh token."""
        tokens = session.get('tokens', {})
        refresh_token = tokens.get('refresh_token')
        
        if not refresh_token:
            return None
        
        try:
            response = requests.post(
                'https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/token',
                data={
                    'grant_type': 'refresh_token',
                    'client_id': current_app.config['BWIDM_CLIENT_ID'],
                    'client_secret': current_app.config['BWIDM_CLIENT_SECRET'],
                    'refresh_token': refresh_token
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                TokenManager.store_tokens(
                    token_data['access_token'],
                    token_data.get('refresh_token', refresh_token),
                    token_data['expires_in']
                )
                return token_data['access_token']
        
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
        
        return None
```

## Code Implementation Details

### Complete bwIDM Integration

```python
# oauth_auth.py - bwIDM specific implementation

def init_oauth(app):
    """Initialize OAuth with bwIDM provider."""
    oauth.init_app(app)
    
    # Register bwIDM provider
    if app.config.get('BWIDM_CLIENT_ID'):
        oauth.register(
            name='bwidm',
            client_id=app.config['BWIDM_CLIENT_ID'],
            client_secret=app.config['BWIDM_CLIENT_SECRET'],
            server_metadata_url=app.config['BWIDM_DISCOVERY_URL'],
            client_kwargs={
                'scope': 'openid profile email eduperson_entitlement',
                'response_type': 'code',
                'prompt': 'login'  # Force fresh authentication
            }
        )

@oauth_bp.route('/login/bwidm')
def login_bwidm():
    """Initiate bwIDM OIDC login flow."""
    
    if not current_app.config.get('BWIDM_CLIENT_ID'):
        flash('bwIDM authentication is not configured', 'error')
        return redirect(url_for('auth.login_page'))
    
    try:
        # Generate state and nonce
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        
        session['oauth_state_bwidm'] = state
        session['oidc_nonce_bwidm'] = nonce
        session.modified = True
        
        # Create authorization URL
        redirect_uri = url_for('oauth.callback', provider='bwidm', _external=True)
        
        auth_url = (
            f"https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/auth?"
            f"client_id={current_app.config['BWIDM_CLIENT_ID']}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=openid profile email eduperson_entitlement&"
            f"response_type=code&"
            f"state={state}&"
            f"nonce={nonce}&"
            f"prompt=login"
        )
        
        logger.info(f"Redirecting to bwIDM: {auth_url}")
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"bwIDM login error: {e}")
        flash(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('auth.login_page'))

def exchange_bwidm_code_for_tokens(code: str, redirect_uri: str) -> Dict:
    """Exchange authorization code for OIDC tokens."""
    
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': current_app.config['BWIDM_CLIENT_ID'],
        'client_secret': current_app.config['BWIDM_CLIENT_SECRET'],
        'code': code,
        'redirect_uri': redirect_uri,
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    logger.info("Exchanging authorization code for tokens...")
    
    response = requests.post(
        'https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/token',
        data=token_data,
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
        raise Exception(f"Token exchange failed: {response.status_code}")
    
    tokens = response.json()
    
    if 'error' in tokens:
        logger.error(f"bwIDM token error: {tokens}")
        raise Exception(f"Token error: {tokens.get('error_description', tokens.get('error'))}")
    
    logger.info("Tokens received successfully")
    return tokens

def get_bwidm_user_info(access_token: str, id_token: str, nonce: str) -> Dict:
    """Get and validate bwIDM user information."""
    
    # Validate ID token
    id_token_payload = validate_id_token(
        id_token, 
        nonce, 
        current_app.config['BWIDM_CLIENT_ID']
    )
    
    # Get additional user info from UserInfo endpoint
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    userinfo_response = requests.get(
        'https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/userinfo',
        headers=headers,
        timeout=30
    )
    
    if userinfo_response.status_code != 200:
        logger.warning(f"UserInfo request failed: {userinfo_response.status_code}")
        # Use ID token claims if UserInfo fails
        return id_token_payload
    
    userinfo = userinfo_response.json()
    
    # Merge ID token and UserInfo claims
    user_info = {**id_token_payload, **userinfo}
    
    logger.info(f"bwIDM user info for: {user_info.get('preferred_username')}")
    return user_info

@oauth_bp.route('/callback/bwidm')
def callback_bwidm():
    """Handle bwIDM OIDC callback."""
    
    try:
        # Check for errors
        error = request.args.get('error')
        if error:
            error_description = request.args.get('error_description', 'Unknown error')
            logger.error(f"bwIDM authorization error: {error} - {error_description}")
            flash(f'Authentication failed: {error_description}', 'error')
            return redirect(url_for('auth.login_page'))
        
        # Verify state
        received_state = request.args.get('state')
        stored_state = session.pop('oauth_state_bwidm', None)
        nonce = session.pop('oidc_nonce_bwidm', None)
        
        if not received_state or received_state != stored_state:
            logger.error("State parameter mismatch")
            flash('Security error: Invalid state parameter', 'error')
            return redirect(url_for('auth.login_page'))
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            logger.error("No authorization code received")
            flash('Authentication failed: No authorization code', 'error')
            return redirect(url_for('auth.login_page'))
        
        # Exchange code for tokens
        redirect_uri = url_for('oauth.callback', provider='bwidm', _external=True)
        tokens = exchange_bwidm_code_for_tokens(code, redirect_uri)
        
        # Get and validate user info
        user_info = get_bwidm_user_info(
            tokens['access_token'],
            tokens['id_token'],
            nonce
        )
        
        # Store tokens
        TokenManager.store_tokens(
            tokens['access_token'],
            tokens.get('refresh_token'),
            tokens['expires_in']
        )
        
        # Create user session
        create_bwidm_session(user_info, user_info)  # ID token payload included in user_info
        
        flash('Successfully logged in via bwIDM!', 'success')
        
        # Redirect to intended page
        next_page = session.pop('next_url', None)
        return redirect(next_page or '/assas_app/home')
        
    except Exception as e:
        logger.error(f"bwIDM callback error: {e}")
        flash(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('auth.login_page'))
```

## Testing and Debugging

### 1. Development Testing

```python
# test_bwidm.py
def test_bwidm_configuration():
    """Test bwIDM configuration and discovery."""
    
    discovery_url = "https://login.bwidm.de/auth/realms/bw/.well-known/openid_configuration"
    
    try:
        response = requests.get(discovery_url)
        config = response.json()
        
        print("✓ bwIDM Discovery endpoint accessible")
        print(f"  Issuer: {config['issuer']}")
        print(f"  Authorization endpoint: {config['authorization_endpoint']}")
        print(f"  Token endpoint: {config['token_endpoint']}")
        print(f"  UserInfo endpoint: {config['userinfo_endpoint']}")
        print(f"  Supported scopes: {config.get('scopes_supported', [])}")
        
    except Exception as e:
        print(f"✗ bwIDM Discovery failed: {e}")

def test_entitlement_parsing():
    """Test AARC entitlement parsing."""
    
    test_entitlements = [
        "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:admin",
        "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:KIT:researcher",
        "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:Project-ATMO:member",
        "urn:mace:dir:entitlement:common-lib-terms"
    ]
    
    parsed = BWIDMRoleProcessor.parse_entitlements(test_entitlements)
    roles = BWIDMRoleProcessor.get_user_roles(test_entitlements, {})
    
    print("Parsed entitlements:")
    print(f"  ASSAS roles: {parsed['assas_roles']}")
    print(f"  Institutions: {parsed['institutions']}")
    print(f"  Projects: {parsed['projects']}")
    print(f"  Derived roles: {roles}")
```

### 2. Debug Endpoints

```python
@oauth_bp.route('/debug/bwidm-config')
def debug_bwidm_config():
    """Debug bwIDM configuration."""
    
    if not current_app.debug:
        return jsonify({'error': 'Debug mode disabled'}), 403
    
    try:
        discovery_response = requests.get(
            current_app.config.get('BWIDM_DISCOVERY_URL', ''),
            timeout=10
        )
        discovery_config = discovery_response.json() if discovery_response.status_code == 200 else None
        
    except Exception as e:
        discovery_config = {'error': str(e)}
    
    return jsonify({
        'bwidm_configured': bool(current_app.config.get('BWIDM_CLIENT_ID')),
        'discovery_url': current_app.config.get('BWIDM_DISCOVERY_URL'),
        'discovery_config': discovery_config,
        'client_id_set': bool(current_app.config.get('BWIDM_CLIENT_ID')),
        'client_secret_set': bool(current_app.config.get('BWIDM_CLIENT_SECRET')),
    })

@oauth_bp.route('/debug/parse-entitlements')
def debug_parse_entitlements():
    """Debug entitlement parsing."""
    
    if not current_app.debug:
        return jsonify({'error': 'Debug mode disabled'}), 403
    
    # Get entitlements from query parameter or use examples
    entitlements_param = request.args.get('entitlements')
    if entitlements_param:
        entitlements = entitlements_param.split(',')
    else:
        entitlements = [
            "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:admin",
            "urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub:KIT:researcher"
        ]
    
    parsed = BWIDMRoleProcessor.parse_entitlements(entitlements)
    roles = BWIDMRoleProcessor.get_user_roles(entitlements, {})
    
    return jsonify({
        'input_entitlements': entitlements,
        'parsed_entitlements': parsed,
        'derived_roles': roles,
        'highest_role': BWIDMRoleProcessor.get_highest_role(roles)
    })
```

## Production Deployment

### 1. Security Configuration

```python
# config.py - Production settings
class ProductionConfig(Config):
    # bwIDM Production Configuration
    BWIDM_CLIENT_ID = os.environ.get('BWIDM_CLIENT_ID')
    BWIDM_CLIENT_SECRET = os.environ.get('BWIDM_CLIENT_SECRET')
    BWIDM_DISCOVERY_URL = 'https://login.bwidm.de/auth/realms/bw/.well-known/openid_configuration'
    
    # Security Settings
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # AARC Entitlements
    AARC_GROUP_CLAIM = 'eduperson_entitlement'
    ASSAS_GROUP_PREFIX = 'urn:geant:helmholtz.de:group:HIFIS:ASSAS-Data-Hub'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/assas-data-hub/app.log'
```

### 2. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PyJWT with cryptography support
RUN pip install PyJWT[crypto] cryptography

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run as non-root user
RUN useradd -m -s /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
```

### 3. Environment Variables

```bash
# .env.production
BWIDM_CLIENT_ID=your_production_client_id
BWIDM_CLIENT_SECRET=your_production_client_secret
SECRET_KEY=your_very_long_production_secret_key
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://user:pass@db:5432/assas_data_hub

# Redis for sessions
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/assas/app.log
```

## Troubleshooting

### Common Issues

#### 1. "Invalid issuer" Error

**Problem:** ID token issuer doesn't match expected value

**Solution:**
```python
# Check discovery configuration
discovery_url = "https://login.bwidm.de/auth/realms/bw/.well-known/openid_configuration"
response = requests.get(discovery_url)
config = response.json()
print(f"Expected issuer: {config['issuer']}")
```

#### 2. "No entitlements found" Warning

**Problem:** User has no ASSAS-specific entitlements

**Possible causes:**
- User not added to ASSAS groups in bwIDM
- Incorrect entitlement format
- Missing scope in request

**Solution:**
```python
# Check user's raw entitlements
print(f"Raw entitlements: {user_info.get('eduperson_entitlement', [])}")

# Verify scope includes entitlements
scope = "openid profile email eduperson_entitlement"
```

#### 3. "Token validation failed" Error

**Problem:** JWT signature verification fails

**Solution:**
```python
# Update JWKS cache
jwks_client = PyJWKClient(
    "https://login.bwidm.de/auth/realms/bw/protocol/openid-connect/certs",
    cache_ttl=3600
)

# Check token header
header = jwt.get_unverified_header(id_token)
print(f"Token algorithm: {header['alg']}")
print(f"Key ID: {header['kid']}")
```

#### 4. "Session expired" Errors

**Problem:** Tokens expire during user session

**Solution:**
```python
# Implement automatic token refresh
def ensure_valid_token():
    if TokenManager.get_valid_access_token() is None:
        # Redirect to re-authentication
        return redirect(url_for('oauth.login', provider='bwidm'))
```

### Debug Checklist

- [ ] bwIDM client registered and approved
- [ ] Client ID and secret configured correctly
- [ ] Discovery URL accessible
- [ ] HTTPS enabled in production
- [ ] Callback URL matches registration
- [ ] Required scopes included in request
- [ ] JWT validation libraries installed
- [ ] Clock synchronization between servers
- [ ] Network connectivity to bwIDM
- [ ] Entitlement format matches AARC standard

### Performance Considerations

1. **Token Caching:**
   ```python
   # Cache decoded tokens to avoid repeated validation
   @lru_cache(maxsize=100)
   def get_decoded_token(token_hash):
       return jwt.decode(token, ...)
   ```

2. **JWKS Caching:**
   ```python
   # Cache public keys to reduce network requests
   jwks_client = PyJWKClient(jwks_uri, cache_ttl=3600)
   ```

3. **Session Storage:**
   ```python
   # Use Redis for session storage in production
   app.config['SESSION_TYPE'] = 'redis'
   app.config['SESSION_REDIS'] = Redis(host='redis', port=6379)
   ```

This bwIDM integration provides enterprise-grade authentication with institutional identity federation, role-based access control through AARC entitlements, and seamless integration