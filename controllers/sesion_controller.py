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


def get_libres_compatibles(id_vehiculo):
    """Retorna espacios libres compatibles con el tipo de vehículo."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT tv.nombre AS tipo_vehiculo
               FROM Vehiculo v
               JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
               WHERE v.id_vehiculo = %s""",
            (id_vehiculo,)
        )
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return True, []
        tipo_v = row['tipo_vehiculo']
        if tipo_v == 'Moto':
            cursor.execute("""
                SELECT e.id_espacio,
                       CONCAT('Esp.', e.numero, ' (', e.tipo_espacio, ') - ', z.nombre) AS descripcion
                FROM EspacioParqueo e
                JOIN Zona z ON e.id_zona = z.id_zona
                WHERE e.estado = 'Libre' AND e.tipo_espacio = 'Motos'
                ORDER BY z.nombre, e.numero
            """)
        else:
            cursor.execute("""
                SELECT e.id_espacio,
                       CONCAT('Esp.', e.numero, ' (', e.tipo_espacio, ') - ', z.nombre) AS descripcion
                FROM EspacioParqueo e
                JOIN Zona z ON e.id_zona = z.id_zona
                WHERE e.estado = 'Libre' AND e.tipo_espacio != 'Motos'
                ORDER BY z.nombre, e.numero
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
        valid, msg = sesion_parqueo_model.validate_espacio_vehiculo(
            conn, data['id_vehiculo'], data['id_espacio']
        )
        if not valid:
            conn.close()
            return False, msg
        new_id = sesion_parqueo_model.create(conn, data)
        espacio_parqueo_model.update_estado(conn, data['id_espacio'], 'Ocupado')
        conn.close()
        return True, f"Sesión #{new_id} abierta exitosamente."
    except Exception as e:
        return False, str(e)


def close_session(id_sesion, fecha_fin):
    try:
        conn = get_connection()
        valor, tipo_cobro = sesion_parqueo_model.close_session(conn, id_sesion, fecha_fin)
        conn.close()
        return True, f"Sesión cerrada. Total: ${valor:,.2f} — {tipo_cobro}"
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


# Reportes
def reporte_ocupacion_zonas(fecha_inicio, fecha_fin):
    try:
        conn = get_connection()
        data = sesion_parqueo_model.reporte_ocupacion_zonas(conn, fecha_inicio, fecha_fin)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)


def reporte_ganancias_mensuales():
    try:
        conn = get_connection()
        data = sesion_parqueo_model.reporte_ganancias_mensuales(conn)
        conn.close()
        return True, data
    except Exception as e:
        return False, str(e)
