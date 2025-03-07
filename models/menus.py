from utils.db import db

class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    menu = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    path = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    orden = db.Column(db.Float)
    padre = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
