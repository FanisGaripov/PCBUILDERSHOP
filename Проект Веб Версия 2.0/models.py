from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

#manufacturer_items = db.Table('manufacturer_items',
    #.Column('manufacturer_id', db.Integer, db.ForeignKey('manufacturer.id'), primary_key=True),
    #db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True)
#)


class Manufacturer_items(db.Model):
    __tablename__ = "manufacturer_items"
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)

    def __repr__(self):
        return '<Manufacturer_items %r>' % self.name


class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    items = db.relationship('Item', secondary='manufacturer_items', backref=db.backref('manufacturers', lazy=True))

    def __repr__(self):
        return '<Manufacturer %r>' % self.name

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    items = db.relationship('Item', backref='category')

    def __repr__(self):
        return '<Category %r>' % self.name

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<Item %r>' % self.name


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    pokupki = db.Column(db.Integer, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)