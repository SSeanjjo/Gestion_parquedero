def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_suscripcion, s.fecha_inicio, s.fecha_final, s.estado,
               s.descuento, s.horario_permitido_inicio, s.horario_permitido_final,
               s.id_vehiculo, v.placa,
               s.id_empresa, e.nombre AS nombre_empresa
        FROM Suscripcion s
        JOIN Vehiculo v ON s.id_vehiculo = v.id_vehiculo
        LEFT JOIN Empresa e ON s.id_empresa = e.id_empresa
        ORDER BY s.fecha_inicio DESC
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


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Suscripcion
           (fecha_inicio, fecha_final, estado, descuento,
            horario_permitido_inicio, horario_permitido_final,
            id_vehiculo, id_empresa)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (data['fecha_inicio'], data['fecha_final'],
         data.get('estado', 'Activa'),
         data.get('descuento', 0),
         data.get('horario_permitido_inicio') or None,
         data.get('horario_permitido_final') or None,
         data['id_vehiculo'],
         data.get('id_empresa') or None)
    )
    conn.commit()
    cursor.close()


def update(conn, id_suscripcion, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Suscripcion SET
           fecha_inicio=%s, fecha_final=%s, estado=%s, descuento=%s,
           horario_permitido_inicio=%s, horario_permitido_final=%s,
           id_vehiculo=%s, id_empresa=%s
           WHERE id_suscripcion=%s""",
        (data['fecha_inicio'], data['fecha_final'],
         data.get('estado', 'Activa'),
         data.get('descuento', 0),
         data.get('horario_permitido_inicio') or None,
         data.get('horario_permitido_final') or None,
         data['id_vehiculo'],
         data.get('id_empresa') or None,
         id_suscripcion)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_suscripcion):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Suscripcion WHERE id_suscripcion = %s",
        (id_suscripcion,)
    )
    conn.commit()
    cursor.close()
