from app import db


class Floor(db.Model):
    __tablename__ = 'floor'

    id = db.Column(db.Integer, primary_key=True)
    floor_name = db.Column(db.String(4), index=True, nullable=False)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    building = db.relationship('Building', back_populates='floor')

    def __init__(self, floor_name, building_id):
        self.floor_name = floor_name
        self.building_id = building_id
