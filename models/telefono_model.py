def get_by_usuario(conn, cedula_usuario):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT cedula_usuario, telefono FROM Telefono WHERE cedula_usuario = %s",
        (cedula_usuario,)
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.cedula_usuario, t.telefono,
               CONCAT(u.primer_nombre, ' ', u.primer_apellido) AS nombre_usuario
        FROM Telefono t
        JOIN Usuario u ON t.cedula_usuario = u.cedula
        ORDER BY u.primer_apellido, t.telefono
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def create(conn, cedula_usuario, telefono):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Telefono (cedula_usuario, telefono) VALUES (%s, %s)",
        (cedula_usuario, telefono)
    )
    conn.commit()
    cursor.close()


def delete(conn, cedula_usuario, telefono):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Telefono WHERE cedula_usuario = %s AND telefono = %s",
        (cedula_usuario, telefono)
    )
    conn.commit()
    cursor.close()


def delete_all_by_usuario(conn, cedula_usuario):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Telefono WHERE cedula_usuario = %s",
        (cedula_usuario,)
    )
    conn.commit()
    cursor.close()
