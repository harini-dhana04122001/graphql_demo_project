from app import db


class Unit(db.Model):
    __tablename__ = 'unit'

    id = db.Column(db.Integer, primary_key=True)
    unit_number = db.Column(db.String(4), index=True, nullable=False)
    floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'), nullable=False)
    floor = db.relationship('Floor', back_populates='unit', lazy='subquery')

    def __init__(self, unit_number=None, floor_id=None):
        self.unit_number = unit_number
        self.floor_id = floor_id