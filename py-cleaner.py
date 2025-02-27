import os
import subprocess
import sys

def is_venv_active():
    return sys.prefix != sys.base_prefix

def generate_report():
    result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
    with open('pyREPORT.txt', 'w') as report_file:
        report_file.write(result.stdout)
    print("Report generated as pyREPORT.txt")

def uninstall_dependencies():
    if not os.path.exists('pyREPORT.txt'):
        print("pyREPORT.txt not found.")
        return
    
    with open('pyREPORT.txt', 'r') as report_file:
        dependencies = report_file.readlines()
    
    print("Dependencies to uninstall:")
    for dep in dependencies:
        print(dep.strip())
    
    confirm = input("Do you want to proceed with uninstallation? (yes/no): ")
    if confirm.lower() != 'yes':
        return
    
    for dep in dependencies:
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', dep.strip()])

def check_environment():
    subprocess.run([sys.executable, '-m', 'pip', 'list'])

def execute_activator():
    subprocess.run(['powershell', '-File', 'Activador VENV.ps1'])

def main():
    while True:
        venv_status = "ON" if is_venv_active() else "OFF"
        print(f"\nEntorno Virtual: {venv_status}")
        print("\nPython Cleaner Tool")
        print("1. Ejecutar Script Activador")
        print("2. Generar Report de Dependencias Instaladas")
        print("3. Desinstalar dependencias del python")
        print("4. Check Python Environment")
        print("5. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            execute_activator()
        elif choice == '2':
            generate_report()
        elif choice == '3':
            uninstall_dependencies()
        elif choice == '4':
            check_environment()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
