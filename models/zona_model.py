def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_zona, nombre, piso, tipo_zona, capacidad FROM Zona ORDER BY piso, nombre"
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_zona):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Zona WHERE id_zona = %s", (id_zona,))
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Zona (nombre, piso, tipo_zona, capacidad)
           VALUES (%s, %s, %s, %s)""",
        (data['nombre'], data['piso'],
         data.get('tipo_zona') or None,
         data.get('capacidad') or None)
    )
    conn.commit()
    cursor.close()


def update(conn, id_zona, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Zona SET nombre=%s, piso=%s, tipo_zona=%s, capacidad=%s
           WHERE id_zona=%s""",
        (data['nombre'], data['piso'],
         data.get('tipo_zona') or None,
         data.get('capacidad') or None,
         id_zona)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_zona):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Zona WHERE id_zona = %s", (id_zona,))
    conn.commit()
    cursor.close()
