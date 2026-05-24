def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.id_empresa, e.nombre, e.nit, e.direccion, e.telefono,
               e.ciudad, e.estado_convenio,
               c.id_convenio, c.porcentaje_descuento,
               c.estado AS estado_convenio_actual
        FROM Empresa e
        LEFT JOIN Convenio c ON c.id_empresa = e.id_empresa
        ORDER BY e.nombre
    """)
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
        """INSERT INTO Empresa (nombre, nit, direccion, telefono, ciudad, estado_convenio)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data['nombre'],
         data.get('nit') or None,
         data.get('direccion') or None,
         data.get('telefono') or None,
         data.get('ciudad') or None,
         data.get('estado_convenio', 'activo'))
    )
    new_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    return new_id


def update(conn, id_empresa, data):
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Empresa SET nombre=%s, nit=%s, direccion=%s,
           telefono=%s, ciudad=%s, estado_convenio=%s
           WHERE id_empresa=%s""",
        (data['nombre'],
         data.get('nit') or None,
         data.get('direccion') or None,
         data.get('telefono') or None,
         data.get('ciudad') or None,
         data.get('estado_convenio', 'activo'),
         id_empresa)
    )
    conn.commit()
    cursor.close()


def deactivate(conn, id_empresa):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Empresa SET estado_convenio='inactivo' WHERE id_empresa=%s",
        (id_empresa,)
    )
    conn.commit()
    cursor.close()


def get_all_for_dropdown(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT id_empresa, nombre, estado_convenio
           FROM Empresa WHERE estado_convenio = 'activo' ORDER BY nombre"""
    )
    result = cursor.fetchall()
    cursor.close()
    return result


def get_all_for_dropdown_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_empresa, nombre FROM Empresa ORDER BY nombre")
    result = cursor.fetchall()
    cursor.close()
    return result


# -----------------------------------------------------------------------
# Reportes CRUD 4
# -----------------------------------------------------------------------

def reporte_catalogo_tarifas(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT tv.nombre AS tipo_vehiculo, t.valor_hora, t.descripcion
        FROM Tarifa t
        JOIN TipoVehiculo tv ON t.id_tipo_vehiculo = tv.id_tipo_vehiculo
        ORDER BY t.valor_hora ASC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def reporte_vehiculos_por_empresa(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.nombre AS empresa, e.estado_convenio,
               c.porcentaje_descuento, c.estado AS estado_convenio_actual,
               v.placa, tv.nombre AS tipo_vehiculo,
               CASE WHEN s.id_suscripcion IS NOT NULL THEN 'Sí' ELSE 'No' END AS tiene_suscripcion_activa
        FROM Empresa e
        JOIN Convenio c ON c.id_empresa = e.id_empresa AND c.estado = 'activo'
        JOIN Vehiculo v ON v.id_empresa = e.id_empresa
        JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        LEFT JOIN Suscripcion s ON s.id_vehiculo = v.id_vehiculo
                                AND s.estado = 'Activa'
                                AND s.fecha_final >= CURDATE()
        ORDER BY e.nombre, v.placa
    """)
    result = cursor.fetchall()
    cursor.close()
    return result
