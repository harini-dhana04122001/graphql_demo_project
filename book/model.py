from app import db


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title, description, year, author_id):
        self.title = title
        self.description = description
        self.year = year
        self.author_id = author_id

    # def __repr__(self):
    #     return '' % self.title % self.description % self.year % self.author_id
