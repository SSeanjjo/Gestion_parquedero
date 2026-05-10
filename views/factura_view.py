import flet as ft
from controllers import factura_controller as ctrl
from components.snackbar import show_success, show_error

ESTADOS_PAGO = ["Pendiente", "Pagado", "Anulado"]


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
            estado = str(row.get('estado_pago', ''))
            color = {
                'Pagado': ft.Colors.GREEN_700,
                'Pendiente': ft.Colors.ORANGE_700,
                'Anulado': ft.Colors.RED_600,
            }.get(estado, ft.Colors.GREY)
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_factura', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('tipo_vehiculo', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha_ingreso', ''))[:16] if row.get('fecha_ingreso') else '')),
                ft.DataCell(ft.Text(str(row.get('fecha_salida', ''))[:16] if row.get('fecha_salida') else '')),
                ft.DataCell(ft.Text(f"{row.get('tiempo', '')} h")),
                ft.DataCell(ft.Text(f"${float(row.get('valor_total', 0)):,.2f}")),
                ft.DataCell(ft.Container(
                    ft.Text(estado, color=ft.Colors.WHITE, size=12),
                    bgcolor=color, border_radius=12, padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Cambiar estado",
                                  icon_color=ft.Colors.BLUE_600,
                                  on_click=lambda e, r=row: open_edit_estado(r)),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Eliminar",
                                  icon_color=ft.Colors.RED_600,
                                  on_click=lambda e, r=row: confirm_delete(r)),
                ], tight=True)),
            ]))
        table.rows.clear()
        table.rows.extend(rows)
        if _built[0]:
            table.update()

    def open_edit_estado(row):
        f_estado = ft.Dropdown(label="Estado de pago *",
                               value=row.get('estado_pago', 'Pendiente'),
                               options=[ft.dropdown.Option(s) for s in ESTADOS_PAGO])

        def save(dlg):
            if not f_estado.value:
                show_error(page, "Seleccione un estado.")
                return
            ok, msg = ctrl.update_estado(row['id_factura'], f_estado.value)
            if ok: page.pop_dialog(); load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Factura #{row['id_factura']} — {row.get('placa','')}", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"Total: ${float(row.get('valor_total', 0)):,.2f}", size=16),
                f_estado,
            ], tight=True, width=380, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ], actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_factura'])
            page.pop_dialog()
            if ok: load_data(); show_success(page, msg)
            else: show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar factura #{row.get('id_factura','')}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Eliminar", style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                                   on_click=lambda e: do_delete(dlg)),
            ], actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def _close(dlg):
        page.pop_dialog()

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ingreso", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Salida", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tiempo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Estado pago", weight=ft.FontWeight.BOLD)),
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
            ft.Text("Facturas", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, ft.Text("Las facturas se generan automáticamente al cerrar una sesión.", italic=True, size=12,
                    color=ft.Colors.SECONDARY)], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
    ], expand=True)
