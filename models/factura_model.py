def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.id_factura, f.fecha_ingreso, f.fecha_salida, f.tiempo,
               f.valor_total, f.estado_pago,
               f.id_sesion, v.placa,
               f.id_tarifa, tv.nombre AS tipo_vehiculo
        FROM Factura f
        JOIN SesionParqueo s  ON f.id_sesion   = s.id_sesion
        JOIN Vehiculo      v  ON s.id_vehiculo  = v.id_vehiculo
        JOIN Tarifa        t  ON f.id_tarifa    = t.id_tarifa
        JOIN TipoVehiculo  tv ON t.id_tipo_vehiculo = tv.id_tipo_vehiculo
        ORDER BY f.fecha_ingreso DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_factura):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Factura WHERE id_factura = %s", (id_factura,))
    result = cursor.fetchone()
    cursor.close()
    return result


def update_estado(conn, id_factura, estado_pago):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Factura SET estado_pago=%s WHERE id_factura=%s",
        (estado_pago, id_factura)
    )
    conn.commit()
    cursor.close()


def delete(conn, id_factura):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Factura WHERE id_factura = %s", (id_factura,))
    conn.commit()
    cursor.close()
