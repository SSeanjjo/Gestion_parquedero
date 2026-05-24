import flet as ft
import csv, os
from datetime import datetime
from controllers import suscripcion_controller as ctrl
from controllers import usuario_controller as u_ctrl
from components.snackbar import show_success, show_error

ESTADOS = ["Activa", "Inactiva", "cancelado"]


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
        hint_text="Buscar por placa, suscriptor...",
        prefix_icon=ft.Icons.SEARCH,
        width=280,
        height=40,
        content_padding=ft.Padding.symmetric(vertical=0, horizontal=10),
        on_change=lambda e: _reset_page(),
    )
    filter_estado = ft.Dropdown(
        label="Estado",
        width=150,
        options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(s) for s in ESTADOS],
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
            if est_f != "Todos" and row.get('estado') != est_f:
                continue
            estado = str(row.get('estado', ''))
            if estado == 'Activa':
                color = ft.Colors.GREEN_700
            elif estado == 'cancelado':
                color = ft.Colors.RED_600
            else:
                color = ft.Colors.ORANGE_700
            all_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('id_suscripcion', '')))),
                ft.DataCell(ft.Text(str(row.get('placa', '')))),
                ft.DataCell(ft.Text(str(row.get('tipo_vehiculo', '')))),
                ft.DataCell(ft.Text(str(row.get('nombre_suscriptor') or '—'))),
                ft.DataCell(ft.Text(str(row.get('fecha_inicio', '')))),
                ft.DataCell(ft.Text(str(row.get('fecha_final', '')))),
                ft.DataCell(ft.Container(
                    ft.Text(estado, color=ft.Colors.WHITE, size=12),
                    bgcolor=color, border_radius=12,
                    padding=ft.Padding.symmetric(vertical=4, horizontal=10))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.DATE_RANGE, tooltip="Extender fecha",
                                  icon_color=ft.Colors.BLUE_600,
                                  on_click=lambda e, r=row: open_extend(r)),
                    ft.IconButton(ft.Icons.CANCEL_OUTLINED, tooltip="Cancelar suscripción",
                                  icon_color=ft.Colors.ORANGE_700,
                                  visible=(estado == 'Activa' or estado == 'Inactiva'),
                                  on_click=lambda e, r=row: confirm_cancel(r)),
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

    def open_create():
        _, vehiculos = ctrl.get_vehiculos()
        _, suscriptores = u_ctrl.get_suscriptores_for_dropdown()
        v_opts = [ft.dropdown.Option(key=str(v['id_vehiculo']),
                                     text=f"{v['placa']} ({v['tipo_vehiculo']})") for v in (vehiculos or [])]
        s_opts = [ft.dropdown.Option(key=u['cedula'],
                                     text=f"{u['nombre_completo']} ({u['cedula']})") for u in (suscriptores or [])]

        f_vehiculo = ft.Dropdown(label="Vehículo *", options=v_opts, width=420)
        f_suscriptor = ft.Dropdown(label="Suscriptor *", options=s_opts, width=420)
        f_inicio = ft.TextField(label="Fecha inicio * (AAAA-MM-DD)")
        f_final = ft.TextField(label="Fecha final * (AAAA-MM-DD)")
        f_estado = ft.Dropdown(label="Estado *", options=[ft.dropdown.Option(s) for s in ESTADOS],
                               value="Activa")
        f_h_ini = ft.TextField(label="Horario permitido inicio (HH:MM:SS)", hint_text="Ej: 06:00:00")
        f_h_fin = ft.TextField(label="Horario permitido fin (HH:MM:SS)", hint_text="Ej: 22:00:00")

        def save(dlg):
            if not f_vehiculo.value or not f_suscriptor.value \
               or not f_inicio.value.strip() or not f_final.value.strip():
                show_error(page, "Vehículo, suscriptor, fecha inicio y fecha final son obligatorios."); return
            ok, msg = ctrl.create({
                'id_vehiculo': int(f_vehiculo.value),
                'fecha_inicio': f_inicio.value.strip(),
                'fecha_final': f_final.value.strip(),
                'estado': f_estado.value,
                'horario_permitido_inicio': f_h_ini.value.strip() or None,
                'horario_permitido_final': f_h_fin.value.strip() or None,
            }, id_suscriptor=f_suscriptor.value)
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nueva Suscripción", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([f_vehiculo, f_suscriptor, f_inicio, f_final,
                               f_estado, f_h_ini, f_h_fin],
                              tight=True, scroll=ft.ScrollMode.AUTO, width=450, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def open_extend(row):
        f_fecha = ft.TextField(label="Nueva fecha final * (AAAA-MM-DD)",
                               value=str(row.get('fecha_final', '')))

        def save(dlg):
            if not f_fecha.value.strip():
                show_error(page, "Ingrese la nueva fecha final."); return
            ok, msg = ctrl.extend_fecha_final(row['id_suscripcion'], f_fecha.value.strip())
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Extender Suscripción #{row['id_suscripcion']}", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"Placa: {row.get('placa','')}"),
                ft.Text(f"Fecha actual: {row.get('fecha_final','')}"),
                f_fecha,
            ], tight=True, width=360, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Extender", icon=ft.Icons.DATE_RANGE, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def confirm_cancel(row):
        def do_cancel(dlg):
            ok, msg = ctrl.cancel(row['id_suscripcion'])
            page.pop_dialog()
            if ok:
                load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Cancelar suscripción"),
            content=ft.Text(f"¿Cancelar suscripción #{row.get('id_suscripcion','')} (placa {row.get('placa','')})?\nSe cambiará el estado a 'cancelado'."),
            actions=[
                ft.TextButton("Atrás", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Cancelar suscripción",
                                   style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE),
                                   on_click=lambda e: do_cancel(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    # ---------------------------------------------------------------- Reportes
    def _show_report_table(title, headers, rows_data):
        cols = [ft.DataColumn(ft.Text(h, weight=ft.FontWeight.BOLD, size=12)) for h in headers]
        rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(v) if v is not None else '', size=12)) for v in row])
                for row in rows_data]
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

    def rep_activas():
        ok, data_r = ctrl.reporte_activas()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["ID", "Placa", "Inicio", "Final", "Estado", "Días restantes"]
        rows = [[r['id_suscripcion'], r['placa'], str(r['fecha_inicio']),
                 str(r['fecha_final']), r['estado'], r['dias_restantes']] for r in data_r]
        _show_report_table("Suscripciones Activas (ordenadas por vencimiento)", hdrs, rows)

    def rep_empresas():
        ok, data_r = ctrl.reporte_por_empresa_convenio()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["Empresa", "Conv. Empresa", "% Desc.", "Conv. Estado", "Placa", "Tipo", "Sub. Activa"]
        rows = [[r['empresa'], r['estado_convenio'], r['porcentaje_descuento'],
                 r['estado_convenio_actual'], r['placa'], r['tipo_vehiculo'],
                 str(r['id_suscripcion'] or 'No')] for r in data_r]
        _show_report_table("Suscripciones por Empresa con Convenio", hdrs, rows)

    def rep_ahorro():
        ok, data_r = ctrl.reporte_ahorro_suscripcion()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["ID Sub.", "Placa", "Inicio", "Final", "Estado", "Sesiones",
                "Pagado con sub.", "Sin sub. pagaría", "Ahorro COP"]
        rows = [[r['id_suscripcion'], r['placa'], str(r['fecha_inicio']), str(r['fecha_final']),
                 r['estado'], r['sesiones_realizadas'], r['pagado_con_suscripcion'],
                 r['habria_pagado_sin_suscripcion'], r['ahorro']] for r in data_r]
        _show_report_table("Ahorro por Suscripción vs Sesiones Individuales", hdrs, rows)

    reportes = [
        ("Suscripciones activas", ft.Icons.CARD_MEMBERSHIP_OUTLINED, ft.Colors.GREEN_700,
         "Listado ordenado por fecha de vencimiento próxima.", rep_activas),
        ("Suscripciones por empresa", ft.Icons.BUSINESS_OUTLINED, ft.Colors.BLUE_600,
         "Vehículos con convenio y estado de suscripción activa.", rep_empresas),
        ("Ahorro por suscripción", ft.Icons.SAVINGS_OUTLINED, ft.Colors.PURPLE_600,
         "Diferencia entre lo pagado con suscripción vs tarifa por hora.", rep_ahorro),
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
            ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Suscriptor", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Inicio", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Final", weight=ft.FontWeight.BOLD)),
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
            ft.Text("CRUD 3 — Suscripciones", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, filter_estado,
                    ft.ElevatedButton("+ Nueva", icon=ft.Icons.ADD,
                                       on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
        ft.Row([counter_text, load_more_btn], spacing=8),
        ft.Divider(),
        ft.Text("Reportes CRUD 3", size=16, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow(
            controls=[ft.Container(card, col={"sm": 12, "md": 6}) for card in rep_cards],
            run_spacing=10, spacing=10,
        ),
    ], expand=True, scroll=ft.ScrollMode.AUTO)
