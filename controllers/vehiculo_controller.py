from config.db import get_connection
from models import vehiculo_model


def get_all():
    try:
        conn = get_connection()
        data = vehiculo_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_all_for_dropdown():
    try:
        conn = get_connection()
        data = vehiculo_model.get_all_for_dropdown(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_without_subscription():
    try:
        conn = get_connection()
        data = vehiculo_model.get_without_subscription(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        vehiculo_model.create(conn, data)
        conn.close()
        return True, "Vehículo registrado exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_vehiculo, data):
    try:
        conn = get_connection()
        vehiculo_model.update(conn, id_vehiculo, data)
        conn.close()
        return True, "Vehículo actualizado exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_vehiculo):
    try:
        conn = get_connection()
        vehiculo_model.delete(conn, id_vehiculo)
        conn.close()
        return True, "Vehículo eliminado exitosamente."
    except Exception as e:
        return False, str(e)
