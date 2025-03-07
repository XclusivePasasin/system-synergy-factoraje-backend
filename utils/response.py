from flask import jsonify

def response_success(data, message="Operación exitosa", code=0, http_status=200):
    return jsonify({
        "data": data,
        "message": message,
        "code": code,
    }), http_status


def response_error(message, code=1, http_status=400):
    return jsonify({
        "data": None,
        "message": message,
        "code": code,
    }), http_status
