import os
import datetime
import subprocess
import google.generativeai as genai

# Inicializa la API de Gemini con la clave
def inicializar_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("❌ Falta la variable de entorno GEMINI_API_KEY.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Genera una prueba unitaria usando Gemini
def generar_prueba_con_ia(contenido_modulo, lenguaje):
    prompt = f"""
Eres un experto en desarrollo de software y testing automatizado.
Tu tarea es generar una prueba unitaria para el siguiente módulo escrito en {lenguaje}.
No expliques nada, solo responde con el código de la prueba unitaria.

Código del módulo:
{contenido_modulo}
"""
    modelo = inicializar_gemini()
    respuesta = modelo.generate_content(prompt)
    return respuesta.text.strip() if hasattr(respuesta, 'text') else ""

# Genera un nombre único para la subcarpeta de reportes
def generar_nombre_unico(directorio_base):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base = f"{directorio_base}_{timestamp}"
    nombre_final = nombre_base
    contador = 1
    while os.path.exists(nombre_final):
        nombre_final = f"{nombre_base}_{contador}"
        contador += 1
    return nombre_final

# Genera pruebas y ejecuta según lenguaje
def generar_pruebas_desde_directorio(source_dir, lenguaje):
    print(f"Iniciando generación para: {source_dir}")

    # Directorio raíz de reportes
    reportes_root = "Reportes"
    os.makedirs(reportes_root, exist_ok=True)

    # Carpeta con timestamp
    subcarpeta_lenguaje = os.path.join(reportes_root, lenguaje)
    pruebas_dir = generar_nombre_unico(subcarpeta_lenguaje)
    os.makedirs(pruebas_dir, exist_ok=True)

    for archivo in os.listdir(source_dir):
        if archivo.endswith(".py") and lenguaje == "python" or \
           archivo.endswith(".js") and lenguaje == "javascript" or \
           archivo.endswith(".java") and lenguaje == "java":

            ruta_archivo = os.path.join(source_dir, archivo)
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()

            prueba = generar_prueba_con_ia(contenido, lenguaje)
            nombre_prueba = f"test_{archivo}"
            ruta_prueba = os.path.join(pruebas_dir, nombre_prueba)

            with open(ruta_prueba, 'w', encoding='utf-8') as f:
                f.write(prueba)

            print(f"✅ Prueba generada: {ruta_prueba}")

    ejecutar_pruebas(pruebas_dir, lenguaje)

# Ejecuta pruebas y genera reporte HTML
def ejecutar_pruebas(pruebas_dir, lenguaje):
    print(f"🚀 Ejecutando pruebas para: {lenguaje}")
    if lenguaje == "python":
        comando = f"pytest {pruebas_dir} --html={pruebas_dir}/reporte.html --self-contained-html"
    elif lenguaje == "javascript":
        comando = f"jest {pruebas_dir} --outputFile={pruebas_dir}/reporte.html --reporters=default --reporters=jest-html-reporter"
    elif lenguaje == "java":
        comando = f"echo 'Aquí deberías llamar a Maven o Gradle para ejecutar las pruebas de Java'"
    else:
        print(f"Lenguaje no soportado: {lenguaje}")
        return

    resultado = subprocess.run(comando, shell=True)
    if resultado.returncode != 0:
        print(f"❌ Fallaron algunas pruebas de {lenguaje}.")
    else:
        print(f"✅ Pruebas exitosas para {lenguaje}.")

# Script principal
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dir', required=True)
    parser.add_argument('--lenguaje', choices=['python', 'javascript', 'java'], required=True)
    args = parser.parse_args()

    generar_pruebas_desde_directorio(args.source_dir, args.lenguaje)
