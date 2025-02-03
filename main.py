import json
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from datetime import date, time
from BD import ConexionBD

class Login(BaseModel):
    correo: str
    contrasena: str
    
class Usuario(BaseModel):
    nombre: str
    email: str
    telefono: str
    contrasena: str

class Seleccion(BaseModel):
    seleccion: str

class Reserva(BaseModel):
    id_usuario: int
    id_tipo_recurso: int
    fecha_reserva: date
    hora_reserva: time
    estado: str

class ReservaCancelar(BaseModel):
    id_reserva: int

class TipoRecurso(BaseModel):
    tipo_recurso: int
    nombre_recurso: str
    disponibilidad: str
    estado: str
    orden: str 
    
class Prestamo(BaseModel):
    id_reserva: int
    id_empleado: int
    fecha_prestamo: date
    hora_prestamo: time
    
class Devolucion(BaseModel):
    id_prestamo: int
    fecha_devolucion: date
    hora_devolucion: time
    id_empleado: int
    
API_KEY = "super_secret_token"  # Cambia esto por una clave más segura

app = FastAPI()

origins = [
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/validate')
async def validate_user(l: Login):
    try:
        valid = ConexionBD.validarLogin(l.correo, l.contrasena)
        if valid:
            return {"message": "Logeado correctamente", "codigo": 202}
        else:
            raise HTTPException(status_code=404, detail="El correo o la contraseña son incorrectos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/registrarUsuario')
async def registrar_usuario(usuario: Usuario):
    """
    Registra un nuevo usuario en la base de datos.
    """
    try:
        resultado = ConexionBD.registrarUsuario(
            usuario.nombre,
            usuario.email,
            usuario.telefono,
            usuario.contrasena
        )
        if "Usuario registrado exitosamente" in resultado:
            return {"message": resultado}
        raise HTTPException(status_code=400, detail=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/consultarUsuarios')
async def consultar_usuarios(id_usuario: int = None):
    """
    Consulta todos los usuarios o un usuario específico por ID.
    """
    try:
        resultado = ConexionBD.consultarUsuarios(id_usuario)
        if isinstance(resultado, str):  # Si es un mensaje de error
            raise HTTPException(status_code=404, detail=resultado)
        return {"usuarios": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put('/actualizarUsuario/{id_usuario}')
async def actualizar_usuario(id_usuario: int, usuario: Usuario):
    """
    Actualiza la información de un usuario en la base de datos.
    """
    try:
        resultado = ConexionBD.actualizarUsuario(
            id_usuario,
            usuario.nombre,
            usuario.email,
            usuario.telefono,
            usuario.contrasena
        )
        if "Usuario actualizado exitosamente" in resultado:
            return {"message": resultado}
        raise HTTPException(status_code=400, detail=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete('/eliminarUsuario/{id_usuario}')
async def eliminar_usuario(id_usuario: int):
    """
    Elimina un usuario de la base de datos.
    """
    try:
        resultado = ConexionBD.eliminarUsuario(id_usuario)
        if "Usuario eliminado exitosamente" in resultado:
            return {"message": resultado}
        raise HTTPException(status_code=400, detail=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/agregarReserva')
async def add_reservation(reserva: Reserva):
    """
    Endpoint para crear una nueva reserva, seleccionando automáticamente un recurso disponible dentro del tipo de recurso solicitado.
    """
    try:
        resultado = ConexionBD.crearReserva(
            reserva.id_usuario,
            reserva.id_tipo_recurso,
            reserva.fecha_reserva,
            reserva.hora_reserva
        )
        if "Reserva creada exitosamente" in resultado:
            return {"message": resultado}
        raise HTTPException(status_code=400, detail=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/cancelarReserva')
async def cancel_reservation(s: ReservaCancelar):
    """
    Endpoint para cancelar una reserva existente
    """
    try:
        resultado = ConexionBD.actualizarReserva(s.idReserva, estado="Cancelada")
        if resultado:
            return {"message": resultado}
        raise HTTPException(status_code=404, detail="Reserva no encontrada para cancelar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/terminarReserva')
async def finish_reservation(s: ReservaCancelar):
    """
    Endpoint para finalizar una reserva
    """
    try:
        resultado = ConexionBD.actualizarReserva(s.idReserva, estado="Finalizada")
        if resultado:
            return {"message": resultado}
        raise HTTPException(status_code=404, detail="Reserva no encontrada para terminar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""@app.get('/Consultar reserva')
async def get_reservation(s: Reserva):
    try:
        result = ConexionBD.consultarReserva(s.idReserva)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""
    

@app.get('/consultarRecursos')
async def consultar_recursos(
    tipo_recurso: str = None,
    estado: str = None,
    nombre_recurso: str = None,
    horario_disponibilidad: str = None,
    orden: str = None
):
    """
    Consultar recursos de la unidad con filtros y ordenamientos, incluyendo horario de disponibilidad.
    """
    try:
        resultado = ConexionBD.consultarRecursos(
            tipo_recurso=tipo_recurso,
            estado=estado,
            nombre_recurso=nombre_recurso,
            horario_disponibilidad=horario_disponibilidad,
            orden=orden
        )
        return {"data": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get('/consultarReservaUsuario')
async def consultar_reservas(
    nombre_usuario: str = None,
    estado: str = None,
    tipo_filtro: str = Query(None, enum=['Vigentes', 'Pasadas', 'Futuras']),
    fecha_inicio: date = None,
    fecha_fin: date = None,
):
    """
    Consultar recursos de la unidad con filtros y ordenamientos, incluyendo horario de disponibilidad.
    """
    try:
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser posterior a la fecha final"
            )
        resultado = ConexionBD.consultarReservas(
            nombre_usuario=nombre_usuario,
            estado=estado,
            tipo_filtro=tipo_filtro,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return {"data": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/reservasVigentes/{id_usuario}')
async def obtener_reservas_vigentes(id_usuario: int):
    """
    Retorna todas las reservas vigentes de un usuario.
    """
    try:
        resultado = ConexionBD.consultarReservasVigentes(id_usuario)
        if isinstance(resultado, str):  # Si es un mensaje de error o sin resultados
            raise HTTPException(status_code=404, detail=resultado)
        return {"reservas_vigentes": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post('/registrarPrestamo')
async def registrar_prestamo(prestamo: Prestamo):
    """
    Registra un préstamo validando que el empleado esté registrado y que la reserva esté vigente.
    """
    try:
        resultado = ConexionBD.registrarPrestamo(
            prestamo.id_reserva,
            prestamo.id_empleado,
            prestamo.fecha_prestamo,
            prestamo.hora_prestamo
        )
        if "Préstamo registrado exitosamente" in resultado:
            return {"message": resultado}
        raise HTTPException(status_code=400, detail=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/prestamosVigentes/{id_usuario}')
async def obtener_prestamos_vigentes(id_usuario: int):
    """
    Retorna todos los préstamos vigentes de un usuario.
    """
    try:
        resultado = ConexionBD.consultarPrestamosVigentes(id_usuario)
        if isinstance(resultado, str):  # Si es un mensaje de error o sin resultados
            raise HTTPException(status_code=404, detail=resultado)
        return {"prestamos_vigentes": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/registrarDevolucion')
async def registrar_devolucion(devolucion: Devolucion):
    """
    Registra una devolución validando que el préstamo exista y que el empleado esté registrado.
    """
    try:
        resultado = ConexionBD.registrarDevolucion(
            devolucion.id_prestamo,
            devolucion.fecha_devolucion,
            devolucion.hora_devolucion,
            devolucion.id_empleado
        )
        if "Devolución registrada exitosamente" in resultado:
            return {"message": resultado}
        raise HTTPException(status_code=400, detail=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/recursosDisponibles')
async def obtener_recursos_disponibles(api_key: str = Header(None)):
    """
    Permite a servicios externos consultar los recursos disponibles.
    Se requiere un token de API válido en los headers para acceder.
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Acceso no autorizado. Token inválido.")

    try:
        resultado = ConexionBD.consultarRecursosDisponibles()
        if isinstance(resultado, str):  # Si es un mensaje de error o sin resultados
            raise HTTPException(status_code=404, detail=resultado)
        return {"recursos_disponibles": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))