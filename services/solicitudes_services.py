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
from jinja2 import Environment, FileSystemLoader
import pdfkit
from io import BytesIO

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
    mes = str(fecha_actual.month).zfill(2)
    dia = str(fecha_actual.day).zfill(2)
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
            int(str(r.total).replace('.', '')), # Total de la solicitud sin punto decimal
            empresa,  # Nombre de la empresa encargada del factoraje
            r.nombre_proveedor,  # Nombre del proveedor
            r.codigo_banco,  # Código del banco
            descripcion,  # Descripción del desembolso
            r.nit_proveedor,  # NIT del proveedor
        ]
        for index, r in enumerate(resultados)
    ]

    # Generar nombre del archivo basado en la fecha actual
    fecha_actual = datetime.now().strftime("%d-%m-%Y")
    nombre_base = f"Desembolsos_{fecha_actual}"
    
    # Intentar diferentes nombres de archivo si el original está en uso
    contador = 0
    while True:
        nombre_archivo = f"{nombre_base}.xlsx" if contador == 0 else f"{nombre_base}_{contador}.xlsx"
        try:
            # Copiar el archivo base antes de modificarlo
            shutil.copy2(ruta_archivo_base_absoluta, nombre_archivo)
            break
        except PermissionError:
            contador += 1
            if contador > 100:  # Límite de intentos
                raise Exception("No se pudo crear el archivo. Demasiados archivos en uso.")

    # Cargar la copia del archivo base y obtener la hoja activa
    libro = load_workbook(nombre_archivo)
    hoja = libro.active

    # Insertar los datos en la hoja de cálculo (empezando desde la fila 2)
    for i, fila in enumerate(data, start=1):  # Empieza desde la fila 1
        for clave, valor in zip(mapeo_columnas.keys(), fila):  
            columna = mapeo_columnas[clave]  # Obtener número de columna según el mapeo
            hoja.cell(row=i, column=columna, value=valor)

    # Guardar el archivo modificado y cerrar el libro
    libro.save(nombre_archivo)
    libro.close()

    # 📌 Intentar enviar el archivo y eliminarlo después
    try:
        return send_file(nombre_archivo, as_attachment=True, download_name=nombre_archivo)
    finally:
        # Asegurarse de que el archivo esté cerrado antes de eliminarlo
        if 'libro' in locals():
            try:
                libro.close()
            except:
                pass
        try:
            os.remove(nombre_archivo)  # Eliminar el archivo después de enviarlo
        except:
            pass  # Ignorar errores al eliminar el archivo


def generar_pdf_solicitud(solicitud):
    """
    Genera un PDF con los detalles de la solicitud usando una plantilla HTML.
    
    Args:
        solicitud: Objeto de solicitud con los datos necesarios
        
    Returns:
        BytesIO: Buffer con el contenido del PDF generado
    """
    try:
        # Configurar el entorno de Jinja2
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('solicitud_pdf.html')

        # Preparar los datos para la plantilla
        datos_solicitud = {
            'numero_factura': solicitud.factura.no_factura,
            'fecha_otorgamiento': solicitud.factura.fecha_otorga.strftime('%d/%m/%Y'),
            'fecha_vencimiento': solicitud.factura.fecha_vence.strftime('%d/%m/%Y'),
            'monto_factura': float(solicitud.factura.monto),
            'descuento': float(solicitud.descuento_app or 0),
            'iva': float(solicitud.iva or 0),
            'subtotal_descuento': float(solicitud.subtotal or 0),
            'total_recibir': float(solicitud.total or 0),
            'nombre_proveedor': solicitud.factura.nombre_proveedor,
            'nit_proveedor': solicitud.factura.nit,
            'nombre_cliente': solicitud.factura.proveedor.razon_social if solicitud.factura and solicitud.factura.proveedor else 'No especificado'
        }

        # Renderizar la plantilla
        html_content = template.render(
            solicitud=datos_solicitud,
            fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        )

        # Configuración de wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        
        # Opciones para el PDF
        options = {
            'page-size': 'Letter',
            'margin-top': '1.85in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }

        # Generar PDF
        pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)
        
        # Crear buffer de memoria con el PDF
        pdf_buffer = BytesIO(pdf)
        pdf_buffer.seek(0)
        
        return pdf_buffer
    except Exception as e:
        raise Exception(f"Error al generar el PDF: {str(e)}")
