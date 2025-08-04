#!/usr/bin/env python3
"""
Prueba específica de la función de generación de reportes corregida
"""

# Importar las librerías necesarias desde py-cleaner.py
import sys
import os
import subprocess
import time

# Simular Rich Console para pruebas básicas
class MockConsole:
    def print(self, *args, **kwargs):
        print(*args)
    
    def status(self, message, spinner=None):
        return self
    
    def __enter__(self):
        print(f"📊 {message if hasattr(self, 'message') else 'Ejecutando...'}")
        return self
    
    def __exit__(self, *args):
        pass

# Crear instancia mock de console
console = MockConsole()

# Copiar la clase EnvironmentManager y funciones relevantes del script principal
class EnvironmentManager:
    """Clase para gestionar diferentes ambientes de Python de forma segura."""
    
    def __init__(self):
        self.current_env = "system"
        self.python_executable = sys.executable
        self.venv_path = None
        self.external_venv_path = None
        
    def detect_environment(self) -> dict:
        """Detecta el entorno actual y devuelve información detallada."""
        info = {
            "is_venv": sys.prefix != sys.base_prefix,
            "python_executable": sys.executable,
            "python_version": sys.version.split()[0],
            "venv_path": sys.prefix if sys.prefix != sys.base_prefix else None,
            "base_prefix": sys.base_prefix,
            "current_dir": os.getcwd(),
            "virtual_env": os.environ.get('VIRTUAL_ENV', None)
        }
        
        # Detectar tipo de ambiente
        if info["is_venv"]:
            # Verificar si es local (en directorio actual)
            local_venv_path = os.path.join(os.getcwd(), ".venv")
            if (info["venv_path"] and 
                os.path.abspath(info["venv_path"]) == os.path.abspath(local_venv_path)):
                info["env_type"] = "local_venv"
                self.current_env = "local_venv"
                self.venv_path = local_venv_path
            else:
                info["env_type"] = "external_venv" 
                self.current_env = "external_venv"
                self.external_venv_path = info["venv_path"]
        else:
            info["env_type"] = "system"
            self.current_env = "system"
            
        return info
    
    def get_pip_executable(self) -> str:
        """Obtiene el ejecutable de pip correcto para el entorno actual."""
        if self.current_env == "system":
            return sys.executable
        elif self.current_env == "local_venv":
            if os.name == 'nt':  # Windows
                return os.path.join(self.venv_path, "Scripts", "python.exe")
            else:  # Unix/Linux/Mac
                return os.path.join(self.venv_path, "bin", "python")
        elif self.current_env == "external_venv" and self.external_venv_path:
            if os.name == 'nt':  # Windows
                return os.path.join(self.external_venv_path, "Scripts", "python.exe")
            else:  # Unix/Linux/Mac
                return os.path.join(self.external_venv_path, "bin", "python")
        else:
            return sys.executable

# Crear instancia del gestor
env_manager = EnvironmentManager()

def generate_report() -> bool:
    """Genera un reporte de dependencias instaladas con interfaz moderna y ambiente correcto."""
    env_info = env_manager.detect_environment()
    pip_executable = env_manager.get_pip_executable()
    
    print(f"📊 Generando reporte de dependencias ({env_info['env_type']})...")
    print(f"🔧 Usando: {pip_executable}")
    
    try:
        result = subprocess.run([pip_executable, '-m', 'pip', 'freeze'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Crear reporte con información del ambiente
            report_content = f"# Reporte de Dependencias - py-cleaner\n"
            report_content += f"# Generado: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            report_content += f"# Ambiente: {env_info['env_type']}\n"
            report_content += f"# Python: {env_info['python_version']}\n"
            report_content += f"# Ejecutable: {env_info['python_executable']}\n"
            if env_info['venv_path']:
                report_content += f"# VENV Path: {env_info['venv_path']}\n"
            report_content += f"#\n"
            report_content += result.stdout
            
            with open('pyREPORT.txt', 'w', encoding='utf-8') as report_file:
                report_file.write(report_content)
            
            # Contar dependencias (excluyendo comentarios)
            deps_count = len([line for line in result.stdout.split('\n') if line.strip() and not line.startswith('#')])
            
            print(f"✅ Reporte generado exitosamente")
            print(f"📄 Archivo: pyREPORT.txt")
            print(f"📦 Dependencias encontradas: {deps_count}")
            print(f"🌍 Ambiente: {env_info['env_type'].upper()}")
            print(f"🐍 Python: {env_info['python_version']}")
            return True
        else:
            print(f"❌ Error al generar reporte: {result.stderr}")
            print(f"Ambiente: {env_info['env_type']}")
            print(f"Ejecutable: {pip_executable}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout al generar reporte desde {env_info['env_type']}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print(f"Ambiente: {env_info['env_type']}, Ejecutable: {pip_executable}")
        return False

def test_pip_list():
    """Prueba el comando pip list para verificar que usa el ambiente correcto."""
    env_info = env_manager.detect_environment()
    pip_executable = env_manager.get_pip_executable()
    
    print(f"\n🔍 Probando 'pip list' en ambiente {env_info['env_type'].upper()}")
    print(f"🔧 Ejecutable: {pip_executable}")
    
    try:
        result = subprocess.run([pip_executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            package_count = len([line for line in lines if line.strip() and not line.startswith('Package') and not line.startswith('---')])
            print(f"✅ Comando exitoso")
            print(f"📦 Paquetes encontrados: {package_count}")
            print(f"📋 Primeras líneas del output:")
            for line in lines[:5]:
                print(f"   {line}")
            if len(lines) > 5:
                print(f"   ... y {len(lines) - 5} líneas más")
        else:
            print(f"❌ Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🧪 PRUEBA DE FUNCIONES CORREGIDAS - py-cleaner v2.1")
    print("=" * 60)
    
    # Detectar ambiente actual
    env_info = env_manager.detect_environment()
    print(f"🌍 Ambiente detectado: {env_info['env_type'].upper()}")
    print(f"🐍 Python: {env_info['python_version']}")
    print(f"📍 Ejecutable original: {sys.executable}")
    print(f"⚙️ Ejecutable corregido: {env_manager.get_pip_executable()}")
    
    # Comparar ejecutables para verificar la corrección
    if env_info['is_venv']:
        if sys.executable != env_manager.get_pip_executable():
            print("🚨 PROBLEMA DETECTADO: El script usaría el ejecutable INCORRECTO")
            print("✅ SOLUCIÓN APLICADA: Ahora usa el ejecutable correcto del venv")
        else:
            print("✅ Ejecutables coinciden (correcto para venv activo)")
    
    print("\n" + "-" * 60)
    
    # Probar pip list
    test_pip_list()
    
    print("\n" + "-" * 60)
    
    # Probar generación de reporte
    success = generate_report()
    
    if success and os.path.exists('pyREPORT.txt'):
        print(f"\n📄 Contenido del reporte generado:")
        with open('pyREPORT.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10]):  # Mostrar primeras 10 líneas
                print(f"   {i+1:2}: {line.rstrip()}")
            if len(lines) > 10:
                print(f"   ... y {len(lines) - 10} líneas más")
    
    print(f"\n🎉 Prueba completada - Reporte {'generado' if success else 'falló'}")

if __name__ == "__main__":
    main()
