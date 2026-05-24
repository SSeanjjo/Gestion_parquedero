def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_suscripcion, s.fecha_inicio, s.fecha_final, s.estado,
               s.horario_permitido_inicio, s.horario_permitido_final,
               s.id_vehiculo, v.placa,
               tv.nombre AS tipo_vehiculo,
               CONCAT(u.primer_nombre,' ',u.primer_apellido) AS propietario,
               ss.id_suscriptor,
               CONCAT(us.primer_nombre,' ',us.primer_apellido) AS nombre_suscriptor
        FROM Suscripcion s
        JOIN Vehiculo v ON s.id_vehiculo = v.id_vehiculo
        JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        JOIN Usuario u ON v.cedula_usuario = u.cedula
        LEFT JOIN SuscriptorSuscripcion ss ON s.id_suscripcion = ss.id_suscripcion
        LEFT JOIN Usuario us ON ss.id_suscriptor = us.cedula
        ORDER BY s.fecha_final ASC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_all_with_convenio(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_suscripcion, s.fecha_inicio, s.fecha_final, s.estado,
               v.placa, tv.nombre AS tipo_vehiculo,
               e.nombre AS nombre_empresa,
               c.porcentaje_descuento, c.estado AS estado_convenio
        FROM Suscripcion s
        JOIN Vehiculo v ON s.id_vehiculo = v.id_vehiculo
        JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        LEFT JOIN Empresa e ON v.id_empresa = e.id_empresa
        LEFT JOIN Convenio c ON c.id_empresa = e.id_empresa AND c.estado = 'activo'
        WHERE v.id_empresa IS NOT NULL
        ORDER BY e.nombre, s.fecha_final ASC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_suscripcion):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Suscripcion WHERE id_suscripcion = %s",
        (id_suscripcion,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def get_active_by_vehiculo(conn, id_vehiculo):
    from datetime import date
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM Suscripcion
           WHERE id_vehiculo = %s AND estado = 'Activa' AND fecha_final >= %s
           ORDER BY fecha_final DESC LIMIT 1""",
        (id_vehiculo, date.today().isoformat())
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Suscripcion
           (fecha_inicio, fecha_final, estado,
            horario_permitido_inicio, horario_permitido_final, id_vehiculo)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data['fecha_inicio'], data['fecha_final'],
         data.get('estado', 'Activa'),
         data.get('horario_permitido_inicio') or None,
         data.get('horario_permitido_final') or None,
         data['id_vehiculo'])
    )
    new_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    return new_id


def link_suscriptor(conn, id_suscriptor, id_suscripcion):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT IGNORE INTO SuscriptorSuscripcion (id_suscriptor, id_suscripcion)
           VALUES (%s, %s)""",
        (id_suscriptor, id_suscripcion)
    )
    conn.commit()
    cursor.close()


def extend_fecha_final(conn, id_suscripcion, nueva_fecha_final):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Suscripcion SET fecha_final=%s WHERE id_suscripcion=%s",
        (nueva_fecha_final, id_suscripcion)
    )
    conn.commit()
    cursor.close()


def cancel(conn, id_suscripcion):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Suscripcion SET estado='cancelado' WHERE id_suscripcion=%s",
        (id_suscripcion,)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_suscripcion):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Suscripcion WHERE id_suscripcion = %s", (id_suscripcion,))
    conn.commit()
    cursor.close()


# -----------------------------------------------------------------------
# Reportes CRUD 3
# -----------------------------------------------------------------------

def reporte_activas(conn):
    from datetime import date
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_suscripcion, s.fecha_inicio, s.fecha_final, s.estado,
               v.placa,
               DATEDIFF(s.fecha_final, CURDATE()) AS dias_restantes
        FROM Suscripcion s
        JOIN Vehiculo v ON s.id_vehiculo = v.id_vehiculo
        WHERE s.estado = 'Activa' AND s.fecha_final >= CURDATE()
        ORDER BY s.fecha_final ASC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def reporte_por_empresa_convenio(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.nombre AS empresa, e.estado_convenio,
               c.porcentaje_descuento, c.estado AS estado_convenio_actual,
               v.placa, tv.nombre AS tipo_vehiculo,
               s.id_suscripcion, s.estado AS estado_suscripcion,
               s.fecha_final
        FROM Empresa e
        JOIN Convenio c ON c.id_empresa = e.id_empresa
        JOIN Vehiculo v ON v.id_empresa = e.id_empresa
        JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        LEFT JOIN Suscripcion s ON s.id_vehiculo = v.id_vehiculo
                                AND s.estado = 'Activa'
                                AND s.fecha_final >= CURDATE()
        ORDER BY e.nombre, v.placa
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def reporte_ahorro_suscripcion(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_suscripcion,
               v.placa,
               s.fecha_inicio, s.fecha_final, s.estado,
               COUNT(sp.id_sesion) AS sesiones_realizadas,
               t.valor_hora,
               COALESCE(SUM(f.valor_total), 0) AS pagado_con_suscripcion,
               COALESCE(SUM(sp.tiempo), 0) * t.valor_hora AS habria_pagado_sin_suscripcion,
               (COALESCE(SUM(sp.tiempo), 0) * t.valor_hora)
                 - COALESCE(SUM(f.valor_total), 0) AS ahorro
        FROM Suscripcion s
        JOIN Vehiculo v ON s.id_vehiculo = v.id_vehiculo
        JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        JOIN Tarifa t ON t.id_tipo_vehiculo = tv.id_tipo_vehiculo
        LEFT JOIN SesionParqueo sp ON sp.id_vehiculo = v.id_vehiculo
                                   AND sp.fecha_inicio >= s.fecha_inicio
                                   AND (sp.fecha_fin IS NULL OR sp.fecha_fin <= s.fecha_final)
        LEFT JOIN Factura f ON f.id_sesion = sp.id_sesion
        GROUP BY s.id_suscripcion, v.placa, s.fecha_inicio,
                 s.fecha_final, s.estado, t.valor_hora
        ORDER BY ahorro DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result
