import flet as ft
import csv, os
from datetime import datetime, date
from controllers import usuario_controller as ctrl
from controllers import turno_controller as t_ctrl
from components.snackbar import show_success, show_error

ROLES = ["Administrador", "Operador", "Suscriptor"]
ESTADOS_OP = ["Activo", "Inactivo"]


def _export_csv(filename, headers, rows):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(desktop, f"{filename}_{ts}.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    return path


def _make_dlg(page, title, fields, save_fn):
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
        content=ft.Column(fields, tight=True, scroll=ft.ScrollMode.AUTO, width=460, spacing=8),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED,
                               on_click=lambda e: save_fn(dlg)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    return dlg


def build(page: ft.Page):
    data = []
    _built = [False]
    _shown = [10]

    search_field = ft.TextField(
        hint_text="Buscar por cédula, nombre, correo...",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        height=40,
        content_padding=ft.Padding.symmetric(vertical=0, horizontal=10),
        on_change=lambda e: _reset_page(),
    )
    filter_rol = ft.Dropdown(
        label="Filtrar rol",
        width=160,
        options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(r) for r in ROLES],
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
        rol_f = filter_rol.value or "Todos"
        all_rows = []
        for row in data:
            if q and not any(q in str(v).lower() for v in row.values()):
                continue
            if rol_f != "Todos" and row.get('rol') != rol_f:
                continue
            nombre = " ".join(filter(None, [
                row.get('primer_nombre'), row.get('segundo_nombre'),
                row.get('primer_apellido'), row.get('segundo_apellido')
            ]))
            all_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row.get('cedula', '')))),
                ft.DataCell(ft.Text(nombre)),
                ft.DataCell(ft.Text(str(row.get('correo', '')))),
                ft.DataCell(ft.Text(str(row.get('rol', '')))),
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

    def open_create():
        f_cedula = ft.TextField(label="Cédula *")
        f_pnombre = ft.TextField(label="Primer nombre *")
        f_snombre = ft.TextField(label="Segundo nombre")
        f_papellido = ft.TextField(label="Primer apellido *")
        f_sapellido = ft.TextField(label="Segundo apellido")
        f_correo = ft.TextField(label="Correo *")
        f_rol = ft.Dropdown(label="Rol *", options=[ft.dropdown.Option(r) for r in ROLES])

        f_pass = ft.TextField(label="Contraseña *", password=True, can_reveal_password=True)
        f_codigo_adm = ft.TextField(label="Código interno admin (auto-generado si vacío)")
        admin_col = ft.Column([f_pass, f_codigo_adm], visible=False, spacing=8)

        f_codigo_op = ft.TextField(label="Código interno operador (auto-generado si vacío)")
        f_estado_op = ft.Dropdown(label="Estado", options=[ft.dropdown.Option(s) for s in ESTADOS_OP],
                                  value="Activo")
        op_col = ft.Column([f_codigo_op, f_estado_op], visible=False, spacing=8)

        f_fecha_reg = ft.TextField(label="Fecha registro (AAAA-MM-DD)",
                                   value=date.today().isoformat())
        sus_col = ft.Column([f_fecha_reg], visible=False, spacing=8)

        def on_rol_change(e):
            admin_col.visible = f_rol.value == "Administrador"
            op_col.visible = f_rol.value == "Operador"
            sus_col.visible = f_rol.value == "Suscriptor"
            page.update()

        f_rol.on_select = on_rol_change

        def save(dlg):
            if not f_cedula.value.strip() or not f_pnombre.value.strip() \
               or not f_papellido.value.strip() or not f_correo.value.strip() or not f_rol.value:
                show_error(page, "Complete los campos obligatorios (*).")
                return
            if f_rol.value == "Administrador" and not f_pass.value:
                show_error(page, "La contraseña es obligatoria para administradores.")
                return
            d = {
                'cedula': f_cedula.value.strip(),
                'primer_nombre': f_pnombre.value.strip(),
                'segundo_nombre': f_snombre.value.strip(),
                'primer_apellido': f_papellido.value.strip(),
                'segundo_apellido': f_sapellido.value.strip(),
                'correo': f_correo.value.strip(),
                'rol': f_rol.value,
                'contrasenia': f_pass.value,
                'codigo_interno': f_codigo_adm.value.strip() or f_codigo_op.value.strip(),
                'estado': f_estado_op.value,
                'fecha_registro': f_fecha_reg.value.strip(),
            }
            ok, msg = ctrl.create(d)
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Usuario", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                f_cedula, f_pnombre, f_snombre, f_papellido, f_sapellido, f_correo, f_rol,
                ft.Divider(), admin_col, op_col, sus_col,
            ], tight=True, scroll=ft.ScrollMode.AUTO, width=460, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def open_edit(row):
        ok, result = ctrl.get_by_cedula(row['cedula'])
        if not ok:
            show_error(page, result); return
        u, sub_a, sub_o, sub_s = result
        rol = row.get('rol', '')

        f_pnombre = ft.TextField(label="Primer nombre *", value=u.get('primer_nombre', ''))
        f_snombre = ft.TextField(label="Segundo nombre", value=u.get('segundo_nombre') or '')
        f_papellido = ft.TextField(label="Primer apellido *", value=u.get('primer_apellido', ''))
        f_sapellido = ft.TextField(label="Segundo apellido", value=u.get('segundo_apellido') or '')
        f_correo = ft.TextField(label="Correo *", value=u.get('correo', ''))

        extra_fields = []
        if rol == 'Administrador' and sub_a:
            extra_fields = [
                ft.TextField(label="Nueva contraseña (vacío = sin cambio)",
                             password=True, can_reveal_password=True, data='contrasenia'),
                ft.TextField(label="Código interno", value=sub_a.get('codigo_interno') or '',
                             data='codigo_interno'),
            ]
        elif rol == 'Operador' and sub_o:
            extra_fields = [
                ft.TextField(label="Código interno", value=sub_o.get('codigo_interno') or '',
                             data='codigo_interno'),
                ft.Dropdown(label="Estado", options=[ft.dropdown.Option(s) for s in ESTADOS_OP],
                            value=sub_o.get('estado') or 'Activo', data='estado'),
            ]
        elif rol == 'Suscriptor' and sub_s:
            extra_fields = [
                ft.TextField(label="Fecha registro", value=str(sub_s.get('fecha_registro') or ''),
                             data='fecha_registro'),
            ]

        def save(dlg):
            if not f_pnombre.value.strip() or not f_papellido.value.strip() or not f_correo.value.strip():
                show_error(page, "Complete los campos obligatorios."); return
            d = {
                'primer_nombre': f_pnombre.value.strip(),
                'segundo_nombre': f_snombre.value.strip(),
                'primer_apellido': f_papellido.value.strip(),
                'segundo_apellido': f_sapellido.value.strip(),
                'correo': f_correo.value.strip(),
                'rol': rol,
            }
            for ef in extra_fields:
                if hasattr(ef, 'data') and ef.data:
                    d[ef.data] = ef.value.strip() if hasattr(ef.value, 'strip') else ef.value
            ok, msg = ctrl.update(row['cedula'], d)
            if ok:
                page.pop_dialog(); load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar — {row['cedula']}", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [f_pnombre, f_snombre, f_papellido, f_sapellido, f_correo,
                 ft.Divider(), ft.Text(f"Rol: {rol}", italic=True)] + extra_fields,
                tight=True, scroll=ft.ScrollMode.AUTO, width=460, spacing=8,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def confirm_delete(row):
        nombre = f"{row.get('primer_nombre','')} {row.get('primer_apellido','')}"

        def do_delete(dlg):
            ok, msg = ctrl.delete(row['cedula'])
            page.pop_dialog()
            if ok:
                load_data(); show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar usuario {nombre} ({row['cedula']}) y todos sus datos?\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Eliminar", style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                                   on_click=lambda e: do_delete(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    # ---------------------------------------------------------------- Reportes
    def _show_report_table(page, title, headers, rows_data):
        cols = [ft.DataColumn(ft.Text(h, weight=ft.FontWeight.BOLD, size=12)) for h in headers]
        rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(v) if v is not None else '', size=12)) for v in row])
            for row in rows_data
        ]
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
                ft.Column([ft.Row([tbl], scroll=ft.ScrollMode.AUTO)],
                          scroll=ft.ScrollMode.AUTO),
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
        fn = title.lower().replace(' ', '_').replace(':', '')
        path = _export_csv(fn, headers, rows_data)
        show_success(page, f"Exportado: {path}")

    def rep_multas():
        ok, data_r = ctrl.reporte_multas_por_estado()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["ID Multa", "Placa", "Propietario", "Fecha", "Motivo", "Valor COP", "Estado"]
        rows = [[r['id_multa'], r['placa'], r['propietario'],
                 str(r['fecha']), r['motivo'] or '', r['valor'], r['estado']] for r in data_r]
        _show_report_table(page, "Multas por Estado", hdrs, rows)

    def rep_suscripciones():
        f_ini = ft.TextField(label="Fecha inicio (vacío = todos) AAAA-MM-DD", width=220)
        f_fin = ft.TextField(label="Fecha fin AAAA-MM-DD", width=220)

        def run(dlg):
            ok, data_r = ctrl.reporte_usuarios_mas_suscripciones(
                f_ini.value.strip() or None, f_fin.value.strip() or None)
            page.pop_dialog()
            if not ok:
                show_error(page, data_r); return
            hdrs = ["Cédula", "Nombre", "Cantidad Suscripciones"]
            rows = [[r['cedula'], r['nombre'], r['cantidad_suscripciones']] for r in data_r]
            _show_report_table(page, "Usuarios con más Suscripciones", hdrs, rows)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Filtrar por periodo", size=16),
            content=ft.Column([f_ini, f_fin], tight=True, width=300, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Ver reporte", on_click=lambda e: run(None)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def rep_horas_op():
        hoy = date.today().isoformat()
        f_ini = ft.TextField(label="Fecha inicio * (AAAA-MM-DD)", value="2025-01-01")
        f_fin = ft.TextField(label="Fecha fin * (AAAA-MM-DD)", value=hoy)

        def run(dlg):
            if not f_ini.value.strip() or not f_fin.value.strip():
                show_error(page, "Ingrese ambas fechas."); return
            ok, data_r = ctrl.reporte_horas_operadores(f_ini.value.strip(), f_fin.value.strip())
            page.pop_dialog()
            if not ok:
                show_error(page, data_r); return
            hdrs = ["Cédula", "Nombre", "Turnos", "Horas Totales (est.)", "Horas Diurnas", "Horas Nocturnas"]
            rows = [[r['cedula'], r['nombre'], r['cantidad_turnos'],
                     r['horas_totales_estimadas'], r['horas_diurnas'], r['horas_nocturnas']] for r in data_r]
            _show_report_table(page, "Horas Trabajadas por Operador", hdrs, rows)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Periodo para reporte de operadores", size=16),
            content=ft.Column([f_ini, f_fin], tight=True, width=300, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.ElevatedButton("Ver reporte", on_click=lambda e: run(None)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def rep_ganancias():
        ok, data_r = ctrl.reporte_usuarios_mayor_ganancia()
        if not ok:
            show_error(page, data_r); return
        hdrs = ["Cédula", "Nombre", "Ganancia Sesiones COP", "Suscripciones Activas", "Ganancia Total"]
        rows = [[r['cedula'], r['nombre'], r['ganancia_sesiones'],
                 r['num_suscripciones'], r['ganancia_total']] for r in data_r]
        _show_report_table(page, "Usuarios con Mayor Ganancia Generada", hdrs, rows)

    reportes = [
        ("Multas por estado", ft.Icons.WARNING_AMBER_OUTLINED, ft.Colors.RED_600,
         "Listado de multas ordenado por estado y fecha.", rep_multas),
        ("Usuarios con más suscripciones", ft.Icons.CARD_MEMBERSHIP_OUTLINED, ft.Colors.BLUE_600,
         "Ranking de usuarios por cantidad de suscripciones (filtrable por periodo).", rep_suscripciones),
        ("Horas operadores", ft.Icons.SCHEDULE_OUTLINED, ft.Colors.GREEN_700,
         "Horas totales, diurnas y nocturnas por operador en un periodo.", rep_horas_op),
        ("Usuarios con mayor ganancia", ft.Icons.ATTACH_MONEY, ft.Colors.PURPLE_600,
         "Clientes que más ingresos han generado (sesiones pagadas + suscripciones activas).", rep_ganancias),
    ]

    rep_cards = []
    for titulo, icon, color, desc, fn in reportes:
        fn_cap = fn
        card = ft.Card(
            content=ft.Container(
                ft.Column([
                    ft.Row([ft.Icon(icon, color=color, size=30),
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
            ft.DataColumn(ft.Text("Cédula", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Nombre completo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Correo", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Rol", weight=ft.FontWeight.BOLD)),
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
            ft.Text("CRUD 1 — Usuarios", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([search_field, filter_rol,
                    ft.ElevatedButton("+ Nuevo", icon=ft.Icons.ADD,
                                       on_click=lambda e: open_create())], spacing=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            ft.Row([ft.Column([table], scroll=ft.ScrollMode.AUTO)], scroll=ft.ScrollMode.AUTO),
            expand=True,
        ),
        ft.Row([counter_text, load_more_btn], spacing=8),
        ft.Divider(),
        ft.Text("Reportes CRUD 1", size=16, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow(
            controls=[ft.Container(card, col={"sm": 12, "md": 6}) for card in rep_cards],
            run_spacing=10, spacing=10,
        ),
    ], expand=True, scroll=ft.ScrollMode.AUTO)
