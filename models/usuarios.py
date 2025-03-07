from utils.db import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(255), nullable=False)  
    apellidos = db.Column(db.String(255), nullable=False)  
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=True)
    temp_password = db.Column(db.String(255))
    cargo = db.Column(db.String(255))
    token = db.Column(db.String(255))
    token_date_end = db.Column(db.DateTime)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete="SET NULL", onupdate="CASCADE"))
    rol = db.relationship('Rol', backref='usuarios')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    activo = db.Column(db.Boolean, default=True, nullable=False)  
    reg_activo = db.Column(db.Boolean, default=True, nullable=False)  
    
    # Relación con el modelo Rol
    rol = db.relationship('Rol', backref='usuarios', lazy='joined')
