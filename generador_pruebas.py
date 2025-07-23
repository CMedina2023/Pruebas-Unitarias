import os
import shutil
import subprocess
import sys
import datetime
import zipfile

def generar_pruebas_desde_directorio(source_dir, output_dir, lenguaje):
    print(f"Iniciando generación para: {source_dir}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pruebas_dir = os.path.join(output_dir, f"pruebas_generadas_{timestamp}")
    os.makedirs(pruebas_dir)

    archivos_fuente = [
        f for f in os.listdir(source_dir)
        if f.endswith(('.py', '.js', '.java'))
    ]

    for archivo in archivos_fuente:
        ruta_archivo = os.path.join(source_dir, archivo)
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            contenido = file.read()

        nombre_modulo = os.path.splitext(archivo)[0]
        pruebas_generadas = generar_pruebas(contenido, lenguaje, nombre_modulo)

        if pruebas_generadas:
            ruta_prueba = os.path.join(pruebas_dir, f"test_{nombre_modulo}.{ext_lenguaje(lenguaje)}")
            with open(ruta_prueba, 'w', encoding='utf-8') as f:
                f.write(pruebas_generadas)

            ejecutar_prueba_y_generar_reporte(ruta_prueba, lenguaje, pruebas_dir)
        else:
            print(f"No se generaron pruebas para {nombre_modulo}")

    copiar_modulos_fuente(source_dir, pruebas_dir)

    comprimir_reportes(pruebas_dir)

def ext_lenguaje(lenguaje):
    return {
        'python': 'py',
        'javascript': 'js',
        'java': 'java'
    }.get(lenguaje.lower(), 'txt')

def generar_pruebas(contenido, lenguaje, nombre_modulo):
    if lenguaje.lower() == 'python':
        return f"""import unittest
import {nombre_modulo}

class Test{nombre_modulo.capitalize()}(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"""
    elif lenguaje.lower() == 'javascript':
        return f"""const assert = require('assert');
const {nombre_modulo} = require('./{nombre_modulo}');

describe('{nombre_modulo} tests', () => {{
    it('should pass placeholder', () => {{
        assert.strictEqual(1, 1);
    }});
}});
"""
    elif lenguaje.lower() == 'java':
        return f"""import org.junit.Test;
import static org.junit.Assert.*;

public class Test{nombre_modulo.capitalize()} {{
    @Test
    public void testPlaceholder() {{
        assertTrue(true);
    }}
}}
"""
    else:
        return ""

def ejecutar_prueba_y_generar_reporte(ruta_prueba, lenguaje, output_dir):
    nombre_archivo = os.path.basename(ruta_prueba)
    nombre_reporte = f"reporte_{nombre_archivo}.html"
    ruta_reporte = os.path.join(output_dir, nombre_reporte)

    if lenguaje.lower() == 'python':
        cmd = [
            sys.executable,
            ruta_prueba
        ]
    elif lenguaje.lower() == 'javascript':
        cmd = ['node', ruta_prueba]
    elif lenguaje.lower() == 'java':
        cmd = ['javac', ruta_prueba]
    else:
        return

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=output_dir)
        salida = result.stdout
        errores = result.stderr
    except Exception as e:
        salida = ""
        errores = str(e)

    with open(ruta_reporte, 'w', encoding='utf-8') as f:
        f.write(f"<h2>Reporte de Pruebas para {nombre_archivo}</h2>")
        f.write("<h3>Salida estándar</h3>")
        f.write(f"<pre>{salida}</pre>")
        f.write("<h3>Errores</h3>")
        f.write(f"<pre>{errores}</pre>")

def comprimir_reportes(directorio):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"reportes-pruebas_{timestamp}.zip"
    zip_path = os.path.join(directorio, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(directorio):
            for file in files:
                if file.endswith('.html'):
                    zipf.write(os.path.join(root, file), arcname=file)

    print(f"✅ Reportes comprimidos en: {zip_path}")

def copiar_modulos_fuente(directorio_fuente, directorio_destino):
    """
    Copia todos los archivos .py, .js y .java del directorio fuente al destino.
    Así, los tests generados pueden importar correctamente los módulos.
    """
    for archivo in os.listdir(directorio_fuente):
        if archivo.endswith(('.py', '.js', '.java')):
            ruta_origen = os.path.join(directorio_fuente, archivo)
            ruta_destino = os.path.join(directorio_destino, archivo)
            try:
                shutil.copyfile(ruta_origen, ruta_destino)
                print(f"📦 Copiado: {archivo} ➝ {directorio_destino}")
            except Exception as e:
                print(f"❌ Error al copiar {archivo}: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generador de Pruebas Multilenguaje")
    parser.add_argument('--source_dir', type=str, required=True, help='Directorio con módulos fuente')
    parser.add_argument('--output_dir', type=str, required=True, help='Directorio para resultados')
    parser.add_argument('--lenguaje', type=str, required=True, choices=['python', 'javascript', 'java'], help='Lenguaje de programación')

    args = parser.parse_args()

    generar_pruebas_desde_directorio(args.source_dir, args.output_dir, args.lenguaje)

