import flet as ft
import csv, os
from datetime import datetime
from controllers import factura_controller as ctrl
from components.snackbar import show_success, show_error


def _export_csv(filename, headers, rows):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(desktop, f"{filename}_{ts}.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    return path


def build(page: ft.Page):
    data = []
    _built = [False]
    _shown = [10]

    search_field = ft.TextField(
        hint_text="Buscar por placa, ID factura, tipo cobro...",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        height=40,
        content_padding=ft.Padding.symmetric(vertical=0, horizontal=10),
        on_change=lambda e: _reset_page(),
    )
    filter_estado = ft.Dropdown(
        label="Estado pago",
        width=150,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Pendiente"),
            ft.dropdown.Option("Pagada"),
        ],
        value="Todos",
        on_select=lambda e: _reset_page(),
    )

    counter_text = ft.Text("", size=12, color=ft.Colors.SECONDARY)
    load_more_btn = ft.TextButton(
        "Cargar 10 más", icon=ft.Icons.EXPAND_MORE, visible=False,
        on_click=lambda e: _load_more(),
    )

    def _reset_page():
        _shown[0] = 10
        refresh_table()

    def _load_more():
        _shown[0] += 10
        refresh_table()

    def load_data():
        nonlocal data
        _shown[0] = 10
        ok, result = ctrl.get_all()
        data = result if ok else []
        refresh_table()

    def refresh_table():
        q = search_field.value.strip().lower() if search_field.value else ""
        est_f = filter_estado.value or "Todos"
        all_rows = []
        for row in data:
            if q and not any(q in str(v).lower() for v in row.values()):
                continue
            if est_f != "Todos" and row.get('estado_pago') != est_f:
                continue

            estado = str(row.get('estado_pago', ''))
            if estado == 'Pagada':
                color = ft.Colors.GREEN_700
            else:
                color = ft.Colors.ORANGE_700

            descuento = row.get('descuento_aplicado', 0) or 0
            desc_txt = f"{descuento}%" if float(descuento) > 0 else "—"

            all_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_factura', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('tipo_vehiculo', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha_ingreso', ''))[:16])),
                ft.DataCell(ft.Text(str(row.get('fecha_salida', ''))[:16])),
                ft.DataCell(ft.Text(f"{row.get('tiempo', '—')} h")),
                ft.DataCell(ft.Text(f"$ {row.get('valor_total', 0):,.0f}")),
                ft.DataCell(ft.Text(desc_txt)),
                ft.DataCell(ft.Text(str(row.get('tipo_cobro', '')))),
                ft.DataCell(ft.Container(
                    ft.Text(estado, color=ft.Colors.WHITE, size=12),
                    bgcolor=color, border_radius=12,
                    padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
                ft.DataCell(ft.Row([
                    ft.IconButton(
                        ft.Icons.CHECK_CIRCLE_OUTLINE,
                        tooltip="Marcar como pagada",
                        icon_color=ft.Colors.GREEN_600,
                        visible=(estado == 'Pendiente'),
                        on_click=lambda e, r=row: confirm_pay(r),
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE,
                        tooltip="Eliminar factura",
                        icon_color=ft.Colors.RED_600,
                        on_click=lambda e, r=row: confirm_delete(r),
                    ),
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

    def confirm_pay(row):
        def do_pay(dlg):
            ok, msg = ctrl.mark_as_paid(row['id_factura'])
            page.pop_dialog()
            if ok:
                load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar pago"),
            content=ft.Column([
                ft.Text(f"Factura #{row.get('id_factura','')} — Placa: {row.get('placa','')}"),
                ft.Text(f"Valor total: $ {row.get('valor_total', 0):,.0f}"),
                ft.Text(f"Tipo de cobro: {row.get('tipo_cobro','')}"),
                ft.Divider(),
                ft.Text("¿Marcar esta factura como Pagada?",
                        weight=ft.FontWeight.BOLD),
            ], tight=True, width=380, spacing=6),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Confirmar pago",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                    on_click=lambda e: do_pay(dlg),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def confirm_delete(row):
        def do_delete(dlg):
            ok, msg = ctrl.delete(row['id_factura'])
            page.pop_dialog()
            if ok:
                load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(
                f"¿Eliminar factura #{row.get('id_factura','')} de la placa {row.get('placa','')}?\n"
                f"Esta acción no se puede deshacer."
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton(
                    "Eliminar",
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                    on_click=lambda e: do_delete(dlg),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    # ---------------------------------------------------------------- Reportes
    def _show_report_table(title, headers, rows_data):
        cols = [ft.DataColumn(ft.Text(h, weight=ft.FontWeight.BOLD, size=12)) for h in headers]
        rows = [ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(v) if v is not None else '', size=12)) for v in row
        ]) for row in rows_data]
        tbl = ft.DataTable(
            columns=cols, rows=rows,
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGH,
            vertical_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        )
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                ft.Column([ft.Row([tbl], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
                width=900, height=500,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Exportar CSV", icon=ft.Icons.DOWNLOAD,
                                   on_click=lambda e: _do_export(title, headers, rows_data)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def _do_export(title, headers, rows_data):
        fn = title.lower().replace(' ', '_')[:30]
        path = _export_csv(fn, headers, rows_data)
        show_success(page, f"Exportado: {path}")

    def rep_tipo_cobro():
        ok, data_r = ctrl.reporte_por_tipo_cobro()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["Tipo de cobro", "Total facturas", "Total recaudado COP", "Promedio COP"]
        rows = [[r['tipo_cobro'], r['total_facturas'],
                 f"$ {r['total_recaudado']:,.0f}" if r['total_recaudado'] else "$ 0",
                 f"$ {float(r['promedio_valor']):,.0f}" if r['promedio_valor'] else "$ 0"]
                for r in data_r]
        _show_report_table("Recaudo por Tipo de Cobro", hdrs, rows)

    def rep_pendientes():
        ok, data_r = ctrl.reporte_pendientes()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["ID", "Placa", "Tipo", "Fecha generación", "Valor COP", "Tipo cobro", "Días pendiente"]
        rows = [[r['id_factura'], r['placa'], r['tipo_vehiculo'],
                 str(r['fecha_ingreso'])[:16],
                 f"$ {r['valor_total']:,.0f}", r['tipo_cobro'],
                 r['dias_pendiente']] for r in data_r]
        _show_report_table("Facturas Pendientes de Pago", hdrs, rows)

    reportes = [
        ("Recaudo por tipo de cobro", ft.Icons.PIE_CHART_OUTLINE, ft.Colors.BLUE_600,
         "Agrupa facturas por tipo (suscripción, convenio, tarifa completa) con totales y promedios.",
         rep_tipo_cobro),
        ("Facturas pendientes", ft.Icons.PENDING_ACTIONS_OUTLINED, ft.Colors.ORANGE_700,
         "Lista todas las facturas aún no pagadas, ordenadas por fecha de generación más antigua.",
         rep_pendientes),
    ]

    rep_cards = []
    for titulo, icon, color, desc, fn in reportes:
        fn_cap = fn
        card = ft.Card(
            content=ft.Container(
                ft.Column([
                    ft.Row([ft.Icon(icon, color=color, size=28),
                            ft.Column([ft.Text(titulo, size=14, weight=ft.FontWeight.BOLD),
                                       ft.Text(desc, size=11, color=ft.Colors.SECONDARY)],
                                      spacing=2, expand=True)], spacing=10),
                    ft.Row([ft.ElevatedButton("Ver reporte", icon=ft.Icons.ASSESSMENT_OUTLINED,
                                              on_click=lambda e, f=fn_cap: f())],
                           alignment=ft.MainAxisAlignment.END),
                ], spacing=8), padding=12, width=380,
            ), elevation=2,
        )
        rep_cards.append(card)

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Placa", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo vehículo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha generación", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Fecha salida", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tiempo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Valor total", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Descuento", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tipo cobro", weight=ft.FontWeight.BOLD)),
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
            ft.Text("CRUD 6 — Facturas", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, filter_estado,
                    ft.ElevatedButton("Actualizar", icon=ft.Icons.REFRESH,
                                       on_click=lambda e: load_data())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
        ft.Row([counter_text, load_more_btn], spacing=8),
        ft.Divider(),
        ft.Text("Reportes CRUD 6", size=16, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow(
            controls=[ft.Container(card, col={"sm": 12, "md": 6}) for card in rep_cards],
            run_spacing=10, spacing=10,
        ),
    ], expand=True, scroll=ft.ScrollMode.AUTO)
