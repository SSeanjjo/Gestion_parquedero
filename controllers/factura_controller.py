from config.db import get_connection
from models import factura_model


def get_all():
    try:
        conn = get_connection()
        data = factura_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def mark_as_paid(id_factura):
    try:
        conn = get_connection()
        factura_model.mark_as_paid(conn, id_factura)
        conn.close()
        return True, f"Factura #{id_factura} marcada como Pagada."
    except Exception as e:
        return False, str(e)


def delete(id_factura):
    try:
        conn = get_connection()
        factura_model.delete(conn, id_factura)
        conn.close()
        return True, f"Factura #{id_factura} eliminada."
    except Exception as e:
        return False, str(e)


def reporte_por_tipo_cobro():
    try:
        conn = get_connection()
        data = factura_model.reporte_por_tipo_cobro(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def reporte_pendientes():
    try:
        conn = get_connection()
        data = factura_model.reporte_pendientes(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)
