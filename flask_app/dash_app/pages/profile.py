"""User Profile Page.

This module provides the layout and functionality for the user profile page,
which displays current user information, roles, and account settings.
"""

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, State
from flask import session
import logging

from ...auth_utils import get_current_user, get_user_roles, has_role

logger = logging.getLogger("assas_app")

# Register this page
dash.register_page(__name__, path="/profile", title="Profile - ASSAS Data Hub")

# Styles
PROFILE_CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "border": "1px solid #e0e6ed",
    "borderRadius": "12px",
    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
    "padding": "2rem",
    "marginBottom": "2rem",
    "transition": "all 0.3s ease",
}

AVATAR_STYLE = {
    "width": "120px",
    "height": "120px",
    "borderRadius": "50%",
    "border": "4px solid #e9ecef",
    "objectFit": "cover",
    "marginBottom": "1rem",
}

BADGE_STYLE = {
    "fontSize": "0.875rem",
    "fontWeight": "600",
    "padding": "0.5rem 1rem",
    "borderRadius": "20px",
    "margin": "0.25rem",
    "display": "inline-block",
}

INFO_LABEL_STYLE = {
    "fontWeight": "600",
    "color": "#495057",
    "fontSize": "0.875rem",
    "textTransform": "uppercase",
    "letterSpacing": "0.5px",
    "marginBottom": "0.5rem",
}

INFO_VALUE_STYLE = {
    "color": "#212529",
    "fontSize": "1rem",
    "marginBottom": "1.5rem",
    "wordBreak": "break-word",
}

def get_role_badge_color(role: str) -> str:
    """Get badge color for role."""
    role_colors = {
        'admin': 'danger',
        'writer': 'warning',
        'reader': 'info',
        'viewer': 'secondary',
    }
    return role_colors.get(role.lower(), 'secondary')

def create_user_info_card() -> dbc.Card:
    """Create user information card."""
    user = get_current_user()
    
    if not user:
        return dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle fa-3x text-warning mb-3"),
                    html.H4("Not Authenticated", className="text-warning"),
                    html.P("Please log in to view your profile."),
                    dbc.Button(
                        [html.I(className="fas fa-sign-in-alt me-2"), "Login"],
                        href="/auth/login",
                        color="primary"
                    )
                ], className="text-center")
            ])
        ], style=PROFILE_CARD_STYLE)
    
    # Avatar section
    avatar_section = html.Div([
        html.Img(
            src=user.get('avatar_url', '/assets/default-avatar.png'),
            style=AVATAR_STYLE,
            alt="User Avatar"
        ) if user.get('avatar_url') else html.Div([
            html.I(
                className="fas fa-user fa-4x text-secondary",
                style={"marginBottom": "1rem"}
            )
        ], style={"textAlign": "center", "marginBottom": "1rem"}),
        
        html.H3(user.get('name', 'Unknown User'), className="text-center mb-2"),
        html.P(f"@{user.get('username', 'unknown')}", className="text-center text-muted mb-3"),
        
        # Role badges
        html.Div([
            dbc.Badge(
                [html.I(className="fas fa-shield-alt me-1"), role.title()],
                color=get_role_badge_color(role),
                style=BADGE_STYLE
            ) for role in user.get('roles', [])
        ], className="text-center mb-3"),
        
        # Provider badge
        html.Div([
            dbc.Badge(
                [
                    html.I(className=f"fab fa-{user.get('provider', 'github')} me-1"),
                    f"via {user.get('provider', 'Unknown').title()}"
                ],
                color="primary",
                style=BADGE_STYLE
            )
        ], className="text-center")
    ], className="text-center")
    
    return dbc.Card([
        dbc.CardBody([avatar_section])
    ], style=PROFILE_CARD_STYLE)

def create_account_details_card() -> dbc.Card:
    """Create account details card."""
    user = get_current_user()
    
    if not user:
        return html.Div()
    
    details = [
        ("User ID", user.get('id', 'N/A')),
        ("Email Address", user.get('email', 'Not provided')),
        ("Display Name", user.get('name', 'Not provided')),
        ("Username", user.get('username', 'Not provided')),
        ("Authentication Provider", user.get('provider', 'Unknown').title()),
    ]
    
    # Add GitHub specific info
    if user.get('provider') == 'github' and user.get('github_profile'):
        details.append(("GitHub Profile", user.get('github_profile')))
    
    detail_rows = []
    for label, value in details:
        if label == "GitHub Profile" and value:
            value_element = html.A(
                value,
                href=value,
                target="_blank",
                className="text-primary",
                style={"textDecoration": "none"}
            )
        elif label == "Email Address" and value and value != "Not provided":
            value_element = html.A(
                value,
                href=f"mailto:{value}",
                className="text-primary",
                style={"textDecoration": "none"}
            )
        else:
            value_element = html.Span(value, style=INFO_VALUE_STYLE)
        
        detail_rows.append(
            html.Div([
                html.Div(label, style=INFO_LABEL_STYLE),
                value_element
            ], className="mb-3")
        )
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-id-card me-2"),
            html.Strong("Account Details")
        ]),
        dbc.CardBody(detail_rows)
    ], style=PROFILE_CARD_STYLE)

def create_permissions_card() -> dbc.Card:
    """Create permissions and access card."""
    user = get_current_user()
    roles = get_user_roles()
    
    if not user:
        return html.Div()
    
    # Define permission mappings
    permission_info = {
        'admin': {
            'color': 'danger',
            'icon': 'fas fa-crown',
            'description': 'Full system access with administrative privileges',
            'permissions': [
                'Manage all datasets',
                'Access admin functions',
                'Modify system settings',
                'View all user data'
            ]
        },
        'writer': {
            'color': 'warning',
            'icon': 'fas fa-edit',
            'description': 'Can create and modify content',
            'permissions': [
                'Upload datasets',
                'Edit metadata',
                'Create documentation',
                'Access collaboration tools'
            ]
        },
        'reader': {
            'color': 'info',
            'icon': 'fas fa-book-open',
            'description': 'Can read and download content',
            'permissions': [
                'Download datasets',
                'View all documentation',
                'Access search functions',
                'Export data'
            ]
        },
        'viewer': {
            'color': 'secondary',
            'icon': 'fas fa-eye',
            'description': 'Basic viewing access',
            'permissions': [
                'Browse public datasets',
                'View basic information',
                'Access help documentation'
            ]
        }
    }
    
    role_cards = []
    for role in roles:
        role_info = permission_info.get(role.lower(), {})
        if role_info:
            role_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.I(
                                className=f"{role_info['icon']} fa-2x me-3",
                                style={"color": f"var(--bs-{role_info['color']})"}
                            ),
                            html.Div([
                                html.H5(role.title(), className="mb-1"),
                                html.P(
                                    role_info['description'],
                                    className="text-muted mb-2",
                                    style={"fontSize": "0.9rem"}
                                ),
                                html.Ul([
                                    html.Li(perm, style={"fontSize": "0.85rem"})
                                    for perm in role_info['permissions']
                                ], className="mb-0")
                            ])
                        ], style={"display": "flex", "alignItems": "flex-start"})
                    ])
                ], className="mb-3", style={"border": f"2px solid var(--bs-{role_info['color']})"})
            )
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-shield-alt me-2"),
            html.Strong("Roles & Permissions")
        ]),
        dbc.CardBody(role_cards if role_cards else [
            html.P("No specific roles assigned.", className="text-muted")
        ])
    ], style=PROFILE_CARD_STYLE)

def create_actions_card() -> dbc.Card:
    """Create actions card with logout and other options."""
    user = get_current_user()
    
    if not user:
        return html.Div()
    
    actions = [
        dbc.Button(
            [html.I(className="fas fa-sign-out-alt me-2"), "Logout"],
            href="/auth/logout",
            color="outline-danger",
            className="me-2 mb-2"
        ),
        dbc.Button(
            [html.I(className="fas fa-home me-2"), "Go to Home"],
            href="/assas_app/home",
            color="outline-primary",
            className="me-2 mb-2"
        ),
        dbc.Button(
            [html.I(className="fas fa-database me-2"), "Browse Database"],
            href="/assas_app/database",
            color="outline-info",
            className="me-2 mb-2"
        )
    ]
    
    # Add debug action for admins
    if has_role('admin'):
        actions.append(
            dbc.Button(
                [html.I(className="fas fa-bug me-2"), "Debug Session"],
                href="/auth/debug/session",
                color="outline-warning",
                className="me-2 mb-2",
                target="_blank"
            )
        )
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-cogs me-2"),
            html.Strong("Quick Actions")
        ]),
        dbc.CardBody(actions)
    ], style=PROFILE_CARD_STYLE)

def layout() -> html.Div:  # ruff: noqa: E501
    """Layout for the user profile page.
    
    Returns:
        html.Div: The layout of the user profile page.
    """
    user = get_current_user()
    
    if not user:
        # Not authenticated layout
        return html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.I(className="fas fa-user-slash fa-4x text-muted mb-4"),
                            html.H2("Authentication Required", className="text-muted mb-3"),
                            html.P(
                                "You need to be logged in to view your profile.",
                                className="lead text-muted mb-4"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-sign-in-alt me-2"), "Login"],
                                href="/auth/login",
                                color="primary",
                                size="lg"
                            )
                        ], className="text-center py-5")
                    ], width=12)
                ])
            ], fluid=True)
        ])
    
    # Authenticated layout
    return html.Div([
        dbc.Container([
            # Page Header
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1([
                            html.I(className="fas fa-user me-3"),
                            "User Profile"
                        ], className="display-6 fw-bold text-primary mb-2"),
                        html.P(
                            f"Welcome back, {user.get('name', 'User')}! Here's your account information.",
                            className="lead text-muted"
                        )
                    ], className="text-center mb-4")
                ], width=12)
            ]),
            
            # Main Content
            dbc.Row([
                # Left Column - User Info
                dbc.Col([
                    create_user_info_card(),
                    create_actions_card()
                ], md=4, sm=12),
                
                # Right Column - Details and Permissions
                dbc.Col([
                    create_account_details_card(),
                    create_permissions_card()
                ], md=8, sm=12)
            ])
        ], fluid=True, style={"maxWidth": "1400px", "margin": "0 auto", "padding": "2rem 1rem"})
    ])