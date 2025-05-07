from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# Usuarios con sus respectivos roles
usuarios_con_roles = {
    "token_admin": "Administrador",
    "token_orquestador": "Orquestador",
    "token_usuario": "Usuario"
}

# --------- Modelos ---------

class OrquestarRequest(BaseModel):
    servicio_destino: str
    parametros_adicionales: Dict[str, Any]

class RegistrarServicioRequest(BaseModel):
    nombre: str
    descripcion: str
    endpoints: List[str]

class ActualizarReglasRequest(BaseModel):
    reglas: Dict[str, Any]

class AutenticarUsuarioRequest(BaseModel):
    nombre_usuario: str
    contrasena: str

class AutorizarAccesoRequest(BaseModel):
    recursos: List[str]
    rol_usuario: str

# Función para revisar el token 

def obtener_rol_desde_token(request: Request):
    token = request.headers.get("Authorization")
    if not token or token not in usuarios_con_roles:
        raise HTTPException(status_code=401, detail="Token inválido o no proporcionado")
    return usuarios_con_roles[token]

# Endpoints 

# 1. Función: orquestar servicios
@app.post("/orquestar")
def orquestar_servicio(data: OrquestarRequest, request: Request):
    rol = obtener_rol_desde_token(request)
    if rol not in ["Administrador", "Orquestador"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    return {
        "mensaje": f"Servicio '{data.servicio_destino}' orquestado correctamente.",
        "parametros": data.parametros_adicionales
    }

# 2. Función: Obtener información del servicio
@app.get("/informacion-servicio/{id}")
def obtener_informacion_servicio(id: int, request: Request):
    rol = obtener_rol_desde_token(request)
    return {
        "id": id,
        "nombre": f"Servicio{id}",
        "descripcion": "Servicio de ejemplo",
        "endpoints": ["https://api.servicio.com/accion"]
    }

# 3. Función: registrar nuevo servicio
@app.post("/registrar-servicio")
def registrar_servicio(data: RegistrarServicioRequest, request: Request):
    rol = obtener_rol_desde_token(request)
    if rol != "Administrador":
        raise HTTPException(status_code=403, detail="Solo administradores pueden registrar servicios")
    return {
        "mensaje": f"Servicio '{data.nombre}' registrado exitosamente.",
        "descripcion": data.descripcion,
        "endpoints": data.endpoints
    }

# 4. Función: Actualizar reglas de orquestación 
@app.put("/actualizar-reglas-orquestacion")
def actualizar_reglas(data: ActualizarReglasRequest, request: Request):
    rol = obtener_rol_desde_token(request)
    if rol != "Orquestador":
        raise HTTPException(status_code=403, detail="Solo orquestadores pueden actualizar reglas")
    return {
        "mensaje": "Reglas de orquestación actualizadas",
        "nuevas_reglas": data.reglas
    }

# 5. Función: Autenticación de usuario
@app.post("/autenticar-usuario")
def autenticar_usuario(data: AutenticarUsuarioRequest):
    if data.nombre_usuario == "admin" and data.contrasena == "123":
        return {"token": "token_admin"}
    elif data.nombre_usuario == "orquestador" and data.contrasena == "123":
        return {"token": "token_orquestador"}
    elif data.nombre_usuario == "usuario" and data.contrasena == "123":
        return {"token": "token_usuario"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# 6. Función: Autorización de acceso
@app.post("/autorizar-acceso")
def autorizar_acceso(data: AutorizarAccesoRequest, request: Request):
    rol = obtener_rol_desde_token(request)
    if rol != data.rol_usuario:
        raise HTTPException(status_code=403, detail="Acceso no autorizado para ese rol")
    return {
        "mensaje": "Acceso autorizado",
        "rol": data.rol_usuario,
        "recursos": data.recursos
    }
