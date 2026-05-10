def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.id_multa, m.fecha, m.motivo, m.valor, m.estado,
               m.id_sesion, v.placa
        FROM Multa m
        JOIN SesionParqueo s ON m.id_sesion  = s.id_sesion
        JOIN Vehiculo      v ON s.id_vehiculo = v.id_vehiculo
        ORDER BY m.fecha DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_multa):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Multa WHERE id_multa = %s", (id_multa,))
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Multa (fecha, motivo, valor, estado, id_sesion)
           VALUES (%s, %s, %s, %s, %s)""",
        (data['fecha'],
         data.get('motivo') or None,
         data['valor'],
         data.get('estado', 'Pendiente'),
         data['id_sesion'])
    )
    conn.commit()
    cursor.close()


def update(conn, id_multa, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Multa SET fecha=%s, motivo=%s, valor=%s, estado=%s, id_sesion=%s
           WHERE id_multa=%s""",
        (data['fecha'],
         data.get('motivo') or None,
         data['valor'],
         data.get('estado', 'Pendiente'),
         data['id_sesion'],
         id_multa)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_multa):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Multa WHERE id_multa = %s", (id_multa,))
    conn.commit()
    cursor.close()
