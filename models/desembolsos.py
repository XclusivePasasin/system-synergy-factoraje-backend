from utils.db import db

class Desembolso(db.Model):
    __tablename__ = 'desembolsos'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_desembolso = db.Column(db.DateTime, nullable=False)
    monto_final = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.String(255))
    cuenta_bancaria = db.Column(db.String(255))
    no_transaccion = db.Column(db.String(255))
    # Cambiamos el tipo de 'estado' a Integer y lo relacionamos con la tabla 'estados'
    estado = db.Column(db.Integer, db.ForeignKey('estados.id', ondelete="SET NULL", onupdate="CASCADE"))
    # Relación con la tabla 'estados'
    estado_relacion = db.relationship('Estado', backref='desembolsos')
    id_solicitud = db.Column(db.Integer, db.ForeignKey('solicitudes.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    solicitud = db.relationship('Solicitud', backref='desembolsos')
    # Agregamos el nuevo campo 'descripcion'
    descripcion = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())