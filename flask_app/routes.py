"""Routes for parent Flask app."""
import datetime
from flask import render_template
from flask import current_app as app

@app.route('/')
def home():
    """Landing page."""
    return render_template('index.html',
        utc_dt=datetime.datetime.utcnow(),
        title='Plotly Dash Flask Tutorial',
        description='Embed Plotly Dash into your Flask applications.',
        template='home-template',
        body="This is a homepage served with Flask."
    )