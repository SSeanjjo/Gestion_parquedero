from config.db import get_connection
from models import usuario_model


def login(cedula, contrasena):
    try:
        conn = get_connection()
        user = usuario_model.login(conn, cedula, contrasena)
        conn.close()
        if user:
            return True, user
        return False, "Cédula o contraseña incorrecta."
    except Exception as e:
        return False, str(e)


def get_all():
    try:
        conn = get_connection()
        data = usuario_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_by_cedula(cedula):
    try:
        conn = get_connection()
        data = usuario_model.get_by_cedula(conn, cedula)
        sub_admin = usuario_model.get_administrador(conn, cedula)
        sub_op = usuario_model.get_operador(conn, cedula)
        sub_sus = usuario_model.get_suscriptor(conn, cedula)
        conn.close()
        return True, (data, sub_admin, sub_op, sub_sus)
    except Exception as e:
        return False, str(e)


def get_all_for_dropdown():
    try:
        conn = get_connection()
        data = usuario_model.get_all_for_dropdown(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        usuario_model.create_usuario(conn, data)
        rol = data.get('rol', '')
        if rol == 'Administrador':
            usuario_model.create_administrador(conn, data['cedula'], data)
        elif rol == 'Operador':
            usuario_model.create_operador(conn, data['cedula'], data)
        elif rol == 'Suscriptor':
            usuario_model.create_suscriptor(conn, data['cedula'], data)
        conn.close()
        return True, "Usuario creado exitosamente."
    except Exception as e:
        return False, str(e)


def update(cedula, data):
    try:
        conn = get_connection()
        usuario_model.update_usuario(conn, cedula, data)
        rol = data.get('rol', '')
        if rol == 'Administrador':
            existing = usuario_model.get_administrador(conn, cedula)
            if existing:
                usuario_model.update_administrador(conn, cedula, data)
        elif rol == 'Operador':
            existing = usuario_model.get_operador(conn, cedula)
            if existing:
                usuario_model.update_operador(conn, cedula, data)
        elif rol == 'Suscriptor':
            existing = usuario_model.get_suscriptor(conn, cedula)
            if existing:
                usuario_model.update_suscriptor(conn, cedula, data)
        conn.close()
        return True, "Usuario actualizado exitosamente."
    except Exception as e:
        return False, str(e)


def delete(cedula):
    try:
        conn = get_connection()
        usuario_model.delete_usuario(conn, cedula)
        conn.close()
        return True, "Usuario eliminado exitosamente."
    except Exception as e:
        return False, str(e)
