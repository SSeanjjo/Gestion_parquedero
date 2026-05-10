import flet as ft
from controllers import suscripcion_controller as ctrl
from components.snackbar import show_success, show_error

ESTADOS = ["Activa", "Inactiva", "Suspendida"]


def build(page: ft.Page):
    data = []
    _built = [False]
    search_field = ft.TextField(
        hint_text="Buscar...",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
        height=40,
        content_padding=ft.Padding.symmetric(vertical=0, horizontal=10),
        on_change=lambda e: refresh_table(),
    )

    def load_data():
        nonlocal data
        ok, result = ctrl.get_all()
        data = result if ok else []
        refresh_table()

    def refresh_table():
        q = search_field.value.strip().lower() if search_field.value else ""
        rows = []
        for row in (r for r in data if not q or any(q in str(v).lower() for v in r.values())):
            estado = str(row.get('estado', ''))
            color = ft.Colors.GREEN_700 if estado == 'Activa' else ft.Colors.ORANGE_700
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_suscripcion', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha_inicio', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha_final', '')))),
                ft.DataCell(ft.Container(
                    ft.Text(estado, color=ft.Colors.WHITE, size=12),
                    bgcolor=color, border_radius=12, padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
                ft.DataCell(ft.Text(f"{row.get('descuento', 0)}%")),
                ft.DataCell(ft.Text(str(row.get('nombre_empresa') or 'Sin empresa'))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Editar",
                                  icon_color=ft.Colors.BLUE_600,
                                  on_click=lambda e, r=row: open_edit(r)),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Eliminar",
                                  icon_color=ft.Colors.RED_600,
                                  on_click=lambda e, r=row: confirm_delete(r)),
                ], tight=True)),
            ]))
        table.rows.clear()
        table.rows.extend(rows)
        if _built[0]:
            table.update()

    def _load_opts():
        _, vehiculos = ctrl.get_vehiculos()
        _, empresas = ctrl.get_empresas()
        v_opts = [ft.dropdown.Option(key=str(v['id_vehiculo']), text=v['placa']) for v in (vehiculos or [])]
        e_opts = [ft.dropdown.Option(key="", text="Sin empresa")] + \
                 [ft.dropdown.Option(key=str(e['id_empresa']), text=e['nombre']) for e in (empresas or [])]
        return v_opts, e_opts

    def _build_fields(row=None):
        v_opts, e_opts = _load_opts()
        return {
            'vehiculo': ft.Dropdown(label="Vehículo (placa) *", options=v_opts, width=420,
                                    value=str(row.get('id_vehiculo', '')) if row else None),
            'empresa': ft.Dropdown(label="Empresa (convenio)", options=e_opts, width=420,
                                   value=str(row.get('id_empresa') or '') if row else ''),
            'inicio': ft.TextField(label="Fecha inicio * (AAAA-MM-DD)",
                                   value=str(row.get('fecha_inicio', '')) if row else ''),
            'final': ft.TextField(label="Fecha final * (AAAA-MM-DD)",
                                  value=str(row.get('fecha_final', '')) if row else ''),
            'estado': ft.Dropdown(label="Estado *", options=[ft.dropdown.Option(s) for s in ESTADOS],
                                  value=row.get('estado', 'Activa') if row else 'Activa'),
            'descuento': ft.TextField(label="Descuento (%)",
                                      value=str(row.get('descuento', '0')) if row else '0',
                                      keyboard_type=ft.KeyboardType.NUMBER),
            'h_inicio': ft.TextField(label="Horario inicio (HH:MM:SS)",
                                     value=str(row.get('horario_permitido_inicio') or '') if row else ''),
            'h_final': ft.TextField(label="Horario fin (HH:MM:SS)",
                                    value=str(row.get('horario_permitido_final') or '') if row else ''),
        }

    def open_create():
        f = _build_fields()

        def save(dlg):
            if not f['vehiculo'].value or not f['inicio'].value.strip() or not f['final'].value.strip():
                show_error(page, "Vehículo, fecha inicio y fecha final son obligatorios.")
                return
            ok, msg = ctrl.create({
                'id_vehiculo': int(f['vehiculo'].value),
                'id_empresa': int(f['empresa'].value) if f['empresa'].value else None,
                'fecha_inicio': f['inicio'].value.strip(),
                'fecha_final': f['final'].value.strip(),
                'estado': f['estado'].value,
                'descuento': float(f['descuento'].value or 0),
                'horario_permitido_inicio': f['h_inicio'].value.strip() or None,
                'horario_permitido_final': f['h_final'].value.strip() or None,
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        fields_list = list(f.values())
        dlg = _make_dlg("Nueva Suscripción", fields_list, save)
        page.show_dialog(dlg)

    def open_edit(row):
        f = _build_fields(row)

        def save(dlg):
            if not f['vehiculo'].value or not f['inicio'].value.strip() or not f['final'].value.strip():
                show_error(page, "Vehículo, fecha inicio y fecha final son obligatorios.")
                return
            ok, msg = ctrl.update(row['id_suscripcion'], {
                'id_vehiculo': int(f['vehiculo'].value),
                'id_empresa': int(f['empresa'].value) if f['empresa'].value else None,
                'fecha_inicio': f['inicio'].value.strip(),
                'fecha_final': f['final'].value.strip(),
                'estado': f['estado'].value,
                'descuento': float(f['descuento'].value or 0),
                'horario_permitido_inicio': f['h_inicio'].value.strip() or None,
                'horario_permitido_final': f['h_final'].value.strip() or None,
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        fields_list = list(f.values())
        dlg = _make_dlg(f"Editar Suscripción #{row['id_suscripcion']}", fields_list, save)
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_suscripcion'])
            page.pop_dialog()
            if ok: load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar suscripción #{row.get('id_suscripcion','')}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Eliminar", style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                                   on_click=lambda e: do_delete(dlg)),
            ], actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def _make_dlg(title, fields, save_fn):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(fields, tight=True, scroll=ft.ScrollMode.AUTO, width=450, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED,
                                   on_click=lambda e: save_fn(dlg)),
            ], actions_alignment=ft.MainAxisAlignment.END,
        )
        return dlg

    def _close(dlg):
        page.pop_dialog()

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Final", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Descuento", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Empresa", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Suscripciones", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.ElevatedButton("+ Nueva", icon=ft.Icons.ADD, on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
