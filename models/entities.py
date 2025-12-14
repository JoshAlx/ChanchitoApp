class Transaccion:
    def __init__(self, id, tipo, monto, categoria, fecha, descripcion):
        self.id = id
        self.tipo = tipo
        self.monto = float(monto)
        self.categoria = categoria
        self.fecha = fecha
        self.descripcion = descripcion

class Categoria:
    def __init__(self, id, nombre, presupuesto):
        self.id = id
        self.nombre = nombre
        self.presupuesto = float(presupuesto)

class Alerta:
    def __init__(self, id, mensaje, fecha, nivel):
        self.id = id
        self.mensaje = mensaje
        self.fecha = fecha
        self.nivel = nivel # 'warning' (80%) o 'danger' (100%)