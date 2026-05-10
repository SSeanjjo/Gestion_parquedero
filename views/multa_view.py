import flet as ft
from datetime import date
from controllers import multa_controller as ctrl
from components.snackbar import show_success, show_error

ESTADOS = ["Pendiente", "Pagada", "Anulada"]


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
            color = {
                'Pagada': ft.Colors.GREEN_700,
                'Pendiente': ft.Colors.ORANGE_700,
                'Anulada': ft.Colors.GREY,
            }.get(estado, ft.Colors.GREY)
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_multa', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha', '')))),
                ft.DataCell(ft.Text(str(row.get('motivo') or ''))),
                ft.DataCell(ft.Text(f"${float(row.get('valor', 0)):,.2f}")),
                ft.DataCell(ft.Container(
                    ft.Text(estado, color=ft.Colors.WHITE, size=12),
                    bgcolor=color, border_radius=12, padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
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

    def _load_sesion_opts():
        ok, sesiones = ctrl.get_sesiones_cerradas()
        return [ft.dropdown.Option(key=str(s['id_sesion']), text=s['descripcion']) for s in (sesiones or [])]

    def open_create():
        s_opts = _load_sesion_opts()
        f_sesion = ft.Dropdown(label="Sesión *", options=s_opts, width=420)
        f_fecha = ft.TextField(label="Fecha * (AAAA-MM-DD)", value=str(date.today()))
        f_motivo = ft.TextField(label="Motivo", multiline=True, min_lines=2)
        f_valor = ft.TextField(label="Valor (COP) *", keyboard_type=ft.KeyboardType.NUMBER)
        f_estado = ft.Dropdown(label="Estado *", options=[ft.dropdown.Option(s) for s in ESTADOS],
                               value="Pendiente")

        def save(dlg):
            if not f_sesion.value or not f_fecha.value.strip() or not f_valor.value.strip():
                show_error(page, "Sesión, fecha y valor son obligatorios.")
                return
            try:
                valor = float(f_valor.value.strip())
            except ValueError:
                show_error(page, "El valor debe ser un número.")
                return
            ok, msg = ctrl.create({
                'id_sesion': int(f_sesion.value),
                'fecha': f_fecha.value.strip(),
                'motivo': f_motivo.value.strip(),
                'valor': valor,
                'estado': f_estado.value,
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg("Nueva Multa", [f_sesion, f_fecha, f_motivo, f_valor, f_estado], save)
        page.show_dialog(dlg)

    def open_edit(row):
        f_fecha = ft.TextField(label="Fecha * (AAAA-MM-DD)", value=str(row.get('fecha', '')))
        f_motivo = ft.TextField(label="Motivo", value=str(row.get('motivo') or ''), multiline=True, min_lines=2)
        f_valor = ft.TextField(label="Valor (COP) *", value=str(row.get('valor', '')),
                               keyboard_type=ft.KeyboardType.NUMBER)
        f_estado = ft.Dropdown(label="Estado *", options=[ft.dropdown.Option(s) for s in ESTADOS],
                               value=row.get('estado', 'Pendiente'))
        f_sesion = ft.Text(f"Sesión: #{row.get('id_sesion','')} — Placa: {row.get('placa','')}")

        def save(dlg):
            if not f_fecha.value.strip() or not f_valor.value.strip():
                show_error(page, "Fecha y valor son obligatorios.")
                return
            try:
                valor = float(f_valor.value.strip())
            except ValueError:
                show_error(page, "El valor debe ser un número.")
                return
            ok, msg = ctrl.update(row['id_multa'], {
                'id_sesion': row['id_sesion'],
                'fecha': f_fecha.value.strip(),
                'motivo': f_motivo.value.strip(),
                'valor': valor,
                'estado': f_estado.value,
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg(f"Editar Multa #{row['id_multa']}", [f_sesion, f_fecha, f_motivo, f_valor, f_estado], save)
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_multa'])
            page.pop_dialog()
            if ok: load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar multa #{row.get('id_multa','')}?"),
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
            content=ft.Column(fields, tight=True, scroll=ft.ScrollMode.AUTO, width=430, spacing=8),
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
            ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Motivo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Valor", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Multas", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.ElevatedButton("+ Nueva", icon=ft.Icons.ADD, on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
