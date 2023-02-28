from app import db


class Building(db.Model):
    __tablename__ = 'building'

    id = db.Column(db.Integer, primary_key=True)
    block_name = db.Column(db.String(256), index=True, nullable=False)
    community_id = db.Column(db.Integer(), db.ForeignKey('community.id'), nullable=False)
    floor = db.relationship('Floor', back_populates='building')
    community = db.relationship('Community', back_populates='building', lazy='subquery')

    def __init__(self, id, block_name=None, community_id=None):
        self.id = id
        self.block_name = block_name
        self.community_id = community_id
