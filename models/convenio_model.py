def get_by_empresa(conn, id_empresa):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Convenio WHERE id_empresa = %s",
        (id_empresa,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def get_active_by_empresa(conn, id_empresa):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Convenio WHERE id_empresa = %s AND estado = 'activo'",
        (id_empresa,)
    )
    result = cursor.fetchone()
    cursor.close()
    return result


def create(conn, id_empresa, porcentaje, estado='activo'):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Convenio (id_empresa, estado, porcentaje_descuento)
           VALUES (%s, %s, %s)""",
        (id_empresa, estado, porcentaje)
    )
    conn.commit()
    cursor.close()


def update(conn, id_empresa, porcentaje, estado):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Convenio SET porcentaje_descuento=%s, estado=%s
           WHERE id_empresa=%s""",
        (porcentaje, estado, id_empresa)
    )
    conn.commit()
    cursor.close()


def upsert(conn, id_empresa, porcentaje, estado):
    existing = get_by_empresa(conn, id_empresa)
    if existing:
        update(conn, id_empresa, porcentaje, estado)
    else:
        create(conn, id_empresa, porcentaje, estado)
