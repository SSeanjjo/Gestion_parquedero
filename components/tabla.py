import flet as ft


def build_table(columns: list[str], rows_data: list[list], on_edit=None, on_delete=None):
    """
    columns: lista de strings con los nombres de columna
    rows_data: lista de listas con valores de cada fila (sin incluir la columna de acciones)
    on_edit: callback(index) cuando se hace clic en editar
    on_delete: callback(index) cuando se hace clic en eliminar
    """
    dt_columns = [ft.DataColumn(ft.Text(c, weight=ft.FontWeight.BOLD)) for c in columns]
    if on_edit or on_delete:
        dt_columns.append(ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)))

    dt_rows = []
    for i, row_vals in enumerate(rows_data):
        cells = [ft.DataCell(ft.Text(str(v) if v is not None else "")) for v in row_vals]
        if on_edit or on_delete:
            action_btns = []
            if on_edit:
                action_btns.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        tooltip="Editar",
                        icon_color=ft.Colors.BLUE_600,
                        on_click=lambda e, idx=i: on_edit(idx),
                    )
                )
            if on_delete:
                action_btns.append(
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Eliminar",
                        icon_color=ft.Colors.RED_600,
                        on_click=lambda e, idx=i: on_delete(idx),
                    )
                )
            cells.append(ft.DataCell(ft.Row(action_btns, tight=True)))
        dt_rows.append(ft.DataRow(cells=cells))

    return ft.DataTable(
        columns=dt_columns,
        rows=dt_rows,
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        vertical_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGH,
    )
