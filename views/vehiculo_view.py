import flet as ft
from controllers import vehiculo_controller as ctrl
from controllers import usuario_controller as u_ctrl
from controllers import tarifa_controller as t_ctrl
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
                ft.DataCell(ft.Text(str(row.get('id_vehiculo', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('color') or ''))),
                ft.DataCell(ft.Text(str(row.get('marca') or ''))),
                ft.DataCell(ft.Text(str(row.get('modelo') or ''))),
                ft.DataCell(ft.Text(str(row.get('nombre_usuario', '')))),
                ft.DataCell(ft.Text(str(row.get('tipo_vehiculo', '')))),
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

    def _get_dropdown_options():
        _, usuarios = u_ctrl.get_all_for_dropdown()
        _, tipos = t_ctrl.get_tipos_vehiculo()
        u_opts = [ft.dropdown.Option(key=u['cedula'],
                                     text=f"{u['nombre_completo']} ({u['cedula']})") for u in (usuarios or [])]
        t_opts = [ft.dropdown.Option(key=str(t['id_tipo_vehiculo']),
                                     text=t['nombre']) for t in (tipos or [])]
        return u_opts, t_opts

    def open_create():
        u_opts, t_opts = _get_dropdown_options()
        f_placa = ft.TextField(label="Placa *")
        f_color = ft.TextField(label="Color")
        f_marca = ft.TextField(label="Marca")
        f_modelo = ft.TextField(label="Modelo")
        f_usuario = ft.Dropdown(label="Propietario (Cédula) *", options=u_opts, width=420)
        f_tipo = ft.Dropdown(label="Tipo de vehículo *", options=t_opts)

        def save(dlg):
            if not f_placa.value.strip() or not f_usuario.value or not f_tipo.value:
                show_error(page, "Complete los campos obligatorios (*).")
                return
            ok, msg = ctrl.create({
                'placa': f_placa.value.strip().upper(),
                'color': f_color.value.strip(),
                'marca': f_marca.value.strip(),
                'modelo': f_modelo.value.strip(),
                'cedula_usuario': f_usuario.value,
                'id_tipo_vehiculo': int(f_tipo.value),
            })
            if ok:
                page.pop_dialog()
                load_data()
                show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = _make_dlg("Nuevo Vehículo",
                        [f_placa, f_color, f_marca, f_modelo, f_usuario, f_tipo], save)
        page.show_dialog(dlg)

    def open_edit(row):
        u_opts, t_opts = _get_dropdown_options()
        f_placa = ft.TextField(label="Placa *", value=str(row.get('placa', '')))
        f_color = ft.TextField(label="Color", value=str(row.get('color') or ''))
        f_marca = ft.TextField(label="Marca", value=str(row.get('marca') or ''))
        f_modelo = ft.TextField(label="Modelo", value=str(row.get('modelo') or ''))
        f_usuario = ft.Dropdown(label="Propietario *", options=u_opts,
                                value=str(row.get('cedula_usuario', '')), width=420)
        f_tipo = ft.Dropdown(label="Tipo *", options=t_opts,
                             value=str(row.get('id_tipo_vehiculo', '')))

        def save(dlg):
            if not f_placa.value.strip() or not f_usuario.value or not f_tipo.value:
                show_error(page, "Complete los campos obligatorios (*).")
                return
            ok, msg = ctrl.update(row['id_vehiculo'], {
                'placa': f_placa.value.strip().upper(),
                'color': f_color.value.strip(),
                'marca': f_marca.value.strip(),
                'modelo': f_modelo.value.strip(),
                'cedula_usuario': f_usuario.value,
                'id_tipo_vehiculo': int(f_tipo.value),
            })
            if ok:
                page.pop_dialog()
                load_data()
                show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = _make_dlg(f"Editar Vehículo #{row['id_vehiculo']}",
                        [f_placa, f_color, f_marca, f_modelo, f_usuario, f_tipo], save)
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_vehiculo'])
            page.pop_dialog()
            if ok:
                load_data()
                show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar vehículo {row.get('placa','')}? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Eliminar", style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600,
                                                                    color=ft.Colors.WHITE),
                                   on_click=lambda e: do_delete(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def _make_dlg(title, fields, save_fn):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(fields, tight=True, scroll=ft.ScrollMode.AUTO,
                              width=450, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED,
                                   on_click=lambda e: save_fn(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        return dlg

    def _close(dlg):
        page.pop_dialog()

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Color", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Marca", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Modelo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Propietario", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Vehículos", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.ElevatedButton("+ Nuevo", icon=ft.Icons.ADD, on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)],
                           scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
