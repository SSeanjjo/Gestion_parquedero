def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_empresa, nombre, nit, direccion, telefono, ciudad FROM Empresa ORDER BY nombre"
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_empresa):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Empresa WHERE id_empresa = %s", (id_empresa,))
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Empresa (nombre, nit, direccion, telefono, ciudad)
           VALUES (%s, %s, %s, %s, %s)""",
        (data['nombre'],
         data.get('nit') or None,
         data.get('direccion') or None,
         data.get('telefono') or None,
         data.get('ciudad') or None)
    )
    conn.commit()
    cursor.close()


def update(conn, id_empresa, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Empresa SET nombre=%s, nit=%s, direccion=%s, telefono=%s, ciudad=%s
           WHERE id_empresa=%s""",
        (data['nombre'],
         data.get('nit') or None,
         data.get('direccion') or None,
         data.get('telefono') or None,
         data.get('ciudad') or None,
         id_empresa)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_empresa):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Empresa WHERE id_empresa = %s", (id_empresa,))
    conn.commit()
    cursor.close()


def get_all_for_dropdown(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_empresa, nombre FROM Empresa ORDER BY nombre"
    )
    result = cursor.fetchall()
    cursor.close()
    return result
