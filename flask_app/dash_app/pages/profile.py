"""User Profile Page.

This module provides the layout and functionality for the user profile page,
which displays current user information, roles, and account settings.
"""

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, State
import logging

from ...auth_utils import get_current_user, get_user_roles, has_role
from ...utils.url_utils import build_auth_url, get_base_url, get_auth_base_url

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
        "admin": "danger",
        "writer": "warning",
        "reader": "info",
        "viewer": "secondary",
    }
    return role_colors.get(role.lower(), "secondary")


def create_user_info_card() -> dbc.Card:
    """Create user information card."""
    current_user = get_current_user()

    if not current_user:
        return dbc.Alert("User information not available", color="warning")

    # Safe role handling
    roles = current_user.get("roles", [])

    # Handle both string and list roles
    if isinstance(roles, str):
        role_list = [roles]
    elif isinstance(roles, list):
        # Flatten nested lists and convert to strings
        role_list = []
        for role in roles:
            if isinstance(role, list):
                role_list.extend([str(r) for r in role])
            else:
                role_list.append(str(role))
    else:
        role_list = ["viewer"]  # Default fallback

    # Create role badges safely
    role_badges = []
    for role in role_list:
        try:
            role_str = str(role).strip()
            if role_str:  # Only add non-empty roles
                role_badges.append(
                    [html.I(className="fas fa-shield-alt me-1"), role_str.title()]
                )
        except Exception as e:
            logger.error(f"Error processing role {role}: {e}")
            role_badges.append(
                [html.I(className="fas fa-shield-alt me-1"), "Unknown Role"]
            )

    # If no valid roles found, add default
    if not role_badges:
        role_badges = [[html.I(className="fas fa-shield-alt me-1"), "Viewer"]]

    return dbc.Card(
        [
            dbc.CardHeader(
                [html.I(className="fas fa-user me-2"), html.Strong("User Information")]
            ),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.P(
                                        [
                                            html.Strong("Username: "),
                                            current_user.get("username", "N/A"),
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.Strong("Email: "),
                                            current_user.get("email", "N/A"),
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.Strong("Name: "),
                                            current_user.get("name", "N/A"),
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.Strong("Institute: "),
                                            current_user.get("institute", "N/A"),
                                        ],
                                        className="mb-2",
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    html.P(
                                        [
                                            html.Strong("Roles: "),
                                            html.Div(
                                                [
                                                    dbc.Badge(
                                                        role_badge,
                                                        color="primary",
                                                        className="me-1 mb-1",
                                                    )
                                                    for role_badge in role_badges
                                                ]
                                            ),
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.Strong("Provider: "),
                                            current_user.get("provider", "N/A")
                                            .replace("_", " ")
                                            .title(),
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.Strong("Status: "),
                                            dbc.Badge(
                                                (
                                                    "Active"
                                                    if current_user.get(
                                                        "is_active", True
                                                    )
                                                    else "Inactive"
                                                ),
                                                color=(
                                                    "success"
                                                    if current_user.get(
                                                        "is_active", True
                                                    )
                                                    else "danger"
                                                ),
                                            ),
                                        ],
                                        className="mb-2",
                                    ),
                                    html.P(
                                        [
                                            html.Strong("Login Count: "),
                                            str(current_user.get("login_count", 0)),
                                        ],
                                        className="mb-2",
                                    ),
                                ],
                                md=6,
                            ),
                        ]
                    )
                ]
            ),
        ],
        className="mb-4",
    )


def create_account_details_card() -> dbc.Card:
    """Create account details card."""
    user = get_current_user()

    if not user:
        return html.Div()

    details = [
        ("User ID", user.get("id", "N/A")),
        ("Email Address", user.get("email", "Not provided")),
        ("Display Name", user.get("name", "Not provided")),
        ("Username", user.get("username", "Not provided")),
        ("Authentication Provider", user.get("provider", "Unknown").title()),
    ]

    # Add GitHub specific info
    if user.get("provider") == "github" and user.get("github_profile"):
        details.append(("GitHub Profile", user.get("github_profile")))

    detail_rows = []
    for label, value in details:
        if label == "GitHub Profile" and value:
            value_element = html.A(
                value,
                href=value,
                target="_blank",
                className="text-primary",
                style={"textDecoration": "none"},
            )
        elif label == "Email Address" and value and value != "Not provided":
            value_element = html.A(
                value,
                href=f"mailto:{value}",
                className="text-primary",
                style={"textDecoration": "none"},
            )
        else:
            value_element = html.Span(value, style=INFO_VALUE_STYLE)

        detail_rows.append(
            html.Div(
                [html.Div(label, style=INFO_LABEL_STYLE), value_element],
                className="mb-3",
            )
        )

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-id-card me-2"),
                    html.Strong("Account Details"),
                ]
            ),
            dbc.CardBody(detail_rows),
        ],
        style=PROFILE_CARD_STYLE,
    )


def create_permissions_card() -> dbc.Card:
    """Create permissions and access card."""
    user = get_current_user()
    roles = get_user_roles()

    if not user:
        return html.Div()

    # Safe role processing - handle both strings and lists
    processed_roles = []
    if isinstance(roles, str):
        processed_roles = [roles]
    elif isinstance(roles, list):
        for role in roles:
            if isinstance(role, list):
                # Handle nested lists
                processed_roles.extend([str(r) for r in role if r])
            elif role:  # Only add non-empty roles
                processed_roles.append(str(role))

    # Remove duplicates and convert to lowercase for lookup
    processed_roles = list(set([role.lower() for role in processed_roles if role]))

    # Define permission mappings
    permission_info = {
        "admin": {
            "color": "danger",
            "icon": "fas fa-crown",
            "description": "Full system access with administrative privileges",
            "permissions": [
                "Manage all datasets",
                "Access admin functions",
                "Modify system settings",
                "View all user data",
            ],
        },
        "researcher": {
            "color": "primary",
            "icon": "fas fa-microscope",
            "description": "Research data access and analysis tools",
            "permissions": [
                "Access research datasets",
                "Run analysis tools",
                "Upload research data",
                "Collaborate with team",
            ],
        },
        "curator": {
            "color": "success",
            "icon": "fas fa-tasks",
            "description": "Data curation and quality control",
            "permissions": [
                "Review data quality",
                "Manage metadata",
                "Approve datasets",
                "Monitor data integrity",
            ],
        },
        "viewer": {
            "color": "secondary",
            "icon": "fas fa-eye",
            "description": "Basic viewing access",
            "permissions": [
                "Browse public datasets",
                "View basic information",
                "Access help documentation",
                "Download permitted data",
            ],
        },
    }

    role_cards = []
    for role in processed_roles:
        role_lower = role.lower() if isinstance(role, str) else str(role).lower()
        role_info = permission_info.get(role_lower, {})

        if role_info:
            role_cards.append(
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        html.I(
                                            className=f"{role_info['icon']} fa-2x me-3",
                                            style={
                                                "color": "var"
                                                f"(--bs-{role_info['color']})"
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.H5(role.title(), className="mb-1"),
                                                html.P(
                                                    role_info["description"],
                                                    className="text-muted mb-2",
                                                    style={"fontSize": "0.9rem"},
                                                ),
                                                html.Ul(
                                                    [
                                                        html.Li(
                                                            perm,
                                                            style={
                                                                "fontSize": "0.85rem"
                                                            },
                                                        )
                                                        for perm in role_info[
                                                            "permissions"
                                                        ]
                                                    ],
                                                    className="mb-0",
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "flex-start",
                                    },
                                )
                            ]
                        )
                    ],
                    className="mb-3",
                    style={"border": f"2px solid var(--bs-{role_info['color']})"},
                )
            )

    # If no valid roles found, show default message
    if not role_cards:
        role_cards = [
            html.P(
                "No specific roles assigned. "
                "Contact an administrator for role assignment.",
                className="text-muted",
            )
        ]

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-shield-alt me-2"),
                    html.Strong("Roles & Permissions"),
                ]
            ),
            dbc.CardBody(role_cards),
        ],
        style=PROFILE_CARD_STYLE,
    )


def create_actions_card() -> dbc.Card:
    """Create actions card with logout and other options."""
    user = get_current_user()
    user_provider = user.get("provider", "Unknown").replace("_", " ").title()

    if not user:
        return html.Div()

    # Enhanced logout with confirmation modal
    logout_section = html.Div(
        [
            dbc.Button(
                [html.I(className="fas fa-sign-out-alt me-2"), "Logout"],
                id="logout-button",
                color="outline-danger",
                className="me-2 mb-2",
                n_clicks=0,
            ),
            # Confirmation Modal
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            [
                                html.I(className="fas fa-sign-out-alt me-2"),
                                "Confirm Logout",
                            ]
                        )
                    ),
                    dbc.ModalBody(
                        [
                            html.P(
                                [
                                    f"Are you sure you want to logout, "
                                    f"{user.get('name', 'User')}?"
                                ],
                                className="mb-3",
                            ),
                            html.Div(
                                [
                                    html.I(
                                        className="fas fa-info-circle me-2",
                                        style={"color": "#17a2b8"},
                                    ),
                                    f"You are currently logged in via {user_provider}.",
                                ],
                                className="alert alert-info mb-0",
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                [html.I(className="fas fa-times me-2"), "Cancel"],
                                id="logout-cancel",
                                color="secondary",
                                className="me-2",
                                n_clicks=0,
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-sign-out-alt me-2"),
                                    "Yes, Logout",
                                ],
                                id="logout-confirm",
                                color="danger",
                                n_clicks=0,
                            ),
                        ]
                    ),
                ],
                id="logout-modal",
                is_open=False,
            ),
            # Hidden redirect component
            dcc.Location(id="logout-redirect", refresh=True),
        ]
    )

    actions = [
        logout_section,
        dbc.Button(
            [html.I(className="fas fa-home me-2"), "Go to Home"],
            href=f"{get_base_url()}/home",
            color="outline-primary",
            className="me-2 mb-2",
        ),
        dbc.Button(
            [html.I(className="fas fa-database me-2"), "Browse Database"],
            href=f"{get_base_url()}/database",
            color="outline-info",
            className="me-2 mb-2",
        ),
    ]

    # Add debug action for admins
    if has_role("admin"):
        actions.append(
            dbc.Button(
                [html.I(className="fas fa-bug me-2"), "Debug Session"],
                href=f"{get_auth_base_url()}/debug/session",
                color="outline-warning",
                className="me-2 mb-2",
                target="_blank",
            )
        )

    return dbc.Card(
        [
            dbc.CardHeader(
                [html.I(className="fas fa-cogs me-2"), html.Strong("Quick Actions")]
            ),
            dbc.CardBody(actions),
        ],
        style=PROFILE_CARD_STYLE,
    )


# Callbacks for logout handling
@callback(
    Output("logout-modal", "is_open"),
    [Input("logout-button", "n_clicks"), Input("logout-cancel", "n_clicks")],
    [State("logout-modal", "is_open")],
    prevent_initial_call=True,
)
def toggle_logout_modal(logout_clicks: int, cancel_clicks: int, is_open: bool) -> bool:
    """Toggle logout confirmation modal."""
    if logout_clicks or cancel_clicks:
        return not is_open
    return is_open


@callback(
    Output("logout-redirect", "href"),
    Input("logout-confirm", "n_clicks"),
    prevent_initial_call=True,
)
def confirm_logout(n_clicks: int | None) -> str:
    """Handle logout confirmation."""
    if n_clicks and n_clicks > 0:
        return f"{get_auth_base_url()}/logout"
    return dash.no_update


def layout() -> html.Div:  # ruff: noqa: E501
    """Layout for the user profile page.

    Returns:
        html.Div: The layout of the user profile page.

    """
    user = get_current_user()

    if not user:
        # Not authenticated layout
        return html.Div(
            [
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.I(
                                                    className="fas fa-user-slash "
                                                    "fa-4x text-muted mb-4"
                                                ),
                                                html.H2(
                                                    "Authentication Required",
                                                    className="text-muted mb-3",
                                                ),
                                                html.P(
                                                    "You need to be logged in to "
                                                    "view your profile.",
                                                    className="lead text-muted mb-4",
                                                ),
                                                dbc.Button(
                                                    [
                                                        html.I(
                                                            className="fas "
                                                            "fa-sign-in-alt me-2"
                                                        ),
                                                        "Login",
                                                    ],
                                                    href=f"{get_auth_base_url()}/login",
                                                    color="primary",
                                                    size="lg",
                                                ),
                                            ],
                                            className="text-center py-5",
                                        )
                                    ],
                                    width=12,
                                )
                            ]
                        )
                    ],
                    fluid=True,
                )
            ]
        )

    # Authenticated layout
    basic_auth_section = []

    if user.get("provider") == "basic_auth":
        basic_auth_section = dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    [
                                        html.I(className="fas fa-key me-2"),
                                        html.Strong("Basic Authentication"),
                                    ]
                                ),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "You are logged in using "
                                            "Basic Authentication.",
                                            className="mb-3",
                                        ),
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-key me-2"),
                                                "Change Password",
                                            ],
                                            href=(
                                                build_auth_url("basic/change-password")
                                            ),
                                            color="warning",
                                            className="me-2",
                                            external_link=True,
                                        ),
                                        html.Small(
                                            "Change your login password",
                                            className="text-muted",
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        )
                    ],
                    width=12,
                )
            ]
        )

    return html.Div(
        [
            dbc.Container(
                [
                    # Page Header
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.H1(
                                                [
                                                    html.I(
                                                        className="fas fa-user me-3"
                                                    ),
                                                    "User Profile",
                                                ],
                                                className="display-6 fw-bold "
                                                "text-primary mb-2",
                                            ),
                                            html.P(
                                                f"Welcome back, "
                                                f"{user.get('name', 'User')}! "
                                                f"Here's your account information.",
                                                className="lead text-muted",
                                            ),
                                        ],
                                        className="text-center mb-4",
                                    )
                                ],
                                width=12,
                            )
                        ]
                    ),
                    # Main Content
                    dbc.Row(
                        [
                            # Left Column - User Info
                            dbc.Col(
                                [create_user_info_card(), create_actions_card()],
                                md=4,
                                sm=12,
                            ),
                            # Right Column - Details and Permissions
                            dbc.Col(
                                [
                                    create_account_details_card(),
                                    create_permissions_card(),
                                ],
                                md=8,
                                sm=12,
                            ),
                        ]
                    ),
                    # Basic Auth Section
                    basic_auth_section,
                ],
                fluid=True,
                style={
                    "maxWidth": "1400px",
                    "margin": "0 auto",
                    "padding": "2rem 1rem",
                },
            )
        ]
    )
