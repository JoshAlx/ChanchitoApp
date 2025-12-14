import flet as ft


class BalanceCard(ft.Container):
    """Componente visual estilo tarjeta de crédito para el balance total"""

    def __init__(self, balance):
        super().__init__()
        # Color dinámico: Azul si es positivo, Rojo oscuro si es negativo
        bg_gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#1E88E5", "#1565C0"] if balance >= 0 else ["#C62828", "#B71C1C"]
        )

        self.gradient = bg_gradient
        self.border_radius = 20
        self.padding = 20
        self.shadow = ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.3, "black"))
        self.margin = ft.margin.only(bottom=20)

        self.content = ft.Column([
            ft.Text("Balance Total", color="white70", size=14),
            ft.Text(f"${balance:,.2f}", color="white", size=32, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Icon(ft.Icons.WIFI, color="white30"),
                ft.Icon(ft.Icons.NFC, color="white30"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ])


class StatCard(ft.Container):
    """Tarjetas pequeñas para Ingresos y Gastos"""

    def __init__(self, titulo, valor, color_icon, icono):
        super().__init__()
        self.bgcolor = ft.Colors.ON_SURFACE_VARIANT
        self.border_radius = 15
        self.padding = 15
        self.expand = 1  # Para que ocupen espacio igual en filas

        self.content = ft.Column([
            ft.Icon(icono, color=color_icon, size=24),
            ft.Text(titulo, color=ft.Colors.ON_SURFACE_VARIANT, size=12),
            ft.Text(f"${valor:,.2f}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        ])


class AppNavigation(ft.NavigationDrawer):
    def __init__(self, on_change_nav):
        super().__init__()
        self.on_change = on_change_nav
        self.selected_index = 0
        self.controls = [
            ft.Container(
                height=150,
                bgcolor=ft.Colors.PRIMARY_CONTAINER,
                padding=20,
                content=ft.Column([
                    ft.Icon(ft.Icons.WALLET, size=50, color=ft.Colors.PRIMARY),
                    ft.Text("Mi Billetera", size=20, weight="bold", color=ft.Colors.ON_PRIMARY_CONTAINER),
                    ft.Text("Gestión Financiera", size=12, color=ft.Colors.ON_PRIMARY_CONTAINER),
                ], alignment=ft.MainAxisAlignment.END)
            ),
            ft.NavigationDrawerDestination(label="Dashboard", icon=ft.Icons.DASHBOARD_OUTLINED,
                                           selected_icon=ft.Icons.DASHBOARD),
            ft.NavigationDrawerDestination(label="Transacciones", icon=ft.Icons.LIST_ALT_OUTLINED,
                                           selected_icon=ft.Icons.LIST_ALT),
            ft.NavigationDrawerDestination(label="Presupuestos", icon=ft.Icons.ATTACH_MONEY,
                                           selected_icon=ft.Icons.MONEY_OFF),
            ft.NavigationDrawerDestination(label="Alertas", icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                                           selected_icon=ft.Icons.NOTIFICATIONS),
            ft.Divider(thickness=1),
            ft.NavigationDrawerDestination(label="Configuración", icon=ft.Icons.SETTINGS_OUTLINED),
        ]