"""Create a Plotly Dash app with Flask integration.

This module initializes a Dash application with Flask, sets up the navbar,
and configures authentication and long callbacks using diskcache.
"""

import os
import logging
import uuid
import diskcache
import dash_bootstrap_components as dbc

from dash import dash, html, Input, Output, State, clientside_callback, ClientsideFunction
from dash.long_callback import DiskcacheLongCallbackManager

from .components import encode_svg_image_hq  # Use high-quality encoder
from flask import redirect, request, Response
from ..auth_utils import auth, is_authenticated, get_current_user

logger = logging.getLogger("assas_app")

def modern_navbar_style() -> dict:
    """Define modern navbar styles.
    
    Returns:
        dict: CSS styles for the navbar.
    """
    return {
        "backgroundColor": "#2c3e50",  # Modern dark blue
        "borderBottom": "3px solid #3498db",  # Blue accent border
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.15)",  # Enhanced shadow
        "fontFamily": "Arial, sans-serif",
        "fontSize": "1rem",
        "padding": "0.5rem 0",
        "position": "sticky",
        "top": "0",
        "zIndex": "1030",
        "transition": "transform 0.3s ease-in-out, opacity 0.3s ease-in-out",  # Add transitions
        "opacity": "1",  # Default opacity
        "transform": "translateY(0)",  # Default position
    }

def top_row_style() -> dict:
    """Define top row styles for brand section.
    
    Returns:
        dict: CSS styles for top row.
    """
    return {
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "padding": "1rem 0",
        "borderBottom": "1px solid #34495e",
        "backgroundColor": "#2c3e50",
    }

def bottom_row_style() -> dict:
    """Define bottom row styles for navigation.
    
    Returns:
        dict: CSS styles for bottom row.
    """
    return {
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "padding": "0.5rem 1rem",
        "backgroundColor": "#34495e",
        "position": "relative",
        
        # Mobile adjustments
        "@media (max-width: 768px)": {
            "justifyContent": "space-between",
        },
    }

def logo_style() -> dict:
    """Define high-quality logo styles.
    
    Returns:
        dict: CSS styles for high-resolution logos.
    """
    return {
        "border": "2px solid #ecf0f1",
        "borderRadius": "6px",
        "padding": "4px",
        "backgroundColor": "#ffffff",
        "transition": "transform 0.2s ease",
        
        # High-quality rendering
        "imageRendering": "high-quality",
        "imageResolution": "from-image",
        "objectFit": "contain",
        "objectPosition": "center",
        "filter": "contrast(1.05) brightness(1.02)",
        
        # Anti-aliasing and smoothing
        "backfaceVisibility": "hidden",
        "perspective": "1000px",
        "transform": "translateZ(0)",
        "willChange": "transform",
        
        ":hover": {
            "transform": "scale(1.05) translateZ(0)",
            "filter": "contrast(1.08) brightness(1.04)",
        },
        
        # Mobile responsive sizing
        "@media (max-width: 768px)": {
            "border": "1px solid #ecf0f1",
            "padding": "3px",
        },
        "@media (max-width: 576px)": {
            "border": "1px solid #ecf0f1",
            "padding": "2px",
        },
    }

def brand_style() -> dict:
    """Define brand text styles.
    
    Returns:
        dict: CSS styles for brand text.
    """
    return {
        "fontSize": "2.75rem",
        "fontWeight": "700",
        "color": "#ecf0f1",
        "fontFamily": "Arial, sans-serif",
        "textShadow": "1px 1px 2px rgba(0, 0, 0, 0.3)",
        "textAlign": "center",
        "whiteSpace": "nowrap",
        "margin": "0",
        
        # Mobile responsive
        "@media (max-width: 768px)": {
            "fontSize": "1.5rem",
        },
        "@media (max-width: 576px)": {
            "fontSize": "1.25rem",
        },
        "@media (max-width: 480px)": {
            "fontSize": "1.1rem",
            "whiteSpace": "normal",
            "lineHeight": "1.2",
        },
    }

def brand_container_style() -> dict:
    """Define brand container styles.
    
    Returns:
        dict: CSS styles for brand container.
    """
    return {
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
        "gap": "2rem",
        "flexWrap": "wrap",
        
        # Mobile responsive
        "@media (max-width: 768px)": {
            "flexDirection": "column",
            "gap": "1rem",
        },
        "@media (max-width: 576px)": {
            "gap": "0.5rem",
        },
    }

def logos_container_style() -> dict:
    """Define logos container styles.
    
    Returns:
        dict: CSS styles for logos container.
    """
    return {
        "display": "flex",
        "alignItems": "center",
        "gap": "1.5rem",
        
        # Mobile responsive
        "@media (max-width: 768px)": {
            "gap": "1rem",
        },
        "@media (max-width: 576px)": {
            "gap": "0.75rem",
        },
    }

def nav_link_style() -> dict:
    """Define navigation link styles.
    
    Returns:
        dict: CSS styles for nav links.
    """
    return {
        "color": "#ecf0f1",
        "fontWeight": "500",
        "fontSize": "1.1rem",
        "padding": "0.75rem 1rem",
        "borderRadius": "6px",
        "transition": "all 0.3s ease",
        "margin": "0 0.25rem",
        "fontFamily": "Arial, sans-serif",
        "textDecoration": "none",
        
        ":hover": {
            "backgroundColor": "#3498db",
            "color": "#ffffff",
            "transform": "translateY(-1px)",
        },
        
        # Mobile styles
        "@media (max-width: 768px)": {
            "fontSize": "1rem",
            "padding": "0.5rem 0.75rem",
            "margin": "0.25rem 0",
            "width": "100%",
            "textAlign": "center",
        },
    }

def hamburger_style() -> dict:
    """Define hamburger menu styles.
    
    Returns:
        dict: CSS styles for hamburger menu.
    """
    return {
        "border": "2px solid #3498db",
        "borderRadius": "6px",
        "padding": "0.5rem",
        "backgroundColor": "transparent",
        "color": "#ecf0f1",
        "fontSize": "1.2rem",
        
        ":focus": {
            "boxShadow": "0 0 0 0.2rem rgba(52, 152, 219, 0.5)",
        },
        ":hover": {
            "backgroundColor": "#3498db",
        },
    }

def footer_style() -> dict:
    """Define footer styles.
    
    Returns:
        dict: CSS styles for footer.
    """
    return {
        "backgroundColor": "#2c3e50",
        "color": "#ecf0f1",
        "padding": "2rem 0",
        "marginTop": "3rem",
        "borderTop": "3px solid #3498db",
        "fontFamily": "Arial, sans-serif",
        "fontSize": "0.9rem",
        
        # Mobile responsive
        "@media (max-width: 768px)": {
            "padding": "1.5rem 0",
            "fontSize": "0.8rem",
        },
    }

def footer_section_style() -> dict:
    """Define footer section styles.
    
    Returns:
        dict: CSS styles for footer sections.
    """
    return {
        "marginBottom": "1.5rem",
        
        # Mobile responsive
        "@media (max-width: 768px)": {
            "marginBottom": "1rem",
            "textAlign": "center",
        },
    }

def footer_title_style() -> dict:
    """Define footer title styles.
    
    Returns:
        dict: CSS styles for footer titles.
    """
    return {
        "color": "#3498db",
        "fontSize": "1.1rem",
        "fontWeight": "600",
        "marginBottom": "0.75rem",
        "borderBottom": "1px solid #34495e",
        "paddingBottom": "0.5rem",
        
        # Mobile responsive
        "@media (max-width: 768px)": {
            "fontSize": "1rem",
            "marginBottom": "0.5rem",
        },
    }

def footer_link_style() -> dict:
    """Define footer link styles.
    
    Returns:
        dict: CSS styles for footer links.
    """
    return {
        "color": "#bdc3c7",
        "textDecoration": "none",
        "transition": "color 0.3s ease",
        "display": "block",
        "padding": "0.25rem 0",
        
        ":hover": {
            "color": "#3498db",
            "textDecoration": "underline",
        },
    }

def footer_copyright_style() -> dict:
    """Define footer copyright styles.
    
    Returns:
        dict: CSS styles for copyright section.
    """
    return {
        "borderTop": "1px solid #34495e",
        "paddingTop": "1.5rem",
        "marginTop": "2rem",
        "textAlign": "center",
        "color": "#95a5a6",
        "fontSize": "0.85rem",
        
        # Mobile responsive
        "@media (max-width: 768px)": {
            "paddingTop": "1rem",
            "marginTop": "1.5rem",
            "fontSize": "0.8rem",
        },
    }

# Footer component
footer = html.Footer([
    dbc.Container([
        dbc.Row([
            # Organization Info
            dbc.Col([
                html.H5("ASSAS Project", style=footer_title_style()),
                html.P([
                    "Advanced Seismic Simulation and Analysis System for ",
                    "geothermal energy applications at KIT."
                ], style={"lineHeight": "1.6", "marginBottom": "1rem"}),
                html.Div([
                    html.I(className="fas fa-map-marker-alt me-2"),
                    "Karlsruhe Institute of Technology (KIT)"
                ], style={"marginBottom": "0.5rem"}),
                html.Div([
                    html.I(className="fas fa-envelope me-2"),
                    html.A(
                        "contact@assas-project.org",
                        href="mailto:contact@assas-project.org",
                        style=footer_link_style()
                    )
                ], style={"display": "inline-block"}),
            ], md=4, sm=12, style=footer_section_style()),
            
            # Quick Links
            dbc.Col([
                html.H5("Quick Links", style=footer_title_style()),
                html.Div([
                    html.A("Home", href="/assas_app/home", style=footer_link_style()),
                    html.A("Database", href="/assas_app/database", style=footer_link_style()),
                    html.A("About", href="/assas_app/about", style=footer_link_style()),
                    html.A("Documentation", href="#", style=footer_link_style()),
                    html.A("API Reference", href="#", style=footer_link_style()),
                ])
            ], md=2, sm=6, style=footer_section_style()),
            
            # Resources
            dbc.Col([
                html.H5("Resources", style=footer_title_style()),
                html.Div([
                    html.A("Research Papers", href="#", style=footer_link_style()),
                    html.A("Data Sets", href="#", style=footer_link_style()),
                    html.A("Tutorials", href="#", style=footer_link_style()),
                    html.A("FAQ", href="#", style=footer_link_style()),
                    html.A("Support", href="#", style=footer_link_style()),
                ])
            ], md=2, sm=6, style=footer_section_style()),
            
            # Partners & Social
            dbc.Col([
                html.H5("Partners", style=footer_title_style()),
                html.Div([
                    # Partner logos
                    html.Div([
                        html.Img(
                            src=encode_svg_image_hq("kit_logo.drawio.svg"),
                            height="40px",
                            width="80px",
                            style={
                                "backgroundColor": "#ffffff",
                                "padding": "4px",
                                "borderRadius": "4px",
                                "marginBottom": "1rem",
                                "filter": "contrast(1.05) brightness(1.02)",
                            },
                            alt="KIT Logo"
                        )
                    ], style={"marginBottom": "1rem"}),
                    
                    # Social links
                    html.Div([
                        html.A([
                            html.I(className="fab fa-github me-2"),
                            "GitHub"
                        ], href="https://github.com/Helmholtz-AI-Energy/assas-data-hub", 
                           style=footer_link_style(), target="_blank"),
                        html.A([
                            html.I(className="fas fa-globe me-2"),
                            "Website"
                        ], href="#", style=footer_link_style(), target="_blank"),
                    ])
                ])
            ], md=4, sm=12, style=footer_section_style()),
        ]),
        
        # Copyright section
        html.Hr(style={"borderColor": "#34495e", "margin": "2rem 0 1.5rem 0"}),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P([
                        "© 2024 ASSAS Data Hub. All rights reserved. | ",
                        html.A("Privacy Policy", href="#", style=footer_link_style()),
                        " | ",
                        html.A("Terms of Service", href="#", style=footer_link_style()),
                        " | ",
                        html.A("Imprint", href="#", style=footer_link_style())
                    ], style={
                        "margin": "0",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "flexWrap": "wrap",
                        "gap": "0.5rem",
                    }),
                    html.P([
                        "Powered by ",
                        html.A("Dash", href="https://plotly.com/dash/", 
                               style=footer_link_style(), target="_blank"),
                        " & ",
                        html.A("Flask", href="https://flask.palletsprojects.com/", 
                               style=footer_link_style(), target="_blank")
                    ], style={
                        "margin": "0.5rem 0 0 0",
                        "fontSize": "0.8rem",
                        "color": "#7f8c8d"
                    })
                ], style=footer_copyright_style())
            ], width=12)
        ])
    ], fluid=True)
], style=footer_style())

# Two-row navbar structure without toggle button
navbar = html.Div([
    # Top Row - Brand and Logos (Reordered: ASSAS - Brand - KIT) - INCREASED LOGO HEIGHT
    html.Div([
        dbc.Container([
            html.A([
                html.Div([
                    # ASSAS Logo (First) - INCREASED size
                    html.Img(
                        src=encode_svg_image_hq("assas_logo_mod.svg"),
                        height="80px",  # Increased from 60px
                        width="160px",  # Increased from 120px
                        style=logo_style(),
                        alt="ASSAS Logo",
                        className="logo-high-quality logo-assas"
                    ),
                    
                    # Brand title (Center)
                    html.H1(
                        "ASSAS Data Hub",
                        style=brand_style(),
                        className="brand-title brand-center"
                    ),
                    
                    # KIT Logo (Last) - INCREASED size
                    html.Img(
                        src=encode_svg_image_hq("kit_logo.drawio.svg"),
                        height="80px",  # Increased from 60px
                        width="160px",  # Increased from 120px
                        style=logo_style(),
                        alt="KIT Logo",
                        className="logo-high-quality logo-kit"
                    ),
                ], style=brand_container_style())
            ], 
            href="/assas_app/home",
            style={"textDecoration": "none"},
            className="brand-link"
            )
        ], fluid=True, style={"maxWidth": "1400px"})
    ], style=top_row_style()),
    
    # Bottom Row - Navigation
    html.Div([
        dbc.Container([
            # Navigation content wrapper
            html.Div([
                # Hamburger menu (visible on mobile)
                dbc.Button(
                    html.I(className="fas fa-bars"),
                    id="navbar-toggler",
                    n_clicks=0,
                    style=hamburger_style(),
                    className="navbar-toggler-mobile d-md-none"
                ),
                
                # Navigation menu
                dbc.Collapse([
                    dbc.Nav([
                        dbc.NavItem(
                            dbc.NavLink([
                                html.I(className="fas fa-home me-2"),
                                "Home"
                            ], 
                            href="/assas_app/home", 
                            active="exact",
                            style=nav_link_style(),
                            className="nav-link-modern"
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink([
                                html.I(className="fas fa-database me-2"),  # Fixed missing opening parenthesis
                                "Database"
                            ], 
                            href="/assas_app/database", 
                            active="exact",
                            style=nav_link_style(),
                            className="nav-link-modern"
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink([
                                html.I(className="fas fa-info-circle me-2"),
                                "About"
                            ], 
                            href="/assas_app/about", 
                            active="exact",
                            style=nav_link_style(),
                            className="nav-link-modern"
                            )
                        ),
                    ], 
                    className="nav-items-container",
                    horizontal=True,
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "gap": "1rem",
                        "width": "100%",
                    })
                ],
                id="navbar-collapse",
                is_open=False,
                className="navbar-collapse-custom"
                ),
            ], 
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "width": "100%",
                "position": "relative",
            })
        ], fluid=True)
    ], style=bottom_row_style()),
    
    # Scroll progress indicator
    html.Div(id="scroll-progress", className="scroll-indicator"),
], 
id="main-navbar",
style=modern_navbar_style(),
className="navbar-two-row sticky-top"
)

def init_dashboard(server: object) -> object:
    """Create a Plotly Dash dashboard.

    Args:
        server: The Flask server instance to attach the Dash app to.

    """
    pages_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
    assets_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    logger.debug("pages folder %s, assets_folder %s" % (pages_folder, assets_folder))

    launch_uid = uuid.uuid4()

    ## Diskcache
    cache = diskcache.Cache("./cache")
    long_callback_manager = DiskcacheLongCallbackManager(
        cache,
        cache_by=[lambda: launch_uid],
        expire=60,
    )

    # Protect Dash pages
    @server.before_request
    @auth.login_required
    def restrict_access() -> Response:
        """Restrict access to Dash pages for unauthenticated users."""
        logger.info("Checking authentication for Dash app access.")
        currrent_user = get_current_user()
        logger.info(f"Current user: {currrent_user}")

        if not is_authenticated() and request.path.startswith("/assas_app/"):
            return redirect("/login")

    dash_app = dash.Dash(
        server=server,
        url_base_pathname="/assas_app/",
        title="ASSAS Data Hub",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"  # Font Awesome icons
        ],
        use_pages=True,
        pages_folder=pages_folder,
        assets_folder=assets_folder,
        long_callback_manager=long_callback_manager,
        suppress_callback_exceptions=True,
    )
    
    # Navbar toggle callback - WORKING BURGER MENU
    @dash_app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
        prevent_initial_call=True
    )
    def toggle_navbar_collapse(n_clicks, is_open):
        """Toggle the navbar collapse state."""
        if n_clicks:
            return not is_open
        return is_open

    # Simplified clientside callback for scroll behavior only
    dash_app.clientside_callback(
        """
        function(id) {
            let lastScrollTop = 0;
            let scrollTimeout;
            
            function handleScroll() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
                const scrollProgress = scrollTop / scrollHeight;
                
                const navbar = document.getElementById('main-navbar');
                const scrollIndicator = document.getElementById('scroll-progress');
                
                if (!navbar) return {};
                
                // Update scroll indicator
                if (scrollIndicator) {
                    scrollIndicator.style.transform = `scaleX(${scrollProgress})`;
                }
                
                // Determine scroll direction and distance
                const scrollDelta = scrollTop - lastScrollTop;
                const scrollDistance = Math.abs(scrollDelta);
                
                // Clear existing classes
                navbar.classList.remove('navbar-hidden', 'navbar-compact', 'navbar-visible');
                
                if (scrollTop === 0) {
                    // At top of page - show full navbar
                    navbar.classList.add('navbar-visible');
                    navbar.style.transform = 'translateY(0)';
                    navbar.style.opacity = '1';
                } else if (scrollDelta > 0 && scrollDistance > 10) {
                    // Scrolling down - hide navbar
                    if (scrollTop > 30) {
                        navbar.classList.add('navbar-hidden');
                        navbar.style.transform = 'translateY(-100%)';
                        navbar.style.opacity = '0';
                    } else {
                        navbar.classList.add('navbar-compact');
                        navbar.style.transform = 'translateY(0) scale(0.95)';
                        navbar.style.opacity = '0.9';
                    }
                } else if (scrollDelta < 0 && scrollDistance > 100) {
                    // Scrolling up - show compact navbar
                    navbar.classList.add('navbar-compact');
                    navbar.style.transform = 'translateY(0) scale(0.95)';
                    navbar.style.opacity = '0.9';
                } else if (scrollTop < 50) {
                    // Near top - show full navbar
                    navbar.classList.add('navbar-visible');
                    navbar.style.transform = 'translateY(0)';
                    navbar.style.opacity = '1';
                }
                
                lastScrollTop = scrollTop;
                
                // Clear scrolling state after delay
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    // Show navbar when stopped scrolling
                    if (!navbar.classList.contains('navbar-hidden')) {
                        navbar.classList.remove('navbar-compact');
                        navbar.classList.add('navbar-visible');
                        navbar.style.transform = 'translateY(0)';
                        navbar.style.opacity = '1';
                    }
                }, 150);
                
                return {};
            }
            
            // Throttled scroll handler
            let ticking = false;
            
            function requestTick() {
                if (!ticking) {
                    requestAnimationFrame(handleScroll);
                    ticking = true;
                    setTimeout(() => { ticking = false; }, 16); // ~60fps
                }
            }
            
            // Add scroll listener
            window.addEventListener('scroll', requestTick, { passive: true });
            
            // Show navbar on mouse movement near top
            document.addEventListener('mousemove', function(e) {
                if (navbar && e.clientY < 100 && window.pageYOffset > 100) {
                    navbar.classList.remove('navbar-hidden');
                    navbar.classList.add('navbar-compact');
                    navbar.style.transform = 'translateY(0) scale(0.95)';
                    navbar.style.opacity = '0.9';
                }
            });
            
            // Handle window resize
            window.addEventListener('resize', function() {
                if (navbar) {
                    // Reset navbar state on resize
                    navbar.classList.remove('navbar-hidden', 'navbar-compact');
                    navbar.classList.add('navbar-visible');
                    navbar.style.transform = 'translateY(0)';
                    navbar.style.opacity = '1';
                }
            });
            
            return {};
        }
        """,
        Output("scroll-progress", "style"),
        Input("main-navbar", "id"),
        prevent_initial_call=False
    )

    # Create Dash Layout with Footer
    dash_app.layout = html.Div(
        [
            navbar,
            # Main content wrapper
            html.Div([
                # Page content container
                html.Div(
                    dash.page_container,
                    style={
                        "minHeight": "calc(100vh - 160px - 200px)",  # Account for navbar and footer
                        "paddingTop": "160px",  # Space for fixed navbar
                        "paddingLeft": "1rem",
                        "paddingRight": "1rem",
                        "paddingBottom": "2rem",  # Space before footer
                    }
                ),
                # Footer
                footer
            ], style={
                "display": "flex",
                "flexDirection": "column",
                "minHeight": "100vh",
            })
        ], 
        id="dash-container",
        style={
            "fontFamily": "Arial, sans-serif",
            "backgroundColor": "#f8f9fa",
        }
    )

    return dash_app.server
