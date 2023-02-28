from app import db


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, username, password, refresh_token):
        self.username = username
        self.password = password
        self.refresh_token = refresh_token


class PermissionField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    field = db.Column(db.String, nullable=False)
    access_type = db.Column(db.String, nullable=False)

    def __init__(self, permission_id, model, field, access_type):
        self.permission_id = permission_id
        self.model = model
        self.field = field
        self.access_type = access_type
