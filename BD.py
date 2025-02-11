import psycopg2
import json
import jwt
import os
import bcrypt
import re
from datetime import datetime, timedelta , date, timezone


SECRET_KEY = "super-secret-key"  # Usa una variable de entorno para mayor seguridad
ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 60  # Expira en 1 hora

class TokenHandler:
    @staticmethod
    def generar_token(id_usuario):
        """
        Genera un token JWT con el ID del usuario.
        """
        expira = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
        payload = {"id_usuario": id_usuario, "exp": expira}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token


    @staticmethod
    def verificar_token(token):
        """
        Verifica si un token JWT es válido y devuelve el ID del usuario si es correcto.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Verificar si el token ha expirado manualmente
            exp = payload.get("exp")
            if exp and datetime.now(timezone.utc).timestamp() > exp:
                print("Error: Token expirado")  # 🔍 Para depuración
                return None
            
            return payload.get("id_usuario")  # Extraemos el ID del usuario del token

        except jwt.ExpiredSignatureError:
            print("Error: Token expirado (jwt.ExpiredSignatureError)")
            return None
        except jwt.InvalidTokenError as e:
            print("Error: Token inválido", e)
            return None


class PasswordHandler:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash de la contraseña usando bcrypt.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        # Convertimos la contraseña a bytes y generamos el hash
        password_bytes = password.encode('utf-8')
        # Generamos un salt y hacemos el hash
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        # Retornamos el hash como string
        return password_hash.decode('utf-8')
    
    @staticmethod
    def verificar_contrasena(contrasena_ingresada, contrasena_encriptada):
        """
        Compara una contraseña ingresada con su versión encriptada.
        """
        return bcrypt.checkpw(contrasena_ingresada.encode('utf-8'), contrasena_encriptada.encode('utf-8'))    

class ConexionBD:

    user = "integraservicios_lqna_user"
    password = "T4hF17e0ujtlWuLhpiBEHFTRa10K5OxU"
    host = "dpg-cug0gl5ds78s73fq5j6g-a.oregon-postgres.render.com"
    port = 5432  # Puerto predeterminado para PostgreSQL
    dbname = "integraservicios_lqna"
 

    @staticmethod
    def conectar():
        """
        Establece una conexión a la base de datos PostgreSQL.
        """
        try:
            conexion = psycopg2.connect(
                user=ConexionBD.user,
                password=ConexionBD.password,
                host=ConexionBD.host,
                port=ConexionBD.port,
                dbname=ConexionBD.dbname
            )
            return conexion
        except Exception as e:
            print("Error de conexión:", e)
            return None

    @staticmethod
    def validarLogin(correo, contrasena):
        """
        Valida el login de un usuario comparando la contraseña encriptada.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return False

        try:
            cursor = conexion.cursor()
            query = "SELECT id_usuario, contrasena FROM usuario WHERE email = %s"
            cursor.execute(query, (correo,))
            result = cursor.fetchone()  # Obtiene una fila con (id_usuario, contrasena)

            if result:
                id_usuario, contrasena_encriptada = result  # Extrae los valores correctamente
                
                # Verificar la contraseña
                if PasswordHandler.verificar_contrasena(contrasena, contrasena_encriptada):
                    ConexionBD.idUsuarioValido = id_usuario
                    token = TokenHandler.generar_token(id_usuario)
                    return token 

            return False  # Si no hay resultado o la contraseña es incorrecta

        except Exception as e:
            print("Error en validarLogin:", e)
            return False
        finally:
            conexion.close()
    @staticmethod
    def registrarUsuario(nombre, email, telefono, contrasena):
        """
        Registra un nuevo usuario en la base de datos.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()

            # Verificar si el correo ya está registrado
            cursor.execute("SELECT ID_Usuario FROM Usuario WHERE Email = %s", (email,))
            if cursor.fetchone():
                return "El correo ya está registrado."

            contrasena_hash = PasswordHandler.hash_password(contrasena)
            # Insertar el nuevo usuario
            query = """
            INSERT INTO Usuario (Nombre, Email, Telefono, Contrasena)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (nombre, email, telefono, contrasena_hash))
            conexion.commit()

            return "Usuario registrado exitosamente."

        except Exception as e:
            return f"Error al registrar el usuario: {str(e)}"
        finally:
            conexion.close()
            
    @staticmethod
    def consultarUsuarios(id_usuario=None):
        """
        Consulta todos los usuarios o uno en específico por ID.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()
            if id_usuario:
                query = "SELECT ID_Usuario, Nombre, Email, Telefono FROM Usuario WHERE ID_Usuario = %s"
                cursor.execute(query, (id_usuario,))
                usuario = cursor.fetchone()
                if usuario:
                    return {"id_usuario": usuario[0], "nombre": usuario[1], "email": usuario[2], "telefono": usuario[3]}
                return "Usuario no encontrado."
            else:
                query = "SELECT ID_Usuario, Nombre, Email, Telefono FROM Usuario"
                cursor.execute(query)
                usuarios = cursor.fetchall()
                return [{"id_usuario": u[0], "nombre": u[1], "email": u[2], "telefono": u[3]} for u in usuarios]

        except Exception as e:
            return f"Error al consultar usuarios: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def actualizarUsuario(id_usuario, nombre=None, email=None, telefono=None, contrasena=None):
        """
        Actualiza la información de un usuario en la base de datos.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()
            campos = []
            valores = []

            if nombre:
                campos.append("Nombre = %s")
                valores.append(nombre)
            if email:
                campos.append("Email = %s")
                valores.append(email)
            if telefono:
                campos.append("Telefono = %s")
                valores.append(telefono)
            if contrasena:
                campos.append("Contrasena = %s")
                valores.append(contrasena)

            if not campos:
                return "Nada que actualizar."

            valores.append(id_usuario)
            query = f"UPDATE Usuario SET {', '.join(campos)} WHERE ID_Usuario = %s"
            cursor.execute(query, valores)
            conexion.commit()

            return "Usuario actualizado exitosamente."

        except Exception as e:
            return f"Error al actualizar el usuario: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def eliminarUsuario(id_usuario):
        """
        Elimina un usuario de la base de datos.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Usuario WHERE ID_Usuario = %s", (id_usuario,))
            conexion.commit()
            return "Usuario eliminado exitosamente."

        except Exception as e:
            return f"Error al eliminar el usuario: {str(e)}"
        finally:
            conexion.close()





    @staticmethod
    def crearReserva(id_usuario, id_tipo_recurso, fecha_reserva, hora_reserva):
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()

            # Validar si el usuario existe
            cursor.execute("SELECT ID_Usuario FROM Usuario WHERE ID_Usuario = %s", (id_usuario,))
            usuario_existe = cursor.fetchone()
            if not usuario_existe:
                return "El usuario no está registrado."

            # Obtener recursos disponibles dentro del tipo de recurso solicitado
            query_recursos = """
            SELECT Id_Recurso, Horario_Disponibilidad FROM Recurso
            WHERE ID_Tipo_Recurso = %s AND Estado = 'Disponible'
            """
            cursor.execute(query_recursos, (id_tipo_recurso,))
            recursos_disponibles = cursor.fetchall()

            if not recursos_disponibles:
                return "No hay recursos disponibles en este tipo."

            # Validar si algún recurso está disponible en el horario solicitado
            for id_recurso, horario in recursos_disponibles:
                if ConexionBD.validarHorarioDisponible(horario, hora_reserva):
                    # Verificar si el recurso ya está reservado en la fecha y hora
                    query_disponibilidad = """
                    SELECT ID_Reserva FROM Reserva WHERE ID_Recurso = %s AND Fecha_Reserva = %s AND Hora_Reserva = %s
                    """
                    cursor.execute(query_disponibilidad, (id_recurso, fecha_reserva, hora_reserva))
                    conflicto = cursor.fetchone()

                    if not conflicto:
                        # Insertar la reserva con el primer recurso disponible
                        query_reserva = """
                        INSERT INTO Reserva (ID_Usuario, ID_Recurso, Fecha_Reserva, Hora_Reserva, Estado)
                        VALUES (%s, %s, %s, %s, 'Vigente')
                        """
                        cursor.execute(query_reserva, (id_usuario, id_recurso, fecha_reserva, hora_reserva))
                        conexion.commit()
                        return f"Reserva creada exitosamente con el recurso ID {id_recurso}"

            return "No hay recursos disponibles en el horario solicitado."

        except Exception as e:
            
            return "Error al crear la reserva."
        finally:
            conexion.close()

    @staticmethod
    def validarHorarioDisponible(horario_disponibilidad, hora_reserva):
        """
        Verifica si la hora de la reserva está dentro del horario de disponibilidad.
        Formato esperado del horario: 'Lunes a Viernes 07:00-19:00'
        """
        import re
        match = re.search(r'(\d{2}:\d{2})-(\d{2}:\d{2})', horario_disponibilidad)
        if match:
            hora_inicio, hora_fin = match.groups()
            return hora_inicio <= hora_reserva.strftime("%H:%M") <= hora_fin
        return False
    @staticmethod
    def consultarReserva(idReserva=None):
        """
        Consultar una o todas las reservas.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor()
            query = "SELECT id_usuario, id_recurso, fecha_reserva, hora_reserva, estado FROM reserva"
            params = []
            if idReserva:
                query += " WHERE idreserva = %s"
                params.append(idReserva)
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print("Error al consultar las reservas:", e)
        finally:
            conexion.close()

    @staticmethod
    def actualizarReserva(idReserva, estado=None, detalles=None):
        """
        Actualizar el estado o los detalles de una reserva.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor()
            query = "UPDATE reserva SET "
            params = []
            updates = []

            if estado:
                updates.append("estado = %s")
                params.append(estado)
            if detalles:
                updates.append("detalles = %s")
                params.append(detalles)

            if not updates:
                return "Nada que actualizar"

            query += ", ".join(updates) + " WHERE idreserva = %s"
            params.append(idReserva)

            cursor.execute(query, params)
            conexion.commit()
            return "Reserva actualizada correctamente"
        except Exception as e:
            print("Error al actualizar la reserva:", e)
        finally:
            conexion.close()

    @staticmethod
    def eliminarReserva(idReserva):
        """
        Eliminar una reserva de la base de datos.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor()
            query = "DELETE FROM reserva WHERE idreserva = %s"
            cursor.execute(query, (idReserva,))
            conexion.commit()
            return "Reserva eliminada exitosamente"
        except Exception as e:
            print("Error al eliminar la reserva:", e)
        finally:
            conexion.close()
            
    @staticmethod
    def consultarRecursos(tipo_recurso=None, estado=None, nombre_recurso=None, orden=None, horario_disponibilidad=None):
        conexion = ConexionBD.conectar()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor()

            # Consulta base con JOIN para relacionar recurso y tipo_recurso
            query = """
            SELECT recurso.id_Recurso, recurso.nombre, tipo_recurso.nombre AS Tipo, recurso.horario_disponibilidad, recurso.estado
            FROM recurso
            JOIN tipo_recurso ON recurso.id_tipo_recurso = tipo_recurso.id_tipo_recurso
            WHERE 1=1
            """
            filtros = []
            parametros = []

            # Filtros dinámicos según los criterios proporcionados
            if tipo_recurso:
                filtros.append("tipo_recurso.nombre = %s")
                parametros.append(tipo_recurso)

            if estado:
                filtros.append("recurso.estado = %s")
                parametros.append(estado)

            if nombre_recurso:
                filtros.append("recurso.nombre ILIKE %s")
                parametros.append(f"%{nombre_recurso}%")

            if horario_disponibilidad:
                filtros.append("recurso.horario_disponibilidad ILIKE %s")
                parametros.append(f"%{horario_disponibilidad}%")

            # Aplicar los filtros dinámicamente
            if filtros:
                query += " AND " + " AND ".join(filtros)

            # Ordenamiento dinámico
            if orden:
                query += f" ORDER BY {orden}"

            cursor.execute(query, parametros)
            resultados = cursor.fetchall()

            # Convertir el resultado a una lista de diccionarios
            recursos = [{"id_recurso": r[0], "nombre": r[1], "tipo_recurso": r[2], "horario_disponibilidad": r[3], "estado": r[4]} for r in resultados]
            return recursos
        except Exception as e:
            return f"Error al consultar recursos: {str(e)}"
        finally:
            conexion.close()
            
    @staticmethod
    def consultarReservas(nombre_usuario= None,estado= None,tipo_filtro = None,fecha_inicio = None,fecha_fin = None):
        """
        Consulta las reservas de un usuario con diferentes filtros.
        
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."
        
        try:
            cursor = conexion.cursor()
            
            # Construimos la consulta base
            query = """
            SELECT r.id_reserva, r.fecha_reserva, r.hora_reserva, r.estado,
                u.nombre as nombre_usuario,
                rec.nombre as nombre_recurso
            FROM reserva r
            JOIN usuario u ON r.id_usuario = u.id_usuario
            JOIN recurso rec ON r.id_recurso = rec.id_recurso
            WHERE 1=1
            """
            params = []
            
            # Añadimos filtros según el tipo solicitado
           
            if tipo_filtro == 'Vigentes':
                query += " AND r.estado = %s"
                params.append('Vigente')
            elif tipo_filtro == 'Pasadas':
                query += " AND r.estado = %s"
                params.append('Pasado')
            elif tipo_filtro == 'Futuras':
                query += " AND r.estado = %s"
                params.append('Futura')
            
            # Añadimos filtro por rango de fechas si se especifica
            
          
            if nombre_usuario:
                query += " AND u.nombre ILIKE %s"
                params.append(f'%{nombre_usuario}%')
            if fecha_inicio:
                query += " AND r.fecha_reserva >= %s"
                params.append(fecha_inicio)
            if fecha_fin:
                query += " AND r.fecha_reserva <= %s"
                params.append(fecha_fin)
            
            # Ordenamos por fecha y hora
            query += " ORDER BY r.fecha_reserva DESC, r.hora_reserva DESC"
            
            cursor.execute(query, params)
            reservas = cursor.fetchall()
            
            # Convertimos los resultados a un formato más amigable
            resultado = []
            for reserva in reservas:
                resultado.append({
                    "id_reserva": reserva[0],
                    "fecha_reserva": reserva[1].strftime('%Y-%m-%d'),
                    "hora_reserva": reserva[2],
                    "estado": reserva[3],
                    "nombre_usuario": reserva[4],
                    "nombre_recurso": reserva[5]
                })
            
            return resultado
            
        except Exception as e:
            return f"Error al consultar las reservas: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def consultarReservasVigentes(id_usuario):
        """
        Retorna las reservas vigentes de un usuario.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()
            query = """
            SELECT ID_Reserva, Fecha_Reserva, Hora_Reserva, Estado, ID_Recurso
            FROM Reserva
            WHERE ID_Usuario = %s AND Estado = 'Vigente'
            """
            cursor.execute(query, (id_usuario,))
            reservas = cursor.fetchall()

            if not reservas:
                return "No hay reservas vigentes para este usuario."

            return [{"id_reserva": r[0], "fecha_reserva": str(r[1]), "hora_reserva": str(r[2]), "estado": r[3], "id_recurso": r[4]} for r in reservas]
        except Exception as e:
            return f"Error al consultar reservas vigentes: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def registrarPrestamo(id_reserva, id_empleado, fecha_prestamo, hora_prestamo):
        """
        Registra un préstamo verificando que el empleado exista y que la reserva esté vigente.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()

            # Validar que la reserva esté vigente
            cursor.execute("SELECT Estado FROM Reserva WHERE ID_Reserva = %s", (id_reserva,))
            reserva = cursor.fetchone()
            if not reserva:
                return "La reserva no existe."
            if reserva[0] != "Vigente":
                return "La reserva no está vigente."

            # Validar que el empleado exista
            cursor.execute("SELECT ID_Empleado FROM Empleado WHERE ID_Empleado = %s", (id_empleado,))
            empleado = cursor.fetchone()
            if not empleado:
                return "El empleado no está registrado."

            # Registrar el préstamo
            query_prestamo = """
            INSERT INTO Prestamo (ID_Reserva, ID_Empleado, Fecha_Prestamo, Hora_Prestamo)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_prestamo, (id_reserva, id_empleado, fecha_prestamo, hora_prestamo))
            conexion.commit()

            return "Préstamo registrado exitosamente."

        except Exception as e:
            return f"Error al registrar el préstamo: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def consultarPrestamosVigentes(id_usuario):
        """
        Retorna los préstamos vigentes de un usuario.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()
            query = """
            SELECT p.ID_Prestamo, p.Fecha_Prestamo, p.Hora_Prestamo, p.ID_Empleado, r.ID_Reserva, r.ID_Recurso
            FROM Prestamo p
            JOIN Reserva r ON p.ID_Reserva = r.ID_Reserva
            WHERE r.ID_Usuario = %s
            """
            cursor.execute(query, (id_usuario,))
            prestamos = cursor.fetchall()

            if not prestamos:
                return "No hay préstamos vigentes para este usuario."

            return [{"id_prestamo": p[0], "fecha_prestamo": str(p[1]), "hora_prestamo": str(p[2]), "id_empleado": p[3], "id_reserva": p[4], "id_recurso": p[5]} for p in prestamos]
        except Exception as e:
            return f"Error al consultar préstamos vigentes: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def registrarDevolucion(id_prestamo, fecha_devolucion, hora_devolucion, id_empleado):
        """
        Registra una devolución validando que el préstamo exista y que el empleado esté registrado.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()

            # Validar que el préstamo existe
            cursor.execute("SELECT ID_Prestamo FROM Prestamo WHERE ID_Prestamo = %s", (id_prestamo,))
            prestamo = cursor.fetchone()
            if not prestamo:
                return "El préstamo no existe."

            # Validar que el empleado esté registrado
            cursor.execute("SELECT ID_Empleado FROM Empleado WHERE ID_Empleado = %s", (id_empleado,))
            empleado = cursor.fetchone()
            if not empleado:
                return "El empleado no está registrado."

            # Registrar la devolución
            query_devolucion = """
            INSERT INTO Devolucion (ID_Prestamo, Fecha_Devolucion, Hora_Devolucion)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query_devolucion, (id_prestamo, fecha_devolucion, hora_devolucion))
            conexion.commit()

            return "Devolución registrada exitosamente."

        except Exception as e:
            return f"Error al registrar la devolución: {str(e)}"
        finally:
            conexion.close()

    @staticmethod
    def consultarRecursosDisponibles():
        """
        Retorna una lista de los recursos disponibles en el sistema.
        """
        conexion = ConexionBD.conectar()
        if not conexion:
            return "Error al conectar con la base de datos."

        try:
            cursor = conexion.cursor()
            query = """
            SELECT R.ID_Recurso, R.Nombre, T.Nombre AS Tipo_Recurso, R.Horario_Disponibilidad
            FROM Recurso R
            JOIN Tipo_Recurso T ON R.ID_Tipo_Recurso = T.ID_Tipo_Recurso
            WHERE R.Estado = 'Disponible'
            """
            cursor.execute(query)
            recursos = cursor.fetchall()

            if not recursos:
                return {"recursos_disponibles": []}  # Retornar lista vacía si no hay recursos.

            def transformar_horario(horario):
                """
                Convierte un rango de días en una lista con cada día y su horario.
                """
                dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                resultado = []

                # Buscar el formato "Lunes a Viernes 08:00-18:00"
                import re
                match = re.match(r"(\w+) a (\w+) (\d{2}:\d{2}-\d{2}:\d{2})", horario)

                if match:
                    dia_inicio, dia_fin, horas = match.groups()
                    if dia_inicio in dias_semana and dia_fin in dias_semana:
                        i_inicio = dias_semana.index(dia_inicio)
                        i_fin = dias_semana.index(dia_fin)
                        resultado = [f"{dias_semana[i]} {horas}" for i in range(i_inicio, i_fin + 1)]
                else:
                    # Si el formato es solo un día específico
                    partes = horario.split()
                    if len(partes) == 2 and partes[0] in dias_semana:
                        resultado = [horario]

                return resultado

            recursos_formateados = []
            for r in recursos:
                recurso = {
                    "id_recurso": r[0],
                    "nombre": r[1],
                    "tipo_recurso": r[2],
                    "horario_disponibilidad": transformar_horario(r[3])
                }
                recursos_formateados.append(recurso)

            return recursos_formateados

        except Exception as e:
            return f"Error al consultar recursos disponibles: {str(e)}"
        finally:
            conexion.close()

