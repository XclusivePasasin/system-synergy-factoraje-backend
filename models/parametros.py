from utils.db import db

class Parametro(db.Model):
    __tablename__ = 'parametros'
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
