import flet as ft
import csv
import os
from datetime import datetime
from config.db import get_connection
from components.snackbar import show_success, show_error


def _export_csv(filename: str, headers: list, rows: list) -> str:
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(desktop, f"{filename}_{ts}.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return path


def _reporte_sesiones_activas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id_sesion, v.placa, v.marca, v.modelo,
               CONCAT(u.primer_nombre, ' ', u.primer_apellido) AS propietario,
               ep.numero AS espacio,
               z.nombre AS zona,
               s.fecha_inicio,
               TIMESTAMPDIFF(MINUTE, s.fecha_inicio, NOW()) AS minutos_transcurridos
        FROM SesionParqueo s
        JOIN Vehiculo       v  ON s.id_vehiculo = v.id_vehiculo
        JOIN Usuario        u  ON v.cedula_usuario = u.cedula
        JOIN EspacioParqueo ep ON s.id_espacio  = ep.id_espacio
        JOIN Zona           z  ON ep.id_zona    = z.id_zona
        WHERE s.fecha_fin IS NULL
        ORDER BY s.fecha_inicio
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    headers = ["ID Sesión", "Placa", "Marca", "Modelo", "Propietario",
               "Espacio", "Zona", "Inicio", "Minutos transcurridos"]
    rows = [[r['id_sesion'], r['placa'], r['marca'] or '', r['modelo'] or '',
             r['propietario'], r['espacio'], r['zona'],
             str(r['fecha_inicio']), r['minutos_transcurridos']] for r in data]
    return headers, rows


def _reporte_ingresos_facturas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.id_factura, v.placa, tv.nombre AS tipo_vehiculo,
               f.fecha_ingreso, f.fecha_salida, f.tiempo, f.valor_total,
               f.estado_pago, t.valor_hora
        FROM Factura f
        JOIN SesionParqueo s  ON f.id_sesion = s.id_sesion
        JOIN Vehiculo      v  ON s.id_vehiculo = v.id_vehiculo
        JOIN Tarifa        t  ON f.id_tarifa = t.id_tarifa
        JOIN TipoVehiculo  tv ON t.id_tipo_vehiculo = tv.id_tipo_vehiculo
        ORDER BY f.fecha_ingreso DESC
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    headers = ["ID Factura", "Placa", "Tipo Vehículo", "Ingreso", "Salida",
               "Horas", "Total COP", "Estado Pago", "Tarifa/hora"]
    rows = [[r['id_factura'], r['placa'], r['tipo_vehiculo'],
             str(r['fecha_ingreso']), str(r['fecha_salida']),
             r['tiempo'], r['valor_total'], r['estado_pago'], r['valor_hora']] for r in data]
    return headers, rows


def _reporte_vehiculos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.id_vehiculo, v.placa, v.color, v.marca, v.modelo,
               tv.nombre AS tipo,
               CONCAT(u.primer_nombre, ' ', u.primer_apellido) AS propietario,
               u.cedula, u.correo,
               CASE WHEN s.id_suscripcion IS NOT NULL THEN 'Sí' ELSE 'No' END AS tiene_suscripcion
        FROM Vehiculo v
        JOIN TipoVehiculo tv ON v.id_tipo_vehiculo = tv.id_tipo_vehiculo
        JOIN Usuario      u  ON v.cedula_usuario   = u.cedula
        LEFT JOIN Suscripcion s ON v.id_vehiculo   = s.id_vehiculo
        ORDER BY v.placa
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    headers = ["ID", "Placa", "Color", "Marca", "Modelo", "Tipo", "Propietario",
               "Cédula", "Correo", "Suscripción activa"]
    rows = [[r['id_vehiculo'], r['placa'], r['color'] or '', r['marca'] or '',
             r['modelo'] or '', r['tipo'], r['propietario'], r['cedula'],
             r['correo'], r['tiene_suscripcion']] for r in data]
    return headers, rows


def _reporte_multas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.id_multa, v.placa,
               CONCAT(u.primer_nombre, ' ', u.primer_apellido) AS propietario,
               m.fecha, m.motivo, m.valor, m.estado
        FROM Multa m
        JOIN SesionParqueo s ON m.id_sesion    = s.id_sesion
        JOIN Vehiculo      v ON s.id_vehiculo   = v.id_vehiculo
        JOIN Usuario       u ON v.cedula_usuario = u.cedula
        ORDER BY m.fecha DESC
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    headers = ["ID Multa", "Placa", "Propietario", "Fecha", "Motivo", "Valor COP", "Estado"]
    rows = [[r['id_multa'], r['placa'], r['propietario'], str(r['fecha']),
             r['motivo'] or '', r['valor'], r['estado']] for r in data]
    return headers, rows


REPORTES = [
    {
        'titulo': 'Sesiones Activas',
        'descripcion': 'Vehículos actualmente en el parqueadero con tiempo transcurrido.',
        'icono': ft.Icons.DIRECTIONS_CAR_OUTLINED,
        'color': ft.Colors.BLUE_600,
        'fn': _reporte_sesiones_activas,
        'filename': 'reporte_sesiones_activas',
    },
    {
        'titulo': 'Ingresos (Facturas)',
        'descripcion': 'Todas las facturas generadas con totales y estado de pago.',
        'icono': ft.Icons.RECEIPT_OUTLINED,
        'color': ft.Colors.GREEN_600,
        'fn': _reporte_ingresos_facturas,
        'filename': 'reporte_facturas',
    },
    {
        'titulo': 'Vehículos Registrados',
        'descripcion': 'Listado completo de vehículos con propietario y tipo de suscripción.',
        'icono': ft.Icons.LOCAL_PARKING,
        'color': ft.Colors.PURPLE_600,
        'fn': _reporte_vehiculos,
        'filename': 'reporte_vehiculos',
    },
    {
        'titulo': 'Multas',
        'descripcion': 'Registro de todas las multas con estado de pago.',
        'icono': ft.Icons.WARNING_AMBER_OUTLINED,
        'color': ft.Colors.RED_600,
        'fn': _reporte_multas,
        'filename': 'reporte_multas',
    },
]


def build(page: ft.Page):
    def export(reporte):
        try:
            headers, rows = reporte['fn']()
            path = _export_csv(reporte['filename'], headers, rows)
            show_success(page, f"Exportado: {path}")
        except Exception as e:
            show_error(page, f"Error al exportar: {e}")

    cards = []
    for r in REPORTES:
        r_copy = r
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(r['icono'], color=r['color'], size=36),
                        ft.Column([
                            ft.Text(r['titulo'], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(r['descripcion'], size=12, color=ft.Colors.SECONDARY),
                        ], spacing=2, expand=True),
                    ], spacing=12),
                    ft.Divider(),
                    ft.Row([
                        ft.ElevatedButton(
                            "Exportar CSV",
                            icon=ft.Icons.SAVE_OUTLINED,
                            on_click=lambda e, rep=r_copy: export(rep),
                        ),
                    ], alignment=ft.MainAxisAlignment.END),
                ], spacing=8),
                padding=16,
                width=400,
            ),
            elevation=2,
        )
        cards.append(card)

    return ft.Column([
        ft.Row([
            ft.Text("Reportes y Exportaciones", size=22, weight=ft.FontWeight.BOLD),
        ]),
        ft.Text("Los reportes se exportan como CSV al Escritorio.", italic=True, size=12,
                color=ft.Colors.SECONDARY),
        ft.Divider(),
        ft.ResponsiveRow(
            controls=[ft.Container(card, col={"sm": 12, "md": 6}) for card in cards],
            run_spacing=12,
            spacing=12,
        ),
    ], expand=True, scroll=ft.ScrollMode.AUTO)
