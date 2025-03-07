from io import BytesIO
import pandas as pd
from utils.db import db
from models.solicitudes import Solicitud
from models.facturas import Factura
from models.proveedores_calificados import ProveedorCalificado
from models.parametros import Parametro
from flask import jsonify, send_file
import shutil
from datetime import datetime
from openpyxl import load_workbook
import os

def actualizar_solicitudes(lista_ids):
    """
    Actualiza el estado de solicitudes a 'Procesada' (id_estado = 4) solo si están en la lista de valores unicos recibida.
    """
    if not lista_ids or not isinstance(lista_ids, list):
        return None, "Debe proporcionar una lista de valores unicos válida"

    solicitudes_a_procesar = Solicitud.query.filter(Solicitud.id.in_(lista_ids), Solicitud.id_estado != 4).all()
    
    if not solicitudes_a_procesar:
        return None, "No se encontraron solicitudes para actualizar"

    for solicitud in solicitudes_a_procesar:
        solicitud.id_estado = 4
    
    db.session.commit()
    return print(f'Se procesaron:{len(solicitudes_a_procesar)} solicitudes.'), None  


def exportar_solicitudes(lista_ids, formato="excel", ruta_archivo_base="utils/plantilla_desembolsos.xlsx"):
    """
    Extrae la información de las solicitudes, copia un archivo base de Excel,
    inserta los datos en celdas específicas y devuelve el archivo generado.
    """
    ruta_archivo_base_absoluta = os.path.abspath(ruta_archivo_base)
    
    # Verificar si el archivo base existe
    if not os.path.exists(ruta_archivo_base_absoluta):
        return jsonify({"error": f"El archivo base no existe en la ruta: {ruta_archivo_base_absoluta}"}), 400
    
    # Imprimir la ruta absoluta para verificar
    print(f"Ruta absoluta del archivo base: {ruta_archivo_base_absoluta}")
    
    # Obtener el valor de la empresa desde la tabla parámetros
    empresa_parametro = db.session.query(Parametro.valor).filter(Parametro.clave == "NOM-EMPRESA").first()
    empresa = empresa_parametro.valor if empresa_parametro else "Desconocido"
    
    # Consulta a la base de datos
    query = db.session.query(
        Solicitud.total, 
        Factura.no_factura.label("numero_factura"), 
        Factura.monto.label("monto_factura"),
        Factura.fecha_emision.label("fecha_factura"),
        ProveedorCalificado.razon_social.label("nombre_proveedor"), 
        ProveedorCalificado.cuenta_bancaria.label("numero_cuenta_bancaria_proveedor"),
        ProveedorCalificado.correo_electronico.label("email_proveedor"),
        ProveedorCalificado.codigo_banco,
        ProveedorCalificado.nit.label("nit_proveedor"),
    ).join(Factura, Solicitud.id_factura == Factura.id)\
     .join(ProveedorCalificado, Factura.id_proveedor == ProveedorCalificado.id)\
     .filter(Solicitud.id.in_(lista_ids))

    resultados = query.all()
    
    # Extraer año, mes y día
    fecha_actual = datetime.now()
    año = fecha_actual.year
    mes = fecha_actual.month
    dia = fecha_actual.day
    descripcion = "Desembolso factoraje"

    # Definir el mapeo de columnas
    mapeo_columnas = {
        "numero_cuenta_bancaria_proveedor": 4,  # Columna D (4)
        "numero_registro": 5,  # Columna E (5) - AUTOINCREMENTAL
        "año": 6,  # Columna F (6)
        "mes": 7,  # Columna G (7)
        "dia": 8,  # Columna H (8)
        "total": 9,  # Columna I (9)
        "empresa": 11,  # Columna K (11)
        "nombre_proveedor": 13,  # Columna M (13)
        "codigo_banco": 15,  # Columna O (15)
        "descripcion": 16,  # Columna P (16)
        "nit_proveedor": 17,  # Columna Q (17)
    }

    # Crear una lista de datos en el orden del mapeo, agregando el número de registro
    data = [
        [
            r.numero_cuenta_bancaria_proveedor,
            index + 1,  # Número de registro autoincremental (Empieza en 1)
            año,  # Año actual
            mes,  # Mes actual
            dia,  # Día actual
            r.total, # Total de la solicitud
            empresa,  # Nombre de la empresa encargada del factoraje
            r.nombre_proveedor,  # Nombre del proveedor
            r.codigo_banco,  # Código del banco
            descripcion,  # Descripción del desembolso
            r.nit_proveedor,  # NIT del proveedor
        ]
        for index, r in enumerate(resultados)
    ]

    # Generar nombre del archivo basado en la fecha actual
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    nombre_archivo = f"Desembolsos_{fecha_actual}.xlsx"

    # Copiar el archivo base antes de modificarlo
    shutil.copy(ruta_archivo_base_absoluta, nombre_archivo)

    # Cargar la copia del archivo base y obtener la hoja activa
    libro = load_workbook(nombre_archivo)
    hoja = libro.active

    # Insertar los datos en la hoja de cálculo (empezando desde la fila 2)
    for i, fila in enumerate(data, start=1):  # Empieza desde la fila 1
        for clave, valor in zip(mapeo_columnas.keys(), fila):  
            columna = mapeo_columnas[clave]  # Obtener número de columna según el mapeo
            hoja.cell(row=i, column=columna, value=valor)

    # Guardar el archivo modificado
    libro.save(nombre_archivo)

    # 📌 Intentar enviar el archivo y eliminarlo después
    try:
        return send_file(nombre_archivo, as_attachment=True, download_name=nombre_archivo)
    finally:
        os.remove(nombre_archivo)  # Eliminar el archivo después de enviarlo
