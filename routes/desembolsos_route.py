from flask import Blueprint, request
from sqlalchemy import or_, and_
from utils.db import db
from utils.response import response_success, response_error
from models.solicitudes import Solicitud
from models.desembolsos import Desembolso
from models.facturas import Factura
from models.proveedores_calificados import ProveedorCalificado
from models.estados import Estado
from utils.interceptor import token_required

desembolsos_bp = Blueprint('desembolso', __name__)

@desembolsos_bp.route('/obtener-desembolsos', methods=['GET'])
@token_required
def obtener_desembolsos():
    try:
        # Recuperar parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        fecha_inicio = request.args.get('fecha_inicio', type=str)
        fecha_fin = request.args.get('fecha_fin', type=str)
        estado = request.args.get('estado', type=str)
        proveedor = request.args.get('proveedor', type=str)

        # Construcción de filtros dinámicos
        query = Desembolso.query.join(Solicitud).join(Factura).join(ProveedorCalificado).join(Solicitud.estado)

        if fecha_inicio and fecha_fin:
            query = query.filter(Desembolso.fecha_desembolso.between(fecha_inicio, fecha_fin))
        if estado:
            query = query.filter(Desembolso.estado.ilike(f"%{estado}%"))
        if proveedor:
            query = query.filter(
                or_(
                    ProveedorCalificado.razon_social.ilike(f"%{proveedor}%"),
                    ProveedorCalificado.correo_electronico.ilike(f"%{proveedor}%"),
                    ProveedorCalificado.nrc.ilike(f"%{proveedor}%"),
                    ProveedorCalificado.telefono.ilike(f"%{proveedor}%")
                )
            )

        # Aplicar paginación
        paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)
        desembolsos = paginated_query.items

        # Construir la respuesta
        response_data = {
            "current_page": paginated_query.page,
            "per_page": paginated_query.per_page,
            "total_pages": paginated_query.pages,
            "desembolsos": [
                {
                    "id": desembolso.id,
                    "fecha_desembolso": desembolso.fecha_desembolso.isoformat(),
                    "monto_final": float(desembolso.monto_final),
                    "metodo_pago": desembolso.metodo_pago,
                    "estado": desembolso.estado,
                    "solicitud": {
                        "id": desembolso.solicitud.id,
                        "nombre_cliente": desembolso.solicitud.nombre_cliente,
                        "contacto": desembolso.solicitud.contacto,
                        "email": desembolso.solicitud.email,
                        "iva": float(desembolso.solicitud.iva),
                        "subtotal": float(desembolso.solicitud.subtotal),
                        "total": float(desembolso.solicitud.total),
                        "id_estado": desembolso.solicitud.id_estado,
                        "estado": desembolso.solicitud.estado.clave if desembolso.solicitud.estado else None,
                        "factura": {
                            "id": desembolso.solicitud.factura.id,
                            "no_factura": desembolso.solicitud.factura.no_factura,
                            "monto": float(desembolso.solicitud.factura.monto),
                            "fecha_emision": desembolso.solicitud.factura.fecha_emision.isoformat(),
                            "fecha_vence": desembolso.solicitud.factura.fecha_vence.isoformat(),
                            "proveedor": {
                                "id": desembolso.solicitud.factura.proveedor.id,
                                "razon_social": desembolso.solicitud.factura.proveedor.razon_social,
                                "correo_electronico": desembolso.solicitud.factura.proveedor.correo_electronico,
                                "telefono": desembolso.solicitud.factura.proveedor.telefono
                            }
                        }
                    }
                } for desembolso in desembolsos
            ]
        }

        return response_success(response_data, "Consulta exitosa")

    except Exception as e:
        return response_error(f"Error al consultar desembolsos: {str(e)}", http_status=500)
    
@desembolsos_bp.route('/detalle-desembolso', methods=['GET'])
@token_required
def obtener_detalle_desembolso():
    try:
        # Recuperar el ID del desembolso desde los parámetros de consulta
        desembolso_id = request.args.get('desembolso_id', type=int)
        
        if not desembolso_id:
            return response_error("El parámetro 'desembolso_id' es requerido", http_status=400)

        # Realizar la consulta con los joins necesarios
        desembolso = db.session.query(
            Desembolso.id,
            Desembolso.fecha_desembolso,
            Desembolso.monto_final,
            Desembolso.metodo_pago,
            Desembolso.no_transaccion,
            Desembolso.estado,
            ProveedorCalificado.id.label('proveedor_id'),
            ProveedorCalificado.razon_social,
            ProveedorCalificado.correo_electronico,
            ProveedorCalificado.telefono
        ).join(
            Solicitud, Desembolso.id_solicitud == Solicitud.id
        ).join(
            Factura, Solicitud.id_factura == Factura.id
        ).join(
            ProveedorCalificado, Factura.id_proveedor == ProveedorCalificado.id
        ).filter(
            Desembolso.id == desembolso_id
        ).first()

        # Verificar si el desembolso fue encontrado
        if not desembolso:
            return response_error("Desembolso no encontrado para el ID indicado", http_status=404)

        # Construir la respuesta con los datos obtenidos
        response_data = {
            "desembolso": {
                "id": desembolso.id,
                "fecha_desembolso": desembolso.fecha_desembolso.isoformat(),
                "monto_final": float(desembolso.monto_final),
                "metodo_pago": desembolso.metodo_pago,
                "no_transaccion": desembolso.no_transaccion,
                "estado": desembolso.estado,
                "proveedor": {
                    "id": desembolso.proveedor_id,
                    "razon_social": desembolso.razon_social,
                    "correo_electronico": desembolso.correo_electronico,
                    "telefono": desembolso.telefono
                }
            }
        }

        return response_success(response_data, "Consulta exitosa")

    except Exception as e:
        return response_error(f"Error al obtener el detalle del desembolso: {str(e)}", http_status=500)

    