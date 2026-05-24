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
        data = empresa_model.get_all_for_dropdown_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data, id_suscriptor=None):
    try:
        conn = get_connection()
        new_id = suscripcion_model.create(conn, data)
        if id_suscriptor:
            suscripcion_model.link_suscriptor(conn, id_suscriptor, new_id)
        conn.close()
        return True, f"Suscripción #{new_id} creada exitosamente."
    except Exception as e:
        return False, str(e)


def extend_fecha_final(id_suscripcion, nueva_fecha_final):
    try:
        conn = get_connection()
        suscripcion_model.extend_fecha_final(conn, id_suscripcion, nueva_fecha_final)
        conn.close()
        return True, "Fecha final extendida exitosamente."
    except Exception as e:
        return False, str(e)


def cancel(id_suscripcion):
    try:
        conn = get_connection()
        suscripcion_model.cancel(conn, id_suscripcion)
        conn.close()
        return True, "Suscripción cancelada exitosamente."
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


# Reportes
def reporte_activas():
    try:
        conn = get_connection()
        data = suscripcion_model.reporte_activas(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def reporte_por_empresa_convenio():
    try:
        conn = get_connection()
        data = suscripcion_model.reporte_por_empresa_convenio(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def reporte_ahorro_suscripcion():
    try:
        conn = get_connection()
        data = suscripcion_model.reporte_ahorro_suscripcion(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)
