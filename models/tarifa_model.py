def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.id_tarifa, t.valor_hora, t.descripcion,
               t.id_tipo_vehiculo, tv.nombre AS tipo_vehiculo
        FROM Tarifa t
        JOIN TipoVehiculo tv ON t.id_tipo_vehiculo = tv.id_tipo_vehiculo
        ORDER BY tv.nombre
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_tarifa):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Tarifa WHERE id_tarifa = %s", (id_tarifa,))
    result = cursor.fetchone()
    cursor.close()
    return result


def get_by_tipo_vehiculo(conn, id_tipo_vehiculo):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Tarifa WHERE id_tipo_vehiculo = %s",
        (id_tipo_vehiculo,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Tarifa (valor_hora, descripcion, id_tipo_vehiculo)
           VALUES (%s, %s, %s)""",
        (data['valor_hora'],
         data.get('descripcion') or None,
         data['id_tipo_vehiculo'])
    )
    conn.commit()
    cursor.close()


def update(conn, id_tarifa, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Tarifa SET valor_hora=%s, descripcion=%s, id_tipo_vehiculo=%s
           WHERE id_tarifa=%s""",
        (data['valor_hora'],
         data.get('descripcion') or None,
         data['id_tipo_vehiculo'],
         id_tarifa)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_tarifa):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tarifa WHERE id_tarifa = %s", (id_tarifa,))
    conn.commit()
    cursor.close()
