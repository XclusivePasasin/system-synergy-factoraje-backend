from flask import Blueprint, request
from services.proveedores_service import *
from utils.response import response_success, response_error
from utils.interceptor import token_required
import logging

proveedor_bp = Blueprint('proveedor', __name__)

@proveedor_bp.route('/registrar-proveedor', methods=['POST'])
@token_required
def registrar_proveedor():
    try:
        data = request.get_json()
        if not data:
            return response_error("El cuerpo de la solicitud está vacío", http_status=400)

        # Validación de campos obligatorios
        campos_obligatorios = [
            'id', 'razon_social', 'nrc', 'nit', 'correo_electronico', 'cuenta_bancaria', 'min_factoring', 'max_factoring', 'banco', 'codigo_banco', 'nombre_contacto', 'telefono'
        ]
        faltantes = [campo for campo in campos_obligatorios if campo not in data]
        if faltantes:
            return response_error(f"Faltan los campos obligatorios: {', '.join(faltantes)}", http_status=400)

        # Llamar al servicio
        proveedor = crear_proveedor(data)
        return response_success(proveedor, "Proveedor creado exitosamente")

    except ValueError as e:
        return response_error(str(e), http_status=400)
    except Exception as e:
        return response_error("Error interno del servidor", http_status=500)

@proveedor_bp.route('/obtener-proveedor', methods=['GET'])
@token_required
def obtener_proveedor():
    try:
        id = request.args.get('id')  # Obtener ID desde query param
        
        if not id:
            return response_error("El ID del proveedor es obligatorio como query param (?id=...)", http_status=400)

        proveedor = obtener_proveedor_service(id)
        return response_success(proveedor, "Proveedor obtenido exitosamente")

    except ValueError as e:
        logging.warning(f"Error de validación al obtener proveedor: {e}")
        return response_error(str(e), http_status=404)

    except Exception as e:
        logging.error(f"Error inesperado al obtener proveedor: {e}", exc_info=True)
        return response_error("Error interno del servidor", http_status=500)
    
@proveedor_bp.route('/actualizar-proveedor', methods=['PUT'])
@token_required
def modificar_proveedor():
    try:
        id = request.args.get('id')  
        
        if not id:
            return response_error("El ID del proveedor es obligatorio como query param (?id=...)", http_status=400)

        data = request.get_json()
        if not data:
            return response_error("El cuerpo de la solicitud está vacío", http_status=400)

        proveedor_actualizado = actualizar_proveedor(id, data)
        return response_success(proveedor_actualizado, "Proveedor actualizado exitosamente")

    except ValueError as e:
        return response_error(str(e), http_status=400)

    except Exception as e:
        return response_error("Error interno del servidor", http_status=500)
    
@proveedor_bp.route('/eliminar-proveedor', methods=['DELETE'])
@token_required
def suprimir_proveedor():
    try:
        id = request.args.get('id')  # Obtener ID desde query param

        if not id:
            return response_error("El ID del proveedor es obligatorio como query param (?id=...)", http_status=400)

        eliminar_proveedor(id)
        return response_success(None, "Proveedor eliminado exitosamente")

    except ValueError as e:
        logging.warning(f"Error de validación al eliminar proveedor: {e}")
        return response_error(str(e), http_status=404)

    except Exception as e:
        logging.error(f"Error inesperado al eliminar proveedor: {e}", exc_info=True)
        return response_error("Error interno del servidor", http_status=500)

@proveedor_bp.route('/listar-proveedores', methods=['GET'])
@token_required
def obtener_proveedores():
    try:
        # Obtener los parámetros de consulta
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        razon_social = request.args.get('razon_social')
        nrc = request.args.get('nrc')
        nit = request.args.get('nit')
        correo_electronico = request.args.get('correo_electronico')
        cuenta_bancaria = request.args.get('cuenta_bancaria')
        banco = request.args.get('banco')
        nombre_contacto = request.args.get('nombre_contacto')
        telefono = request.args.get('telefono')

        # Construir la consulta base
        query = ProveedorCalificado.query

        # Aplicar filtros opcionales
        if razon_social:
            query = query.filter(ProveedorCalificado.razon_social.ilike(f"%{razon_social}%"))
        if nrc:
            query = query.filter(ProveedorCalificado.nrc.ilike(f"%{nrc}%"))
        if nit:
            query = query.filter(ProveedorCalificado.nit.ilike(f"%{nit}%"))
        if correo_electronico:
            query = query.filter(ProveedorCalificado.correo_electronico.ilike(f"%{correo_electronico}%"))
        if cuenta_bancaria:
            query = query.filter(ProveedorCalificado.cuenta_bancaria.ilike(f"%{cuenta_bancaria}%"))
        if banco:
            query = query.filter(ProveedorCalificado.banco.ilike(f"%{banco}%"))
        if nombre_contacto:
            query = query.filter(ProveedorCalificado.nombre_contacto.ilike(f"%{nombre_contacto}%"))
        if telefono:
            query = query.filter(ProveedorCalificado.telefono.ilike(f"%{telefono}%"))

        # Obtener el total de proveedores antes de la paginación
        total_proveedores = query.count()

        # Aplicar paginación
        proveedores = query.offset((page - 1) * per_page).limit(per_page).all()

        # Construir la respuesta
        response_data = {
            "current_page": page,
            "per_page": per_page,
            "total_pages": (total_proveedores + per_page - 1) // per_page,
            "proveedores": [
                {
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
                for proveedor in proveedores
            ]
        }

        return response_success(response_data, "Lista de proveedores obtenida exitosamente")

    except Exception as e:
        logging.error(f"Error inesperado al listar proveedores: {e}", exc_info=True)
        return response_error("Error interno del servidor", http_status=500)