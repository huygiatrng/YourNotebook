from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class ImageToRemoveBackground(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_location = db.Column(db.String(150), nullable=False)
    output_location = db.Column(db.String(150), nullable=False)
    input_img_name = db.Column(db.String(150), nullable=False)
    output_img_name = db.Column(db.String(150), nullable=False)
    mimetype = db.Column(db.Text, nullable = False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_location = db.Column(db.String(150), nullable=False)
    img_path = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    pages = db.relationship('Page')
    images = db.relationship('Image')
