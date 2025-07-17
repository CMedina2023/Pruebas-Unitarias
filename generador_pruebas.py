import os
import subprocess
from datetime import datetime
import re
import concurrent.futures
import sys
import google.generativeai as genai

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Error: La variable de entorno 'GEMINI_API_KEY' no está configurada.")
    sys.exit(1)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

EXTENSION_LENGUAJE_FRAMEWORK = {
    ".py": ("Python", "unittest"),
    ".js": ("JavaScript", "Jest"),
    ".java": ("Java", "JUnit"),
}


def leer_codigo_de_archivo(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error al leer '{ruta_archivo}': {e}")
        return None


def generar_pruebas_con_timeout(codigo_fuente, nombre_modulo, lenguaje_objetivo, timeout=200):
    if not codigo_fuente:
        return None

    def llamar_modelo():
        prompt = f"""
        Eres un experto en pruebas de software. Genera pruebas unitarias en {lenguaje_objetivo} para el siguiente código del módulo '{nombre_modulo}'.
        El código es:
        ```{lenguaje_objetivo.lower()}
        {codigo_fuente}
        ```
        Devuelve solo el código de las pruebas.
        """
        response = model.generate_content(prompt)
        texto = response.text.strip()
        texto = re.sub(r"```.*?\n", "", texto, count=1).strip() if texto.startswith("```") else texto
        return texto.rstrip("`").strip() if texto.endswith("```") else texto

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(llamar_modelo)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"Tiempo de espera agotado para el módulo: {nombre_modulo}")
            return None


def crear_html_reporte(nombre_archivo, stdout, stderr, ruta_html):
    contenido_html = f"""
    <html>
    <head><title>Reporte de Pruebas - {nombre_archivo}</title></head>
    <body>
    <h1>Reporte de Pruebas para {nombre_archivo}</h1>
    <h2>Salida estándar</h2>
    <pre>{stdout}</pre>
    <h2>Errores</h2>
    <pre>{stderr}</pre>
    </body>
    </html>
    """
    with open(ruta_html, "w", encoding="utf-8") as f:
        f.write(contenido_html)


def ejecutar_prueba_y_generar_reporte(ruta_prueba, lenguaje, pruebas_dir):
    print(f"Ejecutando prueba: {ruta_prueba}")
    try:
        if lenguaje == "Python":
            comando = f"python {ruta_prueba}"
        elif lenguaje == "JavaScript":
            comando = f"npx jest {ruta_prueba}"
        elif lenguaje == "Java":
            # Para Java, compilar antes y ejecutar JUnitCore
            # Suponemos que compilaste todos en otro paso (o aquí mismo)
            nombre_clase = os.path.splitext(os.path.basename(ruta_prueba))[0]
            # classpath incluye junit y hamcrest, que deben estar descargados
            classpath = f".:{pruebas_dir}/junit.jar:{pruebas_dir}/hamcrest.jar:{pruebas_dir}"
            comando = f"java -cp \"{classpath}\" org.junit.runner.JUnitCore {nombre_clase}"
        else:
            print(f"Lenguaje {lenguaje} no soportado para ejecución automática.")
            return

        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)

        nombre_html = f"reporte_{os.path.basename(ruta_prueba)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        ruta_html = os.path.join(pruebas_dir, nombre_html)
        crear_html_reporte(os.path.basename(ruta_prueba), resultado.stdout, resultado.stderr, ruta_html)
        print(f"Reporte guardado en: {ruta_html}")

    except Exception as e:
        print(f"Error ejecutando prueba {ruta_prueba}: {e}")


def generar_pruebas_desde_directorio(source_dir, pruebas_dir, lenguaje_objetivo=None):
    os.makedirs(pruebas_dir, exist_ok=True)

    # Para Java, descarga JUnit y Hamcrest solo una vez para luego compilar y ejecutar
    junit_path = os.path.join(pruebas_dir, "junit.jar")
    hamcrest_path = os.path.join(pruebas_dir, "hamcrest.jar")
    if not (os.path.exists(junit_path) and os.path.exists(hamcrest_path)):
        import urllib.request
        print("Descargando JUnit y Hamcrest...")
        urllib.request.urlretrieve("https://repo1.maven.org/maven2/junit/junit/4.13.2/junit-4.13.2.jar", junit_path)
        urllib.request.urlretrieve(
            "https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar", hamcrest_path)

    for filename in os.listdir(source_dir):
        ruta_codigo = os.path.join(source_dir, filename)

        if not os.path.isfile(ruta_codigo):
            continue

        ext = os.path.splitext(filename)[1]

        if lenguaje_objetivo:
            lenguaje = lenguaje_objetivo
        elif ext in EXTENSION_LENGUAJE_FRAMEWORK:
            lenguaje, _ = EXTENSION_LENGUAJE_FRAMEWORK[ext]
        else:
            print(f"Extensión {ext} no soportada. Archivo omitido: {filename}")
            continue

        nombre_modulo = filename.replace(ext, '')
        print(f"Generando pruebas para {nombre_modulo} en {lenguaje}...")

        codigo_fuente = leer_codigo_de_archivo(ruta_codigo)
        pruebas = generar_pruebas_con_timeout(codigo_fuente, nombre_modulo, lenguaje)

        if pruebas:
            extension_salida = ext if ext in EXTENSION_LENGUAJE_FRAMEWORK else '.txt'
            nombre_prueba = f"test_{nombre_modulo}{extension_salida}"
            ruta_prueba = os.path.join(pruebas_dir, nombre_prueba)

            try:
                with open(ruta_prueba, 'w', encoding='utf-8') as f:
                    f.write(pruebas)
                print(f"Pruebas guardadas en: {ruta_prueba}")
            except Exception as e:
                print(f"Error al guardar pruebas de {nombre_modulo}: {e}")
                continue

            # Para Java, compilar test generado inmediatamente
            if lenguaje == "Java":
                print(f"Compilando prueba Java: {nombre_prueba}")
                compile_cmd = f"javac -cp .:{junit_path}:{hamcrest_path} {ruta_prueba}"
                compila = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
                if compila.returncode != 0:
                    print(f"Error compilando {nombre_prueba}:\n{compila.stderr}")
                    continue

            # Ejecutar la prueba y generar reporte HTML
            ejecutar_prueba_y_generar_reporte(ruta_prueba, lenguaje, pruebas_dir)
        else:
            print(f"No se generaron pruebas para {nombre_modulo}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generador y ejecución automática de pruebas multilenguaje')
    parser.add_argument('--source_dir', type=str, required=True, help='Directorio con módulos fuente')
    parser.add_argument('--output_dir', type=str, required=True, help='Directorio para guardar pruebas y reportes')
    parser.add_argument('--lenguaje', type=str, help='Lenguaje objetivo manual (opcional)')
    args = parser.parse_args()

    generar_pruebas_desde_directorio(args.source_dir, args.output_dir, args.lenguaje)
