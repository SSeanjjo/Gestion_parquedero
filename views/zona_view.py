import flet as ft
from controllers import zona_controller as ctrl
from components.snackbar import show_success, show_error

TIPOS_ZONA = ["Cubierta", "Descubierta", "Mixta", "VIP"]


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
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_zona', '')))),
                ft.DataCell(ft.Text(str(row.get('nombre', '')))),
                ft.DataCell(ft.Text(str(row.get('piso', '')))),
                ft.DataCell(ft.Text(str(row.get('tipo_zona') or ''))),
                ft.DataCell(ft.Text(str(row.get('capacidad') or ''))),
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

    def open_create():
        f_nombre = ft.TextField(label="Nombre *")
        f_piso = ft.TextField(label="Piso *", keyboard_type=ft.KeyboardType.NUMBER)
        f_tipo = ft.Dropdown(label="Tipo de zona",
                             options=[ft.dropdown.Option(t) for t in TIPOS_ZONA])
        f_capacidad = ft.TextField(label="Capacidad", keyboard_type=ft.KeyboardType.NUMBER)

        def save(dlg):
            if not f_nombre.value.strip() or not f_piso.value.strip():
                show_error(page, "Nombre y piso son obligatorios.")
                return
            ok, msg = ctrl.create({
                'nombre': f_nombre.value.strip(),
                'piso': int(f_piso.value.strip()),
                'tipo_zona': f_tipo.value,
                'capacidad': int(f_capacidad.value) if f_capacidad.value.strip() else None,
            })
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = _make_dlg("Nueva Zona", [f_nombre, f_piso, f_tipo, f_capacidad], save)
        page.show_dialog(dlg)

    def open_edit(row):
        f_nombre = ft.TextField(label="Nombre *", value=str(row.get('nombre', '')))
        f_piso = ft.TextField(label="Piso *", value=str(row.get('piso', '')),
                              keyboard_type=ft.KeyboardType.NUMBER)
        f_tipo = ft.Dropdown(label="Tipo de zona", value=row.get('tipo_zona'),
                             options=[ft.dropdown.Option(t) for t in TIPOS_ZONA])
        f_capacidad = ft.TextField(label="Capacidad", value=str(row.get('capacidad') or ''),
                                   keyboard_type=ft.KeyboardType.NUMBER)

        def save(dlg):
            if not f_nombre.value.strip() or not f_piso.value.strip():
                show_error(page, "Nombre y piso son obligatorios.")
                return
            ok, msg = ctrl.update(row['id_zona'], {
                'nombre': f_nombre.value.strip(),
                'piso': int(f_piso.value.strip()),
                'tipo_zona': f_tipo.value,
                'capacidad': int(f_capacidad.value) if f_capacidad.value.strip() else None,
            })
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = _make_dlg(f"Editar Zona #{row['id_zona']}", [f_nombre, f_piso, f_tipo, f_capacidad], save)
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_zona'])
            page.pop_dialog()
            if ok: load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar zona '{row.get('nombre','')}'?"),
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
            ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Piso", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Capacidad", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Zonas", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.ElevatedButton("+ Nueva", icon=ft.Icons.ADD, on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
