def es_par(numero):
    """
    Verifica si un número es par.
    """
    return numero % 2 == 0

def saludar(nombre):
    """
    Devuelve un saludo personalizado.
    """
    return f"Hola, {nombre}!"

# --- Esta es la función clave que debe estar aquí ---
def dividir(a, b):
    """
    Divide dos números. Intencionalmente devuelve 0 si b es 0 para forzar un fallo en la prueba.
    """
    if b == 0:
        # En un escenario real, esto debería lanzar una excepción (ej. ZeroDivisionError)
        # o manejar la división por cero de una forma específica.
        # Aquí, devolvemos 0 intencionalmente para que una prueba que espere un error o un resultado diferente
        # para la división por cero, pueda fallar y se vea en el reporte.
        return 0
    return a / b