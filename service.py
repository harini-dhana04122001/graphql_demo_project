from app import db


def create_details(book):
    db.session.add(book)
    db.session.commit()
