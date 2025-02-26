import os
import subprocess
import sys

def activate_venv(venv_path='venv'):
    activate_script = os.path.join(venv_path, 'Scripts', 'activate_this.py')
    if os.path.exists(activate_script):
        exec(open(activate_script).read(), {'__file__': activate_script})
        return True
    return False

def list_directories(path='.'):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def navigate_to_venv():
    current_path = '.'
    while True:
        directories = list_directories(current_path)
        print("Select a directory:")
        for i, directory in enumerate(directories):
            print(f"{i + 1}. {directory}")
        print("0. Select this directory")

        choice = int(input("Choose an option: "))
        if choice == 0:
            return current_path
        elif 1 <= choice <= len(directories):
            current_path = os.path.join(current_path, directories[choice - 1])
        else:
            print("Invalid choice. Please try again.")

def generate_report():
    env_choice = input("Generate report for (1) virtual environment or (2) global environment? (1/2): ")
    if env_choice == '1':
        venv_path = navigate_to_venv()
        if activate_venv(venv_path):
            print(f"Using virtual environment at {venv_path}.")
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
        else:
            print("Failed to activate virtual environment.")
            return
    else:
        print("Using global Python environment.")
        result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
    
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
    
    env_choice = input("Uninstall in (1) virtual environment or (2) global environment? (1/2): ")
    if env_choice == '1':
        venv_path = navigate_to_venv()
        if activate_venv(venv_path):
            print(f"Using virtual environment at {venv_path}.")
            for dep in dependencies:
                subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', dep.strip()])
        else:
            print("Failed to activate virtual environment.")
    elif env_choice == '2':
        print("Using global Python environment.")
        for dep in dependencies:
            subprocess.run(['pip', 'uninstall', '-y', dep.strip()])
    else:
        print("Invalid choice or virtual environment not found.")

def check_environment():
    if activate_venv():
        print("Virtual environment details:")
        subprocess.run([sys.executable, '-m', 'pip', 'list'])
    else:
        print("Global Python environment details:")
        subprocess.run(['pip', 'list'])

def check_venv_status():
    if os.path.exists('venv') or os.path.exists('.venv'):
        print("Virtual environment found.")
        if activate_venv('venv') or activate_venv('.venv'):
            print("Virtual environment is activated.")
            subprocess.run([sys.executable, '-m', 'pip', 'list'])
        else:
            print("Failed to activate virtual environment.")
    else:
        print("No virtual environment found in the root directory.")

def main():
    while True:
        print("\nPython Cleaner Tool")
        print("1. Generate dependency report")
        print("2. Uninstall dependencies")
        print("3. Check Python environment")
        print("4. Check VENV status")
        print("5. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            generate_report()
        elif choice == '2':
            uninstall_dependencies()
        elif choice == '3':
            check_environment()
        elif choice == '4':
            check_venv_status()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
