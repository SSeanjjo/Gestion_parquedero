import flet as ft
from datetime import date
from controllers import notificacion_controller as ctrl
from controllers import usuario_controller as u_ctrl
from components.snackbar import show_success, show_error

TIPOS = ["Alerta", "Información", "Recordatorio", "Multa", "Suscripción"]


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
                ft.DataCell(ft.Text(str(row.get('id_notificacion', '')))),
                ft.DataCell(ft.Text(str(row.get('nombre_usuario', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha', '')))),
                ft.DataCell(ft.Text(str(row.get('tipo_notificacion') or ''))),
                ft.DataCell(ft.Text(str(row.get('mensaje', ''))[:60] + ('...' if len(str(row.get('mensaje', ''))) > 60 else ''))),
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

    def _get_usuario_opts():
        ok, users = u_ctrl.get_all_for_dropdown()
        return [ft.dropdown.Option(key=u['cedula'], text=f"{u['nombre_completo']} ({u['cedula']})")
                for u in (users or [])]

    def open_create():
        u_opts = _get_usuario_opts()
        f_usuario = ft.Dropdown(label="Usuario destinatario *", options=u_opts, width=420)
        f_fecha = ft.TextField(label="Fecha * (AAAA-MM-DD)", value=str(date.today()))
        f_tipo = ft.Dropdown(label="Tipo de notificación",
                             options=[ft.dropdown.Option(t) for t in TIPOS])
        f_mensaje = ft.TextField(label="Mensaje *", multiline=True, min_lines=3)

        def save(dlg):
            if not f_usuario.value or not f_fecha.value.strip() or not f_mensaje.value.strip():
                show_error(page, "Usuario, fecha y mensaje son obligatorios.")
                return
            ok, msg = ctrl.create({
                'cedula_usuario': f_usuario.value,
                'fecha': f_fecha.value.strip(),
                'tipo_notificacion': f_tipo.value,
                'mensaje': f_mensaje.value.strip(),
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg("Nueva Notificación", [f_usuario, f_fecha, f_tipo, f_mensaje], save)
        page.show_dialog(dlg)

    def open_edit(row):
        u_opts = _get_usuario_opts()
        f_usuario = ft.Dropdown(label="Usuario *", options=u_opts, value=row.get('cedula_usuario'), width=420)
        f_fecha = ft.TextField(label="Fecha * (AAAA-MM-DD)", value=str(row.get('fecha', '')))
        f_tipo = ft.Dropdown(label="Tipo", options=[ft.dropdown.Option(t) for t in TIPOS],
                             value=row.get('tipo_notificacion'))
        f_mensaje = ft.TextField(label="Mensaje *", value=str(row.get('mensaje', '')),
                                 multiline=True, min_lines=3)

        def save(dlg):
            if not f_usuario.value or not f_fecha.value.strip() or not f_mensaje.value.strip():
                show_error(page, "Usuario, fecha y mensaje son obligatorios.")
                return
            ok, msg = ctrl.update(row['id_notificacion'], {
                'cedula_usuario': f_usuario.value,
                'fecha': f_fecha.value.strip(),
                'tipo_notificacion': f_tipo.value,
                'mensaje': f_mensaje.value.strip(),
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg(f"Editar Notificación #{row['id_notificacion']}",
                        [f_usuario, f_fecha, f_tipo, f_mensaje], save)
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_notificacion'])
            page.pop_dialog()
            if ok: load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar notificación #{row.get('id_notificacion','')}?"),
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
            ft.DataColumn(ft.Text("Usuario", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Mensaje", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Notificaciones", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.ElevatedButton("+ Nueva", icon=ft.Icons.ADD, on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
