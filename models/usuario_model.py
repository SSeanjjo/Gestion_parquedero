def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.cedula, u.primer_nombre, u.segundo_nombre,
               u.primer_apellido, u.segundo_apellido, u.correo,
               CASE
                 WHEN a.cedula IS NOT NULL THEN 'Administrador'
                 WHEN o.cedula IS NOT NULL THEN 'Operador'
                 WHEN s.cedula IS NOT NULL THEN 'Suscriptor'
                 ELSE 'Sin rol'
               END AS rol
        FROM Usuario u
        LEFT JOIN Administrador a ON u.cedula = a.cedula
        LEFT JOIN Operador      o ON u.cedula = o.cedula
        LEFT JOIN Suscriptor    s ON u.cedula = s.cedula
        ORDER BY u.primer_apellido, u.primer_nombre
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_cedula(conn, cedula):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Usuario WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    cursor.close()
    return result


def login(conn, cedula, contrasena):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT u.*, 'Administrador' AS rol
           FROM Usuario u
           JOIN Administrador a ON u.cedula = a.cedula
           WHERE u.cedula = %s AND a.contrasena = %s""",
        (cedula, contrasena)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def get_administrador(conn, cedula):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Administrador WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    cursor.close()
    return result


def get_operador(conn, cedula):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Operador WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    cursor.close()
    return result


def get_suscriptor(conn, cedula):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Suscriptor WHERE cedula = %s", (cedula,))
    result = cursor.fetchone()
    cursor.close()
    return result


def create_usuario(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Usuario
           (cedula, primer_nombre, segundo_nombre, primer_apellido,
            segundo_apellido, correo)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data['cedula'], data['primer_nombre'], data.get('segundo_nombre') or None,
         data['primer_apellido'], data.get('segundo_apellido') or None,
         data['correo'])
    )
    conn.commit()
    cursor.close()


def create_administrador(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Administrador
           (cedula, contrasena, nivel_acceso, fecha_asignacion, area_responsable)
           VALUES (%s, %s, %s, %s, %s)""",
        (cedula, data['contrasena'], data['nivel_acceso'],
         data['fecha_asignacion'], data['area_responsable'])
    )
    conn.commit()
    cursor.close()


def create_operador(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Operador
           (cedula, fecha_inicio_turno, fecha_final_turno,
            codigo_interno, turno_asignado, estado)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (cedula,
         data.get('fecha_inicio_turno') or None,
         data.get('fecha_final_turno') or None,
         data.get('codigo_interno') or None,
         data.get('turno_asignado') or None,
         data.get('estado') or None)
    )
    conn.commit()
    cursor.close()


def create_suscriptor(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Suscriptor (cedula, tipo_suscriptor, fecha_registro)
           VALUES (%s, %s, %s)""",
        (cedula,
         data.get('tipo_suscriptor') or None,
         data.get('fecha_registro') or None)
    )
    conn.commit()
    cursor.close()


def update_usuario(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Usuario SET
           primer_nombre=%s, segundo_nombre=%s, primer_apellido=%s,
           segundo_apellido=%s, correo=%s
           WHERE cedula=%s""",
        (data['primer_nombre'], data.get('segundo_nombre') or None,
         data['primer_apellido'], data.get('segundo_apellido') or None,
         data['correo'], cedula)
    )
    conn.commit()
    cursor.close()


def update_administrador(conn, cedula, data):
    cursor = conn.cursor()
    if data.get('contrasena'):
        cursor.execute(
            """UPDATE Administrador SET contrasena=%s, nivel_acceso=%s,
               fecha_asignacion=%s, area_responsable=%s WHERE cedula=%s""",
            (data['contrasena'], data['nivel_acceso'],
             data['fecha_asignacion'], data['area_responsable'], cedula)
        )
    else:
        cursor.execute(
            """UPDATE Administrador SET nivel_acceso=%s,
               fecha_asignacion=%s, area_responsable=%s WHERE cedula=%s""",
            (data['nivel_acceso'], data['fecha_asignacion'],
             data['area_responsable'], cedula)
        )
    conn.commit()
    cursor.close()


def update_operador(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Operador SET fecha_inicio_turno=%s, fecha_final_turno=%s,
           codigo_interno=%s, turno_asignado=%s, estado=%s
           WHERE cedula=%s""",
        (data.get('fecha_inicio_turno') or None,
         data.get('fecha_final_turno') or None,
         data.get('codigo_interno') or None,
         data.get('turno_asignado') or None,
         data.get('estado') or None, cedula)
    )
    conn.commit()
    cursor.close()


def update_suscriptor(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Suscriptor SET tipo_suscriptor=%s, fecha_registro=%s
           WHERE cedula=%s""",
        (data.get('tipo_suscriptor') or None,
         data.get('fecha_registro') or None, cedula)
    )
    conn.commit()
    cursor.close()


def delete_usuario(conn, cedula):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Usuario WHERE cedula = %s", (cedula,))
    conn.commit()
    cursor.close()


def get_all_for_dropdown(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT cedula,
                  CONCAT(primer_nombre, ' ', primer_apellido) AS nombre_completo
           FROM Usuario ORDER BY primer_apellido, primer_nombre"""
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def get_role(conn, cedula):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT
             CASE
               WHEN a.cedula IS NOT NULL THEN 'Administrador'
               WHEN o.cedula IS NOT NULL THEN 'Operador'
               WHEN s.cedula IS NOT NULL THEN 'Suscriptor'
               ELSE NULL
             END AS rol
           FROM Usuario u
           LEFT JOIN Administrador a ON u.cedula = a.cedula
           LEFT JOIN Operador      o ON u.cedula = o.cedula
           LEFT JOIN Suscriptor    s ON u.cedula = s.cedula
           WHERE u.cedula = %s""",
        (cedula,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row['rol'] if row else None
