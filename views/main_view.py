import flet as ft
from views import (
    usuario_view, vehiculo_view, sesion_view, factura_view,
    tarifa_view, espacio_view, zona_view, suscripcion_view,
    empresa_view, multa_view, notificacion_view, reportes_view,
)

MODULES = [
    ("Usuarios",       "usuarios",       ft.Icons.PEOPLE_OUTLINE),
    ("Vehículos",      "vehiculos",      ft.Icons.DIRECTIONS_CAR_OUTLINED),
    ("Sesiones",       "sesiones",       ft.Icons.TIMER_OUTLINED),
    ("Facturas",       "facturas",       ft.Icons.RECEIPT_OUTLINED),
    ("Espacios",       "espacios",       ft.Icons.GRID_VIEW_OUTLINED),
    ("Zonas",          "zonas",          ft.Icons.MAP_OUTLINED),
    ("Tarifas",        "tarifas",        ft.Icons.ATTACH_MONEY),
    ("Suscripciones",  "suscripciones",  ft.Icons.CARD_MEMBERSHIP_OUTLINED),
    ("Empresas",       "empresas",       ft.Icons.BUSINESS_OUTLINED),
    ("Multas",         "multas",         ft.Icons.WARNING_AMBER_OUTLINED),
    ("Notificaciones", "notificaciones", ft.Icons.NOTIFICATIONS_OUTLINED),
    ("Reportes",       "reportes",       ft.Icons.ASSESSMENT_OUTLINED),
]

VIEW_BUILDERS = {
    "usuarios":       usuario_view.build,
    "vehiculos":      vehiculo_view.build,
    "sesiones":       sesion_view.build,
    "facturas":       factura_view.build,
    "espacios":       espacio_view.build,
    "zonas":          zona_view.build,
    "tarifas":        tarifa_view.build,
    "suscripciones":  suscripcion_view.build,
    "empresas":       empresa_view.build,
    "multas":         multa_view.build,
    "notificaciones": notificacion_view.build,
    "reportes":       reportes_view.build,
}


def build(page: ft.Page, current_user: dict, on_logout):
    current_module = {"value": "usuarios"}
    nav_buttons = {}

    content_container = ft.Container(expand=True, padding=ft.Padding.all(16))

    def load_module(module_key: str):
        current_module["value"] = module_key
        # Highlight active button
        for key, btn in nav_buttons.items():
            btn.style = ft.ButtonStyle(
                color=ft.Colors.PRIMARY if key == module_key else ft.Colors.ON_SURFACE,
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.PRIMARY_CONTAINER
                    if key == module_key else ft.Colors.TRANSPARENT,
                },
            )
        content_container.content = VIEW_BUILDERS[module_key](page)
        page.update()

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        )
        page.update()

    def do_logout(e):
        page.appbar = None
        page.update()
        on_logout()

    # Build navigation buttons
    for label, key, icon in MODULES:
        btn = ft.TextButton(
            content=ft.Row([ft.Icon(icon, size=16), ft.Text(label, size=13)], tight=True, spacing=4),
            on_click=lambda e, k=key: load_module(k),
            style=ft.ButtonStyle(color=ft.Colors.ON_SURFACE),
        )
        nav_buttons[key] = btn

    nombre_usuario = (
        f"{current_user.get('primer_nombre', '')} {current_user.get('primer_apellido', '')}"
    ).strip()

    nav_row = ft.Row(
        controls=list(nav_buttons.values()),
        scroll=ft.ScrollMode.AUTO,
        spacing=2,
    )

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.LOCAL_PARKING, color=ft.Colors.PRIMARY),
        leading_width=48,
        title=ft.Text("GestiónParqueadero", weight=ft.FontWeight.BOLD),
        center_title=False,
        actions=[
            ft.Container(
                ft.Text(f"  {nombre_usuario}", size=13, color=ft.Colors.SECONDARY),
                padding=ft.Padding.symmetric(vertical=0, horizontal=8),
            ),
            ft.IconButton(
                icon=ft.Icons.BRIGHTNESS_6_ROUNDED,
                tooltip="Alternar tema",
                on_click=toggle_theme,
            ),
            ft.IconButton(
                icon=ft.Icons.LOGOUT_ROUNDED,
                tooltip="Cerrar sesión",
                on_click=do_logout,
            ),
        ],
    )

    load_module("usuarios")

    return ft.Column(
        controls=[
            ft.Container(
                content=nav_row,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                padding=ft.Padding.symmetric(vertical=4, horizontal=8),
            ),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            content_container,
        ],
        expand=True,
        spacing=0,
    )
