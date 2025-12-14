import re

def validar_monto(valor):
    """Valida que el campo sea numérico y positivo[cite: 15]."""
    if not valor:
        return "El monto es obligatorio."
    try:
        monto = float(valor)
        if monto <= 0:
            return "El monto debe ser mayor a 0."
        return None  # Sin error
    except ValueError:
        return "Ingrese un número válido."

def validar_descripcion(texto):
    """Valida longitud y caracteres especiales[cite: 17]."""
    if not texto or len(texto.strip()) < 3:
        return "La descripción es muy corta."
    if len(texto) > 50:
        return "La descripción no debe superar 50 caracteres."
    # Ejemplo de regex para evitar caracteres muy extraños (opcional)
    if not re.match(r"^[a-zA-Z0-9\s\.\,\-]+$", texto):
        return "Caracteres no permitidos."
    return None

def validar_categoria(valor):
    """Valida que se haya seleccionado una opción."""
    if not valor:
        return "Seleccione una categoría."
    return None