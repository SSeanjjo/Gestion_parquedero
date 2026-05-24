import math
from datetime import datetime


def get_all(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_sesion, s.fecha_inicio, s.fecha_fin, s.tiempo,
               s.id_vehiculo, v.placa, tv.nombre AS tipo_vehiculo,
               s.id_espacio,
               CONCAT('Esp.', ep.numero, ' (', ep.tipo_espacio, ') - ', z.nombre) AS espacio_desc,
               CASE WHEN s.fecha_fin IS NULL THEN 'Activa' ELSE 'Cerrada' END AS estado,
               TIMESTAMPDIFF(MINUTE, s.fecha_inicio,
                   IFNULL(s.fecha_fin, NOW())) AS minutos_transcurridos
        FROM SesionParqueo s
        JOIN Vehiculo       v  ON s.id_vehiculo = v.id_vehiculo
        JOIN TipoVehiculo   tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        JOIN EspacioParqueo ep ON s.id_espacio  = ep.id_espacio
        JOIN Zona           z  ON ep.id_zona    = z.id_zona
        ORDER BY s.fecha_inicio DESC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_active(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_sesion, s.fecha_inicio,
               v.placa, tv.nombre AS tipo_vehiculo,
               CONCAT('Esp.', ep.numero, ' (', ep.tipo_espacio, ') - ', z.nombre) AS espacio_desc,
               ep.tipo_espacio,
               TIMESTAMPDIFF(MINUTE, s.fecha_inicio, NOW()) AS minutos
        FROM SesionParqueo s
        JOIN Vehiculo       v  ON s.id_vehiculo = v.id_vehiculo
        JOIN TipoVehiculo   tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        JOIN EspacioParqueo ep ON s.id_espacio  = ep.id_espacio
        JOIN Zona           z  ON ep.id_zona    = z.id_zona
        WHERE s.fecha_fin IS NULL
        ORDER BY s.fecha_inicio
    """)
    result = cursor.fetchall()
    cursor.close()
    return result


def get_by_id(conn, id_sesion):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SesionParqueo WHERE id_sesion = %s", (id_sesion,))
    result = cursor.fetchone()
    cursor.close()
    return result


def validate_espacio_vehiculo(conn, id_vehiculo, id_espacio):
    """Valida que tipo_espacio coincida con tipo_vehiculo."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT tv.nombre AS tipo_v, ep.tipo_espacio
           FROM Vehiculo v
           JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
           JOIN EspacioParqueo ep ON ep.id_espacio = %s
           WHERE v.id_vehiculo = %s""",
        (id_espacio, id_vehiculo)
    )
    row = cursor.fetchone()
    cursor.close()
    if not row:
        return False, "Vehículo o espacio no encontrado."
    tipo_v = row['tipo_v']
    tipo_e = row['tipo_espacio']
    if tipo_v == 'Moto' and tipo_e != 'Motos':
        return False, f"Las motos solo pueden usar espacios tipo 'Motos'. Espacio seleccionado: '{tipo_e}'."
    if tipo_v != 'Moto' and tipo_e == 'Motos':
        return False, f"El espacio tipo 'Motos' es exclusivo para motos. Vehículo: {tipo_v}."
    return True, "OK"


def create(conn, data):
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO SesionParqueo (fecha_inicio, id_vehiculo, id_espacio)
           VALUES (%s, %s, %s)""",
        (data['fecha_inicio'], data['id_vehiculo'], data['id_espacio'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return new_id


def close_session(conn, id_sesion, fecha_fin):
    """Cierra sesión y genera Factura con lógica:
    1. Suscripcion activa → valor 0
    2. Convenio activo   → descuento porcentual
    3. Sin nada          → tarifa completa
    """
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.id_sesion, s.fecha_inicio, s.id_vehiculo, s.id_espacio,
               v.id_tipo_vehiculo, v.id_empresa,
               t.id_tarifa, t.valor_hora
        FROM SesionParqueo s
        JOIN Vehiculo v ON s.id_vehiculo  = v.id_vehiculo
        JOIN Tarifa   t ON v.id_tipo_vehiculo = t.id_tipo_vehiculo
        WHERE s.id_sesion = %s AND s.fecha_fin IS NULL
    """, (id_sesion,))
    sesion = cursor.fetchone()

    if not sesion:
        cursor.close()
        raise ValueError("Sesión no encontrada o ya cerrada.")

    if isinstance(fecha_fin, str):
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d %H:%M:%S")
    else:
        fecha_fin_dt = fecha_fin

    fecha_inicio_dt = sesion['fecha_inicio']
    if isinstance(fecha_inicio_dt, str):
        fecha_inicio_dt = datetime.strptime(fecha_inicio_dt, "%Y-%m-%d %H:%M:%S")

    duracion_segundos = (fecha_fin_dt - fecha_inicio_dt).total_seconds()
    duracion_horas_real = round(duracion_segundos / 3600, 2)
    # Menos de 5 minutos no se cobra; de lo contrario se redondea al entero superior
    MINUTOS_GRACIA = 5
    if duracion_segundos < MINUTOS_GRACIA * 60:
        duracion_horas_cobro = 0
    else:
        duracion_horas_cobro = math.ceil(duracion_horas_real)
    tarifa_base = float(sesion['valor_hora'])

    # 1. Verificar suscripcion activa
    from datetime import date
    cursor.execute("""
        SELECT id_suscripcion FROM Suscripcion
        WHERE id_vehiculo = %s AND estado = 'Activa' AND fecha_final >= %s
        LIMIT 1
    """, (sesion['id_vehiculo'], date.today().isoformat()))
    tiene_sub = cursor.fetchone()

    descuento_pct = 0.0
    tipo_cobro = 'Tarifa completa'

    if tiene_sub:
        valor_total = 0.0
        tipo_cobro = 'Suscripcion activa'
    elif duracion_horas_cobro == 0:
        valor_total = 0.0
        tipo_cobro = 'Sin cargo (< 5 min)'
    else:
        # 2. Verificar convenio activo de la empresa del vehículo
        if sesion['id_empresa']:
            cursor.execute("""
                SELECT porcentaje_descuento FROM Convenio
                WHERE id_empresa = %s AND estado = 'activo'
                LIMIT 1
            """, (sesion['id_empresa'],))
            conv = cursor.fetchone()
            if conv:
                descuento_pct = float(conv['porcentaje_descuento'])
                valor_total = round(duracion_horas_cobro * tarifa_base * (1 - descuento_pct / 100), 2)
                tipo_cobro = f'Convenio ({descuento_pct}% desc.)'
            else:
                valor_total = round(duracion_horas_cobro * tarifa_base, 2)
        else:
            valor_total = round(duracion_horas_cobro * tarifa_base, 2)

    # Actualizar sesion (tiempo real, no redondeado)
    cursor.execute(
        "UPDATE SesionParqueo SET fecha_fin=%s, tiempo=%s WHERE id_sesion=%s",
        (fecha_fin_dt, duracion_horas_real, id_sesion)
    )

    # Liberar espacio
    cursor.execute(
        "UPDATE EspacioParqueo SET estado='Libre' WHERE id_espacio=%s",
        (sesion['id_espacio'],)
    )

    # Crear factura (tiempo cobrado = horas enteras redondeadas arriba)
    cursor.execute(
        """INSERT INTO Factura
           (fecha_ingreso, fecha_salida, tiempo, valor_total, estado_pago,
            descuento_aplicado, tipo_cobro, id_sesion, id_tarifa)
           VALUES (%s, %s, %s, %s, 'Pendiente', %s, %s, %s, %s)""",
        (sesion['fecha_inicio'], fecha_fin_dt, duracion_horas_cobro, valor_total,
         descuento_pct, tipo_cobro, id_sesion, sesion['id_tarifa'])
    )

    conn.commit()
    cursor.close()
    return valor_total, tipo_cobro


def delete(conn, id_sesion):
    cursor = conn.cursor()
    # Liberar espacio si la sesion estaba activa
    cursor.execute(
        """UPDATE EspacioParqueo ep
           JOIN SesionParqueo sp ON sp.id_espacio = ep.id_espacio
           SET ep.estado = 'Libre'
           WHERE sp.id_sesion = %s AND sp.fecha_fin IS NULL""",
        (id_sesion,)
    )
    cursor.execute("DELETE FROM SesionParqueo WHERE id_sesion = %s", (id_sesion,))
    conn.commit()
    cursor.close()


# -----------------------------------------------------------------------
# Reportes CRUD 5
# -----------------------------------------------------------------------

def reporte_ocupacion_zonas(conn, fecha_inicio, fecha_fin):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT z.nombre AS zona, z.piso, ep.tipo_espacio,
               ep.numero AS espacio,
               COUNT(s.id_sesion) AS total_sesiones,
               ROUND(AVG(s.tiempo), 2) AS promedio_horas
        FROM Zona z
        JOIN EspacioParqueo ep ON ep.id_zona = z.id_zona
        LEFT JOIN SesionParqueo s ON s.id_espacio = ep.id_espacio
                                  AND s.fecha_inicio >= %s
                                  AND s.fecha_inicio <= %s
        GROUP BY z.id_zona, z.nombre, z.piso, ep.id_espacio, ep.tipo_espacio, ep.numero
        ORDER BY total_sesiones DESC
    """, (fecha_inicio, fecha_fin))
    result = cursor.fetchall()
    cursor.close()
    return result


def reporte_ganancias_mensuales(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DATE_FORMAT(f.fecha_ingreso, '%Y-%m') AS mes,
               COUNT(f.id_factura) AS total_sesiones,
               SUM(f.valor_total) AS ganancia_total
        FROM Factura f
        WHERE f.valor_total > 0
          AND f.fecha_ingreso >= '2025-01-01'
          AND f.fecha_ingreso <= '2026-05-31'
        GROUP BY DATE_FORMAT(f.fecha_ingreso, '%Y-%m')
        ORDER BY mes ASC
    """)
    result = cursor.fetchall()
    cursor.close()
    return result
