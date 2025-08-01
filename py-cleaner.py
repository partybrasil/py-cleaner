
# --- CLI Original ---
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
    print("generate_report() ejecutado correctamente.")

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
    print("uninstall_dependencies() ejecutado correctamente.")

def check_environment():
    subprocess.run([sys.executable, '-m', 'pip', 'list'])
    print("check_environment() ejecutado correctamente.")

def execute_activator():
    subprocess.run(['powershell', '-File', 'Activador VENV.ps1'])
    print("execute_activator() ejecutado correctamente.")

def manual_command():
    print("\nCrear Ambiente Virtual VENV:")
    print("python -m venv .venv")
    print("\nActivar Ambiente Virtual VENV:")
    print(".\\.venv\\Scripts\\Activate")
    print("\nDesactivar Ambiente Virtual VENV:")
    print("deactivate")
    print("\nVerificar y manejar Politica de Ejecucion de Scripts en PowerShell:")
    print("Set-ExecutionPolicy (Restricted, AllSigned, RemoteSigned, Unrestricted)")
    while True:
        choice = input("\nElija una opción:\n1. Volver al menú\n2. Salir\nOpción: ")
        if choice == '1':
            return
        elif choice == '2':
            print("Saliendo...")
            raise SystemExit
        else:
            print("Opción inválida. Por favor, intente de nuevo.")
    print("manual_command() ejecutado correctamente.")

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

# --- GUI con PySide6 ---
def iniciar_gui():
    import sys
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit,
        QTableWidget, QTableWidgetItem, QStatusBar, QDialog, QMessageBox, QCheckBox, QGroupBox, QGridLayout, QLineEdit
    )
    from PySide6.QtGui import QIcon, QColor, QPalette
    from PySide6.QtCore import Qt, QTimer, QDateTime

    class LedIndicator(QLabel):
        def __init__(self, color_off=QColor('gray'), color_on=QColor('green'), size=18, parent=None):
            super().__init__(parent)
            self.color_off = color_off
            self.color_on = color_on
            self.size = size
            self.setFixedSize(size, size)
            self.set_off()
        def set_on(self):
            self.setStyleSheet(f"background-color: {self.color_on.name()}; border-radius: {self.size//2}px; border: 1px solid #333;")
        def set_off(self):
            self.setStyleSheet(f"background-color: {self.color_off.name()}; border-radius: {self.size//2}px; border: 1px solid #333;")

    class LogWidget(QTextEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setReadOnly(True)
            self.setStyleSheet("background: #222; color: #eee; font-family: Consolas, monospace; font-size: 13px;")
        def log(self, msg, level="info"):
            color = {"info": "#8be9fd", "ok": "#50fa7b", "warn": "#f1fa8c", "err": "#ff5555"}.get(level, "#fff")
            emoji = {"info": "ℹ️", "ok": "✅", "warn": "⚠️", "err": "❌"}.get(level, "")
            timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
            self.append(f'<span style="color:{color}">{emoji} [{timestamp}] {msg}</span>')

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("py-cleaner GUI")
            self.setWindowIcon(QIcon())
            self.resize(900, 600)
            self.log_widget = LogWidget()
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.init_ui()
            self.update_env_indicators()

        def init_ui(self):
            main_layout = QVBoxLayout()
            # Indicadores de entorno
            env_layout = QHBoxLayout()
            self.led_venv = LedIndicator(color_on=QColor('green'))
            self.led_global = LedIndicator(color_on=QColor('red'))
            env_layout.addWidget(QLabel("VIRTUAL ENV:"))
            env_layout.addWidget(self.led_venv)
            env_layout.addWidget(QLabel("GLOBAL ENV:"))
            env_layout.addWidget(self.led_global)
            env_layout.addStretch()
            self.lbl_python = QLabel(f"Python: {sys.version.split()[0]}")
            env_layout.addWidget(self.lbl_python)
            main_layout.addLayout(env_layout)

            # Botones de operaciones
            btn_layout = QHBoxLayout()
            self.btn_crear_venv = QPushButton("🆕 Crear VENV")
            self.btn_activador = QPushButton("⚡ Activar VENV")
            self.btn_reporte = QPushButton("📄 Generar Reporte")
            self.btn_uninstall = QPushButton("🧹 Desinstalar Dependencias")
            self.btn_check = QPushButton("🔍 Verificar Entorno")
            self.btn_manual = QPushButton("🛠️ Comandos Manuales")
            self.btn_salir = QPushButton("🚪 Salir")
            for btn in [self.btn_crear_venv, self.btn_activador, self.btn_reporte, self.btn_uninstall, self.btn_check, self.btn_manual, self.btn_salir]:
                btn.setMinimumHeight(40)
                btn_layout.addWidget(btn)
            main_layout.addLayout(btn_layout)

            # Panel dinámico (tabla de dependencias, comandos, etc.)
            self.panel = QWidget()
            self.panel_layout = QVBoxLayout()
            self.panel.setLayout(self.panel_layout)
            main_layout.addWidget(self.panel)

            # Log de operaciones
            main_layout.addWidget(QLabel("Log de Operaciones:"))
            main_layout.addWidget(self.log_widget)

            # Widget central
            central = QWidget()
            central.setLayout(main_layout)
            self.setCentralWidget(central)

            # Conexiones
            self.btn_crear_venv.clicked.connect(self.crear_venv)
            self.btn_activador.clicked.connect(self.activar_venv)
        def crear_venv(self):
            self.log_widget.log("Ejecutando script de creación de VENV...", "info")
            try:
                subprocess.run(['powershell', '-File', 'Creador VENV.ps1'])
                self.log_widget.log("Script de creación ejecutado.", "ok")
                self.update_env_indicators()
            except Exception as e:
                self.log_widget.log(f"Error al crear VENV: {e}", "err")
            self.btn_reporte.clicked.connect(self.generar_reporte)
            self.btn_uninstall.clicked.connect(self.desinstalar_dependencias)
            self.btn_check.clicked.connect(self.verificar_entorno)
            self.btn_manual.clicked.connect(self.comandos_manuales)
            self.btn_salir.clicked.connect(self.close)

        def update_env_indicators(self):
            if is_venv_active():
                self.led_venv.set_on()
                self.led_global.set_off()
                self.status_bar.showMessage("Entorno Virtual Activo", 5000)
            else:
                self.led_venv.set_off()
                self.led_global.set_on()
                self.status_bar.showMessage("Entorno Global Activo", 5000)

        def activar_venv(self):
            self.log_widget.log("Ejecutando script de activación de VENV...", "info")
            try:
                execute_activator()
                self.log_widget.log("Script de activación ejecutado.", "ok")
                self.update_env_indicators()
            except Exception as e:
                self.log_widget.log(f"Error al activar VENV: {e}", "err")

        def generar_reporte(self):
            self.log_widget.log("Generando reporte de dependencias...", "info")
            try:
                generate_report()
                self.log_widget.log("Reporte generado como pyREPORT.txt.", "ok")
                self.mostrar_dependencias()
            except Exception as e:
                self.log_widget.log(f"Error al generar reporte: {e}", "err")

        def mostrar_dependencias(self):
            self.panel_layout.takeAt(0)
            self.panel_layout.addWidget(QLabel("Dependencias instaladas:"))
            table = QTableWidget()
            try:
                with open('pyREPORT.txt', 'r') as f:
                    deps = [line.strip() for line in f if line.strip()]
                table.setRowCount(len(deps))
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(["Paquete", "Seleccionar"])
                for i, dep in enumerate(deps):
                    pkg = dep.split('==')[0] if '==' in dep else dep
                    table.setItem(i, 0, QTableWidgetItem(pkg))
                    chk = QCheckBox()
                    table.setCellWidget(i, 1, chk)
                table.resizeColumnsToContents()
                self.panel_layout.addWidget(table)
            except Exception as e:
                self.panel_layout.addWidget(QLabel(f"Error al leer pyREPORT.txt: {e}"))

        def desinstalar_dependencias(self):
            self.log_widget.log("Desinstalando dependencias...", "warn")
            try:
                uninstall_dependencies()
                self.log_widget.log("Dependencias desinstaladas.", "ok")
            except Exception as e:
                self.log_widget.log(f"Error al desinstalar dependencias: {e}", "err")

        def verificar_entorno(self):
            self.log_widget.log("Verificando entorno de Python...", "info")
            try:
                check_environment()
                self.log_widget.log("Entorno verificado.", "ok")
            except Exception as e:
                self.log_widget.log(f"Error al verificar entorno: {e}", "err")

        def comandos_manuales(self):
            self.panel_layout.takeAt(0)
            group = QGroupBox("Comandos Manuales Útiles")
            layout = QVBoxLayout()
            cmds = [
                ("Crear Ambiente Virtual VENV", "python -m venv .venv"),
                ("Activar Ambiente Virtual VENV", ".\\.venv\\Scripts\\Activate"),
                ("Desactivar Ambiente Virtual VENV", "deactivate"),
                ("Política de Ejecución PowerShell", "Set-ExecutionPolicy (Restricted, AllSigned, RemoteSigned, Unrestricted)")
            ]
            for desc, cmd in cmds:
                h = QHBoxLayout()
                h.addWidget(QLabel(f"{desc}:"))
                line = QLineEdit(cmd)
                line.setReadOnly(True)
                btn = QPushButton("Copiar")
                btn.clicked.connect(lambda _, l=line: QApplication.clipboard().setText(l.text()))
                h.addWidget(line)
                h.addWidget(btn)
                layout.addLayout(h)
            group.setLayout(layout)
            self.panel_layout.addWidget(group)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

# --- Arranque híbrido CLI/GUI ---
if __name__ == "__main__":
    if "--gui" in sys.argv:
        iniciar_gui()
    else:
        print("Bienvenido a la Herramienta de Limpieza de Python")
        print("Por favor, asegúrese de que el entorno virtual esté activado antes de ejecutar esta aplicación.")
        signal.signal(signal.SIGINT, signal_handler)
        main()
