import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_graphql_auth import GraphQLAuth

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
    app.config['ACCESS_EXP_LENGTH'] = 30
    app.config['REFRESH_EXP_LENGTH'] = 30
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
    auth = GraphQLAuth(app)
    db.init_app(app)

    from views import display

    app.register_blueprint(display, url_prefix='/main-view')

    with app.app_context():
        db.create_all()
        return app


