from db import db
import datetime

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    dept_id = db.Column(db.Integer)
    date_added = db.Column(db.Date)
    login_ip = db.Column(db.String(20))

    def __init__(self, username, dept_id, login_ip):
        self.username = username
        self.dept_id = dept_id
        self.login_ip = login_ip
        self.date_added = datetime.datetime.utcnow()

    def json(self):
        return {
            'id': self.id, 
            'name': self.name,
            }

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
