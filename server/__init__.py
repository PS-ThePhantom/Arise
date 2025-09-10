import os
from flask import Flask

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, '..', 'static'),
        template_folder=os.path.join(base_dir, '..', 'templates')
    )

    from .main_routes import main_routes
    from .api_routes import api_routes

    app.register_blueprint(main_routes)
    app.register_blueprint(api_routes, url_prefix='/api')

    return app