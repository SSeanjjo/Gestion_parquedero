import flet as ft
from datetime import datetime
from controllers import sesion_controller as ctrl
from controllers import vehiculo_controller as v_ctrl
from controllers import espacio_controller as e_ctrl
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
            estado = str(row.get('estado', ''))
            color = ft.Colors.GREEN_700 if estado == 'Activa' else ft.Colors.BLUE_GREY_400
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_sesion', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('espacio_desc', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha_inicio', ''))[:16] if row.get('fecha_inicio') else '')),
                ft.DataCell(ft.Text(str(row.get('fecha_fin', '') or '—')[:16] if row.get('fecha_fin') else '—')),
                ft.DataCell(ft.Text(f"{row.get('tiempo', '') or '—'} h")),
                ft.DataCell(ft.Container(
                    ft.Text(estado, color=ft.Colors.WHITE, size=12),
                    bgcolor=color, border_radius=12, padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.CANCEL_OUTLINED, tooltip="Cerrar sesión",
                                  icon_color=ft.Colors.ORANGE_700,
                                  visible=(estado == 'Activa'),
                                  on_click=lambda e, r=row: open_close(r)),
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
        ok_v, vehiculos = v_ctrl.get_all_for_dropdown()
        ok_e, espacios = e_ctrl.get_libres()
        v_opts = [ft.dropdown.Option(key=str(v['id_vehiculo']), text=v['placa']) for v in (vehiculos or [])]
        e_opts = [ft.dropdown.Option(key=str(e['id_espacio']), text=e['descripcion']) for e in (espacios or [])]

        f_vehiculo = ft.Dropdown(label="Vehículo (placa) *", options=v_opts, width=420)
        f_espacio = ft.Dropdown(label="Espacio libre *", options=e_opts, width=420)
        f_fecha = ft.TextField(label="Fecha y hora inicio (AAAA-MM-DD HH:MM:SS)",
                               value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        def save(dlg):
            if not f_vehiculo.value or not f_espacio.value:
                show_error(page, "Vehículo y espacio son obligatorios.")
                return
            ok, msg = ctrl.create({
                'id_vehiculo': int(f_vehiculo.value),
                'id_espacio': int(f_espacio.value),
                'fecha_inicio': f_fecha.value.strip(),
            })
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = _make_dlg("Nueva Sesión de Parqueo", [f_vehiculo, f_espacio, f_fecha], save)
        page.show_dialog(dlg)

    def open_close(row):
        f_fecha = ft.TextField(label="Fecha y hora de salida (AAAA-MM-DD HH:MM:SS)",
                               value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        def save(dlg):
            if not f_fecha.value.strip():
                show_error(page, "Ingrese la fecha de salida.")
                return
            ok, msg = ctrl.close_session(row['id_sesion'], f_fecha.value.strip())
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Cerrar Sesión #{row['id_sesion']} — {row.get('placa','')}", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"Espacio: {row.get('espacio_desc', '')}"),
                ft.Text(f"Inicio: {str(row.get('fecha_inicio',''))[:16]}"),
                ft.Divider(),
                f_fecha,
                ft.Text("Al cerrar se genera la factura automáticamente.", italic=True, size=12),
            ], tight=True, width=420, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Cerrar sesión", icon=ft.Icons.CANCEL_OUTLINED,
                                   on_click=lambda e: save(dlg)),
            ], actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_sesion'])
            page.pop_dialog()
            if ok: load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar sesión #{row.get('id_sesion','')}?"),
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
            ft.DataColumn(ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Espacio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fin", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tiempo", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Sesiones de Parqueo", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.ElevatedButton("+ Nueva sesión", icon=ft.Icons.ADD, on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
