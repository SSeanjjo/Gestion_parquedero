from config.db import get_connection
from models import empresa_model


def get_all():
    try:
        conn = get_connection()
        data = empresa_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        empresa_model.create(conn, data)
        conn.close()
        return True, "Empresa registrada exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_empresa, data):
    try:
        conn = get_connection()
        empresa_model.update(conn, id_empresa, data)
        conn.close()
        return True, "Empresa actualizada exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_empresa):
    try:
        conn = get_connection()
        empresa_model.delete(conn, id_empresa)
        conn.close()
        return True, "Empresa eliminada exitosamente."
    except Exception as e:
        return False, str(e)
