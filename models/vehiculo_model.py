def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.id_vehiculo, v.placa, v.color, v.marca, v.modelo,
               v.cedula_usuario,
               CONCAT(u.primer_nombre, ' ', u.primer_apellido) AS nombre_usuario,
               v.id_tipo_vehiculo,
               tv.nombre AS tipo_vehiculo
        FROM Vehiculo v
        JOIN Usuario     u  ON v.cedula_usuario   = u.cedula
        JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        ORDER BY v.placa
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_vehiculo):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Vehiculo WHERE id_vehiculo = %s",
        (id_vehiculo,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Vehiculo
           (placa, color, marca, modelo, cedula_usuario, id_tipo_vehiculo)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data['placa'],
         data.get('color') or None,
         data.get('marca') or None,
         data.get('modelo') or None,
         data['cedula_usuario'],
         data['id_tipo_vehiculo'])
    )
    conn.commit()
    cursor.close()


def update(conn, id_vehiculo, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Vehiculo SET
           placa=%s, color=%s, marca=%s, modelo=%s,
           cedula_usuario=%s, id_tipo_vehiculo=%s
           WHERE id_vehiculo=%s""",
        (data['placa'],
         data.get('color') or None,
         data.get('marca') or None,
         data.get('modelo') or None,
         data['cedula_usuario'],
         data['id_tipo_vehiculo'],
         id_vehiculo)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_vehiculo):
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM SesionParqueo WHERE id_vehiculo = %s AND fecha_fin IS NULL",
        (id_vehiculo,)
    )
    activas = cursor.fetchone()[0]
    if activas:
        cursor.close()
        raise ValueError("No se puede eliminar: el vehículo tiene una sesión de parqueo activa.")

    cursor.execute(
        "SELECT COUNT(*) FROM SesionParqueo WHERE id_vehiculo = %s",
        (id_vehiculo,)
    )
    total = cursor.fetchone()[0]
    if total:
        cursor.close()
        raise ValueError(
            f"No se puede eliminar: el vehículo tiene {total} sesión(es) en el historial. "
            "Elimine primero las sesiones desde el módulo Sesiones."
        )

    cursor.execute("DELETE FROM Vehiculo WHERE id_vehiculo = %s", (id_vehiculo,))
    conn.commit()
    cursor.close()


def get_all_for_dropdown(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_vehiculo, placa FROM Vehiculo ORDER BY placa"
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def get_without_subscription(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.id_vehiculo, v.placa
        FROM Vehiculo v
        LEFT JOIN Suscripcion s ON v.id_vehiculo = s.id_vehiculo
        WHERE s.id_vehiculo IS NULL
        ORDER BY v.placa
    """)
    result = cursor.fetchall()
    cursor.close()
    return result
