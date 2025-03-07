def metrica_factura(dias, monto_factura, interes_anual):
    # Calcular interés diario
    interes_diario = interes_anual / 365 / 100
    
    # Calcular descuento diario
    descuento_diario = monto_factura * interes_diario
    
    # Calcular descuento total por pronto pago
    pronto_pago = dias * descuento_diario
    
    # Calcular IVA sobre el descuento
    iva = pronto_pago * 0.13  # Asumiendo 13% de IVA
    
    subtotal_descuento = pronto_pago + iva
    
    # Total a recibir después del descuento
    total_a_recibir = monto_factura - subtotal_descuento

    # Retornar los resultados en un JSON
    resultado = {
        "descuento_app": round(pronto_pago, 2),
        "iva": round(iva, 2),
        "subtotal": round(subtotal_descuento, 2),
        "total": round(total_a_recibir, 2),
        "descuento_diario": descuento_diario,
    }
    
    return resultado