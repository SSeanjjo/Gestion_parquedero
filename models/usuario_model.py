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


def get_by_cedula_or_name(conn, term):
    cursor = conn.cursor(dictionary=True)
    like = f"%{term}%"
    cursor.execute("""
        SELECT cedula,
               CONCAT(primer_nombre, ' ', primer_apellido) AS nombre_completo
        FROM Usuario
        WHERE cedula LIKE %s
           OR primer_nombre LIKE %s
           OR primer_apellido LIKE %s
           OR CONCAT(primer_nombre, ' ', primer_apellido) LIKE %s
        ORDER BY primer_apellido, primer_nombre
        LIMIT 50
    """, (like, like, like, like))
    result = cursor.fetchall()
    cursor.close()
    return result


def login(conn, cedula, contrasenia):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT u.*, 'Administrador' AS rol
           FROM Usuario u
           JOIN Administrador a ON u.cedula = a.cedula
           WHERE u.cedula = %s AND a.contrasenia = %s""",
        (cedula, contrasenia)
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
    import random, string
    codigo = data.get('codigo_interno') or 'ADM-' + ''.join(random.choices(string.digits, k=4))
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Administrador
           (cedula, contrasenia, fecha_asignacion, codigo_interno)
           VALUES (%s, %s, %s, %s)""",
        (cedula, data['contrasenia'],
         data.get('fecha_asignacion') or __import__('datetime').date.today().isoformat(),
         codigo)
    )
    conn.commit()
    cursor.close()


def create_operador(conn, cedula, data):
    import random, string
    codigo = data.get('codigo_interno') or 'OP-' + ''.join(random.choices(string.digits, k=4))
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Operador (cedula, codigo_interno, estado)
           VALUES (%s, %s, %s)""",
        (cedula, codigo, data.get('estado') or 'Activo')
    )
    conn.commit()
    cursor.close()


def create_suscriptor(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Suscriptor (cedula, fecha_registro)
           VALUES (%s, %s)""",
        (cedula, data.get('fecha_registro') or None)
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
    if data.get('contrasenia'):
        cursor.execute(
            """UPDATE Administrador SET contrasenia=%s, fecha_asignacion=%s,
               codigo_interno=%s WHERE cedula=%s""",
            (data['contrasenia'],
             data.get('fecha_asignacion') or __import__('datetime').date.today().isoformat(),
             data.get('codigo_interno') or None, cedula)
        )
    else:
        cursor.execute(
            """UPDATE Administrador SET fecha_asignacion=%s,
               codigo_interno=%s WHERE cedula=%s""",
            (data.get('fecha_asignacion') or __import__('datetime').date.today().isoformat(),
             data.get('codigo_interno') or None, cedula)
        )
    conn.commit()
    cursor.close()


def update_operador(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Operador SET codigo_interno=%s, estado=%s WHERE cedula=%s""",
        (data.get('codigo_interno') or None,
         data.get('estado') or None, cedula)
    )
    conn.commit()
    cursor.close()


def update_suscriptor(conn, cedula, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Suscriptor SET fecha_registro=%s WHERE cedula=%s""",
        (data.get('fecha_registro') or None, cedula)
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


def get_suscriptores_for_dropdown(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT u.cedula,
                  CONCAT(u.primer_nombre, ' ', u.primer_apellido) AS nombre_completo
           FROM Usuario u
           JOIN Suscriptor s ON u.cedula = s.cedula
           ORDER BY u.primer_apellido, u.primer_nombre"""
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


# -----------------------------------------------------------------------
# Reportes CRUD 1
# -----------------------------------------------------------------------

def reporte_multas_por_estado(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.id_multa, m.fecha, m.motivo, m.valor, m.estado,
               v.placa,
               CONCAT(u.primer_nombre,' ',u.primer_apellido) AS propietario
        FROM Multa m
        JOIN SesionParqueo sp ON m.id_sesion = sp.id_sesion
        JOIN Vehiculo v ON sp.id_vehiculo = v.id_vehiculo
        JOIN Usuario u ON v.cedula_usuario = u.cedula
        ORDER BY m.estado, m.fecha DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def reporte_usuarios_mas_suscripciones(conn, fecha_inicio=None, fecha_fin=None):
    cursor = conn.cursor(dictionary=True)
    if fecha_inicio and fecha_fin:
        cursor.execute("""
            SELECT u.cedula,
                   CONCAT(u.primer_nombre,' ',u.primer_apellido) AS nombre,
                   COUNT(ss.id_suscripcion) AS cantidad_suscripciones
            FROM Usuario u
            JOIN Suscriptor s ON u.cedula = s.cedula
            JOIN SuscriptorSuscripcion ss ON s.cedula = ss.id_suscriptor
            JOIN Suscripcion sub ON ss.id_suscripcion = sub.id_suscripcion
            WHERE sub.fecha_inicio >= %s AND sub.fecha_inicio <= %s
            GROUP BY u.cedula, u.primer_nombre, u.primer_apellido
            ORDER BY cantidad_suscripciones DESC
        """, (fecha_inicio, fecha_fin))
    else:
        cursor.execute("""
            SELECT u.cedula,
                   CONCAT(u.primer_nombre,' ',u.primer_apellido) AS nombre,
                   COUNT(ss.id_suscripcion) AS cantidad_suscripciones
            FROM Usuario u
            JOIN Suscriptor s ON u.cedula = s.cedula
            JOIN SuscriptorSuscripcion ss ON s.cedula = ss.id_suscriptor
            GROUP BY u.cedula, u.primer_nombre, u.primer_apellido
            ORDER BY cantidad_suscripciones DESC
        """)
    result = cursor.fetchall()
    cursor.close()
    return result


def reporte_horas_operadores(conn, fecha_inicio, fecha_fin):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.cedula,
               CONCAT(u.primer_nombre,' ',u.primer_apellido) AS nombre,
               COUNT(t.id_turno) AS cantidad_turnos,
               SUM(DATEDIFF(
                   LEAST(t.fecha_final_turno, %s),
                   GREATEST(t.fecha_inicio_turno, %s)
               ) + 1) * 8 AS horas_totales_estimadas,
               SUM(CASE
                 WHEN TIME(t.fecha_inicio_turno) < '18:00:00'
                      OR TIME(t.fecha_final_turno) < '18:00:00'
                 THEN DATEDIFF(LEAST(t.fecha_final_turno,%s), GREATEST(t.fecha_inicio_turno,%s))+1
                 ELSE 0
               END) * 8 AS horas_diurnas,
               SUM(CASE
                 WHEN TIME(t.fecha_inicio_turno) >= '18:00:00'
                      OR TIME(t.fecha_final_turno) >= '18:00:00'
                 THEN DATEDIFF(LEAST(t.fecha_final_turno,%s), GREATEST(t.fecha_inicio_turno,%s))+1
                 ELSE 0
               END) * 8 AS horas_nocturnas
        FROM Turno t
        JOIN Operador o ON t.id_operador = o.cedula
        JOIN Usuario u ON o.cedula = u.cedula
        WHERE t.fecha_inicio_turno <= %s AND t.fecha_final_turno >= %s
        GROUP BY u.cedula, u.primer_nombre, u.primer_apellido
        ORDER BY horas_totales_estimadas DESC
    """, (fecha_fin, fecha_inicio,
          fecha_fin, fecha_inicio,
          fecha_fin, fecha_inicio,
          fecha_fin, fecha_inicio))
    result = cursor.fetchall()
    cursor.close()
    return result


def reporte_usuarios_mayor_ganancia(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.cedula,
               CONCAT(u.primer_nombre,' ',u.primer_apellido) AS nombre,
               COALESCE(SUM(f.valor_total), 0) AS ganancia_sesiones,
               COUNT(DISTINCT s.id_suscripcion) AS num_suscripciones,
               COALESCE(SUM(f.valor_total), 0) AS ganancia_total
        FROM Usuario u
        LEFT JOIN Vehiculo v ON v.cedula_usuario = u.cedula
        LEFT JOIN SesionParqueo sp ON sp.id_vehiculo = v.id_vehiculo
        LEFT JOIN Factura f ON f.id_sesion = sp.id_sesion AND f.valor_total > 0
        LEFT JOIN Suscripcion s ON s.id_vehiculo = v.id_vehiculo AND s.estado = 'Activa'
        GROUP BY u.cedula, u.primer_nombre, u.primer_apellido
        HAVING ganancia_total > 0
        ORDER BY ganancia_total DESC
        LIMIT 50
    """)
    result = cursor.fetchall()
    cursor.close()
    return result
