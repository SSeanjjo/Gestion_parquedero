import flet as ft
import csv, os
from datetime import datetime, date
from controllers import sesion_controller as ctrl
from controllers import vehiculo_controller as v_ctrl
from components.snackbar import show_success, show_error


def _export_csv(filename, headers, rows):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(desktop, f"{filename}_{ts}.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    return path


def build(page: ft.Page):
    data = []
    _built = [False]
    _shown = [10]

    search_field = ft.TextField(
        hint_text="Buscar por placa, espacio, zona...",
        prefix_icon=ft.Icons.SEARCH,
        width=280,
        height=40,
        content_padding=ft.Padding.symmetric(vertical=0, horizontal=10),
        on_change=lambda e: _reset_page(),
    )
    filter_estado = ft.Dropdown(
        label="Estado",
        width=130,
        options=[ft.dropdown.Option("Todos"),
                 ft.dropdown.Option("Activa"),
                 ft.dropdown.Option("Cerrada")],
        value="Todos",
        on_select=lambda e: _reset_page(),
    )

    counter_text = ft.Text("", size=12, color=ft.Colors.SECONDARY)
    load_more_btn = ft.TextButton(
        "Cargar 10 más", icon=ft.Icons.EXPAND_MORE, visible=False,
        on_click=lambda e: _load_more(),
    )

    def _reset_page():
        _shown[0] = 10
        refresh_table()

    def _load_more():
        _shown[0] += 10
        refresh_table()

    def load_data():
        nonlocal data
        _shown[0] = 10
        ok, result = ctrl.get_all()
        data = result if ok else []
        refresh_table()

    def refresh_table():
        q = search_field.value.strip().lower() if search_field.value else ""
        est_f = filter_estado.value or "Todos"
        all_rows = []
        for row in data:
            if q and not any(q in str(v).lower() for v in row.values()):
                continue
            if est_f != "Todos" and row.get('estado') != est_f:
                continue
            estado = str(row.get('estado', ''))
            color = ft.Colors.GREEN_700 if estado == 'Activa' else ft.Colors.BLUE_GREY_400
            mins = row.get('minutos_transcurridos')
            all_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_sesion', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('tipo_vehiculo', '')))),
                ft.DataCell(ft.Text(str(row.get('espacio_desc', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha_inicio', ''))[:16])),
                ft.DataCell(ft.Text(str(row.get('fecha_fin') or '—')[:16] if row.get('fecha_fin') else '—')),
                ft.DataCell(ft.Text(f"{row.get('tiempo', '—') or '—'} h")),
                ft.DataCell(ft.Text(f"{mins} min" if mins is not None and estado == 'Activa' else '—')),
                ft.DataCell(ft.Container(
                    ft.Text(estado, color=ft.Colors.WHITE, size=12),
                    bgcolor=color, border_radius=12,
                    padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.LOCK_CLOCK, tooltip="Cerrar sesión",
                                  icon_color=ft.Colors.ORANGE_700,
                                  visible=(estado == 'Activa'),
                                  on_click=lambda e, r=row: open_close(r)),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Cancelar/Eliminar",
                                  icon_color=ft.Colors.RED_600,
                                  on_click=lambda e, r=row: confirm_delete(r)),
                ], tight=True)),
            ]))
        visible = all_rows[:_shown[0]]
        table.rows.clear()
        table.rows.extend(visible)
        counter_text.value = f"Mostrando {len(visible)} de {len(all_rows)}"
        load_more_btn.visible = len(visible) < len(all_rows)
        if _built[0]:
            table.update()
            counter_text.update()
            load_more_btn.update()

    def open_create():
        ok_v, vehiculos = v_ctrl.get_all_for_dropdown()
        all_v_opts = [ft.dropdown.Option(
            key=str(v['id_vehiculo']),
            text=f"{v['placa']} ({v['tipo_vehiculo']})")
            for v in (vehiculos or [])]

        search_v = ft.TextField(
            label="Buscar vehículo por placa o tipo...",
            prefix_icon=ft.Icons.SEARCH,
            width=440,
        )
        f_vehiculo = ft.Dropdown(label="Seleccione vehículo *", options=all_v_opts, width=440)
        f_espacio = ft.Dropdown(label="Espacio disponible *", options=[], width=440)
        f_fecha = ft.TextField(label="Fecha y hora inicio (AAAA-MM-DD HH:MM:SS)",
                               value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        info_txt = ft.Text("", color=ft.Colors.ORANGE_700, size=12, italic=True)

        def _filter_vehiculo(e):
            term = search_v.value.strip().lower()
            f_vehiculo.options = [o for o in all_v_opts if term in o.text.lower()] if term else all_v_opts
            f_vehiculo.value = None
            f_espacio.options = []
            info_txt.value = ""
            page.update()

        search_v.on_change = _filter_vehiculo

        def on_vehiculo_change(e):
            if not f_vehiculo.value:
                return
            ok_e, espacios = ctrl.get_libres_compatibles(int(f_vehiculo.value))
            if ok_e:
                f_espacio.options = [
                    ft.dropdown.Option(key=str(esp['id_espacio']), text=esp['descripcion'])
                    for esp in espacios
                ]
                if not espacios:
                    info_txt.value = "No hay espacios disponibles compatibles con este tipo de vehículo."
                else:
                    info_txt.value = f"{len(espacios)} espacio(s) disponible(s)."
            else:
                info_txt.value = str(espacios)
            page.update()

        f_vehiculo.on_select = on_vehiculo_change

        def save(dlg):
            if not f_vehiculo.value or not f_espacio.value:
                show_error(page, "Vehículo y espacio son obligatorios."); return
            ok, msg = ctrl.create({
                'id_vehiculo': int(f_vehiculo.value),
                'id_espacio': int(f_espacio.value),
                'fecha_inicio': f_fecha.value.strip(),
            })
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nueva Sesión de Parqueo", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Los espacios se filtran automáticamente según el tipo de vehículo.",
                        size=11, italic=True, color=ft.Colors.SECONDARY),
                search_v, f_vehiculo, info_txt, f_espacio, f_fecha,
            ], tight=True, scroll=ft.ScrollMode.AUTO, width=460, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Abrir sesión", icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                                   on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def open_close(row):
        f_fecha = ft.TextField(label="Fecha y hora de salida (AAAA-MM-DD HH:MM:SS)",
                               value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        def save(dlg):
            if not f_fecha.value.strip():
                show_error(page, "Ingrese la fecha de salida."); return
            ok, msg = ctrl.close_session(row['id_sesion'], f_fecha.value.strip())
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Cerrar Sesión #{row['id_sesion']} — {row.get('placa','')}", size=16,
                          weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"Espacio: {row.get('espacio_desc', '')}"),
                ft.Text(f"Inicio: {str(row.get('fecha_inicio',''))[:16]}"),
                ft.Text(f"Tiempo transcurrido: {row.get('minutos_transcurridos', '—')} min"),
                ft.Divider(),
                f_fecha,
                ft.Text("Al cerrar se genera la factura automáticamente.\n"
                        "Descuento por suscripción activa o convenio si aplica.",
                        italic=True, size=11, color=ft.Colors.SECONDARY),
            ], tight=True, width=440, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Cerrar y facturar", icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                                   on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def confirm_delete(row):
        estado = row.get('estado', '')
        accion = "cancelar" if estado == 'Activa' else "eliminar"

        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_sesion'])
            page.pop_dialog()
            if ok:
                load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Confirmar {accion}"),
            content=ft.Text(f"¿{accion.capitalize()} sesión #{row.get('id_sesion','')} (placa {row.get('placa','')})?"
                            + ("\nSe liberará el espacio." if estado == 'Activa' else '')),
            actions=[
                ft.TextButton("Atrás", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(accion.capitalize(),
                                   style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                                   on_click=lambda e: do_delete(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    # ---------------------------------------------------------------- Reportes
    def _show_report_table(title, headers, rows_data):
        cols = [ft.DataColumn(ft.Text(h, weight=ft.FontWeight.BOLD, size=12)) for h in headers]
        rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(v) if v is not None else '', size=12)) for v in row])
                for row in rows_data]
        tbl = ft.DataTable(
            columns=cols, rows=rows,
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGH,
            vertical_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        )
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                ft.Column([ft.Row([tbl], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
                width=900, height=500,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Exportar CSV", icon=ft.Icons.DOWNLOAD,
                                   on_click=lambda e: _do_export(title, headers, rows_data)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def _do_export(title, headers, rows_data):
        fn = title.lower().replace(' ', '_')[:30]
        path = _export_csv(fn, headers, rows_data)
        show_success(page, f"Exportado: {path}")

    def rep_ocupacion():
        hoy = date.today().isoformat()
        f_ini = ft.TextField(label="Fecha inicio * (AAAA-MM-DD)", value="2025-01-01")
        f_fin = ft.TextField(label="Fecha fin * (AAAA-MM-DD)", value=hoy)

        def run(dlg):
            if not f_ini.value.strip() or not f_fin.value.strip():
                show_error(page, "Ingrese ambas fechas."); return
            ok, data_r = ctrl.reporte_ocupacion_zonas(f_ini.value.strip(), f_fin.value.strip())
            page.pop_dialog()
            if not ok:
                show_error(page, data_r); return
            hdrs = ["Zona", "Piso", "Tipo Espacio", "Espacio #", "Total Sesiones", "Prom. Horas/Sesión"]
            rows = [[r['zona'], r['piso'], r['tipo_espacio'], r['espacio'],
                     r['total_sesiones'], r['promedio_horas']] for r in data_r]
            _show_report_table("Zonas y Espacios con Mayor Ocupación", hdrs, rows)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Periodo para reporte de ocupación", size=16),
            content=ft.Column([f_ini, f_fin], tight=True, width=300, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Ver reporte", on_click=lambda e: run(None)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def rep_ganancias():
        ok, data_r = ctrl.reporte_ganancias_mensuales()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["Mes", "Total Sesiones (sin suscripción)", "Ganancia COP"]
        rows = [[r['mes'], r['total_sesiones'], r['ganancia_total']] for r in data_r]
        _show_report_table("Ganancias Mensuales por Sesiones (Ene 2025 – May 2026)", hdrs, rows)

    reportes = [
        ("Ocupación de zonas y espacios", ft.Icons.MAP_OUTLINED, ft.Colors.BLUE_600,
         "Zonas y espacios con mayor cantidad de sesiones en un periodo, ordenado por sesiones DESC.",
         rep_ocupacion),
        ("Ganancias mensuales", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN_700,
         "Ganancias por sesiones sin suscripción desde Ene 2025 hasta May 2026.", rep_ganancias),
    ]

    rep_cards = []
    for titulo, icon, color, desc, fn in reportes:
        fn_cap = fn
        card = ft.Card(
            content=ft.Container(
                ft.Column([
                    ft.Row([ft.Icon(icon, color=color, size=28),
                            ft.Column([ft.Text(titulo, size=14, weight=ft.FontWeight.BOLD),
                                       ft.Text(desc, size=11, color=ft.Colors.SECONDARY)],
                                      spacing=2, expand=True)], spacing=10),
                    ft.Row([ft.ElevatedButton("Ver reporte", icon=ft.Icons.ASSESSMENT_OUTLINED,
                                              on_click=lambda e, f=fn_cap: f())],
                           alignment=ft.MainAxisAlignment.END),
                ], spacing=8), padding=12, width=380,
            ), elevation=2,
        )
        rep_cards.append(card)

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Espacio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fin", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tiempo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Transcurrido", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGH,
        vertical_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
    )

    load_data()
    _built[0] = True

    return ft.Column([
        ft.Row([
            ft.Text("CRUD 5 — Sesiones de Parqueo", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, filter_estado,
                    ft.ElevatedButton("+ Nueva sesión", icon=ft.Icons.ADD,
                                       on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
        ft.Row([counter_text, load_more_btn], spacing=8),
        ft.Divider(),
        ft.Text("Reportes CRUD 5", size=16, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow(
            controls=[ft.Container(card, col={"sm": 12, "md": 6}) for card in rep_cards],
            run_spacing=10, spacing=10,
        ),
    ], expand=True, scroll=ft.ScrollMode.AUTO)
