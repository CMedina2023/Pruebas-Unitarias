import os
import datetime
import subprocess
import google.generativeai as genai

# Inicializa la API de Gemini con la clave
def inicializar_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("\u274c Falta la variable de entorno GEMINI_API_KEY.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Genera una prueba unitaria usando Gemini
def generar_prueba_con_ia(contenido_modulo, lenguaje):
    prompt = f"""
Eres un experto en desarrollo de software y testing automatizado.
Tu tarea es generar una prueba unitaria para el siguiente módulo escrito en {lenguaje}.
No expliques nada, solo responde con el código de la prueba unitaria.

Código del módulo:
"""
{contenido_modulo}
"""
    """
    modelo = inicializar_gemini()
    respuesta = modelo.generate_content(prompt)
    return respuesta.text.strip() if hasattr(respuesta, 'text') else ""

# Genera un nombre único de carpeta si ya existe
def generar_nombre_unico(directorio_base):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base = f"{directorio_base}_{timestamp}"
    nombre_final = nombre_base
    contador = 1
    while os.path.exists(nombre_final):
        nombre_final = f"{nombre_base}_{contador}"
        contador += 1
    return nombre_final

# Ejecuta pruebas y genera reporte HTML
def ejecutar_pruebas(pruebas_dir, lenguaje):
    print(f"\U0001f680 Ejecutando pruebas para: {lenguaje}")
    if lenguaje == "python":
        comando = f"pytest {pruebas_dir} --html={pruebas_dir}/reporte.html --self-contained-html"
    elif lenguaje == "javascript":
        jest_config_path = os.path.join(pruebas_dir, "jest.config.js")
        with open(jest_config_path, "w") as f:
            f.write("""
module.exports = {
  reporters: [
    "default",
    ["jest-html-reporter", {
      "outputPath": "reporte.html",
      "pageTitle": "Reporte de Pruebas"
    }]
  ]
};
            """)
        comando = f"npx jest --config {jest_config_path}"
    elif lenguaje == "java":
        print("\u26a0\ufe0f Reporte HTML para Java no implementado. Agrega soporte con Maven/Gradle si es necesario.")
        return
    else:
        print(f"Lenguaje no soportado: {lenguaje}")
        return

    resultado = subprocess.run(comando, shell=True)
    ruta_reporte = os.path.join(pruebas_dir, "reporte.html")
    if os.path.exists(ruta_reporte):
        print(f"\u2705 Reporte generado: {ruta_reporte}")
    else:
        print(f"\u26a0\ufe0f No se generó el reporte en: {ruta_reporte}")

    if resultado.returncode != 0:
        print(f"\u274c Fallaron algunas pruebas de {lenguaje}.")
    else:
        print(f"\u2705 Pruebas exitosas para {lenguaje}.")

# Genera pruebas y ejecuta según lenguaje
def generar_pruebas_desde_directorio(source_dir, output_dir, lenguaje):
    print(f"Iniciando generación para: {source_dir}")

    subcarpeta_lenguaje = os.path.join(output_dir, lenguaje)
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

            print(f"\u2705 Prueba generada: {ruta_prueba}")

    ejecutar_pruebas(pruebas_dir, lenguaje)

# Script principal
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--lenguaje', choices=['python', 'javascript', 'java'], required=True)
    args = parser.parse_args()

    generar_pruebas_desde_directorio(args.source_dir, args.output_dir, args.lenguaje)
