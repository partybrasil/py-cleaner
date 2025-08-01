
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
        QTableWidget, QTableWidgetItem, QStatusBar, QDialog, QMessageBox, QCheckBox, QGroupBox, QGridLayout, QLineEdit, QTabWidget, QPlainTextEdit
    )
    from PySide6.QtGui import QIcon, QColor, QPalette
    from PySide6.QtCore import Qt, QTimer, QDateTime

    class LedIndicator(QLabel):
        def __init__(self, color_off=QColor('red'), color_on=QColor('yellow'), size=18, parent=None):
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

    class ConsoleWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            self.console = QPlainTextEdit()
            self.console.setReadOnly(True)
            self.console.setStyleSheet("background: #111; color: #eee; font-family: Consolas, monospace; font-size: 13px;")
            self.input_line = QLineEdit()
            self.input_line.setPlaceholderText("Escribe un comando y presiona Enter...")
            self.input_line.returnPressed.connect(self.send_command)
            layout.addWidget(self.console)
            layout.addWidget(self.input_line)
            self.setLayout(layout)
            self.process = None
            self.current_python = sys.executable
        def set_python(self, python_path):
            self.current_python = python_path
        def send_command(self):
            cmd = self.input_line.text()
            if not cmd.strip():
                return
            self.console.appendPlainText(f"> {cmd}")
            self.input_line.clear()
            import threading
            def run():
                try:
                    # Si el comando inicia con 'python' o 'pip', lo redirigimos al python del entorno activo
                    parts = cmd.strip().split()
                    if parts[0] in ["python", "pip"]:
                        parts[0] = self.current_python
                    proc = subprocess.Popen(parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    for line in proc.stdout:
                        self.console.appendPlainText(line.rstrip())
                    for line in proc.stderr:
                        self.console.appendPlainText(line.rstrip())
                except Exception as e:
                    self.console.appendPlainText(f"Error: {e}")
            threading.Thread(target=run, daemon=True).start()

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
            self.led_venv = LedIndicator()
            self.led_global = LedIndicator()
            self.led_externo = LedIndicator()
            env_layout.addWidget(QLabel("VIRTUAL ENV:"))
            env_layout.addWidget(self.led_venv)
            env_layout.addWidget(QLabel("GLOBAL ENV:"))
            env_layout.addWidget(self.led_global)
            env_layout.addWidget(QLabel("EXTERNO:"))
            env_layout.addWidget(self.led_externo)
            env_layout.addStretch()
            self.lbl_python = QLabel(f"Python: {sys.version.split()[0]}")
            env_layout.addWidget(self.lbl_python)
            # Botones para alternar ambientes
            self.btn_cargar_venv = QPushButton("📂 Cargar VENV externo")
            self.btn_global = QPushButton("🌐 Cargar VENV GLOBAL")
            self.btn_local = QPushButton("📁 Cargar VENV LOCAL")
            env_layout.addWidget(self.btn_cargar_venv)
            env_layout.addWidget(self.btn_global)
            env_layout.addWidget(self.btn_local)
            # Label para mostrar el path del venv cargado
            self.lbl_venv_path = QLabel("")
            env_layout.addWidget(self.lbl_venv_path)
            main_layout.addLayout(env_layout)

            # Pestañas: Log y Consola
            self.tabs = QTabWidget()
            self.tab_log = QWidget()
            log_layout = QVBoxLayout()
            log_layout.addWidget(QLabel("Log de Operaciones:"))
            log_layout.addWidget(self.log_widget)
            self.tab_log.setLayout(log_layout)
            self.tab_console = ConsoleWidget()
            self.tabs.addTab(self.tab_log, "Log de Operaciones")
            self.tabs.addTab(self.tab_console, "Consola")
            main_layout.addWidget(self.tabs)

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

            # Widget central
            central = QWidget()
            central.setLayout(main_layout)
            self.setCentralWidget(central)

            # Estado de entorno activo
            self.entorno_activo = "local"  # Puede ser 'local', 'global', 'externo'
            self.python_local = sys.executable
            self.python_externo = None

            # Conexiones
            self.btn_crear_venv.clicked.connect(self.crear_venv)
            self.btn_activador.clicked.connect(self.activar_venv)
            self.btn_cargar_venv.clicked.connect(self.cargar_venv_externo)
            self.btn_global.clicked.connect(self.cargar_global)
            self.btn_local.clicked.connect(self.cargar_local)
        def cargar_global(self):
            self.entorno_activo = "global"
            self.tab_console.set_python(sys.base_prefix + ("/python.exe" if os.name == "nt" else "/bin/python"))
            self.led_global.set_on()
            self.led_venv.set_off()
            self.led_externo.set_off()
            self.lbl_venv_path.setText("Python GLOBAL activo")
            self.log_widget.log("Cambiado a entorno GLOBAL", "info")

        def cargar_local(self):
            self.entorno_activo = "local"
            self.tab_console.set_python(self.python_local)
            self.led_global.set_off()
            self.led_venv.set_on()
            self.led_externo.set_off()
            self.lbl_venv_path.setText("VENV LOCAL activo")
            self.log_widget.log("Cambiado a entorno LOCAL", "info")

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
            self.btn_cargar_venv.clicked.connect(self.cargar_venv_externo)
        def cargar_venv_externo(self):
            from PySide6.QtWidgets import QFileDialog
            venv_dir = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta del VENV")
            if venv_dir:
                posibles = ["Scripts/python.exe", "bin/python", "bin/python3"]
                encontrado = False
                for rel in posibles:
                    python_path = os.path.join(venv_dir, rel)
                    if os.path.exists(python_path):
                        self.python_externo = python_path
                        self.entorno_activo = "externo"
                        self.tab_console.set_python(python_path)
                        self.led_global.set_off()
                        self.led_venv.set_off()
                        self.led_externo.set_on()
                        self.lbl_venv_path.setText(f"VENV externo activo: {venv_dir}")
                        self.log_widget.log(f"VENV externo cargado: {venv_dir}", "ok")
                        encontrado = True
                        break
                if not encontrado:
                    self.lbl_venv_path.setText("VENV no válido")
                    self.log_widget.log(f"La carpeta seleccionada no es un VENV válido: {venv_dir}", "err")
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
            # Actualiza los LEDs según el entorno activo
            if self.entorno_activo == "local":
                self.led_venv.set_on()
                self.led_global.set_off()
                self.led_externo.set_off()
                self.status_bar.showMessage("Entorno Virtual Activo", 5000)
            elif self.entorno_activo == "global":
                self.led_venv.set_off()
                self.led_global.set_on()
                self.led_externo.set_off()
                self.status_bar.showMessage("Entorno Global Activo", 5000)
            elif self.entorno_activo == "externo":
                self.led_venv.set_off()
                self.led_global.set_off()
                self.led_externo.set_on()
                self.status_bar.showMessage("VENV Externo Activo", 5000)

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
