import sqlite3
from datetime import datetime
from models.entities import Transaccion, Categoria, Alerta


class Database:
    def __init__(self, db_name="finanzas.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
        self.seed_data()  # Insertar datos iniciales

    def create_tables(self):
        cursor = self.conn.cursor()
        # Tabla Transacciones
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS transacciones
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           tipo
                           TEXT,
                           monto
                           REAL,
                           categoria
                           TEXT,
                           fecha
                           TEXT,
                           descripcion
                           TEXT
                       )
                       """)
        # Tabla Categorías (Nueva)
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS categorias
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           nombre
                           TEXT
                           UNIQUE,
                           presupuesto
                           REAL
                       )
                       """)
        # Tabla Alertas (Nueva)
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS alertas
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           mensaje
                           TEXT,
                           fecha
                           TEXT,
                           nivel
                           TEXT
                       )
                       """)
        self.conn.commit()

    def seed_data(self):
        """Inserta categorías por defecto si no existen"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT count(*) FROM categorias")
        if cursor.fetchone()[0] == 0:
            categorias_default = [
                ("Alimentación", 500.0),
                ("Transporte", 200.0),
                ("Entretenimiento", 150.0),
                ("Servicios", 300.0),
                ("Salario", 0.0)  # Ingresos no suelen tener presupuesto
            ]
            cursor.executemany("INSERT INTO categorias (nombre, presupuesto) VALUES (?, ?)", categorias_default)
            self.conn.commit()

    # --- MÉTODOS DE TRANSACCIONES ---
    def agregar_transaccion(self, transaccion: Transaccion):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO transacciones (tipo, monto, categoria, fecha, descripcion) VALUES (?, ?, ?, ?, ?)",
                       (transaccion.tipo, transaccion.monto, transaccion.categoria, transaccion.fecha,
                        transaccion.descripcion))
        self.conn.commit()

        # Verificar presupuesto inmediatamente después de agregar gasto
        if transaccion.tipo == 'gasto':
            return self.verificar_presupuesto(transaccion.categoria)
        return None

    def obtener_transacciones(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM transacciones ORDER BY fecha DESC")
        return [Transaccion(*row) for row in cursor.fetchall()]

    def eliminar_transaccion(self, id_tx):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transacciones WHERE id = ?", (id_tx,))
        self.conn.commit()

    def obtener_balance(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='ingreso'")
        ingresos = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='gasto'")
        gastos = cursor.fetchone()[0] or 0.0
        return ingresos, gastos

    # --- MÉTODOS DE PRESUPUESTOS Y ALERTAS ---
    def obtener_categorias(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM categorias")
        return [Categoria(*row) for row in cursor.fetchall()]

    def actualizar_presupuesto(self, nombre_categoria, nuevo_presupuesto):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE categorias SET presupuesto = ? WHERE nombre = ?", (nuevo_presupuesto, nombre_categoria))
        self.conn.commit()

    def obtener_alertas(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM alertas ORDER BY fecha DESC")
        return [Alerta(*row) for row in cursor.fetchall()]

    def verificar_presupuesto(self, categoria_nombre):
        """Lógica crítica: Calcula si se pasó el presupuesto"""
        cursor = self.conn.cursor()

        # 1. Obtener presupuesto
        cursor.execute("SELECT presupuesto FROM categorias WHERE nombre = ?", (categoria_nombre,))
        res = cursor.fetchone()
        if not res: return None
        presupuesto_max = res[0]

        if presupuesto_max <= 0: return None  # Si es 0, asumimos que no tiene límite

        # 2. Sumar gastos
        cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='gasto' AND categoria = ?", (categoria_nombre,))
        total_gastado = cursor.fetchone()[0] or 0.0

        # 3. Calcular porcentaje
        porcentaje = (total_gastado / presupuesto_max) * 100
        alerta = None

        # CORRECCIÓN AQUÍ: Usamos 'porcentaje' en lugar de 'percentage'
        if porcentaje >= 100:
            alerta = Alerta(None, f"¡Presupuesto excedido en {categoria_nombre}! ({int(porcentaje)}%)",
                            datetime.now().strftime("%Y-%m-%d"), "danger")
        elif porcentaje >= 80:
            alerta = Alerta(None, f"Advertencia: {categoria_nombre} al {int(porcentaje)}% del presupuesto",
                            datetime.now().strftime("%Y-%m-%d"), "warning")

        # 4. Si hay alerta, guardarla
        if alerta:
            cursor.execute("INSERT INTO alertas (mensaje, fecha, nivel) VALUES (?, ?, ?)",
                           (alerta.mensaje, alerta.fecha, alerta.nivel))
            self.conn.commit()
            return alerta

        return None