from config.db import get_connection
from models import espacio_parqueo_model, zona_model


def get_all():
    try:
        conn = get_connection()
        data = espacio_parqueo_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_libres():
    try:
        conn = get_connection()
        data = espacio_parqueo_model.get_libres(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_zonas():
    try:
        conn = get_connection()
        data = zona_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        espacio_parqueo_model.create(conn, data)
        conn.close()
        return True, "Espacio creado exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_espacio, data):
    try:
        conn = get_connection()
        espacio_parqueo_model.update(conn, id_espacio, data)
        conn.close()
        return True, "Espacio actualizado exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_espacio):
    try:
        conn = get_connection()
        espacio_parqueo_model.delete(conn, id_espacio)
        conn.close()
        return True, "Espacio eliminado exitosamente."
    except Exception as e:
        return False, str(e)
