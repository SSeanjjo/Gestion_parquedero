def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_sesion, s.fecha_inicio, s.fecha_fin, s.tiempo,
               s.id_vehiculo, v.placa,
               s.id_espacio,
               CONCAT('Esp.', ep.numero, ' - ', z.nombre) AS espacio_desc,
               CASE WHEN s.fecha_fin IS NULL THEN 'Activa' ELSE 'Cerrada' END AS estado
        FROM SesionParqueo s
        JOIN Vehiculo       v  ON s.id_vehiculo = v.id_vehiculo
        JOIN EspacioParqueo ep ON s.id_espacio  = ep.id_espacio
        JOIN Zona           z  ON ep.id_zona    = z.id_zona
        ORDER BY s.fecha_inicio DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_active(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_sesion, s.fecha_inicio,
               v.placa,
               CONCAT('Esp.', ep.numero, ' - ', z.nombre) AS espacio_desc
        FROM SesionParqueo s
        JOIN Vehiculo       v  ON s.id_vehiculo = v.id_vehiculo
        JOIN EspacioParqueo ep ON s.id_espacio  = ep.id_espacio
        JOIN Zona           z  ON ep.id_zona    = z.id_zona
        WHERE s.fecha_fin IS NULL
        ORDER BY s.fecha_inicio
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_sesion):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM SesionParqueo WHERE id_sesion = %s",
        (id_sesion,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO SesionParqueo (fecha_inicio, id_vehiculo, id_espacio)
           VALUES (%s, %s, %s)""",
        (data['fecha_inicio'], data['id_vehiculo'], data['id_espacio'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id


def close_session(conn, id_sesion, fecha_fin):
    """Cierra la sesión: calcula tiempo y genera la Factura automáticamente."""
    cursor = conn.cursor(dictionary=True)

    # Obtener datos de la sesión y tarifa
    cursor.execute("""
        SELECT s.id_sesion, s.fecha_inicio, s.id_vehiculo, s.id_espacio,
               v.id_tipo_vehiculo, t.id_tarifa, t.valor_hora
        FROM SesionParqueo s
        JOIN Vehiculo    v ON s.id_vehiculo    = v.id_vehiculo
        JOIN Tarifa      t ON v.id_tipo_vehiculo = t.id_tipo_vehiculo
        WHERE s.id_sesion = %s AND s.fecha_fin IS NULL
    """, (id_sesion,))
    sesion = cursor.fetchone()

    if not sesion:
        cursor.close()
        raise ValueError("Sesión no encontrada o ya cerrada.")

    from datetime import datetime
    if isinstance(fecha_fin, str):
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d %H:%M:%S")
    else:
        fecha_fin_dt = fecha_fin

    if isinstance(sesion['fecha_inicio'], str):
        fecha_inicio_dt = datetime.strptime(sesion['fecha_inicio'], "%Y-%m-%d %H:%M:%S")
    else:
        fecha_inicio_dt = sesion['fecha_inicio']

    duracion_horas = (fecha_fin_dt - fecha_inicio_dt).total_seconds() / 3600
    duracion_horas = round(duracion_horas, 2)
    valor_total = round(duracion_horas * float(sesion['valor_hora']), 2)

    # Actualizar la sesión
    cursor.execute(
        """UPDATE SesionParqueo SET fecha_fin=%s, tiempo=%s
           WHERE id_sesion=%s""",
        (fecha_fin_dt, duracion_horas, id_sesion)
    )

    # Liberar el espacio
    cursor.execute(
        "UPDATE EspacioParqueo SET estado='Libre' WHERE id_espacio=%s",
        (sesion['id_espacio'],)
    )

    # Crear la factura
    cursor.execute(
        """INSERT INTO Factura
           (fecha_ingreso, fecha_salida, tiempo, valor_total, estado_pago, id_sesion, id_tarifa)
           VALUES (%s, %s, %s, %s, 'Pendiente', %s, %s)""",
        (sesion['fecha_inicio'], fecha_fin_dt, duracion_horas, valor_total,
         id_sesion, sesion['id_tarifa'])
    )

    conn.commit()
    cursor.close()
    return valor_total


def delete(conn, id_sesion):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM SesionParqueo WHERE id_sesion = %s",
        (id_sesion,)
    )
    conn.commit()
    cursor.close()
