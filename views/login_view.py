import flet as ft
from controllers import usuario_controller as ctrl
from components.snackbar import show_error


def build(page: ft.Page, on_login_success):
    cedula_field = ft.TextField(
        label="Cédula",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        width=340,
        autofocus=True,
    )
    password_field = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        width=340,
    )
    loading = ft.ProgressRing(visible=False, width=24, height=24)

    def do_login(e):
        if not cedula_field.value.strip():
            cedula_field.error_text = "Ingrese su cédula"
            page.update()
            return
        cedula_field.error_text = None

        if not password_field.value:
            password_field.error_text = "Ingrese su contraseña"
            page.update()
            return
        password_field.error_text = None

        loading.visible = True
        page.update()

        ok, result = ctrl.login(cedula_field.value.strip(), password_field.value)

        loading.visible = False
        page.update()

        if ok:
            on_login_success(result)
        else:
            show_error(page, result)

    password_field.on_submit = do_login

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.LOCAL_PARKING, size=80, color=ft.Colors.PRIMARY),
                ft.Text(
                    "GestiónParqueadero",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Sistema de administración de parqueadero",
                    size=14,
                    color=ft.Colors.SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                cedula_field,
                password_field,
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                ft.Row(
                    [loading, ft.ElevatedButton(
                        "Iniciar sesión",
                        icon=ft.Icons.LOGIN,
                        width=200,
                        on_click=do_login,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    )],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
    )
