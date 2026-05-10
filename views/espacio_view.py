import flet as ft
from controllers import espacio_controller as ctrl
from components.snackbar import show_success, show_error

ESTADOS = ["Libre", "Ocupado", "Mantenimiento"]
TIPOS_ESPACIO = ["Estándar", "Discapacitados", "Motos", "VIP", "Carga"]


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
            color = ft.Colors.GREEN_700 if estado == 'Libre' else (
                ft.Colors.RED_600 if estado == 'Ocupado' else ft.Colors.ORANGE_600)
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_espacio', '')))),
                ft.DataCell(ft.Text(str(row.get('numero', '')))),
                ft.DataCell(ft.Container(
                    ft.Text(estado, color=ft.Colors.WHITE, size=12),
                    bgcolor=color, border_radius=12, padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
                ft.DataCell(ft.Text(str(row.get('tipo_espacio') or ''))),
                ft.DataCell(ft.Text(str(row.get('nombre_zona', '')))),
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

    def _get_zona_opts():
        ok, zonas = ctrl.get_zonas()
        return [ft.dropdown.Option(key=str(z['id_zona']), text=z['nombre']) for z in (zonas or [])]

    def open_create():
        zona_opts = _get_zona_opts()
        f_numero = ft.TextField(label="Número *", keyboard_type=ft.KeyboardType.NUMBER)
        f_estado = ft.Dropdown(label="Estado *", value="Libre",
                               options=[ft.dropdown.Option(s) for s in ESTADOS])
        f_tipo = ft.Dropdown(label="Tipo de espacio",
                             options=[ft.dropdown.Option(t) for t in TIPOS_ESPACIO])
        f_zona = ft.Dropdown(label="Zona *", options=zona_opts)

        def save(dlg):
            if not f_numero.value.strip() or not f_estado.value or not f_zona.value:
                show_error(page, "Número, estado y zona son obligatorios.")
                return
            ok, msg = ctrl.create({
                'numero': int(f_numero.value.strip()),
                'estado': f_estado.value,
                'tipo_espacio': f_tipo.value,
                'id_zona': int(f_zona.value),
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg("Nuevo Espacio", [f_numero, f_estado, f_tipo, f_zona], save)
        page.show_dialog(dlg)

    def open_edit(row):
        zona_opts = _get_zona_opts()
        f_numero = ft.TextField(label="Número *", value=str(row.get('numero', '')),
                                keyboard_type=ft.KeyboardType.NUMBER)
        f_estado = ft.Dropdown(label="Estado *", value=row.get('estado', 'Libre'),
                               options=[ft.dropdown.Option(s) for s in ESTADOS])
        f_tipo = ft.Dropdown(label="Tipo de espacio", value=row.get('tipo_espacio'),
                             options=[ft.dropdown.Option(t) for t in TIPOS_ESPACIO])
        f_zona = ft.Dropdown(label="Zona *", value=str(row.get('id_zona', '')), options=zona_opts)

        def save(dlg):
            if not f_numero.value.strip() or not f_estado.value or not f_zona.value:
                show_error(page, "Número, estado y zona son obligatorios.")
                return
            ok, msg = ctrl.update(row['id_espacio'], {
                'numero': int(f_numero.value.strip()),
                'estado': f_estado.value,
                'tipo_espacio': f_tipo.value,
                'id_zona': int(f_zona.value),
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg(f"Editar Espacio #{row['id_espacio']}", [f_numero, f_estado, f_tipo, f_zona], save)
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_espacio'])
            page.pop_dialog()
            if ok: load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar espacio #{row.get('numero','')}?"),
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
            content=ft.Column(fields, tight=True, scroll=ft.ScrollMode.AUTO, width=420, spacing=8),
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
            ft.DataColumn(ft.Text("Número", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Zona", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Espacios de Parqueo", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.ElevatedButton("+ Nuevo", icon=ft.Icons.ADD, on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
