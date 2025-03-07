from config import db

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    no_factura = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False)
    fecha_vence = db.Column(db.DateTime, nullable=False)
    fecha_otorga = db.Column(db.DateTime, nullable=False)
    dias_credito = db.Column(db.Integer, nullable=False)
    nombre_proveedor = db.Column(db.String(255))
    nit = db.Column(db.String(50))
    noti_cliente = db.Column(db.String(1), default='N', nullable=False)  
    noti_contador = db.Column(db.String(1), default='N', nullable=False)  
    factura_hash = db.Column(db.String(255), nullable=False)
    id_proveedor = db.Column(db.String(50), db.ForeignKey('proveedores_calificados.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    proveedor = db.relationship('ProveedorCalificado', backref='facturas')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class ProveedorCalificado(db.Model):
    __tablename__ = 'proveedores_calificados'
    id = db.Column(db.String(50), primary_key=True)
    razon_social = db.Column(db.String(255), nullable=False)
    nrc = db.Column(db.String(50), nullable=False)
    nit = db.Column(db.String(50))
    min_factoring = db.Column(db.Numeric(10, 2))
    max_factoring = db.Column(db.Numeric(10, 2))
    cuenta_bancaria = db.Column(db.String(255))
    nombre_contacto = db.Column(db.String(255))
    correo_electronico = db.Column(db.String(255))
    telefono = db.Column(db.String(50))
    codigo_banco = db.Column(db.String(20), nullable=False, default="0")
    banco = db.Column(db.String(100), default='Banco desconocido')  
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
