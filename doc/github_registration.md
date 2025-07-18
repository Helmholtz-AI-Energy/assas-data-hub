# GitHub OAuth Registration and Setup Guide

This guide explains how to register your application with GitHub OAuth, understand the OAuth 2.0 flow, and integrate it with the ASSAS Data Hub.

## Table of Contents

1. [GitHub OAuth App Registration](#github-oauth-app-registration)
2. [OAuth 2.0 Flow Explanation](#oauth-20-flow-explanation)
3. [Security Features](#security-features)
4. [Code Implementation Details](#code-implementation-details)
5. [Testing and Debugging](#testing-and-debugging)
6. [Troubleshooting](#troubleshooting)

## GitHub OAuth App Registration

### Step 1: Create a GitHub OAuth Application

1. **Navigate to GitHub Settings:**
   - Go to [GitHub](https://github.com)
   - Click on your profile picture → Settings
   - In the left sidebar, click "Developer settings"
   - Click "OAuth Apps"

2. **Register New Application:**
   - Click "New OAuth App"
   - Fill in the application details:

   ```
   Application name: ASSAS Data Hub (Development)
   Homepage URL: http://localhost:5000
   Application description: ASSAS Data Hub development authentication for research data management
   Authorization callback URL: http://localhost:5000/auth/callback/github
   ```

3. **Get Your Credentials:**
   - After registration, note down:
     - **Client ID**: `abc123def456...` (public)
     - **Client Secret**: `secret789xyz...` (keep private!)

### Step 2: Environment Configuration

Create a `.env` file in your project root:

```bash
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here

# Flask Configuration
SECRET_KEY=your-very-long-random-secret-key-for-session-security-at-least-32-characters
FLASK_ENV=development
FLASK_DEBUG=True
```

### Step 3: Production vs Development URLs

**Development:**
```
Homepage URL: http://localhost:5000
Callback URL: http://localhost:5000/auth/callback/github
```

**Production:**
```
Homepage URL: https://yourdomain.com
Callback URL: https://yourdomain.com/auth/callback/github
```

## OAuth 2.0 Flow Explanation

OAuth 2.0 uses the "Authorization Code Grant" flow - a secure method where your application never sees the user's password.

### Complete Flow Diagram

```
User Browser    Your App         GitHub
     |             |               |
     |------------>|               |  1. User clicks "Login with GitHub"
     |             |               |
     |             |-------------->|  2. Redirect to GitHub authorization
     |<---------------------------|     URL with client_id, state, scope
     |             |               |
     |  [User logs in & authorizes] |
     |             |               |
     |------------>|<--------------|  3. GitHub redirects back with code
     |             |               |
     |             |-------------->|  4. Exchange code for access token
     |             |<--------------|     (server-to-server with secret)
     |             |               |
     |             |-------------->|  5. Use token to get user info
     |             |<--------------|
     |             |               |
     |<------------|               |  6. Create session & redirect to app
```

### Step-by-Step Process

#### Step 1: Authorization Request

**User Action:** Clicks "Sign in with GitHub"  
**Your App:** `/auth/login/github`

```python
# Generate CSRF protection state
state = secrets.token_urlsafe(32)  # "HN-jWMzV1S_j7oAGZ-hJJ46KyjT_mYoE_LLEIJGlnr4"
session['oauth_state_github'] = state

# Create GitHub authorization URL
authorization_url = "https://github.com/login/oauth/authorize?" + urlencode({
    'client_id': 'your_github_client_id',
    'redirect_uri': 'http://localhost:5000/auth/callback/github',
    'scope': 'user:email read:user',
    'state': state,
    'response_type': 'code'
})
```

#### Step 2: User Authorization

**What the user sees on GitHub:**
```
ASSAS Data Hub would like to:
✓ Read your public profile information
✓ Read your email addresses

[Authorize ASSAS Data Hub] [Cancel]
```

#### Step 3: Authorization Response

**If approved**, GitHub redirects to:
```
http://localhost:5000/auth/callback/github?
    code=38eb38c8e4c2f53c7a8a&
    state=HN-jWMzV1S_j7oAGZ-hJJ46KyjT_mYoE_LLEIJGlnr4
```

**If denied**, GitHub redirects to:
```
http://localhost:5000/auth/callback/github?
    error=access_denied&
    error_description=The user has denied your application access&
    state=HN-jWMzV1S_j7oAGZ-hJJ46KyjT_mYoE_LLEIJGlnr4
```

#### Step 4: Token Exchange

**Your app's server-to-server request:**

```python
token_data = {
    'client_id': 'your_github_client_id',
    'client_secret': 'your_github_client_secret',  # Secret stays on server!
    'code': '38eb38c8e4c2f53c7a8a',  # From step 3
    'redirect_uri': 'http://localhost:5000/auth/callback/github',
}

response = requests.post(
    'https://github.com/login/oauth/access_token',
    data=token_data,
    headers={'Accept': 'application/json'}
)
```

**GitHub's response:**
```json
{
  "access_token": "gho_16C7e42F292c6912E7710c838347Ae178B4a",
  "scope": "user:email,read:user",
  "token_type": "bearer"
}
```

#### Step 5: Get User Information

**API requests with access token:**

```python
headers = {
    'Authorization': 'token gho_16C7e42F292c6912E7710c838347Ae178B4a',
    'Accept': 'application/vnd.github.v3+json',
}

# Get user profile
user_response = requests.get('https://api.github.com/user', headers=headers)
```

**GitHub user data:**
```json
{
  "login": "username",
  "id": 12345678,
  "name": "John Doe",
  "email": "john@example.com",
  "avatar_url": "https://avatars.githubusercontent.com/u/12345678?v=4",
  "html_url": "https://github.com/username",
  "bio": "Software developer",
  "company": "ACME Corp",
  "location": "Berlin, Germany",
  "public_repos": 25,
  "followers": 100,
  "following": 50
}
```

**If email is private, get it separately:**
```python
# GET https://api.github.com/user/emails
emails_response = requests.get('https://api.github.com/user/emails', headers=headers)
```

**Email response:**
```json
[
  {
    "email": "john@example.com",
    "primary": true,
    "verified": true,
    "visibility": "private"
  },
  {
    "email": "john.doe@company.com",
    "primary": false,
    "verified": true,
    "visibility": "public"
  }
]
```

#### Step 6: Create User Session

```python
session['user'] = {
    'id': '12345678',
    'username': 'username',
    'email': 'john@example.com',
    'name': 'John Doe',
    'provider': 'github',
    'authenticated': True,
    'roles': ['viewer'],  # Based on your role mapping
    'avatar_url': 'https://avatars.githubusercontent.com/u/12345678?v=4',
    'github_profile': 'https://github.com/username',
}
```

## Security Features

### 1. State Parameter (CSRF Protection)

**Purpose:** Prevents Cross-Site Request Forgery attacks

```python
# Generate random state for each request
state = secrets.token_urlsafe(32)
session['oauth_state_github'] = state

# Verify state matches when GitHub redirects back
received_state = request.args.get('state')
stored_state = session.pop('oauth_state_github')

if received_state != stored_state:
    # Potential CSRF attack - reject the request
    raise SecurityError("State parameter mismatch")
```

### 2. Authorization Code vs Access Token

| Aspect | Authorization Code | Access Token |
|--------|-------------------|--------------|
| **Lifetime** | ~10 minutes | Hours/days |
| **Usage** | One-time only | Multiple requests |
| **Exposure** | Via browser (URL) | Server-only |
| **Purpose** | Prove user consent | Access APIs |

### 3. Client Secret Protection

**❌ Never expose client secret in:**
- Frontend JavaScript
- Mobile apps
- Public repositories
- Client-side code

**✅ Only use client secret in:**
- Server-to-server requests
- Environment variables
- Secure server configuration

### 4. Scope Limitation

**Requested scopes:**
```python
'scope': 'user:email read:user'
```

**What this allows:**
- ✅ Read public profile
- ✅ Read email addresses
- ❌ Write to repositories
- ❌ Delete data
- ❌ Access private repositories

## Code Implementation Details

### Role Assignment Logic

```python
class GitHubRoleProcessor:
    @staticmethod
    def get_user_role(username: str, email: str) -> str:
        role_mappings = current_app.config.get('GITHUB_ROLE_MAPPINGS', {})
        
        # Check specific username
        if username in role_mappings:
            return role_mappings[username]
        
        # Check email domain (example)
        if email and email.endswith('@your-organization.com'):
            return 'admin'
        
        # Default role
        return role_mappings.get('*', 'viewer')
```

**Configuration example:**
```python
GITHUB_ROLE_MAPPINGS = {
    'your-github-username': 'admin',
    'researcher1': 'writer',
    'student-user': 'reader',
    '*': 'viewer'  # Default for all others
}
```

### Session Management

```python
def create_user_session(user_info: Dict, provider: str) -> None:
    session.permanent = True  # Use permanent session
    
    session['user'] = {
        'id': str(user_info.get('id')),
        'username': user_info.get('login'),
        'email': user_info.get('email'),
        'name': user_info.get('name') or user_info.get('login'),
        'provider': provider,
        'authenticated': True,
        'roles': [GitHubRoleProcessor.get_user_role(username, email)],
        'avatar_url': user_info.get('avatar_url'),
        'github_profile': user_info.get('html_url'),
        'login_time': datetime.utcnow().isoformat(),
    }
```

### Error Handling

```python
@oauth_bp.route('/callback/<provider>')
def callback(provider: str):
    try:
        # Check for OAuth errors
        error = request.args.get('error')
        if error == 'access_denied':
            flash('Authorization was cancelled by user', 'info')
            return redirect(url_for('auth.login_page'))
        elif error:
            flash(f'OAuth error: {error}', 'error')
            return redirect(url_for('auth.login_page'))
        
        # Verify state parameter
        received_state = request.args.get('state')
        stored_state = session.pop(f'oauth_state_{provider}', None)
        
        if not received_state or received_state != stored_state:
            flash('Security error: Invalid state parameter', 'error')
            return redirect(url_for('auth.login_page'))
        
        # ... continue with token exchange
        
    except requests.exceptions.Timeout:
        flash('GitHub is not responding. Please try again.', 'error')
        return redirect(url_for('auth.login_page'))
    except requests.exceptions.ConnectionError:
        flash('Network error. Please check your connection.', 'error')
        return redirect(url_for('auth.login_page'))
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login_page'))
```

## Testing and Debugging

### 1. Test OAuth Endpoints

```python
# test_oauth.py
import requests

def test_oauth_flow():
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Test login page
    response = session.get(f"{base_url}/auth/login")
    assert response.status_code == 200
    
    # Test GitHub redirect
    response = session.get(f"{base_url}/auth/login/github", allow_redirects=False)
    assert response.status_code == 302
    assert 'github.com' in response.headers['Location']
    
    # Test debug endpoint
    response = session.get(f"{base_url}/auth/debug/session")
    if response.status_code == 200:
        data = response.json()
        print(f"GitHub configured: {data['config']['github_configured']}")
```

### 2. Debug Session Data

Visit `/auth/debug/session` to see:
```json
{
  "session_keys": ["user", "_flashes"],
  "user_authenticated": true,
  "user_data": {
    "id": "12345678",
    "username": "your-username",
    "email": "your-email@example.com",
    "roles": ["admin"]
  },
  "config": {
    "github_configured": true,
    "secret_key_set": true
  }
}
```

### 3. Manual Testing Steps

1. **Start your application:**
   ```bash
   python run.py
   ```

2. **Navigate to login:**
   ```
   http://localhost:5000/auth/login
   ```

3. **Click "Sign in with GitHub"**

4. **Authorize on GitHub**

5. **Verify you're redirected back and logged in**

6. **Check your profile:**
   ```
   http://localhost:5000/assas_app/profile
   ```

## Troubleshooting

### Common Issues

#### 1. "Application not configured" Error

**Problem:** GitHub OAuth app not set up correctly

**Solution:**
- Verify `.env` file has correct `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`
- Check GitHub OAuth app settings
- Ensure callback URL matches exactly

#### 2. "State parameter mismatch" Error

**Problem:** CSRF protection failing

**Possible causes:**
- Session not working (check `SECRET_KEY`)
- Multiple browser tabs/windows
- Clock synchronization issues

**Solution:**
```python
# Check session configuration
app.config['SECRET_KEY'] = 'your-long-secret-key'
app.config['SESSION_COOKIE_SECURE'] = False  # True only with HTTPS
```

#### 3. "Redirect URI mismatch" Error

**Problem:** GitHub callback URL doesn't match registered URL

**Solution:**
- Development: `http://localhost:5000/auth/callback/github`
- Production: `https://yourdomain.com/auth/callback/github`
- URLs must match exactly (including protocol and port)

#### 4. "Rate limit exceeded" Error

**Problem:** Too many API requests to GitHub

**Solution:**
- Implement token caching
- Reduce API calls
- Wait for rate limit reset

### Debug Checklist

- [ ] GitHub OAuth app created and configured
- [ ] Client ID and secret in `.env` file
- [ ] Callback URL matches exactly
- [ ] Secret key set for Flask sessions
- [ ] Network connectivity to GitHub
- [ ] Browser allows cookies
- [ ] No ad blockers interfering
- [ ] Check application logs for detailed errors

### Environment Variables Validation

```python
def validate_oauth_config():
    required_vars = ['GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET', 'SECRET_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    if len(os.getenv('SECRET_KEY', '')) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long")
```

## Security Best Practices

1. **Environment Variables:**
   - Never commit `.env` file to version control
   - Use different credentials for development/production
   - Rotate secrets regularly

2. **Session Security:**
   - Use long, random secret keys
   - Enable secure cookies in production
   - Set appropriate session timeouts

3. **Error Handling:**
   - Don't expose sensitive information in error messages
   - Log security events for monitoring
   - Implement rate limiting

4. **Production Deployment:**
   - Use HTTPS for all OAuth redirects
   - Implement proper logging and monitoring
   - Regular security updates

---

This OAuth implementation provides secure, industry-standard authentication while maintaining user privacy and system