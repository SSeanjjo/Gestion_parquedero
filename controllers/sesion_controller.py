from config.db import get_connection
from models import sesion_parqueo_model, espacio_parqueo_model


def get_all():
    try:
        conn = get_connection()
        data = sesion_parqueo_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        new_id = sesion_parqueo_model.create(conn, data)
        # Marcar espacio como Ocupado
        espacio_parqueo_model.update_estado(conn, data['id_espacio'], 'Ocupado')
        conn.close()
        return True, f"Sesión #{new_id} abierta exitosamente."
    except Exception as e:
        return False, str(e)


def close_session(id_sesion, fecha_fin):
    try:
        conn = get_connection()
        valor = sesion_parqueo_model.close_session(conn, id_sesion, fecha_fin)
        conn.close()
        return True, f"Sesión cerrada. Total: ${valor:,.2f}"
    except Exception as e:
        return False, str(e)


def delete(id_sesion):
    try:
        conn = get_connection()
        sesion_parqueo_model.delete(conn, id_sesion)
        conn.close()
        return True, "Sesión eliminada exitosamente."
    except Exception as e:
        return False, str(e)
