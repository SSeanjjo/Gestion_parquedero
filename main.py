import flet as ft
from views import login_view, main_view


def main(page: ft.Page):
    page.title = "GestiónParqueadero"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_GREY)
    page.window.width = 1280
    page.window.height = 780
    page.window.min_width = 900
    page.window.min_height = 600
    page.padding = 0

    def show_login():
        page.appbar = None
        page.clean()
        page.add(login_view.build(page, on_login_success=show_main))
        page.update()

    def show_main(user: dict):
        page.clean()
        page.add(main_view.build(page, current_user=user, on_logout=show_login))
        page.update()

    show_login()


ft.app(target=main)
