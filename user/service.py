from app import db
from user.model import User


def create_user_details(username, email):
    db.session.add(User(username, email))
    db.session.commit()
