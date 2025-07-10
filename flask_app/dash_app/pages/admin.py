"""Admin Dashboard Page.

This module provides administrative functionality for managing users,
monitoring system status, and accessing administrative tools.
Only accessible to users with admin role.
"""

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, State, dash_table
from flask import session
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from ...auth_utils import get_current_user, has_role, require_role
from ...database.user_manager import UserManager

logger = logging.getLogger("assas_app")

# Register this page - accessible at /assas_app/admin
dash.register_page(__name__, path="/admin", title="Admin Dashboard - ASSAS Data Hub")

# Styles
ADMIN_CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "border": "1px solid #e0e6ed",
    "borderRadius": "12px",
    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
    "padding": "1.5rem",
    "marginBottom": "2rem",
}

STAT_CARD_STYLE = {
    "backgroundColor": "#f8f9fa",
    "border": "2px solid #e9ecef",
    "borderRadius": "10px",
    "padding": "1.5rem",
    "textAlign": "center",
    "height": "120px",
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "center",
}

def get_user_stats() -> Dict[str, Any]:
    """Get user statistics from MongoDB."""
    try:
        user_manager = UserManager()
        all_users = user_manager.get_all_users()
        
        stats = {
            'total_users': len(all_users),
            'active_users': len([u for u in all_users if u.get('is_active', True)]),
            'github_users': len([u for u in all_users if u.get('provider') == 'github']),
            'bwidm_users': len([u for u in all_users if u.get('provider') == 'bwidm']),
            'admin_users': len([u for u in all_users if 'admin' in u.get('roles', [])]),
            'recent_logins': len([u for u in all_users if u.get('last_login') and 
                                (datetime.utcnow() - datetime.fromisoformat(u['last_login'].replace('Z', '+00:00'))).days <= 7])
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return {
            'total_users': 0,
            'active_users': 0,
            'github_users': 0,
            'bwidm_users': 0,
            'admin_users': 0,
            'recent_logins': 0
        }

def create_stats_cards() -> html.Div:
    """Create user statistics cards."""
    stats = get_user_stats()
    
    cards = [
        dbc.Col([
            html.Div([
                html.H3(str(stats['total_users']), className="mb-1 text-primary"),
                html.P("Total Users", className="mb-0 text-muted")
            ], style=STAT_CARD_STYLE)
        ], md=2, sm=6),
        
        dbc.Col([
            html.Div([
                html.H3(str(stats['active_users']), className="mb-1 text-success"),
                html.P("Active Users", className="mb-0 text-muted")
            ], style=STAT_CARD_STYLE)
        ], md=2, sm=6),
        
        dbc.Col([
            html.Div([
                html.H3(str(stats['github_users']), className="mb-1 text-info"),
                html.P("GitHub Users", className="mb-0 text-muted")
            ], style=STAT_CARD_STYLE)
        ], md=2, sm=6),
        
        dbc.Col([
            html.Div([
                html.H3(str(stats['bwidm_users']), className="mb-1 text-warning"),
                html.P("bwIDM Users", className="mb-0 text-muted")
            ], style=STAT_CARD_STYLE)
        ], md=2, sm=6),
        
        dbc.Col([
            html.Div([
                html.H3(str(stats['admin_users']), className="mb-1 text-danger"),
                html.P("Admin Users", className="mb-0 text-muted")
            ], style=STAT_CARD_STYLE)
        ], md=2, sm=6),
        
        dbc.Col([
            html.Div([
                html.H3(str(stats['recent_logins']), className="mb-1 text-secondary"),
                html.P("Recent Logins", className="mb-0 text-muted small"),
                html.Small("(7 days)", className="text-muted")
            ], style=STAT_CARD_STYLE)
        ], md=2, sm=6),
    ]
    
    return dbc.Row(cards, className="mb-4")

def get_users_data() -> List[Dict]:
    """Get users data for the table."""
    try:
        user_manager = UserManager()
        all_users = user_manager.get_all_users()
        
        users_data = []
        for user in all_users:
            # Format last login
            last_login = user.get('last_login')
            if last_login:
                try:
                    if isinstance(last_login, str):
                        last_login_dt = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
                    else:
                        last_login_dt = last_login
                    last_login_str = last_login_dt.strftime('%Y-%m-%d %H:%M')
                except:
                    last_login_str = str(last_login)
            else:
                last_login_str = 'Never'
            
            # Format creation date
            created_at = user.get('created_at')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_dt = created_at
                    created_str = created_dt.strftime('%Y-%m-%d')
                except:
                    created_str = str(created_at)
            else:
                created_str = 'Unknown'
            
            users_data.append({
                'id': str(user.get('_id', '')),
                'username': user.get('username', ''),
                'email': user.get('email', ''),
                'name': user.get('name', ''),
                'provider': user.get('provider', '').upper(),
                'roles': ', '.join(user.get('roles', [])),
                'is_active': '✓' if user.get('is_active', True) else '✗',
                'last_login': last_login_str,
                'created_at': created_str,
                'login_count': user.get('login_count', 0)
            })
        
        return users_data
        
    except Exception as e:
        logger.error(f"Error getting users data: {e}")
        return []

def create_users_table() -> html.Div:
    """Create users data table."""
    users_data = get_users_data()
    
    if not users_data:
        return html.Div([
            html.P("No users found in database.", className="text-muted text-center py-4")
        ])
    
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(users_data)
    
    # Define table columns
    columns = [
        {"name": "Username", "id": "username", "type": "text"},
        {"name": "Email", "id": "email", "type": "text"},
        {"name": "Name", "id": "name", "type": "text"},
        {"name": "Provider", "id": "provider", "type": "text"},
        {"name": "Roles", "id": "roles", "type": "text"},
        {"name": "Active", "id": "is_active", "type": "text"},
        {"name": "Last Login", "id": "last_login", "type": "text"},
        {"name": "Created", "id": "created_at", "type": "text"},
        {"name": "Logins", "id": "login_count", "type": "numeric"},
    ]
    
    return html.Div([
        dash_table.DataTable(
            id='users-table',
            columns=columns,
            data=df.to_dict('records'),
            sort_action="native",
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=20,
            style_table={
                'overflowX': 'auto'
            },
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Inter, sans-serif',
                'fontSize': '14px',
                'border': '1px solid #e0e6ed',
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'color': '#495057',
                'border': '1px solid #dee2e6',
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{is_active} = ✗'},
                    'backgroundColor': '#f8d7da',
                    'color': 'black',
                },
                {
                    'if': {'filter_query': '{roles} contains admin'},
                    'backgroundColor': '#d1ecf1',
                    'color': 'black',
                }
            ],
            export_format="csv",
            export_headers="display",
        )
    ])

def layout() -> html.Div:
    """Layout for the admin dashboard page."""
    # Check if user is admin
    current_user = get_current_user()
    
    if not current_user:
        return html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.I(className="fas fa-sign-in-alt fa-4x text-muted mb-4"),
                            html.H2("Authentication Required", className="text-muted mb-3"),
                            html.P("Please log in to access the admin dashboard.", className="lead text-muted mb-4"),
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
    
    if not has_role('admin'):
        return html.Div([
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.I(className="fas fa-ban fa-4x text-danger mb-4"),
                            html.H2("Access Denied", className="text-danger mb-3"),
                            html.P(
                                "You don't have administrator privileges to access this page.",
                                className="lead text-muted mb-4"
                            ),
                            html.P(f"Current roles: {', '.join(current_user.get('roles', []))}", className="text-muted mb-4"),
                            dbc.Button(
                                [html.I(className="fas fa-home me-2"), "Go Home"],
                                href="/assas_app/",
                                color="primary",
                                size="lg"
                            )
                        ], className="text-center py-5")
                    ], width=12)
                ])
            ], fluid=True)
        ])
    
    # Admin dashboard layout
    return html.Div([
        dbc.Container([
            # Page Header
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1([
                            html.I(className="fas fa-users-cog me-3"),
                            "Admin Dashboard"
                        ], className="display-6 fw-bold text-primary mb-2"),
                        html.P(
                            f"Welcome, {current_user.get('name', 'Admin')}! Manage users and system settings.",
                            className="lead text-muted"
                        )
                    ], className="mb-4")
                ], width=12)
            ]),
            
            # Statistics Cards
            create_stats_cards(),
            
            # Admin Actions
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-tools me-2"),
                            html.Strong("Admin Actions")
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        [html.I(className="fas fa-sync me-2"), "Refresh Data"],
                                        id="refresh-users-btn",
                                        color="primary",
                                        className="me-2"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-download me-2"), "Export CSV"],
                                        id="export-users-btn",
                                        color="success",
                                        className="me-2"
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-cog me-2"), "System Settings"],
                                        id="system-settings-btn",
                                        color="secondary",
                                        disabled=True  # For future implementation
                                    )
                                ], md=12)
                            ])
                        ])
                    ], style=ADMIN_CARD_STYLE)
                ], width=12)
            ]),
            
            # Users Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-users me-2"),
                                    html.Strong("Registered Users")
                                ], style={"display": "flex", "alignItems": "center"}),
                                html.Small(
                                    f"Total: {len(get_users_data())} users",
                                    className="text-muted"
                                )
                            ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"})
                        ]),
                        dbc.CardBody([
                            html.Div(id="users-table-container", children=[
                                create_users_table()
                            ])
                        ])
                    ], style=ADMIN_CARD_STYLE)
                ], width=12)
            ]),
            
            # System Information
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-info-circle me-2"),
                            html.Strong("System Information")
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.P([
                                        html.Strong("Database: "),
                                        "MongoDB connected ✓"
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Authentication: "),
                                        "GitHub & bwIDM enabled ✓"
                                    ], className="mb-2"),
                                ], md=6),
                                dbc.Col([
                                    html.P([
                                        html.Strong("Last refresh: "),
                                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    ], className="mb-2"),
                                    html.P([
                                        html.Strong("Admin user: "),
                                        current_user.get('email', 'Unknown')
                                    ], className="mb-2"),
                                ], md=6),
                            ])
                        ])
                    ], style=ADMIN_CARD_STYLE)
                ], width=12)
            ])
            
        ], fluid=True, style={"maxWidth": "1400px", "margin": "0 auto", "padding": "2rem 1rem"})
    ])

# Callbacks for admin functionality
@callback(
    Output('users-table-container', 'children'),
    Input('refresh-users-btn', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_users_table(n_clicks):
    """Refresh the users table."""
    if n_clicks:
        logger.info("Admin refreshed users table")
        return create_users_table()
    return dash.no_update