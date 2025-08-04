#!/usr/bin/env python3
"""
Script de prueba para verificar que la consola embebida funciona correctamente.
Este script se ejecuta independientemente de la app principal.
"""

import os
import sys
import subprocess

def test_embedded_console():
    """Prueba la funcionalidad de la consola embebida."""
    print("🧪 PRUEBA DE CONSOLA EMBEBIDA")
    print("=" * 50)
    
    # Verificar el entorno actual
    print(f"🐍 Python actual: {sys.executable}")
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"🔗 VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'No establecido')}")
    print(f"🌐 PATH (primeros 100 chars): {os.environ.get('PATH', '')[:100]}...")
    
    # Probar comando pip list
    print("\n📦 Probando 'pip list':")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[:5]  # Primeras 5 líneas
            for line in lines:
                print(f"  {line}")
            print(f"  ... (mostrando {len(lines)} de {len(result.stdout.strip().split())} líneas)")
        else:
            print(f"❌ Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Excepción: {e}")
    
    print("\n✅ Prueba completada")

if __name__ == "__main__":
    test_embedded_console()
