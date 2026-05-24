import flet as ft
import csv, os
from datetime import datetime
from controllers import empresa_controller as ctrl
from components.snackbar import show_success, show_error

ESTADOS_CONV = ["activo", "inactivo"]


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
        hint_text="Buscar por nombre, NIT, ciudad...",
        prefix_icon=ft.Icons.SEARCH,
        width=280,
        height=40,
        content_padding=ft.Padding.symmetric(vertical=0, horizontal=10),
        on_change=lambda e: _reset_page(),
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
        all_rows = []
        for row in data:
            if q and not any(q in str(v).lower() for v in row.values()):
                continue
            est = str(row.get('estado_convenio') or 'activo')
            color_conv = ft.Colors.GREEN_700 if est == 'activo' else ft.Colors.RED_600
            est_act = str(row.get('estado_convenio_actual') or '—')
            pct = row.get('porcentaje_descuento')
            all_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_empresa', '')))),
                ft.DataCell(ft.Text(str(row.get('nombre', '')))),
                ft.DataCell(ft.Text(str(row.get('nit') or ''))),
                ft.DataCell(ft.Text(str(row.get('ciudad') or ''))),
                ft.DataCell(ft.Text(str(row.get('telefono') or ''))),
                ft.DataCell(ft.Container(
                    ft.Text(est, color=ft.Colors.WHITE, size=12),
                    bgcolor=color_conv, border_radius=12,
                    padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
                ft.DataCell(ft.Text(f"{pct}%" if pct is not None else '—')),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Editar",
                                  icon_color=ft.Colors.BLUE_600,
                                  on_click=lambda e, r=row: open_edit(r)),
                    ft.IconButton(ft.Icons.BLOCK, tooltip="Desactivar empresa",
                                  icon_color=ft.Colors.RED_600,
                                  on_click=lambda e, r=row: confirm_deactivate(r)),
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

    def _build_fields(row=None):
        is_edit = row is not None
        return {
            'nombre': ft.TextField(label="Nombre *",
                                   value=str(row.get('nombre', '') if is_edit else '')),
            'nit': ft.TextField(label="NIT",
                                value=str(row.get('nit') or '' if is_edit else '')),
            'ciudad': ft.TextField(label="Ciudad",
                                   value=str(row.get('ciudad') or '' if is_edit else '')),
            'telefono': ft.TextField(label="Teléfono",
                                     value=str(row.get('telefono') or '' if is_edit else '')),
            'direccion': ft.TextField(label="Dirección",
                                      value=str(row.get('direccion') or '' if is_edit else '')),
            'estado_conv': ft.Dropdown(
                label="Estado empresa",
                options=[ft.dropdown.Option(s) for s in ESTADOS_CONV],
                value=str(row.get('estado_convenio') or 'activo') if is_edit else 'activo',
            ),
            'conv_estado': ft.Dropdown(
                label="Estado convenio",
                options=[ft.dropdown.Option(s) for s in ESTADOS_CONV],
                value=str(row.get('estado_convenio_actual') or 'activo') if is_edit else 'activo',
            ),
            'pct': ft.TextField(
                label="% de descuento convenio",
                value=str(row.get('porcentaje_descuento') or '0') if is_edit else '0',
                keyboard_type=ft.KeyboardType.NUMBER,
            ),
        }

    def open_create():
        f = _build_fields()

        def save(dlg):
            if not f['nombre'].value.strip():
                show_error(page, "El nombre es obligatorio."); return
            ok, msg = ctrl.create({
                'nombre': f['nombre'].value.strip(),
                'nit': f['nit'].value.strip(),
                'ciudad': f['ciudad'].value.strip(),
                'telefono': f['telefono'].value.strip(),
                'direccion': f['direccion'].value.strip(),
                'estado_convenio': f['estado_conv'].value,
                'porcentaje_descuento': float(f['pct'].value or 0),
                'estado_convenio_conv': f['conv_estado'].value,
            })
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nueva Empresa con Convenio", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(list(f.values()),
                              tight=True, scroll=ft.ScrollMode.AUTO, width=440, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def open_edit(row):
        f = _build_fields(row)

        def save(dlg):
            if not f['nombre'].value.strip():
                show_error(page, "El nombre es obligatorio."); return
            ok, msg = ctrl.update(row['id_empresa'], {
                'nombre': f['nombre'].value.strip(),
                'nit': f['nit'].value.strip(),
                'ciudad': f['ciudad'].value.strip(),
                'telefono': f['telefono'].value.strip(),
                'direccion': f['direccion'].value.strip(),
                'estado_convenio': f['estado_conv'].value,
                'porcentaje_descuento': float(f['pct'].value or 0),
                'estado_convenio_conv': f['conv_estado'].value,
            })
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Empresa #{row['id_empresa']}", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(list(f.values()),
                              tight=True, scroll=ft.ScrollMode.AUTO, width=440, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def confirm_deactivate(row):
        def do_deactivate(dlg):
            ok, msg = ctrl.deactivate(row['id_empresa'])
            page.pop_dialog()
            if ok:
                load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Desactivar empresa"),
            content=ft.Text(f"¿Desactivar empresa '{row.get('nombre','')}' y su convenio?\nEsto no elimina los datos."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Desactivar",
                                   style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                                   on_click=lambda e: do_deactivate(dlg)),
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
                width=800, height=480,
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

    def rep_tarifas():
        ok, data_r = ctrl.reporte_catalogo_tarifas()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["Tipo Vehículo", "Valor/hora COP", "Descripción"]
        rows = [[r['tipo_vehiculo'], r['valor_hora'], r['descripcion'] or ''] for r in data_r]
        _show_report_table("Catálogo de Tarifas por Tipo de Vehículo", hdrs, rows)

    def rep_vehiculos_empresa():
        ok, data_r = ctrl.reporte_vehiculos_por_empresa()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["Empresa", "Est. Convenio Emp.", "% Desc.", "Est. Conv.", "Placa", "Tipo", "Tiene Suscripción"]
        rows = [[r['empresa'], r['estado_convenio'], r['porcentaje_descuento'],
                 r['estado_convenio_actual'], r['placa'], r['tipo_vehiculo'],
                 r['tiene_suscripcion_activa']] for r in data_r]
        _show_report_table("Vehículos por Empresa con Convenio Activo", hdrs, rows)

    reportes = [
        ("Catálogo de tarifas", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN_700,
         "Tipos de vehículo, valor por hora y descripción, ordenados por tarifa.", rep_tarifas),
        ("Vehículos por empresa", ft.Icons.DIRECTIONS_CAR_OUTLINED, ft.Colors.BLUE_600,
         "Vehículos vinculados a empresas con convenio activo y su estado de suscripción.", rep_vehiculos_empresa),
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
            ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("NIT", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ciudad", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Estado empresa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("% Desc.", weight=ft.FontWeight.BOLD)),
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
            ft.Text("CRUD 4 — Empresas con Convenio", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field,
                    ft.ElevatedButton("+ Nueva", icon=ft.Icons.ADD,
                                       on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
        ft.Row([counter_text, load_more_btn], spacing=8),
        ft.Divider(),
        ft.Text("Reportes CRUD 4", size=16, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow(
            controls=[ft.Container(card, col={"sm": 12, "md": 6}) for card in rep_cards],
            run_spacing=10, spacing=10,
        ),
    ], expand=True, scroll=ft.ScrollMode.AUTO)
