# ASSAS Data Hub Authentication Strategy

## Overview

This document outlines the comprehensive authentication strategy implemented for the ASSAS Data Hub research application. The strategy employs a **three-tier authentication system** that balances security, usability, and institutional requirements.

## Authentication Tiers

### 1. 🏛️ **Institutional Authentication (Tier 1 - Highest Trust)**
**Provider**: bwIDM (Baden-Württemberg Identity Management)  
**Access Level**: Open to all institutional users  
**Trust Level**: High  
**Auto-approval**: Yes  

#### Features:
- Automatic approval for university and research institution members
- Pre-vetted users through institutional authentication
- Default role assignment: `researcher`
- Integration with German research network (DFN-AAI)

#### User Flow:
```mermaid
graph TD
    A[User clicks "Login with bwIDM"] --> B[Redirect to bwIDM]
    B --> C[User authenticates at institution]
    C --> D[bwIDM returns profile]
    D --> E[Auto-create/update user]
    E --> F[Grant access with researcher role]
```

### 2. 🐙 **GitHub OAuth (Tier 2 - Medium Trust)**
**Provider**: GitHub  
**Access Level**: Allow-list based (Pre-registration required)  
**Trust Level**: Medium  
**Auto-approval**: No  

#### Features:
- Pre-registration required by administrators
- Enhanced validation checks
- Role assignment based on pre-registration
- Integration with development workflows

#### User Flow:
```mermaid
graph TD
    A[User clicks "Login with GitHub"] --> B[Check pre-registration]
    B --> C{User pre-registered?}
    C -->|Yes| D[GitHub OAuth flow]
    C -->|No| E[Access denied message]
    D --> F[Activate pre-registered account]
    F --> G[Grant access with assigned roles]
```

### 3. 🔑 **Basic Authentication (Tier 3 - Internal)**
**Provider**: Internal username/password  
**Access Level**: Admin-created accounts only  
**Trust Level**: High (manually vetted)  
**Auto-approval**: No  

#### Features:
- Manually created accounts by administrators
- Full control over user credentials
- Used for special cases and administrative accounts
- No external dependencies

## Security Architecture

### Trust Levels and Access Control

| Authentication Method | Trust Level | Auto-Approval | Default Roles | Use Case |
|----------------------|-------------|---------------|---------------|----------|
| bwIDM OAuth | High | ✅ Yes | `researcher` | University members |
| GitHub OAuth | Medium | ❌ No | `viewer` | External collaborators |
| Basic Auth | High | ❌ No | `viewer` | Special accounts |

### Role-Based Access Control (RBAC)

```python
USER_ROLES = {
    'viewer': {
        'permissions': ['browse_public_data', 'view_metadata'],
        'description': 'Basic viewing access'
    },
    'researcher': {
        'permissions': ['access_research_data', 'use_analysis_tools', 'upload_data'],
        'description': 'Full research capabilities'
    },
    'curator': {
        'permissions': ['manage_metadata', 'review_quality', 'approve_datasets'],
        'description': 'Data curation and quality control'
    },
    'admin': {
        'permissions': ['full_access', 'user_management', 'system_administration'],
        'description': 'Complete system administration'
    }
}
```

## Data Access Levels

### Tiered Data Access
```python
DATA_ACCESS_LEVELS = {
    'public': {
        'auth_required': False,
        'description': 'Published datasets, metadata'
    },
    'research': {
        'auth_required': True,
        'min_role': 'researcher',
        'description': 'Research datasets, preliminary results'
    },
    'sensitive': {
        'auth_required': True,
        'min_role': 'collaborator',
        'additional_auth': ['project_membership', 'data_agreement'],
        'description': 'Sensitive research data'
    },
    'admin': {
        'auth_required': True,
        'min_role': 'admin',
        'description': 'System administration'
    }
}
```

## Security Best Practices

### 1. **Principle of Least Privilege**
- Users receive minimal necessary permissions
- Role escalation requires administrative approval
- Regular role audits and cleanup

### 2. **Zero Trust Architecture**
- Every request is authenticated and authorized
- No implicit trust based on network location
- Continuous verification of user identity

### 3. **Institutional Trust Leveraging**
- bwIDM users benefit from institutional vetting
- GitHub users require additional verification
- Basic auth for special cases only

### 4. **Audit and Compliance**
- All authentication events logged
- User activity tracking
- Regular security reviews

## Advantages of This Strategy

### ✅ **For Researchers**
- **Familiar authentication methods** (institutional login, GitHub)
- **Single sign-on experience** where possible
- **Quick access** for institutional users
- **Collaboration-friendly** for external partners

### ✅ **For Administrators**
- **Granular access control**
- **Easy user management**
- **Clear audit trails**
- **Flexible role assignment**

### ✅ **For Security**
- **Multiple trust levels** based on authentication method
- **Defense in depth** with multiple security layers
- **Controlled external access** through pre-registration
- **Session security** with proper serialization

### ✅ **For Compliance**
- **Institutional authentication** for regulatory compliance
- **Audit logging** for access tracking
- **Role-based access** for data protection
- **User lifecycle management**

## Future Enhancements

### Potential Additions
- **ORCID integration** for researcher identity verification
- **SAML/Shibboleth** for broader institutional support
- **Multi-factor authentication** for high-privilege accounts
- **API token authentication** for programmatic access
- **Federation with other research networks**

### Monitoring and Analytics
- **Authentication success/failure rates**
- **User activity patterns**
- **Security incident detection**
- **Performance metrics**

## Conclusion

This three-tier authentication strategy provides a robust, scalable, and user-friendly approach to securing the ASSAS Data Hub. By leveraging institutional trust, controlling external access, and maintaining administrative flexibility, the system ensures both security and usability for the research community.

The implementation successfully balances:
- **Security requirements** with user experience
- **Institutional trust** with external collaboration needs
- **Administrative control** with user autonomy
- **Compliance needs** with operational efficiency