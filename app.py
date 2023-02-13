import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
    db.init_app(app)

    from book.views import display as book_display
    from user.views import display as user_display

    app.register_blueprint(book_display, name='book_display', url_prefix='/book')
    app.register_blueprint(user_display, name='user_display', url_prefix='/users')

    with app.app_context():
        db.create_all()
        return app


