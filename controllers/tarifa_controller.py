from config.db import get_connection
from models import tarifa_model, tipo_vehiculo_model


def get_all():
    try:
        conn = get_connection()
        data = tarifa_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_tipos_vehiculo():
    try:
        conn = get_connection()
        data = tipo_vehiculo_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        tarifa_model.create(conn, data)
        conn.close()
        return True, "Tarifa creada exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_tarifa, data):
    try:
        conn = get_connection()
        tarifa_model.update(conn, id_tarifa, data)
        conn.close()
        return True, "Tarifa actualizada exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_tarifa):
    try:
        conn = get_connection()
        tarifa_model.delete(conn, id_tarifa)
        conn.close()
        return True, "Tarifa eliminada exitosamente."
    except Exception as e:
        return False, str(e)
