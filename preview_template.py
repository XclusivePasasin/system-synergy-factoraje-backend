from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def preview():
    # Datos de ejemplo similares a los que usamos en el servicio
    datos_solicitud = {
        'numero_factura': '123456',
        'fecha_otorgamiento': '20/12/2023',
        'fecha_vencimiento': '18/02/2024',
        'monto_factura': 15000.00,
        'descuento': 450.00,
        'iva': 67.50,
        'subtotal_descuento': 517.50,
        'total_recibir': 14482.50,
        'nombre_proveedor': 'Proveedor de Ejemplo S.A.',
        'nit_proveedor': '1234567-8'
    }
    
    return render_template(
        'solicitud_pdf.html',
        solicitud=datos_solicitud,
        fecha_generacion=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    )

if __name__ == '__main__':
    app.run(port=5001)
