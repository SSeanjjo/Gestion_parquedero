from config.db import get_connection
from models import suscripcion_model, vehiculo_model, empresa_model


def get_all():
    try:
        conn = get_connection()
        data = suscripcion_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_vehiculos_sin_suscripcion():
    try:
        conn = get_connection()
        data = vehiculo_model.get_without_subscription(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_vehiculos():
    try:
        conn = get_connection()
        data = vehiculo_model.get_all_for_dropdown(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_empresas():
    try:
        conn = get_connection()
        data = empresa_model.get_all_for_dropdown(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        suscripcion_model.create(conn, data)
        conn.close()
        return True, "Suscripción creada exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_suscripcion, data):
    try:
        conn = get_connection()
        suscripcion_model.update(conn, id_suscripcion, data)
        conn.close()
        return True, "Suscripción actualizada exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_suscripcion):
    try:
        conn = get_connection()
        suscripcion_model.delete(conn, id_suscripcion)
        conn.close()
        return True, "Suscripción eliminada exitosamente."
    except Exception as e:
        return False, str(e)
