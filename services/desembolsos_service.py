from models.desembolsos import Desembolso
from sqlalchemy import or_, and_
from utils.db import db
from datetime import datetime
from sqlalchemy import func



def procesar_txt_desembolsos(txt_content):
    # Normalizar saltos de línea y dividir contenido
    lines = [line.strip() for line in txt_content.replace('\r\n', '\n').replace('\r', '\n').split('\n') if line.strip()]
    
    resultado = {
        "encabezado": {},
        "transacciones": [],
        "actualizados": 0
    }

    # Procesar encabezado básico
    for line in lines:
        if "Consulta del detalle del env" in line:
            parts = [p for p in line.split(' ') if p]
            if len(parts) >= 12:
                resultado["encabezado"].update({
                    "numero_envio": parts[5],
                    "plan": parts[8],
                    "cuenta": parts[11]
                })
        elif "(GMT-" in line:
            resultado["encabezado"]["fecha_consulta"] = line.strip()

    # Procesar tabla de resumen
    for i, line in enumerate(lines):
        if "|N" in line and "mero de pl|" in line:  # Detectar encabezado de tabla
            # Buscar la línea de datos (2 líneas después del encabezado)
            if i + 2 < len(lines) and "|" in lines[i+2]:
                data_line = lines[i+2]
                parts = [p.strip() for p in data_line.split('|') if p.strip()]
                if len(parts) >= 8:
                    resultado["encabezado"].update({
                        "numero_plan": parts[0],
                        "numero_envio": parts[1],
                        "monto": parts[2],
                        "impuesto": parts[3],
                        "total": parts[4],
                        "registros": parts[5],
                        "fecha_hora_pago": parts[6],
                        "estado": parts[7]
                    })

    # Procesar transacciones y actualizar desembolsos
    for i, line in enumerate(lines):
        if "Transacciones del env" in line:
            # Buscar el inicio de la tabla de transacciones
            for j in range(i, len(lines)):
                if "|Referencia" in lines[j]:
                    # Procesar desde j+2 hasta la próxima línea divisoria
                    k = j + 2
                    while k < len(lines) and not lines[k].startswith("----"):
                        if "|" in lines[k]:
                            parts = [p.strip() for p in lines[k].split('|') if p.strip()]
                            if len(parts) >= 11:
                                try:
                                    # Usar el monto (parts[4]) en lugar del total para la comparación
                                    monto = float(parts[4].replace('USD', '').replace(',', '').strip())
                                    total = float(parts[6].replace('USD', '').replace(',', '').strip())
                                    impuesto = float(parts[5].replace('USD', '').replace(',', '').strip())
                                except:
                                    monto = 0.0
                                    total = 0.0
                                    impuesto = 0.0
                                
                                try:
                                    fecha_pago = datetime.strptime(parts[7], '%d/%m/%Y %I:%M %p')
                                except:
                                    fecha_pago = None
                                
                                transaccion = {
                                    "referencia": parts[0],
                                    "no_cuenta_proveedor": parts[1],
                                    "nombre_en_archivo": parts[2],
                                    "nombre_cuentahabiente": parts[3],
                                    "monto": monto,
                                    "impuesto": impuesto,
                                    "total": total,
                                    "fecha_hora_pago": fecha_pago,
                                    "factura": parts[8],
                                    "descripcion": parts[9],
                                    "estado": parts[10]
                                }
                                
                                # Buscar y actualizar desembolsos coincidentes
                                desembolso = Desembolso.query.filter(
                                    and_(
                                        func.lower(Desembolso.descripcion) == func.lower(parts[9]),
                                        Desembolso.monto_final == monto,  # Comparar con el monto, no con el total
                                        Desembolso.cuenta_bancaria == parts[1]
                                    )
                                ).first()
                                
                                if desembolso:
                                    desembolso.estado = 6  # ID del estado a actualizar
                                    desembolso.no_transaccion = parts[0]
                                    if fecha_pago:
                                        desembolso.fecha_desembolso = fecha_pago
                                    db.session.commit()
                                    resultado["actualizados"] += 1
                                
                                resultado["transacciones"].append(transaccion)
                        k += 1
                    break
            break

    return resultado