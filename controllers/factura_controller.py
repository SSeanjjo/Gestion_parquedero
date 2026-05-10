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


def update_estado(id_factura, estado_pago):
    try:
        conn = get_connection()
        factura_model.update_estado(conn, id_factura, estado_pago)
        conn.close()
        return True, "Estado de factura actualizado."
    except Exception as e:
        return False, str(e)


def delete(id_factura):
    try:
        conn = get_connection()
        factura_model.delete(conn, id_factura)
        conn.close()
        return True, "Factura eliminada exitosamente."
    except Exception as e:
        return False, str(e)
