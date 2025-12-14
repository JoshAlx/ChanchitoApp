import flet as ft
from datetime import datetime
from views.components import BalanceCard, StatCard


# --- PANTALLA 1: DASHBOARD ---
class DashboardScreen(ft.Column):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.scroll = ft.ScrollMode.HIDDEN
        self.expand = True
        self.cargar_contenido()

    def cargar_contenido(self):
        # Solicitamos datos al controlador
        ingresos, gastos = self.controller.obtener_balance()
        balance = ingresos - gastos

        c_ingreso = "#00C853"
        c_gasto = "#FF1744"

        self.controls = [
            ft.Container(padding=20, content=ft.Column([
                BalanceCard(balance),
                ft.Row([
                    StatCard("Ingresos", ingresos, c_ingreso, ft.Icons.TRENDING_UP),
                    ft.Container(width=10),
                    StatCard("Gastos", gastos, c_gasto, ft.Icons.TRENDING_DOWN),
                ]),
                ft.Divider(height=30, color="transparent"),
                ft.Text("Distribución de Gastos", size=18, weight="bold"),
                ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.ON_SURFACE_VARIANT),
                    border_radius=15,
                    padding=20,
                    content=ft.PieChart(
                        sections=[
                            ft.PieChartSection(ingresos, color=c_ingreso, radius=40,
                                               title_style=ft.TextStyle(size=0, color=ft.Colors.TRANSPARENT)),
                            ft.PieChartSection(gastos, color=c_gasto, radius=40,
                                               title_style=ft.TextStyle(size=0, color=ft.Colors.TRANSPARENT)),
                        ],
                        height=200, center_space_radius=60, sections_space=2
                    )
                ),
                ft.Row([
                    ft.Row(
                        [ft.Container(width=10, height=10, bgcolor=c_ingreso, border_radius=5), ft.Text("Ingresos")]),
                    ft.Row([ft.Container(width=10, height=10, bgcolor=c_gasto, border_radius=5), ft.Text("Gastos")]),
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], scroll=ft.ScrollMode.AUTO))
        ]


# --- PANTALLA 2: TRANSACCIONES ---
class TransactionsScreen(ft.Column):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.expand = True
        self.transacciones = []
        self.id_a_eliminar = None

        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Icono")),
                ft.DataColumn(ft.Text("Detalle")),
                ft.DataColumn(ft.Text("Monto", text_align=ft.TextAlign.RIGHT), numeric=True),
                ft.DataColumn(ft.Text("")),
            ],
            column_spacing=20, data_row_max_height=60,
        )

        self.dlg_confirmar = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Eliminar?"),
            content=ft.Text("Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("No", on_click=self.cerrar_confirmacion),
                ft.TextButton("Sí, borrar", on_click=self.ejecutar_eliminacion,
                              style=ft.ButtonStyle(color=ft.Colors.ERROR)),
            ]
        )

        self.controls = [
            ft.Container(padding=10, content=ft.Row([
                ft.Text("Historial", size=20, weight="bold"),
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(text="Exportar a Excel", icon=ft.Icons.TABLE_VIEW,
                                         on_click=self.exportar_excel),
                        ft.PopupMenuItem(text="Exportar a PDF", icon=ft.Icons.PICTURE_AS_PDF,
                                         on_click=self.exportar_pdf),
                    ]
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)),
            ft.Container(
                expand=True,
                padding=ft.padding.symmetric(horizontal=10),
                content=ft.Column([
                    ft.Row([self.tabla], scroll=ft.ScrollMode.ADAPTIVE)
                ], scroll=ft.ScrollMode.AUTO)
            )
        ]

    def did_mount(self):
        self.cargar_datos()

    def cargar_datos(self):
        # Petición al controlador
        self.transacciones = self.controller.obtener_transacciones()
        self.tabla.rows = []

        for t in self.transacciones:
            es_ingreso = t.tipo == 'ingreso'
            color = ft.Colors.GREEN if es_ingreso else ft.Colors.RED
            icono = ft.Icons.ARROW_UPWARD if es_ingreso else ft.Icons.ARROW_DOWNWARD

            self.tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Container(bgcolor=color, border_radius=50, padding=5,
                                         content=ft.Icon(icono, color="white", size=16))),
                ft.DataCell(ft.Column([
                    ft.Text(t.descripcion, weight="bold", size=14, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{t.fecha} • {t.categoria}", size=11, color="grey"),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)),
                ft.DataCell(ft.Text(f"${t.monto:,.0f}", color=color, weight="bold")),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color="grey",
                                          on_click=lambda e, x=t.id: self.solicitar_eliminacion(x))),
            ]))
        self.update()

    def solicitar_eliminacion(self, id_tx):
        self.id_a_eliminar = id_tx
        self.page.open(self.dlg_confirmar)

    def cerrar_confirmacion(self, e=None):
        self.page.close(self.dlg_confirmar)

    def ejecutar_eliminacion(self, e):
        if self.id_a_eliminar:
            self.controller.eliminar_transaccion(self.id_a_eliminar)
            self.page.close(self.dlg_confirmar)
            self.mostrar_mensaje("Eliminado correctamente")
            self.cargar_datos()

    def exportar_excel(self, e):
        msg = self.controller.exportar_excel(self.transacciones)
        self.mostrar_mensaje(msg)

    def exportar_pdf(self, e):
        msg = self.controller.exportar_pdf(self.transacciones)
        self.mostrar_mensaje(msg)

    def mostrar_mensaje(self, t):
        self.page.snack_bar = ft.SnackBar(ft.Text(t), bgcolor=ft.Colors.INVERSE_SURFACE)
        self.page.snack_bar.open = True
        self.page.update()

    def abrir_modal_agregar(self, e):
        # Obtenemos categorias del controlador
        cats = self.controller.obtener_categorias()
        opciones_categorias = [ft.dropdown.Option(c.nombre) for c in cats] or [ft.dropdown.Option("General")]

        self.fecha_seleccionada = datetime.now().strftime("%Y-%m-%d")

        monto_ref = ft.Ref[ft.TextField]()
        desc_ref = ft.Ref[ft.TextField]()
        cat_ref = ft.Ref[ft.Dropdown]()
        tipo_ref = ft.Ref[ft.RadioGroup]()
        fecha_btn_ref = ft.Ref[ft.ElevatedButton]()

        def on_date_change(e):
            if date_picker.value:
                self.fecha_seleccionada = date_picker.value.strftime("%Y-%m-%d")
                fecha_btn_ref.current.text = self.fecha_seleccionada
                fecha_btn_ref.current.update()

        date_picker = ft.DatePicker(on_change=on_date_change)
        self.page.overlay.clear()
        self.page.overlay.append(date_picker)
        self.page.update()

        def on_save(e):
            # Llamamos al controlador para validar y guardar
            resultado = self.controller.agregar_transaccion(
                tipo=tipo_ref.current.value,
                monto=monto_ref.current.value,
                categoria=cat_ref.current.value,
                descripcion=desc_ref.current.value,
                fecha=self.fecha_seleccionada
            )

            if resultado["status"] == "error":
                self.mostrar_mensaje(f"⚠️ {resultado['message']}")
                return

            # Éxito
            self.page.close(dlg)
            self.cargar_datos()

            if resultado["alerta"]:
                dlg_alerta = ft.AlertDialog(title=ft.Text("⚠️ ALERTA"), content=ft.Text(resultado["alerta"].mensaje))
                self.page.open(dlg_alerta)
            else:
                self.mostrar_mensaje("Guardado exitosamente")
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Nueva Transacción", text_align="center"),
            content=ft.Column([
                ft.Container(
                    bgcolor=ft.Colors.ON_SURFACE_VARIANT, border_radius=10, padding=5,
                    content=ft.RadioGroup(ref=tipo_ref, value="gasto", content=ft.Row([
                        ft.Radio(value="ingreso", label="Ingreso", fill_color=ft.Colors.GREEN),
                        ft.Radio(value="gasto", label="Gasto", fill_color=ft.Colors.RED)
                    ], alignment="center"))
                ),
                ft.TextField(ref=monto_ref, label="Monto", prefix_text="$", keyboard_type=ft.KeyboardType.NUMBER,
                             border_radius=10),
                ft.Dropdown(ref=cat_ref, label="Categoría", options=opciones_categorias, border_radius=10),
                ft.TextField(ref=desc_ref, label="Descripción", border_radius=10),
                ft.OutlinedButton(ref=fecha_btn_ref, text="Hoy", icon=ft.Icons.CALENDAR_MONTH,
                                  on_click=lambda _: date_picker.pick_date())
            ], height=340, width=300, spacing=15, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                ft.FilledButton("Guardar", on_click=on_save)
            ],
            actions_alignment="center"
        )
        self.page.open(dlg)
        self.page.update()


# --- PANTALLA 3: PRESUPUESTOS ---
class BudgetScreen(ft.Column):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.expand = True
        self.cargar()

    def cargar(self):
        cats = self.controller.obtener_categorias()
        items = []
        for c in cats:
            progreso = 0
            # Aquí podrías pedir al controlador el % real gastado
            items.append(
                ft.Container(
                    bgcolor=ft.Colors.SURFACE, padding=15, border_radius=10, margin=ft.margin.only(bottom=10),
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, "black")),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(c.nombre, weight="bold", size=16),
                            ft.IconButton(ft.Icons.EDIT, icon_size=20, on_click=lambda e, cat=c: self.editar(cat))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(value=progreso, color=ft.Colors.BLUE, bgcolor=ft.Colors.BLUE_50),
                        ft.Text(f"Presupuesto: ${c.presupuesto:,.0f}", size=12, color="grey")
                    ])
                )
            )
        self.controls = [
            ft.Text("Mis Presupuestos", size=22, weight="bold"),
            ft.ListView(controls=items, expand=True, spacing=10)
        ]

    def editar(self, c):
        txt_monto = ft.TextField(label="Nuevo Límite", value=str(c.presupuesto), keyboard_type=ft.KeyboardType.NUMBER)

        def on_save(e):
            try:
                valor = float(txt_monto.value)
                self.controller.actualizar_presupuesto(c.nombre, valor)
                self.page.close(dlg)
                self.cargar()
                self.update()
                self.page.snack_bar = ft.SnackBar(ft.Text("Actualizado"))
                self.page.snack_bar.open = True
                self.page.update()
            except ValueError:
                txt_monto.error_text = "Número inválido"
                txt_monto.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Editar {c.nombre}"), content=txt_monto,
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                     ft.FilledButton("Guardar", on_click=on_save)]
        )
        self.page.open(dlg)
        self.page.update()


# --- PANTALLA 4: ALERTAS ---
class AlertsScreen(ft.ListView):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.expand = True
        self.padding = 20
        self.cargar()

    def cargar(self):
        alertas = self.controller.obtener_alertas()
        if not alertas:
            self.controls = [
                ft.Column([ft.Icon(ft.Icons.CHECK_CIRCLE, size=50, color="green"), ft.Text("Todo en orden")],
                          alignment="center")]
            return

        for a in alertas:
            color = ft.Colors.RED_100 if a.nivel == 'danger' else ft.Colors.ORANGE_100
            icono = ft.Icons.WARNING if a.nivel == 'danger' else ft.Icons.INFO
            self.controls.append(
                ft.Container(
                    bgcolor=color, padding=15, border_radius=10, margin=ft.margin.only(bottom=10),
                    content=ft.Row([
                        ft.Icon(icono, color="black54"),
                        ft.Column([
                            ft.Text(a.mensaje, weight="bold", color="black87", size=13),
                            ft.Text(a.fecha, size=10, color="black54")
                        ], expand=True)
                    ])
                )
            )