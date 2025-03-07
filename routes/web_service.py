from flask import Blueprint, jsonify

wsFactoraje_bp = Blueprint('wsFactoraje', __name__)

# Datos de ejemplo proporcionados
facturas = [
    {
        "id": "AL0008",
        "razon_social": "ENMANUEL S.A. DE C.V.",
        "nrc": "238413-2",
        "nit": "0614-271014-103-8",
        "correo_electronico": "test@gmail.com",
        "telefono": None,
        "id_fac": "1",
        "no_factura": "DTE-03M001P001-000000000000580",
        "Monto": "1806.870000",
        "Total Pagado": "0.000000",
        "fecha_emision": "2024-11-30 00:00:00.0000000",
        "fecha_vence": "2024-01-30 00:00:00.0000000"
    },
    {
        "id": "AL0008",
        "razon_social": "ENMANUEL S.A. DE C.V.",
        "nrc": "238413-2",
        "nit": "0614-271014-103-8",
        "correo_electronico": "test@gmail.com",
        "telefono": None,
        "id_fac": "2",
        "no_factura": "DTE-03-M001P001-0000000000000536",
        "Monto": "2529.620000",
        "Total Pagado": "0.000000",
        "fecha_emision": "2024-12-12 00:00:00.0000000",
        "fecha_vence": "2025-01-12 00:00:00.0000000"
    },
    {
        "id": "AL0008",
        "razon_social": "ENMANUEL S.A. DE C.V.",
        "nrc": "238413-2",
        "nit": "0614-271014-103-8",
        "correo_electronico": "test@gmail.com",
        "telefono": None,
        "id_fac": "3",
        "no_factura": "DTE-03-S002P001-240000000000872",
        "Monto": "7573.800000",
        "Total Pagado": "0.000000",
        "fecha_emision": "2024-12-07 00:00:00.0000000",
        "fecha_vence": "2025-01-30 00:00:00.0000000"
    },
    {
        "id": "AL0008",
        "razon_social": "ENMANUEL S.A. DE C.V.",
        "nrc": "238413-2",
        "nit": "0614-271014-103-8",
        "correo_electronico": "test@gmail.com",
        "telefono": None,
        "id_fac": "4",
        "no_factura": "DTE-03-M001P001-000000000000579",
        "Monto": "2529.620000",
        "Total Pagado": "0.000000",
        "fecha_emision": "2024-12-09 00:00:00.0000000",
        "fecha_vence": "2025-01-30 00:00:00.0000000"
    },
    {
        "id": "AL0008",
        "razon_social": "BRENNTAG EL SALVADOR, S.A. DE C.V.",
        "nrc": "262-3",
        "nit": "0614-150277-002-9",
        "correo_electronico": "test@gmail.com",
        "telefono": "2294-1877",
        "id_fac": "5",
        "no_factura": "DTE-03-M001P001-000000000002607",
        "Monto": "1345.490000",
        "Total Pagado": "0.000000",
        "fecha_emision": "2024-12-12 00:00:00.0000000",
        "fecha_vence": "2024-12-30 00:00:00.0000000"
    }
]


@wsFactoraje_bp.route('/', methods=['GET'])
def retornar_factura():
    return jsonify(facturas)