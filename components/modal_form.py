import flet as ft


def open_modal(page: ft.Page, title: str, fields: list, on_save):
    """
    Abre un AlertDialog genérico.
    fields: lista de controles Flet (TextField, Dropdown, etc.)
    on_save: callback(dlg) que ejecuta la lógica de guardado y cierra el diálogo si es exitoso
    """
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=fields,
            tight=True,
            scroll=ft.ScrollMode.AUTO,
            width=450,
        ),
        actions=[
            ft.TextButton(
                "Cancelar",
                on_click=lambda e: _close(page, dlg),
            ),
            ft.ElevatedButton(
                "Guardar",
                icon=ft.Icons.SAVE_OUTLINED,
                on_click=lambda e: on_save(dlg),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)


def _close(page: ft.Page, dlg: ft.AlertDialog):
    page.pop_dialog()
