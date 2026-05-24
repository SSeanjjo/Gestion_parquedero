from config.db import get_connection
from models import turno_model, usuario_model


def get_all():
    try:
        conn = get_connection()
        data = turno_model.get_all(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def get_operadores():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.cedula,
                   CONCAT(u.primer_nombre,' ',u.primer_apellido) AS nombre
            FROM Operador o
            JOIN Usuario u ON o.cedula = u.cedula
            ORDER BY u.primer_apellido
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
        turno_model.create(conn, data)
        conn.close()
        return True, "Turno registrado exitosamente."
    except Exception as e:
        return False, str(e)


def delete(id_turno):
    try:
        conn = get_connection()
        turno_model.delete(conn, id_turno)
        conn.close()
        return True, "Turno eliminado exitosamente."
    except Exception as e:
        return False, str(e)
