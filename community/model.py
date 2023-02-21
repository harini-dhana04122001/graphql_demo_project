from app import db


class Community(db.Model):
    __tablename__ = 'community'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, nullable=False)
    agent_name = db.Column(db.String, nullable=False)
    agent_contact = db.Column(db.String, nullable=False)
    building = db.relationship('Building', back_populates='community')

    def __init__(self, name, agent_name, agent_contact):
        self.name = name
        self.agent_name = agent_name
        self.agent_contact = agent_contact

    # def __repr__(self):
    #     return '' % self.title % self.description % self.year % self.author_id
