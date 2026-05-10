from config.db import get_connection
from models import zona_model


def get_all():
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
        zona_model.create(conn, data)
        conn.close()
        return True, "Zona creada exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_zona, data):
    try:
        conn = get_connection()
        zona_model.update(conn, id_zona, data)
        conn.close()
        return True, "Zona actualizada exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_zona):
    try:
        conn = get_connection()
        zona_model.delete(conn, id_zona)
        conn.close()
        return True, "Zona eliminada exitosamente."
    except Exception as e:
        return False, str(e)
