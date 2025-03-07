from utils.db import db

class Estado(db.Model):
    __tablename__ = 'estados'
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(255))
    clasificacion = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
