# controllers/app_controller.py
import flet as ft
from datetime import datetime

# Importamos la base de datos desde la carpeta models
from models.database import Database
# Importamos las entidades (Transaccion) desde la carpeta models
from models.entities import Transaccion
# Importamos las utilidades desde la carpeta utils
from utils import validators, reports


class AppController:
    def __init__(self, page: ft.Page):
        self.db = Database()
        self.page = page

    # --- LÓGICA DE TRANSACCIONES ---
    def obtener_transacciones(self):
        return self.db.obtener_transacciones()

    def agregar_transaccion(self, tipo, monto, categoria, descripcion, fecha):
        # 1. Validar datos (Logica de Negocio)
        if validators.validar_monto(monto) or validators.validar_descripcion(
                descripcion) or validators.validar_categoria(categoria):
            return {"status": "error", "message": "Datos inválidos o incompletos"}

        # 2. Crear objeto Modelo
        nueva_tx = Transaccion(None, tipo, monto, categoria, fecha, descripcion)

        # 3. Guardar en BD
        alerta = self.db.agregar_transaccion(nueva_tx)

        # 4. Retornar resultado a la vista
        return {"status": "success", "alerta": alerta}

    def eliminar_transaccion(self, id_tx):
        self.db.eliminar_transaccion(id_tx)

    def exportar_excel(self, transacciones):
        return reports.generar_excel(transacciones)

    def exportar_pdf(self, transacciones):
        return reports.generar_pdf(transacciones)

    # --- LÓGICA DE DASHBOARD ---
    def obtener_balance(self):
        return self.db.obtener_balance()

    # --- LÓGICA DE PRESUPUESTOS ---
    def obtener_categorias(self):
        return self.db.obtener_categorias()

    def actualizar_presupuesto(self, nombre, nuevo_valor):
        self.db.actualizar_presupuesto(nombre, nuevo_valor)

    def obtener_alertas(self):
        return self.db.obtener_alertas()