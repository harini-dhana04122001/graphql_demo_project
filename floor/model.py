from app import db


class Floor(db.Model):
    __tablename__ = 'floor'

    id = db.Column(db.Integer, primary_key=True)
    floor_name = db.Column(db.String(4), index=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    unit = db.relationship('Unit', back_populates='floor')
    building = db.relationship('Building', back_populates='floor', lazy='subquery')

    def __init__(self, id, floor_name=None, building_id=None):
        self.id = id
        self.floor_name = floor_name
        self.building_id = building_id
