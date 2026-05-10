def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_tipo_vehiculo, nombre FROM TipoVehiculo ORDER BY nombre"
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_tipo_vehiculo):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM TipoVehiculo WHERE id_tipo_vehiculo = %s",
        (id_tipo_vehiculo,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, nombre):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO TipoVehiculo (nombre) VALUES (%s)",
        (nombre,)
    )
    conn.commit()
    cursor.close()


def update(conn, id_tipo_vehiculo, nombre):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE TipoVehiculo SET nombre = %s WHERE id_tipo_vehiculo = %s",
        (nombre, id_tipo_vehiculo)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_tipo_vehiculo):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM TipoVehiculo WHERE id_tipo_vehiculo = %s",
        (id_tipo_vehiculo,)
    )
    conn.commit()
    cursor.close()
