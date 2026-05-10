from config.db import get_connection
from models import multa_model, sesion_parqueo_model


def get_all():
    try:
        conn = get_connection()
        data = multa_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_sesiones_cerradas():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id_sesion,
                   CONCAT('#', s.id_sesion, ' - ', v.placa) AS descripcion
            FROM SesionParqueo s
            JOIN Vehiculo v ON s.id_vehiculo = v.id_vehiculo
            WHERE s.fecha_fin IS NOT NULL
              AND s.id_sesion NOT IN (SELECT id_sesion FROM Multa)
            ORDER BY s.fecha_inicio DESC
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def create(data):
    try:
        conn = get_connection()
        multa_model.create(conn, data)
        conn.close()
        return True, "Multa registrada exitosamente."
    except Exception as e:
        return False, str(e)


def update(id_multa, data):
    try:
        conn = get_connection()
        multa_model.update(conn, id_multa, data)
        conn.close()
        return True, "Multa actualizada exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_multa):
    try:
        conn = get_connection()
        multa_model.delete(conn, id_multa)
        conn.close()
        return True, "Multa eliminada exitosamente."
    except Exception as e:
        return False, str(e)
