import flet as ft


def show_success(page: ft.Page, message: str):
    page.show_dialog(ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN_700,
        open=True,
    ))
    page.update()


def show_error(page: ft.Page, message: str):
    page.show_dialog(ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_700,
        open=True,
    ))
    page.update()
