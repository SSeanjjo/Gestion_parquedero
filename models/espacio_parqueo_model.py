def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.id_espacio, e.numero, e.estado, e.tipo_espacio,
               e.id_zona, z.nombre AS nombre_zona
        FROM EspacioParqueo e
        JOIN Zona z ON e.id_zona = z.id_zona
        ORDER BY z.nombre, e.numero
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_espacio):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM EspacioParqueo WHERE id_espacio = %s",
        (id_espacio,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def get_libres(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.id_espacio,
               CONCAT('Espacio ', e.numero, ' - ', z.nombre) AS descripcion
        FROM EspacioParqueo e
        JOIN Zona z ON e.id_zona = z.id_zona
        WHERE e.estado = 'Libre'
        ORDER BY z.nombre, e.numero
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO EspacioParqueo (numero, estado, tipo_espacio, id_zona)
           VALUES (%s, %s, %s, %s)""",
        (data['numero'],
         data.get('estado', 'Libre'),
         data.get('tipo_espacio') or None,
         data['id_zona'])
    )
    conn.commit()
    cursor.close()


def update(conn, id_espacio, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE EspacioParqueo SET numero=%s, estado=%s, tipo_espacio=%s, id_zona=%s
           WHERE id_espacio=%s""",
        (data['numero'],
         data.get('estado', 'Libre'),
         data.get('tipo_espacio') or None,
         data['id_zona'],
         id_espacio)
    )
    conn.commit()
    cursor.close()


def update_estado(conn, id_espacio, estado):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE EspacioParqueo SET estado=%s WHERE id_espacio=%s",
        (estado, id_espacio)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_espacio):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM EspacioParqueo WHERE id_espacio = %s",
        (id_espacio,)
    )
    conn.commit()
    cursor.close()
