from utils.db import db

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
