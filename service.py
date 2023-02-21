from app import db


def create_details(details):
    db.session.add(details)
    db.session.commit()

def update_details():
    db.session.commit()
