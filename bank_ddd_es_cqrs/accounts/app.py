from flask import Flask
from flask_cors import CORS  # type: ignore
from .api import account_blueprint
from .event_handlers import register_event_handlers
from .infrastructure import event_store_db
from .composition_root import event_manager


def account_app_factory(db_string: str):
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    event_store_db.init_app(app)
    app.register_blueprint(account_blueprint)

    register_event_handlers(event_manager)

    return app

