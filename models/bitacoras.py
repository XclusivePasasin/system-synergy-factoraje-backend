from utils.db import db

class Bitacora(db.Model):
    __tablename__ = 'bitacoras'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(255))
    modulo = db.Column(db.String(255))
    accion = db.Column(db.String(255))
    detalle = db.Column(db.Text)
    exito = db.Column(db.Boolean, default=False)
    tipo = db.Column(db.Enum('bitacora', 'alerta'))
    fecha = db.Column(db.DateTime)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete="SET NULL", onupdate="CASCADE"))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
