def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.id_factura, f.fecha_ingreso, f.fecha_salida, f.tiempo,
               f.valor_total, f.estado_pago, f.descuento_aplicado, f.tipo_cobro,
               f.id_sesion, v.placa, tv.nombre AS tipo_vehiculo, t.valor_hora
        FROM Factura f
        JOIN SesionParqueo sp ON f.id_sesion  = sp.id_sesion
        JOIN Vehiculo       v  ON sp.id_vehiculo = v.id_vehiculo
        JOIN TipoVehiculo   tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        JOIN Tarifa         t  ON f.id_tarifa = t.id_tarifa
        ORDER BY f.fecha_ingreso DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def mark_as_paid(conn, id_factura):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Factura SET estado_pago = 'Pagada' WHERE id_factura = %s AND estado_pago = 'Pendiente'",
        (id_factura,)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    if affected == 0:
        raise ValueError("La factura ya está pagada o no existe.")


def delete(conn, id_factura):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Factura WHERE id_factura = %s", (id_factura,))
    conn.commit()
    cursor.close()


# -----------------------------------------------------------------------
# Reportes CRUD 6
# -----------------------------------------------------------------------

def reporte_por_tipo_cobro(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT tipo_cobro,
               COUNT(*)         AS total_facturas,
               SUM(valor_total) AS total_recaudado,
               AVG(valor_total) AS promedio_valor
        FROM Factura
        GROUP BY tipo_cobro
        ORDER BY total_recaudado DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def reporte_pendientes(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.id_factura, f.fecha_ingreso, f.valor_total,
               f.tipo_cobro, v.placa, tv.nombre AS tipo_vehiculo,
               DATEDIFF(NOW(), f.fecha_ingreso) AS dias_pendiente
        FROM Factura f
        JOIN SesionParqueo sp ON f.id_sesion     = sp.id_sesion
        JOIN Vehiculo       v  ON sp.id_vehiculo  = v.id_vehiculo
        JOIN TipoVehiculo   tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        WHERE f.estado_pago = 'Pendiente'
        ORDER BY f.fecha_ingreso ASC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result
