import os
from jinja2 import Environment, FileSystemLoader
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de prueba
class Config:
    MAIL_SERVER = "smtp.gmail.com"  # Cambiar por el servidor SMTP de tu proveedor
    MAIL_PORT = 587
    MAIL_USERNAME = "clobitechnologiesdevelopmentse@gmail.com"  # Cambiar por tu dirección de correo
    MAIL_PASSWORD = "vhok gjmx gfge inab"       # Cambiar por tu contraseña o clave de aplicación

# Configuración del entorno de plantillas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')  # Asegúrate de que el directorio coincida
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def generar_plantilla(nombre_plantilla, datos):
    """
    Genera un contenido HTML basado en la plantilla especificada y los datos proporcionados.

    Args:
        nombre_plantilla (str): Nombre del archivo de la plantilla HTML (en la carpeta /templates).
        datos (dict): Diccionario con los datos a inyectar en la plantilla.

    Returns:
        str: Cadena HTML renderizada con los datos.
    """
    try:
        # Carga la plantilla específica
        template = env.get_template(nombre_plantilla)
        # Renderiza la plantilla con los datos proporcionados
        return template.render(datos)
    except Exception as e:
        print(f"Error al generar la plantilla {nombre_plantilla}: {e}")
        return None

def enviar_correo(destinatario, asunto, contenido_html):
    try:
        # Configuración del servidor SMTP
        servidor = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        servidor.starttls()
        servidor.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)

        # Crear el mensaje del correo
        mensaje = MIMEMultipart()
        mensaje['From'] = Config.MAIL_USERNAME
        mensaje['To'] = destinatario
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(contenido_html, 'html'))

        # Enviar el correo
        servidor.send_message(mensaje)
        servidor.quit()
        print("Correo enviado correctamente.")
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

# Script de prueba
if __name__ == "__main__":
    # Escenario 1: Confirmación de solicitud pronto pago
    # datos_confirmacion = {
    #     "nombreEmpresa": "Clobi Technologies S.A. de C.V.",
    #     "noFactura": "123456",
    #     "monto": "$15,000.00",
    #     "fechaSolicitud": "20/12/2024",
    # }
    # asunto = f"Confirmación de Recepción de su Solicitud de Pronto Pago FACTURA {datos_confirmacion['noFactura']}"
    # contenido_html_confirmacion = generar_plantilla('correo_confirmacion_solicitud_pp.html', datos_confirmacion)
    # enviar_correo("eliazar.rebollo23@gmail.com", asunto, contenido_html_confirmacion)

    # Escenario 2: Aprobación de solicitud
    # datos_aprobacion = {
    #     "nombreSolicitante": "Fulano de tal",
    #     "noFactura": "123456",
    #     "montoFactura": "$15,000.00",
    #     "descuento": "$450.00",
    #     "iva": "$67.50",
    #     "subtotal": "$517.50",
    #     "fechaSolicitud": "20/12/2024",
    #     "fechaPago": "20/12/2024",
    #     "fechaVencimiento": "18/02/2025",
    #     "diasCredito": "60",
    # }
    # asunto = f"Solicitud de Pronto Pago Aprobada FACTURA {datos_aprobacion['noFactura']}"
    # contenido_html_aprobacion = generar_plantilla('correo_aprobacion_solicitud_pp.html', datos_aprobacion)
    # enviar_correo("eliazar.rebollo23@gmail.com", asunto , contenido_html_aprobacion)

    # # Escenario 3: Denegacion de solicitud
    # datos_denegacion = {
    #     "nombreSolicitante": "Fulano de tal",
    #     "noFactura": "345678",
    #     "montoFactura": "$15,000.00",
    #     "fechaSolicitud": "25/12/2024",
    # }
    # asunto = f"Solicitud de Pronto Pago Denegada FACTURA {datos_denegacion['noFactura']}"
    # contenido_html_denegacion = generar_plantilla('correo_denegacion_solicitud_pp.html', datos_denegacion)
    # enviar_correo("eliazar.rebollo23@gmail.com", asunto, contenido_html_denegacion)
    
    # Escenario 4: Notificacion de nueva solicitud pendiente
    # datos_notificacion = {
    #     "nombreEmpresa": "Clobi Technologies S.A. de C.V.",
    #     "proveedor": "Clobi Technologies S.A. de C.V.",
    #     "noFactura": "345678",
    #     "montoFactura": "$15,000.00",
    #     "fechaSolicitud": "25/12/2024",
    #     "diasCredito": "60",
    # }
    # asunto = f"Nueva Solicitud de Pronto Pago en Espera de Gestión FACTURA {datos_notificacion['noFactura']}"
    # contenido_html_notificacion = generar_plantilla('correo_notificacion_solicitud_pendiente_aprobacion_pp.html', datos_notificacion)
    # enviar_correo("eliazar.rebollo23@gmail.com", asunto, contenido_html_notificacion)

    # Escenario 5: Confirmacion de desembolso de fondos
    datos_desembolso = {
        "nombreEmpresa": "Clobi Technologies S.A. de C.V.",
        "noFactura": "123456",
        "montoFacturaOriginal": "15,000.00",
        "descuentoAplicado": "450.00",
        "montoDesembolsado": "14,482.50",
        "fechaDesembolso": "20/12/2024",
        "cuentaDestino": "XXXX-XXXX-XXXX-1234" 
    }
    asunto = f"Nueva Solicitud de Pronto Pago en Espera de Gestión FACTURA {datos_desembolso['noFactura']}"
    contenido_html_desembolso = generar_plantilla('correo_confirmacion_desembolso_fondos_pp.html', datos_desembolso)
    enviar_correo("eliazar.rebollo23@gmail.com", asunto, contenido_html_desembolso)
    
    # Escenario 6: Confirmacion de desembolso de fondos
    datos_credenciales = {
        "nombreUsuario": "Eliazar Rebollo",
        "correoElectronico": "eliazar.rebollo23@gmail.com",
        "contrasenaTemporal": "12345678",
    }
    asunto = f"Credenciales de acceso al sistema de pronto pago"
    contenido_html_credenciales = generar_plantilla('correo_contraseña_temporal.html', datos_credenciales)
    enviar_correo("eliazar.rebollo23@gmail.com", asunto, contenido_html_credenciales)
    