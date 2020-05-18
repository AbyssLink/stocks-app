from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Data model for user accounts."""

    # as_dict: make object Serialization
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __repr__(self):
        return f'<User {self.username}>'


class News(db.Model):
    """Data model for News."""

    # as_dict: make object Serialization
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img = db.Column(db.String(512))
    title = db.Column(db.String(512))
    description = db.Column(db.String(512))
    link = db.Column(db.String(512))
    date = db.Column(db.String(512))

    def __repr__(self):
        return f'<News {self.title}>'
