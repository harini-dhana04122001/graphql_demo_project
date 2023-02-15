from app import db


class Building(db.Model):
    __tablename__ = 'building'

    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(256), index=True, nullable=False)
    community_id = db.Column(db.Integer(), db.ForeignKey('community.id'), nullable=False)
    floor = db.relationship('Floor', backref='building', lazy=True)

    def __init__(self, name, community_id):
        self.block_name = name
        self.community_id = community_id
