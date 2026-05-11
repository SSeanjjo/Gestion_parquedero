import flet as ft
from controllers import usuario_controller as ctrl
from components.snackbar import show_success, show_error

ROLES = ["Administrador", "Operador", "Suscriptor"]
NIVELES_ACCESO = ["SUPER", "ALTO", "MEDIO", "BAJO"]
TURNOS = ["Mañana", "Tarde", "Noche"]
ESTADOS_OP = ["Activo", "Inactivo"]
TIPOS_SUSCRIPTOR = ["Premium", "Estándar", "Básico"]


def build(page: ft.Page):
    data = []
    table_container = ft.Ref[ft.Column]()
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
            nombre = f"{row.get('primer_nombre','')} {row.get('segundo_nombre') or ''} {row.get('primer_apellido','')} {row.get('segundo_apellido') or ''}".strip()
            rows.append(ft.DataRow(cells=[
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
        table.rows.clear()
        table.rows.extend(rows)
        if table_container.current:
            table_container.current.update()

    def build_rol_fields(rol_dd, rol_value=""):
        admin_fields = ft.Column([
            ft.TextField(label="Nivel de acceso", ref=nivel_ref),
            ft.TextField(label="Fecha asignación (AAAA-MM-DD)", ref=fecha_asig_ref),
            ft.TextField(label="Área responsable", ref=area_ref),
        ], visible=False, spacing=8)
        op_fields = ft.Column([
            ft.TextField(label="Código interno", ref=codigo_ref),
            ft.Dropdown(label="Turno asignado", ref=turno_ref,
                        options=[ft.dropdown.Option(t) for t in TURNOS]),
            ft.Dropdown(label="Estado", ref=estado_op_ref,
                        options=[ft.dropdown.Option(s) for s in ESTADOS_OP]),
            ft.TextField(label="Inicio turno (AAAA-MM-DD HH:MM:SS)", ref=inicio_turno_ref),
            ft.TextField(label="Fin turno (AAAA-MM-DD HH:MM:SS)", ref=fin_turno_ref),
        ], visible=False, spacing=8)
        sus_fields = ft.Column([
            ft.Dropdown(label="Tipo suscriptor", ref=tipo_sus_ref,
                        options=[ft.dropdown.Option(t) for t in TIPOS_SUSCRIPTOR]),
            ft.TextField(label="Fecha registro (AAAA-MM-DD)", ref=fecha_reg_ref),
        ], visible=False, spacing=8)
        return admin_fields, op_fields, sus_fields

    nivel_ref = ft.Ref[ft.TextField]()
    fecha_asig_ref = ft.Ref[ft.TextField]()
    area_ref = ft.Ref[ft.TextField]()
    codigo_ref = ft.Ref[ft.TextField]()
    turno_ref = ft.Ref[ft.Dropdown]()
    estado_op_ref = ft.Ref[ft.Dropdown]()
    inicio_turno_ref = ft.Ref[ft.TextField]()
    fin_turno_ref = ft.Ref[ft.TextField]()
    tipo_sus_ref = ft.Ref[ft.Dropdown]()
    fecha_reg_ref = ft.Ref[ft.TextField]()

    def open_create():
        f_cedula = ft.TextField(label="Cédula *")
        f_pnombre = ft.TextField(label="Primer nombre *")
        f_snombre = ft.TextField(label="Segundo nombre")
        f_papellido = ft.TextField(label="Primer apellido *")
        f_sapellido = ft.TextField(label="Segundo apellido")
        f_correo = ft.TextField(label="Correo *")
        f_rol = ft.Dropdown(label="Rol *", options=[ft.dropdown.Option(r) for r in ROLES])

        f_pass = ft.TextField(label="Contraseña *", password=True, can_reveal_password=True)
        f_nivel = ft.TextField(label="Nivel de acceso")
        f_fecha_asig = ft.TextField(label="Fecha asignación (AAAA-MM-DD)")
        f_area = ft.TextField(label="Área responsable")
        admin_col = ft.Column([f_pass, f_nivel, f_fecha_asig, f_area], visible=False, spacing=8)

        f_codigo = ft.TextField(label="Código interno")
        f_turno = ft.Dropdown(label="Turno asignado", options=[ft.dropdown.Option(t) for t in TURNOS])
        f_estado_op = ft.Dropdown(label="Estado", options=[ft.dropdown.Option(s) for s in ESTADOS_OP])
        f_inicio_t = ft.TextField(label="Inicio turno (AAAA-MM-DD HH:MM:SS)")
        f_fin_t = ft.TextField(label="Fin turno (AAAA-MM-DD HH:MM:SS)")
        op_col = ft.Column([f_codigo, f_turno, f_estado_op, f_inicio_t, f_fin_t], visible=False, spacing=8)

        f_tipo_sus = ft.Dropdown(label="Tipo suscriptor", options=[ft.dropdown.Option(t) for t in TIPOS_SUSCRIPTOR])
        f_fecha_reg = ft.TextField(label="Fecha registro (AAAA-MM-DD)")
        sus_col = ft.Column([f_tipo_sus, f_fecha_reg], visible=False, spacing=8)

        def on_rol_change(e):
            admin_col.visible = f_rol.value == "Administrador"
            op_col.visible = f_rol.value == "Operador"
            sus_col.visible = f_rol.value == "Suscriptor"
            page.update()

        f_rol.on_change = on_rol_change

        def save(dlg):
            if not f_cedula.value.strip() or not f_pnombre.value.strip() \
               or not f_papellido.value.strip() or not f_correo.value.strip() \
               or not f_rol.value:
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
                'contrasena': f_pass.value,
                'rol': f_rol.value,
                'nivel_acceso': f_nivel.value.strip(),
                'fecha_asignacion': f_fecha_asig.value.strip(),
                'area_responsable': f_area.value.strip(),
                'codigo_interno': f_codigo.value.strip(),
                'turno_asignado': f_turno.value,
                'estado': f_estado_op.value,
                'fecha_inicio_turno': f_inicio_t.value.strip(),
                'fecha_final_turno': f_fin_t.value.strip(),
                'tipo_suscriptor': f_tipo_sus.value,
                'fecha_registro': f_fecha_reg.value.strip(),
            }
            ok, msg = ctrl.create(d)
            if ok:
                page.pop_dialog()
                load_data()
                show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Usuario", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column([
                f_cedula, f_pnombre, f_snombre, f_papellido, f_sapellido,
                f_correo, f_rol,
                ft.Divider(),
                admin_col, op_col, sus_col,
            ], tight=True, scroll=ft.ScrollMode.AUTO, width=450, spacing=8),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE_OUTLINED, on_click=lambda e: save(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def open_edit(row):
        ok, result = ctrl.get_by_cedula(row['cedula'])
        if not ok:
            show_error(page, result)
            return
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
                             password=True, can_reveal_password=True, data='contrasena'),
                ft.TextField(label="Nivel de acceso", value=sub_a.get('nivel_acceso', ''),
                             data='nivel_acceso'),
                ft.TextField(label="Fecha asignación", value=str(sub_a.get('fecha_asignacion', '')),
                             data='fecha_asignacion'),
                ft.TextField(label="Área responsable", value=sub_a.get('area_responsable', ''),
                             data='area_responsable'),
            ]
        elif rol == 'Operador' and sub_o:
            extra_fields = [
                ft.TextField(label="Código interno", value=sub_o.get('codigo_interno') or '',
                             data='codigo_interno'),
                ft.TextField(label="Turno asignado", value=sub_o.get('turno_asignado') or '',
                             data='turno_asignado'),
                ft.TextField(label="Estado", value=sub_o.get('estado') or '', data='estado'),
            ]
        elif rol == 'Suscriptor' and sub_s:
            extra_fields = [
                ft.TextField(label="Tipo suscriptor", value=sub_s.get('tipo_suscriptor') or '',
                             data='tipo_suscriptor'),
                ft.TextField(label="Fecha registro", value=str(sub_s.get('fecha_registro') or ''),
                             data='fecha_registro'),
            ]

        def save(dlg):
            if not f_pnombre.value.strip() or not f_papellido.value.strip() or not f_correo.value.strip():
                show_error(page, "Complete los campos obligatorios.")
                return
            d = {
                'primer_nombre': f_pnombre.value.strip(),
                'segundo_nombre': f_snombre.value.strip(),
                'primer_apellido': f_papellido.value.strip(),
                'segundo_apellido': f_sapellido.value.strip(),
                'correo': f_correo.value.strip(),
                'rol': rol,
            }
            for ef in extra_fields:
                d[ef.data] = ef.value.strip()

            ok, msg = ctrl.update(row['cedula'], d)
            if ok:
                page.pop_dialog()
                load_data()
                show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editar Usuario — {row['cedula']}", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [f_pnombre, f_snombre, f_papellido, f_sapellido, f_correo,
                 ft.Divider(), ft.Text(f"Rol: {rol}", italic=True)] + extra_fields,
                tight=True, scroll=ft.ScrollMode.AUTO, width=450, spacing=8,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
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
                load_data()
                show_success(page, msg)
            else:
                show_error(page, msg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Eliminar al usuario {nombre} ({row['cedula']})?\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton("Eliminar", icon=ft.Icons.DELETE_OUTLINE,
                                   style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600,
                                                        color=ft.Colors.WHITE),
                                   on_click=lambda e: do_delete(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def _close(dlg):
        page.pop_dialog()

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

    return ft.Column(
        ref=table_container,
        controls=[
            ft.Row([
                ft.Text("Usuarios", size=22, weight=ft.FontWeight.BOLD),
                ft.Row([search_field,                 ft.ElevatedButton("+ Nuevo", icon=ft.Icons.ADD,
                                  on_click=lambda e: open_create())], spacing=8),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Container(
                content=ft.Row([
                    ft.Column([table], scroll=ft.ScrollMode.AUTO)
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
            ),
        ],
        expand=True,
    )
