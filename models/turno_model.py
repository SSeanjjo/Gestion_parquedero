def get_by_operador(conn, cedula_operador):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT t.id_turno, t.fecha_inicio_turno, t.fecha_final_turno,
                  CONCAT(u.primer_nombre,' ',u.primer_apellido) AS nombre_operador
           FROM Turno t
           JOIN Operador o ON t.id_operador = o.cedula
           JOIN Usuario u ON o.cedula = u.cedula
           WHERE t.id_operador = %s
           ORDER BY t.fecha_inicio_turno DESC""",
        (cedula_operador,)
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.id_turno, t.id_operador,
               CONCAT(u.primer_nombre,' ',u.primer_apellido) AS nombre_operador,
               t.fecha_inicio_turno, t.fecha_final_turno
        FROM Turno t
        JOIN Operador o ON t.id_operador = o.cedula
        JOIN Usuario u ON o.cedula = u.cedula
        ORDER BY t.fecha_inicio_turno DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Turno (id_operador, fecha_inicio_turno, fecha_final_turno)
           VALUES (%s, %s, %s)""",
        (data['id_operador'], data['fecha_inicio_turno'], data['fecha_final_turno'])
    )
    conn.commit()
    cursor.close()


def delete(conn, id_turno):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Turno WHERE id_turno = %s", (id_turno,))
    conn.commit()
    cursor.close()
