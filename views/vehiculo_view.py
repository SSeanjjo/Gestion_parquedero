import flet as ft
from controllers import vehiculo_controller as ctrl
from controllers import usuario_controller as u_ctrl
from controllers import tarifa_controller as t_ctrl
from controllers import empresa_controller as e_ctrl
from components.snackbar import show_success, show_error


def build(page: ft.Page):
    data = []
    _built = [False]
    _shown = [10]

    search_field = ft.TextField(
        hint_text="Buscar por placa...",
        prefix_icon=ft.Icons.SEARCH,
        width=220,
        height=40,
        content_padding=ft.Padding.symmetric(vertical=0, horizontal=10),
        on_change=lambda e: _apply_reset(),
    )
    filter_suscripcion = ft.Dropdown(
        label="Suscripción",
        width=150,
        options=[
            ft.dropdown.Option("Todas"),
            ft.dropdown.Option("Con suscripción activa"),
            ft.dropdown.Option("Sin suscripción"),
        ],
        value="Todas",
        on_select=lambda e: _apply_reset(),
    )

    counter_text = ft.Text("", size=12, color=ft.Colors.SECONDARY)
    load_more_btn = ft.TextButton(
        "Cargar 10 más", icon=ft.Icons.EXPAND_MORE, visible=False,
        on_click=lambda e: _load_more(),
    )

    def _apply_reset():
        _shown[0] = 10
        apply_filters()

    def _load_more():
        _shown[0] += 10
        refresh_table()

    def apply_filters():
        placa = search_field.value.strip() or None
        fs = filter_suscripcion.value or "Todas"
        con_sub = None
        if fs == "Con suscripción activa":
            con_sub = True
        elif fs == "Sin suscripción":
            con_sub = False
        ok, result = ctrl.get_all(con_suscripcion=con_sub, placa=placa)
        nonlocal data
        data = result if ok else []
        refresh_table()

    def load_data():
        nonlocal data
        _shown[0] = 10
        ok, result = ctrl.get_all()
        data = result if ok else []
        refresh_table()

    def refresh_table():
        all_rows = []
        for row in data:
            all_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_vehiculo', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('color') or ''))),
                ft.DataCell(ft.Text(str(row.get('marca') or ''))),
                ft.DataCell(ft.Text(str(row.get('modelo') or ''))),
                ft.DataCell(ft.Text(str(row.get('tipo_vehiculo', '')))),
                ft.DataCell(ft.Text(str(row.get('nombre_usuario', '')))),
                ft.DataCell(ft.Text(str(row.get('nombre_empresa') or 'Ninguna'))),
                ft.DataCell(ft.Text(str(row.get('tiene_suscripcion', 'No')))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Editar",
                                  icon_color=ft.Colors.BLUE_600,
                                  on_click=lambda e, r=row: open_edit(r)),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Eliminar",
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

    def _get_opts():
        _, usuarios = u_ctrl.get_all_for_dropdown()
        _, tipos = t_ctrl.get_tipos_vehiculo()
        _, empresas = e_ctrl.get_all()
        u_opts = [ft.dropdown.Option(key=u['cedula'],
                                     text=f"{u['nombre_completo']} ({u['cedula']})") for u in (usuarios or [])]
        t_opts = [ft.dropdown.Option(key=str(t['id_tipo_vehiculo']), text=t['nombre']) for t in (tipos or [])]
        e_opts = [ft.dropdown.Option(key="", text="Sin empresa")] + \
                 [ft.dropdown.Option(key=str(e['id_empresa']), text=e['nombre']) for e in (empresas or [])]
        return u_opts, t_opts, e_opts

    def open_create():
        # Campo de búsqueda de propietario por nombre o cédula
        search_owner = ft.TextField(label="Buscar propietario por nombre o cédula", width=420)
        owner_dd = ft.Dropdown(label="Propietario *", options=[], width=420)
        search_btn = ft.ElevatedButton("Buscar", icon=ft.Icons.SEARCH,
                                        on_click=lambda e: _search_owner(search_owner.value, owner_dd))

        _, t_opts_list, e_opts_list = _get_opts()
        _, tipos = t_ctrl.get_tipos_vehiculo()
        t_opts = [ft.dropdown.Option(key=str(t['id_tipo_vehiculo']), text=t['nombre']) for t in (tipos or [])]

        _, empresas = e_ctrl.get_all()
        e_opts = [ft.dropdown.Option(key="", text="Sin empresa")] + \
                 [ft.dropdown.Option(key=str(e['id_empresa']), text=e['nombre']) for e in (empresas or [])]

        f_placa = ft.TextField(label="Placa *")
        f_color = ft.TextField(label="Color")
        f_marca = ft.TextField(label="Marca")
        f_modelo = ft.TextField(label="Modelo")
        f_tipo = ft.Dropdown(label="Tipo de vehículo *", options=t_opts)
        f_empresa = ft.Dropdown(label="Empresa (convenio)", options=e_opts, width=420)

        def save(dlg):
            if not f_placa.value.strip() or not owner_dd.value or not f_tipo.value:
                show_error(page, "Placa, propietario y tipo son obligatorios."); return
            ok, msg = ctrl.create({
                'placa': f_placa.value.strip().upper(),
                'color': f_color.value.strip(),
                'marca': f_marca.value.strip(),
                'modelo': f_modelo.value.strip(),
                'cedula_usuario': owner_dd.value,
                'id_tipo_vehiculo': int(f_tipo.value),
                'id_empresa': int(f_empresa.value) if f_empresa.value else None,
            })
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Vehículo", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Buscar propietario:", weight=ft.FontWeight.BOLD, size=13),
                ft.Row([search_owner, search_btn], spacing=8),
                owner_dd,
                ft.Divider(),
                f_placa, f_color, f_marca, f_modelo, f_tipo, f_empresa,
            ], tight=True, scroll=ft.ScrollMode.AUTO, width=460, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def _search_owner(term, owner_dd):
        if not term.strip():
            show_error(page, "Ingrese un término de búsqueda."); return
        ok, result = u_ctrl.search_by_cedula_or_name(term.strip())
        if ok:
            owner_dd.options = [
                ft.dropdown.Option(key=u['cedula'],
                                   text=f"{u['nombre_completo']} ({u['cedula']})") for u in result
            ]
            page.update()
        else:
            show_error(page, result)

    def open_edit(row):
        u_opts, t_opts, e_opts = _get_opts()
        f_placa = ft.TextField(label="Placa *", value=str(row.get('placa', '')))
        f_color = ft.TextField(label="Color", value=str(row.get('color') or ''))
        f_marca = ft.TextField(label="Marca", value=str(row.get('marca') or ''))
        f_modelo = ft.TextField(label="Modelo", value=str(row.get('modelo') or ''))
        f_usuario = ft.Dropdown(label="Propietario *", options=u_opts,
                                value=str(row.get('cedula_usuario', '')), width=420)
        f_tipo = ft.Dropdown(label="Tipo *", options=t_opts,
                             value=str(row.get('id_tipo_vehiculo', '')))
        f_empresa = ft.Dropdown(label="Empresa (convenio)", options=e_opts, width=420,
                                value=str(row.get('id_empresa') or ''))

        def save(dlg):
            if not f_placa.value.strip() or not f_usuario.value or not f_tipo.value:
                show_error(page, "Complete los campos obligatorios."); return
            ok, msg = ctrl.update(row['id_vehiculo'], {
                'placa': f_placa.value.strip().upper(),
                'color': f_color.value.strip(),
                'marca': f_marca.value.strip(),
                'modelo': f_modelo.value.strip(),
                'cedula_usuario': f_usuario.value,
                'id_tipo_vehiculo': int(f_tipo.value),
                'id_empresa': int(f_empresa.value) if f_empresa.value else None,
            })
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Vehículo #{row['id_vehiculo']}", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([f_placa, f_color, f_marca, f_modelo, f_usuario, f_tipo, f_empresa],
                              tight=True, scroll=ft.ScrollMode.AUTO, width=460, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_vehiculo'])
            page.pop_dialog()
            if ok:
                load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar vehículo {row.get('placa','')}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Eliminar",
                                   style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                                   on_click=lambda e: do_delete(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Color", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Marca", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Modelo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Propietario", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Empresa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Suscripción", weight=ft.FontWeight.BOLD)),
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
            ft.Text("CRUD 2 — Vehículos", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, filter_suscripcion,
                    ft.ElevatedButton("+ Nuevo", icon=ft.Icons.ADD,
                                       on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
        ft.Row([counter_text, load_more_btn], spacing=8),
    ], expand=True)
