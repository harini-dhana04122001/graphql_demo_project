from app import db


class Community(db.Model):
    __tablename__ = 'community'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    agent_name = db.Column(db.String)
    agent_contact = db.Column(db.String)
    building = db.relationship('Building', back_populates='community', lazy='subquery')

    def __init__(self, id, name=None, agent_name=None, agent_contact=None):
        self.id = id
        self.name = name
        self.agent_name = agent_name
        self.agent_contact = agent_contact

    # def __repr__(self):
    #     return '' % self.title % self.description % self.year % self.author_id
