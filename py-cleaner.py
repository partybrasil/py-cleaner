import os
import subprocess
import sys
import signal

def is_venv_active():
    return sys.prefix != sys.base_prefix

def generate_report():
    result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
    with open('pyREPORT.txt', 'w') as report_file:
        report_file.write(result.stdout)
    print("Reporte generado como pyREPORT.txt")

def uninstall_dependencies():
    if not os.path.exists('pyREPORT.txt'):
        print("pyREPORT.txt no encontrado.")
        return
    
    with open('pyREPORT.txt', 'r') as report_file:
        dependencies = report_file.readlines()
    
    print("Dependencias a desinstalar:")
    for dep in dependencies:
        print(dep.strip())
    
    confirm = input("¿Desea proceder con la desinstalación? (sí/no): ")
    if confirm.lower() != 'sí':
        return
    
    for dep in dependencies:
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', dep.strip()])

def check_environment():
    subprocess.run([sys.executable, '-m', 'pip', 'list'])

def execute_activator():
    subprocess.run(['powershell', '-File', 'Activador VENV.ps1'])

def manual_command():
    print("\nActivar Ambiente Virtual VENV:")
    print("(WINDOWS):   .\\.venv\\Scripts\\Activate")
    print("\nDesactivar Ambiente Virtual VENV:")
    print("(WINDOWS):   deactivate")
    
    while True:
        choice = input("\nElija una opción:\n1. Volver al menú\n2. Salir\nOpción: ")
        if choice == '1':
            return
        elif choice == '2':
            print("Saliendo...")
            raise SystemExit
        else:
            print("Opción inválida. Por favor, intente de nuevo.")

def main():
    while True:
        venv_status = "VIRTUAL" if is_venv_active() else "GLOBAL"
        print(f"\nEntorno/Ambiente Python Activo: {venv_status}")
        print("\nHerramienta de Limpieza de Python")
        print("1. Ejecutar Script Activador")
        print("2. Generar Reporte de Dependencias Instaladas")
        print("3. Desinstalar dependencias de Python")
        print("4. Verificar Entorno de Python")
        print("5. Comando Manual")
        print("6. Salir")
        
        choice = input("Elija una opción: ")
        
        if choice == '1':
            execute_activator()
        elif choice == '2':
            generate_report()
        elif choice == '3':
            uninstall_dependencies()
        elif choice == '4':
            check_environment()
        elif choice == '5':
            manual_command()
        elif choice == '6':
            print("Saliendo...")
            raise SystemExit
        else:
            print("Opción inválida. Por favor, intente de nuevo.")

def signal_handler(sig, frame):
    print("\nRegresando al menú...")
    main()

if __name__ == "__main__":
    print("Bienvenido a la Herramienta de Limpieza de Python")
    print("Por favor, asegúrese de que el entorno virtual esté activado antes de ejecutar esta aplicación.")
    signal.signal(signal.SIGINT, signal_handler)
    main()
