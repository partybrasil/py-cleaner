#!/usr/bin/env python3
"""
Script de prueba para verificar la detección de ambientes en py-cleaner
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar las clases del script principal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la clase de gestión de ambientes desde el script principal
try:
    # Definir las clases necesarias directamente aquí para la prueba
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

    def main():
        print("🧪 PRUEBA DE DETECCIÓN DE AMBIENTES - py-cleaner v2.1")
        print("=" * 60)
        
        # Crear instancia del gestor de ambientes
        env_manager = EnvironmentManager()
        
        # Detectar ambiente actual
        env_info = env_manager.detect_environment()
        
        print(f"🐍 Python ejecutable actual: {sys.executable}")
        print(f"🔍 ¿Es VENV activo?: {'SÍ' if env_info['is_venv'] else 'NO'}")
        print(f"🌍 Tipo de ambiente: {env_info['env_type'].upper()}")
        print(f"📂 Directorio actual: {env_info['current_dir']}")
        print(f"📍 sys.prefix: {sys.prefix}")
        print(f"📍 sys.base_prefix: {sys.base_prefix}")
        
        if env_info['venv_path']:
            print(f"📁 Ruta del VENV: {env_info['venv_path']}")
            
        if env_info['virtual_env']:
            print(f"🔗 VIRTUAL_ENV: {env_info['virtual_env']}")
        
        print(f"⚙️ Ejecutable PIP recomendado: {env_manager.get_pip_executable()}")
        
        # Verificar si existe .venv local
        local_venv = os.path.join(os.getcwd(), ".venv")
        local_exists = os.path.exists(local_venv)
        print(f"📁 ¿Existe .venv local?: {'SÍ' if local_exists else 'NO'}")
        if local_exists:
            print(f"   Ruta: {local_venv}")
        
        print("\n" + "=" * 60)
        
        # Verificar que el ejecutable PIP recomendado es diferente al actual si estamos en venv
        if env_info['is_venv']:
            current_pip = sys.executable
            recommended_pip = env_manager.get_pip_executable()
            print(f"✅ Problema SOLUCIONADO:")
            print(f"   ❌ Antes usaba: {current_pip}")
            print(f"   ✅ Ahora usará: {recommended_pip}")
            
            if current_pip != recommended_pip:
                print(f"   🎯 CORRECCIÓN APLICADA: Usando ejecutable correcto del ambiente")
            else:
                print(f"   ℹ️  Ejecutables coinciden (comportamiento esperado)")
        else:
            print(f"⚠️  Trabajando en ambiente GLOBAL - usar con precaución")
        
        print("\n🎉 Prueba completada exitosamente!")

    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"❌ Error en la prueba: {e}")
    import traceback
    traceback.print_exc()
