# Documentación de API - Endpoints del backend

## Endpoints Email

### **Enviar correo electrónico de factura**
**Endpoint:** `POST /api/email/enviar-email`
**Descripción:** Envia un correo electrónico con los datos de la factura para notificar al proveedor que 
su factura está disponible para aplicar a pronto pago.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Request Body:**
```json
{
    "destinatario": "test@test.com",
    "asunto": "Opción de Pronto Pago Disponible",
    "datos": {
        "nombreEmpresa": "Clobi Technologies S.A. de C.V.",
        "noFactura": "FAC001",
        "factura_hash": "CCGSGTSJXM",
        "monto": "10000.00",
        "fechaOtorgamiento": "20/11/2024",
        "fechaVencimiento": "19/02/2025",
        "diasCredito": "10"
    }
}

```

## Endpoint Solicitud de Pago

### **Obtener detalles pronto pago de la factura**
**Endpoint:** `GET /api/factura/obtener-detalle-factura`
**Descripción:** Obtiene los detalles de la factura en base a los parámetros proporcionados.

**Query Parameters (Obligatorio):**
- 'no_factura': Numero de la factura que se desea obtener los detalles.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "factura": {
            "descuento_pp": 33.0,
            "dias_restantes": 44,
            "estado": 4,
            "fecha_otorga": "01/11/2024",
            "fecha_vence": "18/01/2025",
            "iva": 4.29,
            "monto": 1500.0,
            "no_factura": "FAC001",
            "factura_hash": "CCGSGTSJXM",
            "nombre_proveedor": "TechNova Solutions S.A.",
            "subtotal": 37.29,
            "total": 1462.71
        }
    },
    "message": "Detalle de factura obtenido correctamente"
}
```

### **Solicitar Solicitud de Pronto Pago**
**Endpoint:** `POST /api/solicitud/solicitar-pago-factura`
**Descripción:** Crea una solicitud de pronto pago para la factura que se desea solicitar.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**request Body:**
```json
{
   "data": {
        "factura": {
            "nombre_proveedor": "TechNova Solutions S.A.",
            "dias_restantes": 47,
            "fecha_otorga": "01/11/2024",
            "fecha_vence": "18/01/2025",
            "iva": 4.58,
            "monto": 1500.0,
            "no_factura": "FAC001",
            "descuento_app": 35.25,
            "subtotal": 39.83,
            "total": 1460.17
        },
       "nombre_solicitante": "Eliazar Antonio Rebollo Pasasin",
       "cargo": "Programador",
       "email": "eliazar.rebollo23@gmail.com"
    }
}
```
**Response (error):**
```json
{
    "code": 1,
    "data": null,
    "message": "La solicitud proporcionada no existe en la base de datos"
}
```

## Endpoints Usuario

### **Crear Usuario**
**Endpoint:** `POST /api/usuario/crear-usuario`
**Descripción:** Crea un nuevo usuario en el sistema con una contraseña temporal y la almacena hasheada.

**Request Body:**
```json
{
    "nombres": "Julian",
    "apellidos": "Zan",
    "email": "julian.zan4@example.com",
    "id_rol": 1
}

```

**Response (success):**
```json
{
    "code": 0,
    "data": {
        "cargo": "Administrador",
        "email": "tes1t@admin.com",
        "id_rol": 1,
        "nombres": "Nombresxd",
        "apellidos": "Apellidosxd",
        "usuario_id": 3
    },
    "message": "Usuario creado exitosamente"
}
```
**Response (error):**
```json
{
    "code": 1,
    "data": null,
    "message": "El correo ya está registrado"
}
```

### **Cambiar Estado de Usuario**
**Endpoint:** `POST /api/usuario/cambiar-estado-usuario`
**Descripción:** Cambia el estado de activación del usuario especificado.

**Request Body:**
```json
{
    "usuario_id": 1,
    "activo": true or false
}
```

**Response (success):**
```json
{
    "code": 0,
    "data": {
        "mensaje": "Estado del usuario activado exitosamente"
    },
    "message": "Estado del usuario activado exitosamente"
}
```

**Response (error):**
```json
{
    "code": 1,
    "data": null,
    "message": "El usuario no existe"
}
```

### **Modificar Usuario**
**Endpoint:** `PUT /api/usuario/actualizar-usuario`
**Descripción:** Modifica los datos de un usuario existente.

**Query Parameters (Obligatorio):**
- 'usuario_id': ID del usuario que se desea actualizar.


**Request Body:**
```json
{
    "nombres": "Luissss",
    "apellidos": "Majanoo",
    "id_rol": 4,
    "password": "" // Opcional
}
```

**Response (success):**
```json
{
    "code": 0,
    "data": {
        "mensaje": "Usuario actualizado exitosamente"
    },
    "message": "Usuario actualizado exitosamente"
}
```

**Response (error):**
```json
{
    "code": 1,
    "data": null,
    "message": "El campo 'nombres' está vacío o no es válido"
}
```
### **Listar Usuarios**
**Endpoint:** `GET /api/usuario/listar-usuarios`
**Descripción:** Devuelve una lista de todos los usuarios que no han sido eliminados.

**Query Parameters (Opcional):**
- 'nombre': Filtrar por nombres.
- 'apellidos': Filtrar por apellidos.
- 'cargo': Filtrar por cargo.
- 'email': Filtrar por email.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```
**Response:**
```json
{
    "code": 0,
    "data": {
        "current_page": 1,
        "per_page": 10,
        "total_pages": 1,
        "usuarios": [
            {
                "activo": true,
                "apellidos": "",
                "cargo": "Administrador",
                "created_at": "2024-12-02T08:27:55",
                "email": "clobitechadmin@clobitech.com",
                "id": 1,
                "id_rol": 1,
                "nombres": "",
                "reg_activo": true,
                "updated_at": "2024-12-09T12:53:43"
            },
            {
                "activo": true,
                "apellidos": "",
                "cargo": "Agente Synergy",
                "created_at": "2024-12-02T11:22:00",
                "email": "sonia.navarro@clobitech.com",
                "id": 2,
                "id_rol": 2,
                "nombres": "",
                "reg_activo": true,
                "updated_at": "2024-12-02T11:30:27"
            }
        ]
    },
    "message": "Lista de usuarios obtenida exitosamente"
}
```

### **Obtener Detalle de Usuario**
**Endpoint:** `GET /api/usuario/detalle-usuario`
**Descripción:** Devuelve los detalles de un usuario específico.

**Query Parameters (Obligatorio):**
- 'usuario_id': ID del usuario que se desea obtener.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "activo": 1,
        "apellidos": "Navarro",
        "cargo": "Agente Synergy",
        "created_at": "Mon, 02 Dec 2024 11:22:00 GMT",
        "email": "sonia.navarro@clobitech.com",
        "id": 2,
        "id_rol": 2,
        "nombres": "Sonia",
        "reg_activo": 1,
        "updated_at": "Mon, 02 Dec 2024 11:30:27 GMT"
    },
    "message": "Detalle del usuario obtenido exitosamente"
}
```


### **Iniciar Sesión**

**Endpoint:** `POST /api/usuario/inicio-sesion`
**Descripción:** Inicia sesión en el sistema con el email y la contraseña proporcionados y genera un token JWT.

**Request Body:**
```json
{
    "email": "juan.perez@example.com",
    "password": "12345678"
}

```

**Response (success):**
```json
{
    "code": 0,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsIZXADDSjfhfyn",
        "change_password": 0,
        "expires_in": 86400,
        "usuario": {
            "email": "tes1t@admin.com",
            "id": 3,
            "nombres": "nombresxd",
            "apellidos": "apellidosxd",
            "permissions": [
                {
                    "create_perm": 1,
                    "delete_perm": 0,
                    "edit_perm": 1,
                    "menu": {
                        "icon": "fa-solid-file",
                        "id": 1,
                        "menu": "Solicitudes",
                        "orden": 2,
                        "padre": 0,
                        "path": "/solicitudes"
                    },
                    "view_perm": 0
                }
            ],
            "role": "Administrador"
        }
    },
    "message": "Autenticación completada"
}
```
**Response (error):**
```json
{
    "code": 1,
    "data": null,
    "message": "El usuario no existe"
}
```

### **Actualizar Contraseña**
**Endpoint:** `POST /api/usuario/cambiar-contraseña`
**Descripción:** Actualiza la contraseña del usuario en su primera sesión.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**request Body:**
```json
{
    "email": "juan.perez@example.com",
    "nueva_contrasena": "12345678"
}
```

**Response (success):**
```json
{
    "code": 0,
    "data": {
        "email": "juan.perez@example.com",
        "mensaje": "Contraseña actualizada exitosamente"
    },
    "message": "Contraseña actualizada correctamente"
}
```


### **Validar Token**

**Endpoint:** `POST /api/usuario/token`
**Descripción:** Valida el token JWT proporcionado y devuelve el usuario y el token.

**Request Body:**
```json
{
    "email": "email@ejemplo.com",
}
```

**Response (success):**
```json
{
    "code": 0,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAYWRtaW4uY29tIiwiZXhwIjoxNzMyODIwMzY2fQ.11UCiRhAEGG_9gxEsjyVA5LLQ-5fqL2_pmEJeh5GoII",
        "expires_in": 86400,
        "usuario": {
            "email": "test@admin.com",
            "id": 2,
            "name": "Test",
            "permissions": [
                {
                    "create_perm": 1,
                    "delete_perm": 0,
                    "edit_perm": 1,
                    "menu": {
                        "icon": "fa-solid-file",
                        "id": 1,
                        "menu": "Solicitudes",
                        "orden": 2,
                        "padre": 0,
                        "path": "/solicitudes"
                    },
                    "view_perm": 0
                }
            ],
            "role": "Administrador"
        }
    },
    "message": "Autenticación completada"
}
```

### **Cerrar Sesión**
**Endpoint:** `POST /api/usuario/cerrar-sesion`  
**Descripción:** Cierra la session del usuario.

**Query Parameters (Obligatorio):**
- 'usuario_id': ID del usuario que se desea cerrar la sesión.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json

{
    "data":null,
    "message": "Se ha cerrado la session exitosamente",
    "code": 0
}

```
### **Eliminar Usuario**
**Endpoint:** `DELETE /api/usuario/eliminar-usuario`
**Descripción:** Elimina un usuario de la base de datos.

**Query Parameters (Obligatorio):**
- 'usuario_id': ID del usuario que se desea eliminar.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "mensaje": "Usuario eliminado exitosamente"
    },
    "message": "Usuario eliminado exitosamente"
}
```

## Endpoints Solicitudes

### **Listar todas las solicitudes**
**Endpoint:** `GET /api/solicitud/obtener-solicitudes`
**Descripción:** Devuelve una lista de solicitudes con soporte para filtros y paginación.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Query Parameters (opcional):**
- 'page': Número de página (ejemplo: `1`).
- 'per_page': Cantidad de elementos por página (ejemplo: `10`).
- 'fecha_inicio', `fecha_fin`: Rango de fechas.
- 'estado': Filtrar por estado.
- 'no_factura': Filtrar por número de factura.
- 'nombre_proveedor': Nombre proveedor
- 'nrc' NRC del proveedor.
- 'telefono' Teléfono del proveedor.
- 'email' Email del solicitante.

**Response (success):**
```json
{
    "code": 0,
    "data": {
        "current_page": 1,
        "per_page": 10,
        "solicitudes": [
            {
                "email": "test@test.com",
                "estado": "PENDIENTE",
                "factura": {
                    "fecha_emision": "2024-11-01T10:00:00",
                    "fecha_otorga": "2024-11-01T11:00:00",
                    "fecha_vence": "2025-01-18T10:00:00",
                    "id": 1,
                    "monto": 1500.0,
                    "no_factura": "FAC001",
                    "proveedor": {
                        "correo_electronico": "contacto@technova.com",
                        "id": 1,
                        "max_factoring": "5000.00",
                        "min_factoring": "1000.00",
                        "nit": "NIT456789123",
                        "nombre_contacto": "Juan Pérez",
                        "nrc": "NRC12345",
                        "razon_social": "TechNova Solutions S.A.",
                        "telefono": "555-12345"
                    }
                },
                "id": 4,
                "id_estado": 1,
                "iva": 4.58,
                "nombre_cliente": "Eliazar Pasasin",
                "subtotal": 39.83,
                "total": 1460.17
            }
        ],
        "total_pages": 1
    },
    "message": "Consulta exitosa"
}
```
### **Mostrar detalle de una solicitud**
**Endpoint:** `GET /api/solicitud/obtener-detalle-solicitud?id=`
**Descripción:** Devuelve los detalles de una solicitud específica.

**Query Parameters (Obligatorio):**
- 'id': Numero de la solicitud que se desea obtener los detalles.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "solicitud": {
            "email": "test@test.com",
            "estado": "PENDIENTE",
            "factura": {
                "fecha_otorga": "01/11/2024",
                "fecha_vence": "18/01/2025",
                "id": 1,
                "monto": 1500.0,
                "no_factura": "FAC001",
                "pronto_pago": 35.25,
                "proveedor": {
                    "correo_electronico": "contacto@technova.com",
                    "id": 1,
                    "razon_social": "TechNova Solutions S.A.",
                    "telefono": "555-12345"
                }
            },
            "id": 4,
            "id_estado": 1,
            "iva": 4.58,
            "nombre_cliente": "Eliazar Pasasin",
            "subtotal": 39.83,
            "total": 1460.17
        }
    },
    "message": "Consulta exitosa"
}
```

### **Aprobar una solicitud**
**Endpoint:** `PUT /api/solicitud/aprobar`
**Descripción:** Cambia el estado de la solicitud a Aprobada y puede registrar información adicional sobre quién aprobó la solicitud.

**Query Parameters (Obligatorio):**
- 'id': Numero de la solicitud que se desea aprobar.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Body (JSON):**
```json
{
  "id_aprobador": 5, 
  "comentario": "Documentacion satisfactoria"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "solicitud": {
            "contacto": "555-12345",
            "email": "eliazar.rebollo23@gmail.com",
            "factura": {
                "id": 1,
                "monto": 1500.0,
                "no_factura": "FAC001",
                "proveedor": {
                    "id": 1,
                    "razon_social": "TechNova Solutions S.A."
                }
            },
            "fecha_aprobacion": "2024-12-04T16:12:34",
            "id": 6,
            "id_aprobador": 1,
            "id_estado": 2,
            "nombre_cliente": "Eliazar Antonio Rebollo Pasasin",
            "total": 1460.17
        }
    },
    "message": "Solicitud aprobada exitosamente. Correo de notificación enviado."
}
```

### **Denegar una solicitud**
**Endpoint:** `PUT /api/solicitud/denegar`
**Descripción:** Cambia el estado de la solicitud a Denegada y permite registrar una razón para la denegación.

**Query Parameters (Obligatorio):**
- 'id': Numero de la solicitud que se desea denegar.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Body (JSON):**
```json
{
  "comentario": "Documentación incompleta."  // (opcional) 
}

```

**Response:**
```json
{
    "code": 0,
    "data": {
        "solicitud": {
            "contacto": "555-12345",
            "email": "eliazar.rebollo23@gmail.com",
            "factura": {
                "id": 1,
                "monto": 1500.0,
                "no_factura": "FAC001",
                "proveedor": {
                    "id": 1,
                    "razon_social": "TechNova Solutions S.A."
                }
            },
            "id": 5,
            "id_estado": 3,
            "nombre_cliente": "Eliazar Antonio Rebollo Pasasin",
            "total": 1460.17
        }
    },
    "message": "Solicitud denegada exitosamente. Correo de notificación enviado."
}
```

### **Obtener métricas de solicitudes**
**Endpoint:** `GET /api/solicitud/panel-solicitudes`
**Descripción:** Devuelve las métricas de solicitudes, incluyendo el número de solicitudes aprobadas y pendientes.

**Query Parameters (opcional):**
- 'fecha_inicio', `fecha_fin`: Rango de fechas.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "filtros_aplicados": {
            "fecha_fin": "2024-12-05",
            "fecha_inicio": "2024-12-01"
        },
        "solicitudes_aprobadas": 1,
        "solicitudes_sin_aprobar": 1,
        "total_solicitudes": 2
    },
    "message": "Métricas de solicitudes obtenidas con éxito"
}
```

### **Procesar Solicitudes**
**Endpoint:** `POST /api/solicitud/procesar-solicitudes`
**Descripción:** Procesa las solicitudes de la lista proporcionada y genera un archivo de Excel con los resultados.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Request Body:**
```json
{
    "ids": [1, 2, 3]
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "message": "Se procesaron:3 solicitudes."
    },
    "message": "Se procesaron:3 solicitudes."
}
```


## Endpoints Permisos

### **Actualizar Permisos**
**Endpoint:** `PUT /api/permiso/actualizar-permisos`
**Descripción:** Actualiza los permisos de un rol existente.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Request Body:**
```json
{
    "id_rol": 1,
    "permisos": [
        {
            "id_menu": 3,
            "create_perm": 1,
            "edit_perm": 1,
            "delete_perm": 1,
            "view_perm": 1
        },
        {
            "id_menu": 2,
            "create_perm": 1,
            "edit_perm": 0,
            "delete_perm": 0,
            "view_perm": 0
        }
    ]
}
```

**Response:**
```json
{
    "code": 0,
    "data": "Permisos asignados exitosamente para el rol 'Auditor Synergy'.",
    "message": "Permisos asignados exitosamente."
}
```


### **Listar Permisos de un Rol**
**Endpoint:** `GET /api/permiso/listar-permisos`
**Descripción:** Devuelve una lista de todos los permisos en base al id_rol proporcionado.

**Query Parameters (Obligatorio):**
- 'id_rol': ID del rol que se desea listar los permisos.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```
**Response:**
```json

{
    "code": 0,
    "data": {
        "descripcion": null,
        "id_rol": 1,
        "nombre": "Administrador",
        "permisos": [
            {
                "create_perm": 0,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 1,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 2,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 3,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 4,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 5,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 6,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 7,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 8,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 9,
                "view_perm": 1
            },
            {
                "create_perm": 1,
                "delete_perm": 1,
                "edit_perm": 1,
                "id_menu": 10,
                "view_perm": 1
            }
        ]
    },
    "message": "Permisos obtenidos exitosamente."
}

```

## Endpoints Proveedores Calificados

### **Crear Proveedor**
**Endpoint:** `POST /api/proveedor/registrar-proveedor`
**Descripción:** Crea un nuevo proveedor en el sistema con la información proporcionada.

**Request Body:**
```json
{
    "id": "PROV12345",
    "razon_social": "Proveedor S.A. de C.V.",
    "nrc": "123456-7",
    "nit": "0614-290120-101-2",
    "correo_electronico": "contacto@proveedor.com",
    "cuenta_bancaria": "1234567890123456",
    "min_factoring": 1000.50,
    "max_factoring": 50000.75,
    "banco": "Banco Nacional",
    "codigo_banco": "002",
    "nombre_contacto": "Juan Pérez",
    "telefono": "+503 2258-1234"
}

```

**Response (success):**
```json
{
    "code": 0,
    "data": {
        "proveedor": {
            "banco": "Banco de América Central",
            "codigo_banco": "0",
            "correo_electronico": "clobitech@clobitech.com",
            "cuenta_bancaria": "1234567890",
            "id": 1,
            "max_factoring": 5000.0,
            "min_factoring": 1000.0,
            "nombre_contacto": "Juan Pérez",
            "nit": "NIT456789123",
            "nrc": "NRC12345",
            "razon_social": "Clobi Technologies S.A. de C.V.",
            "telefono": "555-12345",
            "created_at": "2023-01-01 12:00:00",
            "updated_at": "2023-01-01 12:00:00"
        }
    },
    "message": "Proveedor creado exitosamente"
}
```

**Response (error):**
```json
{
    "code": 1,
    "data": null,
    "message": "Faltan los campos obligatorios:"
}
```

### **Listar todos los proveedores**
**Endpoint:** `GET /api/proveedor/listar-proveedores`
**Descripción:** Devuelve una lista de todos los proveedores en el sistema.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

query params:
- 'page': Número de página (ejemplo: `1`).
- 'per_page': Cantidad de elementos por página (ejemplo: `10`).
- 'razon_social': Filtrar por razón social.
- 'nrc': Filtrar por número de cuenta bancaria.
- 'nit': Filtrar por número de identificación tributaria.
- 'correo_electronico': Filtrar por correo electrónico.
- 'cuenta_bancaria': Filtrar por cuenta bancaria.
- 'banco': Filtrar por banco.
- 'nombre_contacto': Filtrar por nombre del contacto.
- 'telefono': Filtrar por teléfono.

**Response:**
```json
{
    "code": 0,
    "data": [
        "proveedores": [
            {
                "banco": "Banco de América Central",
                "codigo_banco": "0",
                "correo_electronico": "clobitech@clobitech.com",
                "cuenta_bancaria": "1234567890",
                "id": 1,
                "max_factoring": 5000.0,
                "min_factoring": 1000.0,
                "nombre_contacto": "Juan Pérez",
                "nit": "NIT456789123",
                "nrc": "NRC12345",
                "razon_social": "Clobi Technologies S.A. de C.V.",
                "telefono": "555-12345",
                "created_at": "2023-01-01 12:00:00",
                "updated_at": "2023-01-01 12:00:00"
            },
            {
                "banco": "Banco de América Central",
                "codigo_banco": "0",
                "correo_electronico": "clobitech@clobitech.com",
                "cuenta_bancaria": "1234567890",
                "id": 1,
                "max_factoring": 5000.0,
                "min_factoring": "1000.0",
                "nombre_contacto": "Juan Pérez",
                "nit": "NIT456789123",
                "nrc": "NRC12345",
                "razon_social": "Clobi Technologies S.A. de C.V.",
                "telefono": "555-12345",
                "created_at": "2023-01-01 12:00:00",
                "updated_at": "2023-01-01 12:00:00"
            }
        ]   
    ],
    "message": "Lista de proveedores obtenida exitosamente"
}
```

### **Eliminar un proveedor**
**Endpoint:** `DELETE /api/proveedor/eliminar-proveedor`
**Descripción:** Elimina un proveedor del sistema.

**Query Parameters (Obligatorio):**
- 'id': ID del proveedor que se desea eliminar.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "mensaje": "Proveedor eliminado exitosamente"
    },
    "message": "Proveedor eliminado exitosamente"
}
```

### **Actualizar un proveedor**w
**Endpoint:** `PUT /api/proveedor/actualizar-proveedor`
**Descripción:** Actualiza los datos de un proveedor existente.

**Query Parameters (Obligatorio):**
- 'id': ID del proveedor que se desea actualizar.

**Request Body:**
```json
{
    "id": "PROV12345",
    "razon_social": "Proveedor S.A. de C.V.",
    "nrc": "123456-7",
    "nit": "0614-290120-101-2",
    "correo_electronico": "contacto@proveedor.com",
    "cuenta_bancaria": "1234567890123456",
    "min_factoring": 1000.50,
    "max_factoring": 50000.75,
    "banco": "Banco Nacional",
    "codigo_banco": "002",
    "nombre_contacto": "Juan Pérez",
    "telefono": "+503 2258-1234"
}
```

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "proveedor": {
            "banco": "Banco de América Central",
            "codigo_banco": "0",
            "correo_electronico": "clobitech@clobitech.com",
            "cuenta_bancaria": "1234567890",
            "id": 1,
            "max_factoring": 5000.0,
            "min_factoring": 1000.0,
            "nombre_contacto": "Juan Pérez",
            "nit": "NIT456789123",
            "nrc": "NRC12345",
            "razon_social": "Clobi Technologies S.A. de C.V.",
            "telefono": "+503 2258-1234"
        }
    },
    "message": "Proveedor actualizado exitosamente"
}
```

### **Obtener detalles de un proveedor**
**Endpoint:** `GET /api/proveedor/obtener-proveedor`
**Descripción:** Devuelve los detalles de un proveedor específico.

**Query Parameters (Obligatorio):**
- 'id': ID del proveedor que se desea obtener.

**Headers:**
```json
{
    "Authorization": "Bearer <access_token>"
}
```

**Response:**
```json
{
    "code": 0,
    "data": {
        "proveedor": {
            "banco": "Banco de América Central",
            "codigo_banco": "0",
            "correo_electronico": "clobitech@clobitech.com",
            "cuenta_bancaria": "1234567890",
            "id": 1,
            "max_factoring": 5000.0,
            "min_factoring": 1000.0,
            "nombre_contacto": "Juan Pérez",
            "nit": "NIT456789123",
            "nrc": "NRC12345",
            "razon_social": "Clobi Technologies S.A. de C.V.",
            "telefono": "+503 2258-1234"
        }
    }
    "message": "Proveedor obtenido exitosamente"
}