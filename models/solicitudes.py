from utils.db import db

class Solicitud(db.Model):
    __tablename__ = 'solicitudes'
    id = db.Column(db.Integer, primary_key=True)
    nombre_cliente = db.Column(db.String(255), nullable=False)
    contacto = db.Column(db.String(255))
    email = db.Column(db.String(255))
    descuento_app = db.Column(db.Numeric(10, 2))
    cargo = db.Column(db.String(255))
    iva = db.Column(db.Numeric(10, 2))
    subtotal = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    fecha_solicitud = db.Column(db.DateTime)
    fecha_aprobacion = db.Column(db.DateTime)
    id_estado = db.Column(db.Integer, db.ForeignKey('estados.id', ondelete="SET NULL", onupdate="CASCADE"))
    id_factura = db.Column(db.Integer, db.ForeignKey('facturas.id', ondelete="SET NULL", onupdate="CASCADE"))
    id_aprobador = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete="SET NULL", onupdate="CASCADE"))
    estado = db.relationship('Estado', backref='solicitudes')
    factura = db.relationship('Factura', backref='solicitudes')
    aprobador = db.relationship('Usuario', backref='solicitudes_aprobadas')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
