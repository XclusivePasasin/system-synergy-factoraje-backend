from utils.db import db

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.Text, nullable=False)
    id_solicitud = db.Column(db.Integer, db.ForeignKey('solicitudes.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_factura = db.Column(db.Integer, db.ForeignKey('facturas.id', ondelete="SET NULL", onupdate="CASCADE"))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
