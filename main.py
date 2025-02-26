import os
import subprocess
import sys

def activate_venv():
    if os.path.exists('venv'):
        activate_script = os.path.join('venv', 'Scripts', 'activate_this.py')
        if os.path.exists(activate_script):
            exec(open(activate_script).read(), {'__file__': activate_script})
            return True
    return False

def generate_report():
    if activate_venv():
        print("Using virtual environment.")
        result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
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
    if env_choice == '1' and activate_venv():
        print("Using virtual environment.")
        for dep in dependencies:
            subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', dep.strip()])
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

def main():
    while True:
        print("\nPython Cleaner Tool")
        print("1. Generate dependency report")
        print("2. Uninstall dependencies")
        print("3. Check Python environment")
        print("4. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            generate_report()
        elif choice == '2':
            uninstall_dependencies()
        elif choice == '3':
            check_environment()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
