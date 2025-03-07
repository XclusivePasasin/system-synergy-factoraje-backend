from utils.db import db

class Desembolso(db.Model):
    __tablename__ = 'desembolsos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_desembolso = db.Column(db.DateTime, nullable=False)
    monto_final = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(255))
    cuenta_bancaria = db.Column(db.String(255))
    no_transaccion = db.Column(db.String(255))
    estado = db.Column(db.String(50))
    id_solicitud = db.Column(db.Integer, db.ForeignKey('solicitudes.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    solicitud = db.relationship('Solicitud', backref='desembolsos')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
