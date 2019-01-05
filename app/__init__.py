from flask import Flask
from flask_bootstrap import Bootstrap


bootstrap = Bootstrap()

# app = Flask(__name__)
# app.config.from_object(Config)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    bootstrap.init_app(app)

    from app import routes, models
