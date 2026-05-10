def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT n.id_notificacion, n.fecha, n.mensaje, n.tipo_notificacion,
               n.cedula_usuario,
               CONCAT(u.primer_nombre, ' ', u.primer_apellido) AS nombre_usuario
        FROM Notificacion n
        JOIN Usuario u ON n.cedula_usuario = u.cedula
        ORDER BY n.fecha DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_notificacion):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Notificacion WHERE id_notificacion = %s",
        (id_notificacion,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Notificacion (fecha, mensaje, tipo_notificacion, cedula_usuario)
           VALUES (%s, %s, %s, %s)""",
        (data['fecha'],
         data['mensaje'],
         data.get('tipo_notificacion') or None,
         data['cedula_usuario'])
    )
    conn.commit()
    cursor.close()


def update(conn, id_notificacion, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Notificacion SET fecha=%s, mensaje=%s, tipo_notificacion=%s, cedula_usuario=%s
           WHERE id_notificacion=%s""",
        (data['fecha'],
         data['mensaje'],
         data.get('tipo_notificacion') or None,
         data['cedula_usuario'],
         id_notificacion)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_notificacion):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Notificacion WHERE id_notificacion = %s",
        (id_notificacion,)
    )
    conn.commit()
    cursor.close()
