from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_mptt.mixins import BaseNestedSets
from app import app
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy(app)


class Category(db.Model, BaseNestedSets):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), index=True)
    hash = db.Column(db.String(32), index=True)
    parent_hash = db.Column(db.String(32), index=True)

    def __repr__(self):
        return '<Category {}>'.format(self.name)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)  # - первичный ключ
    sku = db.Column(db.String(50))
    category_f = db.Column(db.String(200))
    name = db.Column(db.String(200))
    title = db.Column(db.Text)
    specifications = db.Column(JSONB, server_default="{}")
    price = db.Column(db.String(20))
    priceCurrency = db.Column(db.String(10))
    url = db.Column(db.String(200))
    details = db.Column(db.Text)
    imgs = db.Column(db.Text)
    descr = db.Column(db.Text)
    hash = db.Column(db.String(32))

    id_cat = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category', backref='products')

    # конструктор
    def __init__(self, sku, category_f, name, title, specifications, price, priceCurrency, url, details, imgs, descr,
                 hash):
        self.sku = sku
        self.category_f = category_f
        self.name = name
        self.title = title
        self.specifications = specifications
        self.price = price
        self.priceCurrency = priceCurrency
        self.url = url
        self.details = details
        self.imgs = imgs
        self.descr = descr
        self.hash = hash

    def __repr__(self):
        return '<Product {}>'.format(self.name)


db.create_all()