from models.proveedores_calificados import ProveedorCalificado
from utils.db import db
from sqlalchemy.exc import IntegrityError
import re

def crear_proveedor(data):
     # Validaciones de datos
    validar_datos_proveedor(data)
    # Validar que el id, correo_electronico y cuenta_bancaria no existan
    if ProveedorCalificado.query.filter_by(id=data['id']).first():
        raise ValueError("El ID proveedor ya existe")
    if ProveedorCalificado.query.filter_by(correo_electronico=data['correo_electronico']).first():
        raise ValueError("El correo electrónico ya existe")
    if ProveedorCalificado.query.filter_by(cuenta_bancaria=data['cuenta_bancaria']).first():
        raise ValueError("El número de cuenta bancaria ya existe")

    # Crear el proveedor con todos los campos
    proveedor = ProveedorCalificado(
        id=data['id'],
        razon_social=data['razon_social'],
        nrc=data['nrc'],
        nit=data.get('nit'), 
        min_factoring=data.get('min_factoring'),  
        max_factoring=data.get('max_factoring'),  
        cuenta_bancaria=data['cuenta_bancaria'],
        nombre_contacto=data.get('nombre_contacto'),  
        correo_electronico=data['correo_electronico'],
        telefono=data.get('telefono'),  
        codigo_banco=data.get('codigo_banco', "0"),  
        banco=data.get('banco', 'Banco desconocido')  
    )
    db.session.add(proveedor)
    db.session.commit()
    return {
            "proveedor": {
                "id": proveedor.id,
                "razon_social": proveedor.razon_social,
                "nrc": proveedor.nrc,
                "nit": proveedor.nit,
                "correo_electronico": proveedor.correo_electronico,
                "cuenta_bancaria": proveedor.cuenta_bancaria,
                "min_factoring": float(proveedor.min_factoring) if proveedor.min_factoring else None,
                "max_factoring": float(proveedor.max_factoring) if proveedor.max_factoring else None,
                "banco": proveedor.banco,
                "codigo_banco": proveedor.codigo_banco,
                "nombre_contacto": proveedor.nombre_contacto,
                "telefono": proveedor.telefono,
                "created_at": proveedor.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": proveedor.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

def validar_datos_proveedor(data):
    """ Realiza validaciones sobre los datos del proveedor antes de crearlo. """
    # Campos obligatorios
    campos_obligatorios = ['id', 'razon_social', 'nrc', 'correo_electronico', 'cuenta_bancaria', 'banco', 'codigo_banco', 'nombre_contacto', 'nit', 'min_factoring', 'max_factoring']
    for campo in campos_obligatorios:
        if campo not in data or not data[campo]:
            raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío.")

    # Validación de formato de correo electrónico
    patron_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(patron_email, data['correo_electronico']):
        raise ValueError("El correo electrónico proporcionado no es válido.")

    # Validación de número de teléfono
    if 'telefono' in data and data['telefono']:
        patron_telefono = r'^\+?\d{8,15}$'  # Soporta números con + y mínimo 8 dígitos
        if not re.match(patron_telefono, data['telefono']):
            raise ValueError("El número de teléfono no es válido. Debe tener entre 8 y 15 dígitos.")

    # Validación de valores numéricos
    if 'min_factoring' in data and data['min_factoring'] is not None:
        try:
            if float(data['min_factoring']) < 0:
                raise ValueError("El valor mínimo de factoring no puede ser negativo.")
        except ValueError:
            raise ValueError("El campo 'min_factoring' debe ser un número válido.")

    if 'max_factoring' in data and data['max_factoring'] is not None:
        try:
            if float(data['max_factoring']) < 0:
                raise ValueError("El valor máximo de factoring no puede ser negativo.")
        except ValueError:
            raise ValueError("El campo 'max_factoring' debe ser un número válido.")

def obtener_proveedor_service(id):
    proveedor = ProveedorCalificado.query.get(id)
    if not proveedor:
        raise ValueError(f"No se encontró un proveedor con el ID: '{id}'.")

    return {
        "proveedor": {
            "id": proveedor.id,
            "razon_social": proveedor.razon_social,
            "nrc": proveedor.nrc,
            "nit": proveedor.nit,
            "correo_electronico": proveedor.correo_electronico,
            "cuenta_bancaria": proveedor.cuenta_bancaria,
            "min_factoring": float(proveedor.min_factoring) if proveedor.min_factoring else None,
            "max_factoring": float(proveedor.max_factoring) if proveedor.max_factoring else None,
            "banco": proveedor.banco,
            "codigo_banco": proveedor.codigo_banco,
            "nombre_contacto": proveedor.nombre_contacto,
            "telefono": proveedor.telefono,
            "created_at": proveedor.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": proveedor.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

def actualizar_proveedor(id, data):
    proveedor = ProveedorCalificado.query.get(id)
    if not proveedor:
        raise ValueError(f"No se encontró un proveedor con el ID '{id}'.")

    # Validar que el nuevo ID (si se proporciona) no esté en uso por otro proveedor
    nuevo_id = data.get('id')
    if nuevo_id and nuevo_id != id:
        if ProveedorCalificado.query.filter(ProveedorCalificado.id == nuevo_id).first():
            raise ValueError(f"El ID '{nuevo_id}' ya está en uso por otro proveedor.")

    # Validar que el correo electrónico y la cuenta bancaria no estén en uso por otro proveedor
    if 'correo_electronico' in data:
        if ProveedorCalificado.query.filter(
            ProveedorCalificado.correo_electronico == data['correo_electronico'],
            ProveedorCalificado.id != id
        ).first():
            raise ValueError("El correo electrónico ya está en uso por otro proveedor.")

    if 'cuenta_bancaria' in data:
        if ProveedorCalificado.query.filter(
            ProveedorCalificado.cuenta_bancaria == data['cuenta_bancaria'],
            ProveedorCalificado.id != id
        ).first():
            raise ValueError("El número de cuenta bancaria ya está en uso por otro proveedor.")

    # Campos permitidos para actualización
    campos_actualizables = [
        "id","razon_social", "nrc", "nit", "correo_electronico", "cuenta_bancaria",
        "min_factoring", "max_factoring", "banco", "codigo_banco",
        "nombre_contacto", "telefono"
    ]

    try:
        # Si el ID es diferente y válido, actualizarlo antes de cambiar otros campos
        if nuevo_id and nuevo_id != id:
            proveedor.id = nuevo_id

        # Actualizar solo los campos permitidos
        for key, value in data.items():
            if key in campos_actualizables:
                setattr(proveedor, key, value)

        db.session.commit()

        # Retornar la información actualizada en un formato JSON-friendly
        return {
            "proveedor": {
                "id": proveedor.id,
                "razon_social": proveedor.razon_social,
                "nrc": proveedor.nrc,
                "nit": proveedor.nit,
                "correo_electronico": proveedor.correo_electronico,
                "cuenta_bancaria": proveedor.cuenta_bancaria,
                "min_factoring": float(proveedor.min_factoring) if proveedor.min_factoring else None,
                "max_factoring": float(proveedor.max_factoring) if proveedor.max_factoring else None,
                "banco": proveedor.banco,
                "codigo_banco": proveedor.codigo_banco,
                "nombre_contacto": proveedor.nombre_contacto,
                "telefono": proveedor.telefono,
                "created_at": proveedor.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": proveedor.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Error de integridad en la base de datos. Verifique que los valores sean únicos y válidos.")
    
    except Exception as e:
        db.session.rollback()
        raise ValueError("Ha ocurrido un error inesperado al intentar actualizar el proveedor.")
    
def eliminar_proveedor(id):
    proveedor = ProveedorCalificado.query.get(id)
    if not proveedor:
        raise ValueError(f"No se encontró un proveedor con el ID '{id}'.")

    try:
        db.session.delete(proveedor)
        db.session.commit()
    
    except IntegrityError:
        db.session.rollback()
        raise ValueError("No se puede eliminar el proveedor debido a restricciones en la base de datos.")
    
    except Exception as e:
        db.session.rollback()
        raise ValueError("Ha ocurrido un error inesperado al intentar eliminar el proveedor.")
    
