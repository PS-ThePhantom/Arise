import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_profiler

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, '..', 'static'),
        template_folder=os.path.join(base_dir, '..', 'templates')
    )

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "testDB")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "testPW")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["flask_profiler"] = {
        "enabled": False,
        "storage": {
            "engine": "mongodb",
            "MONGO_URL": "mongodb://mongo:27017/flask_profiler"
        },
        "basicAuth": {
            "enabled": True,
            "username": os.getenv("PROFILER_USERNAME", "admin"),
            "password": os.getenv("PROFILER_PASSWORD", "admin")
        },
        "ignore": [
            "^/static/.*"
        ]
    }

    db.init_app(app)
    migrate.init_app(app, db)

    

    from .services.db import models
    from .main_routes import main_routes
    from .api_routes import api_routes

    app.register_blueprint(main_routes)
    app.register_blueprint(api_routes, url_prefix='/api')

    if os.getenv("ENABLE_PROFILER", "false").lower() == "true":
        flask_profiler.init_app(app)
        
    return app