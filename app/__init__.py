import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from .config import config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    # Register Blueprints
    from .users import users_bp
    app.register_blueprint(users_bp)

    from .products import products_bp
    app.register_blueprint(products_bp)

    from .posts import post_bp
    app.register_blueprint(post_bp, url_prefix="/post")

    from .views import register_routes
    register_routes(app)

    return app


app = create_app()
