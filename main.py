import flet as ft

from controllers.app_controller import AppController
from views.components import AppNavigation
from views.screens import DashboardScreen, TransactionsScreen, BudgetScreen, AlertsScreen


def main(page: ft.Page):
    # --- CONFIGURACIÓN ESTÉTICA GLOBAL ---
    page.title = "Finanzas Personales"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # Definición de Tema
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.INDIGO,
            primary_container=ft.Colors.INDIGO_900,
            secondary=ft.Colors.TEAL,
            surface=ft.Colors.WHITE,
            background="#F5F7FB",
            error=ft.Colors.RED_ACCENT,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
        font_family="Roboto"
    )

    # --- CAMBIO IMPORTANTE MVC ---
    # En lugar de db = Database(), inicializamos el Controlador
    app_controller = AppController(page)

    # --- CONTENEDOR PRINCIPAL ---
    main_container = ft.Container(expand=True, padding=ft.padding.all(15))

    def cambiar_ruta(e):
        # Detectamos si 'e' es un evento o un número directo
        if isinstance(e, int):
            idx = e
        else:
            idx = e.control.selected_index

        drawer.open = False
        page.update()

        main_container.content = None
        page.floating_action_button = None

        # Pantalla por defecto para evitar errores
        pantalla = ft.Container(content=ft.Text("Cargando..."))

        # --- INYECCIÓN DE DEPENDENCIAS ---
        # Ahora pasamos 'app_controller' en lugar de 'db'
        if idx == 0:
            pantalla = DashboardScreen(app_controller)
            page.appbar.title.value = "Dashboard"
        elif idx == 1:
            pantalla = TransactionsScreen(app_controller)
            page.appbar.title.value = "Transacciones"
            # El botón flotante llama al método del controlador a través de la pantalla
            page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                bgcolor=ft.Colors.PRIMARY,
                on_click=pantalla.abrir_modal_agregar
            )
        elif idx == 2:
            pantalla = BudgetScreen(app_controller)
            page.appbar.title.value = "Presupuestos"
        elif idx == 3:
            pantalla = AlertsScreen(app_controller)
            page.appbar.title.value = "Alertas"
        elif idx == 4:
            pantalla = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SETTINGS, size=50, color=ft.Colors.GREY),
                    ft.Text("Configuración", size=30, weight="bold", color=ft.Colors.GREY),
                    ft.Text("Opciones de la app próximamente...", color=ft.Colors.GREY)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center
            )
            page.appbar.title.value = "Configuración"

        main_container.content = pantalla
        page.update()

    drawer = AppNavigation(on_change_nav=cambiar_ruta)

    # --- APPBAR ---
    page.appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.MENU, on_click=lambda e: page.open(drawer), icon_color="white"),
        leading_width=40,
        title=ft.Text("Dashboard", color="white", weight="bold"),
        center_title=True,
        bgcolor=ft.Colors.PRIMARY,
        elevation=0,
        actions=[
            ft.IconButton(ft.Icons.DARK_MODE, icon_color="white",
                          on_click=lambda e: toggle_theme(e))
        ]
    )

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        e.control.icon = ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE
        page.update()

    # Cargar inicio
    page.add(main_container)

    # Iniciar en la pantalla 0 (Dashboard)
    cambiar_ruta(0)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")