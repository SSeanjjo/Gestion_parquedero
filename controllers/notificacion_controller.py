from config.db import get_connection
from models import notificacion_model


def get_all():
    try:
        conn = get_connection()
        data = notificacion_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        notificacion_model.create(conn, data)
        conn.close()
        return True, "Notificación enviada exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_notificacion, data):
    try:
        conn = get_connection()
        notificacion_model.update(conn, id_notificacion, data)
        conn.close()
        return True, "Notificación actualizada exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_notificacion):
    try:
        conn = get_connection()
        notificacion_model.delete(conn, id_notificacion)
        conn.close()
        return True, "Notificación eliminada exitosamente."
    except Exception as e:
        return False, str(e)
