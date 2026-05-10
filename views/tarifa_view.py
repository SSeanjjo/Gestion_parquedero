import flet as ft
from controllers import tarifa_controller as ctrl
from components.snackbar import show_success, show_error


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
                ft.DataCell(ft.Text(str(row.get('id_tarifa', '')))),
                ft.DataCell(ft.Text(str(row.get('tipo_vehiculo', '')))),
                ft.DataCell(ft.Text(f"${float(row.get('valor_hora', 0)):,.2f}")),
                ft.DataCell(ft.Text(str(row.get('descripcion') or ''))),
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

    def _get_tipo_opts(exclude_id=None):
        ok, tipos = ctrl.get_tipos_vehiculo()
        opts = []
        for t in (tipos or []):
            if exclude_id is None or t['id_tipo_vehiculo'] == exclude_id:
                # Include all if we're editing (the current type is already taken)
                pass
            opts.append(ft.dropdown.Option(key=str(t['id_tipo_vehiculo']), text=t['nombre']))
        return opts

    def open_create():
        tipo_opts = _get_tipo_opts()
        f_tipo = ft.Dropdown(label="Tipo de vehículo *", options=tipo_opts)
        f_valor = ft.TextField(label="Valor por hora (COP) *", keyboard_type=ft.KeyboardType.NUMBER)
        f_desc = ft.TextField(label="Descripción", multiline=True, min_lines=2)

        def save(dlg):
            if not f_tipo.value or not f_valor.value.strip():
                show_error(page, "Tipo y valor son obligatorios.")
                return
            try:
                valor = float(f_valor.value.strip())
            except ValueError:
                show_error(page, "El valor debe ser un número.")
                return
            ok, msg = ctrl.create({
                'id_tipo_vehiculo': int(f_tipo.value),
                'valor_hora': valor,
                'descripcion': f_desc.value.strip(),
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg("Nueva Tarifa", [f_tipo, f_valor, f_desc], save)
        page.show_dialog(dlg)

    def open_edit(row):
        tipo_opts = _get_tipo_opts()
        f_tipo = ft.Dropdown(label="Tipo de vehículo *", options=tipo_opts,
                             value=str(row.get('id_tipo_vehiculo', '')))
        f_valor = ft.TextField(label="Valor por hora (COP) *",
                               value=str(row.get('valor_hora', '')),
                               keyboard_type=ft.KeyboardType.NUMBER)
        f_desc = ft.TextField(label="Descripción", value=str(row.get('descripcion') or ''),
                              multiline=True, min_lines=2)

        def save(dlg):
            if not f_tipo.value or not f_valor.value.strip():
                show_error(page, "Tipo y valor son obligatorios.")
                return
            try:
                valor = float(f_valor.value.strip())
            except ValueError:
                show_error(page, "El valor debe ser un número.")
                return
            ok, msg = ctrl.update(row['id_tarifa'], {
                'id_tipo_vehiculo': int(f_tipo.value),
                'valor_hora': valor,
                'descripcion': f_desc.value.strip(),
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg(f"Editar Tarifa #{row['id_tarifa']}", [f_tipo, f_valor, f_desc], save)
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_tarifa'])
            page.pop_dialog()
            if ok: load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar tarifa de {row.get('tipo_vehiculo','')}?"),
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
            ft.DataColumn(ft.Text("Tipo Vehículo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Valor / hora", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Tarifas", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.ElevatedButton("+ Nueva", icon=ft.Icons.ADD, on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
