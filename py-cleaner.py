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
            self._log_history = []
        def log(self, msg, level="info"):
            color = {"info": "#8be9fd", "ok": "#50fa7b", "warn": "#f1fa8c", "err": "#ff5555"}.get(level, "#fff")
            emoji = {"info": "ℹ️", "ok": "✅", "warn": "⚠️", "err": "❌"}.get(level, "")
            timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
            html = f'<span style="color:{color}">{emoji} [{timestamp}] {msg}</span>'
            self.append(html)
            self._log_history.append(f"[{timestamp}] {emoji} {msg}")
        def export_log(self, file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in self._log_history:
                        f.write(line + '\n')
                return True, None
            except Exception as e:
                return False, str(e)

    class ConsoleWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            self.console = QPlainTextEdit()
            self.console.setReadOnly(True)
            self.console.setStyleSheet("background: #111; color: #eee; font-family: Consolas, monospace; font-size: 13px;")
            # Botón de refresco discreto
            self.btn_refresh = QPushButton("🔄")
            self.btn_refresh.setFixedSize(32, 32)
            self.btn_refresh.setToolTip("Reiniciar Terminal/Consola InAPP")
            self.btn_refresh.setStyleSheet("background: #222; color: #8be9fd; border-radius: 8px; font-size: 18px;")
            self.btn_refresh.clicked.connect(self.reiniciar_consola)

            self.input_line = QLineEdit()
            self.input_line.setPlaceholderText("Escribe un comando y presiona Enter...")
            self.input_line.returnPressed.connect(self.send_command)

            # Layout horizontal para botón y input
            input_layout = QHBoxLayout()
            input_layout.addWidget(self.btn_refresh)
            input_layout.addWidget(self.input_line)

            layout.addWidget(self.console)
            layout.addLayout(input_layout)
            self.setLayout(layout)
            self.process = None
            self.current_python = sys.executable
            self.reiniciar_consola()

        def reiniciar_consola(self):
            """Limpia la consola y muestra el prompt y el path de Python activo."""
            self.console.clear()
            self.console.appendPlainText(f"🔄 Terminal InAPP listo. Python activo: {self.current_python}")
            self.console.appendPlainText("> ")
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
                    parts = cmd.strip().split()
                    if parts[0] in ["python", "pip"]:
                        parts[0] = self.current_python
                    # Detecta si el comando es interactivo (usa 'input')
                    # Si es un script python, busca si contiene 'input('
                    is_interactive = False
                    if parts[0].endswith("python.exe") and len(parts) > 1 and parts[1] == "-m":
                        # No podemos saber si el módulo usa input, así que asumimos no interactivo
                        is_interactive = False
                    elif parts[0].endswith("python.exe") and len(parts) > 1 and parts[1].endswith(".py"):
                        try:
                            with open(parts[1], "r", encoding="utf-8") as f:
                                if "input(" in f.read():
                                    is_interactive = True
                        except Exception:
                            pass
                    proc = subprocess.Popen(parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE if is_interactive else None, text=True)
                    for line in proc.stdout:
                        self.console.appendPlainText(line.rstrip())
                    for line in proc.stderr:
                        self.console.appendPlainText(line.rstrip())
                    # Si no es interactivo, muestra el prompt
                    if not is_interactive:
                        self.console.appendPlainText("> ")
                except Exception as e:
                    self.console.appendPlainText(f"Error: {e}")
                    self.console.appendPlainText("> ")
            threading.Thread(target=run, daemon=True).start()
        def send_command_from_gui(self, cmd):
            self.console.appendPlainText(f"> {cmd}")
            import threading
            def run():
                try:
                    parts = cmd.strip().split()
                    if parts[0] in ["python", "pip"]:
                        parts[0] = self.current_python
                    is_interactive = False
                    if parts[0].endswith("python.exe") and len(parts) > 1 and parts[1] == "-m":
                        is_interactive = False
                    elif parts[0].endswith("python.exe") and len(parts) > 1 and parts[1].endswith(".py"):
                        try:
                            with open(parts[1], "r", encoding="utf-8") as f:
                                if "input(" in f.read():
                                    is_interactive = True
                        except Exception:
                            pass
                    proc = subprocess.Popen(parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE if is_interactive else None, text=True)
                    for line in proc.stdout:
                        self.console.appendPlainText(line.rstrip())
                    for line in proc.stderr:
                        self.console.appendPlainText(line.rstrip())
                    if not is_interactive:
                        self.console.appendPlainText("> ")
                except Exception as e:
                    self.console.appendPlainText(f"Error: {e}")
                    self.console.appendPlainText("> ")
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
            # Mueve la inicialización de entorno activo y python_local antes de update_env_indicators
            self.entorno_activo = "local"  # Puede ser 'local', 'global', 'externo'
            self.python_local = sys.executable
            self.python_externo = None
            self.update_env_indicators()
            # Botón exportar log
            self.btn_export_log = QPushButton("💾 Exportar Log")
            self.status_bar.addPermanentWidget(self.btn_export_log)
            self.btn_export_log.clicked.connect(self.exportar_log)

        def update_env_indicators(self):
            """Actualiza los LEDs y el label del entorno activo de forma robusta y pythonic."""
            if self.entorno_activo == "local":
                self.led_venv.set_on()
                self.led_global.set_off()
                self.led_externo.set_off()
                self.lbl_venv_path.setText("VENV LOCAL activo")
            elif self.entorno_activo == "global":
                self.led_venv.set_off()
                self.led_global.set_on()
                self.led_externo.set_off()
                self.lbl_venv_path.setText("Python GLOBAL activo")
            elif self.entorno_activo == "externo":
                self.led_venv.set_off()
                self.led_global.set_off()
                self.led_externo.set_on()
                self.lbl_venv_path.setText(f"VENV externo activo: {self.python_externo}")
            else:
                self.led_venv.set_off()
                self.led_global.set_off()
                self.led_externo.set_off()
                self.lbl_venv_path.setText("Sin entorno activo")

        def exportar_log(self):
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(self, "Exportar Log", "py-cleaner-log.txt", "Archivos de texto (*.txt)")
            if not file_path:
                self.status_bar.showMessage("Exportación de log cancelada.", 3000)
                self.log_widget.log("Exportación de log cancelada por el usuario.", "warn")
                return
            ok, err = self.log_widget.export_log(file_path)
            if ok:
                self.status_bar.showMessage(f"Log exportado a {file_path}", 4000)
                self.log_widget.log(f"Log exportado a {file_path}", "ok")
            else:
                self.status_bar.showMessage(f"Error al exportar log: {err}", 4000)
                self.log_widget.log(f"Error al exportar log: {err}", "err")

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
            reply = QMessageBox.question(self, "Confirmación", "¿Seguro que deseas cambiar al entorno GLOBAL?", QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                self.status_bar.showMessage("Cambio a entorno GLOBAL cancelado.", 3000)
                self.log_widget.log("Cambio a entorno GLOBAL cancelado por el usuario.", "warn")
                return
            self.entorno_activo = "global"
            self.tab_console.set_python(sys.base_prefix + ("/python.exe" if os.name == "nt" else "/bin/python"))
            self.led_global.set_on()
            self.led_venv.set_off()
            self.led_externo.set_off()
            self.lbl_venv_path.setText("Python GLOBAL activo")
            self.log_widget.log("Cambiado a entorno GLOBAL", "info")
            self.status_bar.showMessage("Entorno GLOBAL activo.", 4000)

        def cargar_local(self):
            reply = QMessageBox.question(self, "Confirmación", "¿Seguro que deseas cambiar al entorno LOCAL (VENV)?", QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                self.status_bar.showMessage("Cambio a entorno LOCAL cancelado.", 3000)
                self.log_widget.log("Cambio a entorno LOCAL cancelado por el usuario.", "warn")
                return
            self.entorno_activo = "local"
            self.tab_console.set_python(self.python_local)
            self.led_global.set_off()
            self.led_venv.set_on()
            self.led_externo.set_off()
            self.lbl_venv_path.setText("VENV LOCAL activo")
            self.log_widget.log("Cambiado a entorno LOCAL", "info")
            self.status_bar.showMessage("Entorno LOCAL activo.", 4000)
            # Elimina duplicación de widgets y layouts
            # Solo actualiza los indicadores y el estado, sin reconstruir el layout ni widgets

        def cargar_venv_externo(self):
            from PySide6.QtWidgets import QFileDialog
            venv_dir = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta del VENV")
            if not venv_dir:
                self.status_bar.showMessage("Carga de VENV externo cancelada.", 3000)
                self.log_widget.log("Carga de VENV externo cancelada por el usuario.", "warn")
                return
            # Validación avanzada de venv
            posibles = ["Scripts/python.exe", "bin/python", "bin/python3"]
            encontrado = False
            for rel in posibles:
                python_path = os.path.join(venv_dir, rel)
                if os.path.exists(python_path):
                    # Validar estructura de venv
                    reqs = ["pyvenv.cfg", "Scripts", "Lib"] if os.name == "nt" else ["pyvenv.cfg", "bin", "lib"]
                    valid = all(os.path.exists(os.path.join(venv_dir, r)) for r in reqs)
                    if not valid:
                        self.lbl_venv_path.setText("Estructura de VENV inválida")
                        self.log_widget.log(f"La carpeta seleccionada no tiene estructura válida de VENV: {venv_dir}", "err")
                        self.status_bar.showMessage("Estructura de VENV inválida.", 4000)
                        return
                    reply = QMessageBox.question(self, "Confirmación", f"¿Seguro que deseas cargar el VENV externo?\n{venv_dir}", QMessageBox.Yes | QMessageBox.No)
                    if reply != QMessageBox.Yes:
                        self.status_bar.showMessage("Carga de VENV externo cancelada.", 3000)
                        self.log_widget.log("Carga de VENV externo cancelada por el usuario.", "warn")
                        return
                    self.python_externo = python_path
                    self.entorno_activo = "externo"
                    self.tab_console.set_python(python_path)
                    self.led_global.set_off()
                    self.led_venv.set_off()
                    self.led_externo.set_on()
                    self.lbl_venv_path.setText(f"VENV externo activo: {venv_dir}")
                    self.log_widget.log(f"VENV externo cargado: {venv_dir}", "ok")
                    self.status_bar.showMessage("VENV externo cargado correctamente.", 4000)
                    encontrado = True
                    break
            if not encontrado:
                self.lbl_venv_path.setText("VENV no válido")
                self.log_widget.log(f"La carpeta seleccionada no es un VENV válido: {venv_dir}", "err")
                self.status_bar.showMessage("VENV externo no válido.", 4000)

        def crear_venv(self):
            reply = QMessageBox.question(self, "Confirmación", "¿Seguro que deseas crear un nuevo VENV?", QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                self.status_bar.showMessage("Creación de VENV cancelada.", 3000)
                self.log_widget.log("Creación de VENV cancelada por el usuario.", "warn")
                return
            self.log_widget.log("Ejecutando script de creación de VENV...", "info")
            self.status_bar.showMessage("Creando VENV...", 3000)
            try:
                # Ejecuta el script en la consola embebida
                self.tab_console.send_command_from_gui(f"powershell -File Creador VENV.ps1")
                self.log_widget.log("Script de creación ejecutado.", "ok")
                self.status_bar.showMessage("VENV creado correctamente.", 4000)
                self.update_env_indicators()
            except Exception as e:
                self.log_widget.log(f"Error al crear VENV: {e}", "err")
                self.status_bar.showMessage("Error al crear VENV.", 4000)
            self.btn_reporte.clicked.connect(self.generar_reporte)
            self.btn_uninstall.clicked.connect(self.desinstalar_dependencias)
            self.btn_check.clicked.connect(self.verificar_entorno)
            self.btn_manual.clicked.connect(self.comandos_manuales)
            self.btn_salir.clicked.connect(self.close)

        def activar_venv(self):
            reply = QMessageBox.question(self, "Confirmación", "¿Seguro que deseas activar el VENV local?", QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                self.status_bar.showMessage("Activación de VENV cancelada.", 3000)
                self.log_widget.log("Activación de VENV cancelada por el usuario.", "warn")
                return
            self.log_widget.log("Ejecutando script de activación de VENV...", "info")
            self.status_bar.showMessage("Activando VENV...", 3000)
            try:
                # Ejecuta el script en la consola embebida
                self.tab_console.send_command_from_gui(f"powershell -File Activador VENV.ps1")
                self.log_widget.log("Script de activación ejecutado.", "ok")
                self.status_bar.showMessage("VENV activado correctamente.", 4000)
                self.update_env_indicators()
            except Exception as e:
                self.log_widget.log(f"Error al activar VENV: {e}", "err")
                self.status_bar.showMessage("Error al activar VENV.", 4000)

        def verificar_entorno(self):
            self.log_widget.log("Verificando entorno de Python...", "info")
            self.status_bar.showMessage("Verificando entorno de Python...", 3000)
            try:
                self.tab_console.send_command_from_gui(f"{self.tab_console.current_python} -m pip list")
                self.log_widget.log("Entorno verificado.", "ok")
                self.status_bar.showMessage("Entorno verificado correctamente.", 4000)
            except Exception as e:
                self.log_widget.log(f"Error al verificar entorno: {e}", "err")
                self.status_bar.showMessage("Error al verificar entorno.", 4000)

        def generar_reporte(self):
            self.log_widget.log("Generando reporte de dependencias...", "info")
            self.status_bar.showMessage("Generando reporte de dependencias...", 3000)
            try:
                self.tab_console.send_command_from_gui(f"{self.tab_console.current_python} -m pip freeze > pyREPORT.txt")
                self.log_widget.log("Reporte generado como pyREPORT.txt.", "ok")
                self.status_bar.showMessage("Reporte generado correctamente.", 4000)
                self.mostrar_dependencias()
            except Exception as e:
                self.log_widget.log(f"Error al generar reporte: {e}", "err")
                self.status_bar.showMessage("Error al generar reporte.", 4000)

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
            reply = QMessageBox.question(self, "Desinstalación", "¿Deseas seleccionar los paquetes a desinstalar uno a uno? (Sí = selectivo, No = todos)", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Modo selectivo: mostrar diálogo con los paquetes
                try:
                    with open('pyREPORT.txt', 'r') as f:
                        deps = [line.strip().split('==')[0] if '==' in line else line.strip() for line in f if line.strip()]
                    if not deps:
                        self.log_widget.log("No hay dependencias en pyREPORT.txt.", "warn")
                        self.status_bar.showMessage("No hay dependencias en pyREPORT.txt.", 4000)
                        return
                    # Diálogo de selección
                    from PySide6.QtWidgets import QInputDialog
                    pkg_str = ' '.join(deps)
                    seleccion, ok = QInputDialog.getText(self, "Seleccionar paquetes", f"Paquetes disponibles:\n{pkg_str}\n\nEscribe los nombres de los paquetes a desinstalar separados por espacio:")
                    if not ok or not seleccion.strip():
                        self.log_widget.log("Desinstalación selectiva cancelada por el usuario.", "warn")
                        self.status_bar.showMessage("Desinstalación selectiva cancelada.", 3000)
                        return
                    pkgs = seleccion.strip().split()
                    self.log_widget.log(f"Desinstalando selectivamente: {' '.join(pkgs)}", "warn")
                    self.status_bar.showMessage("Desinstalando paquetes seleccionados...", 3000)
                    for dep in pkgs:
                        subprocess.run([self.tab_console.current_python, '-m', 'pip', 'uninstall', '-y', dep])
                        self.log_widget.log(f"Desinstalado: {dep}", "ok")
                    self.status_bar.showMessage("Desinstalación selectiva finalizada.", 4000)
                except Exception as e:
                    self.log_widget.log(f"Error en desinstalación selectiva: {e}", "err")
                    self.status_bar.showMessage("Error en desinstalación selectiva.", 4000)
                return
            # Modo normal: desinstalar todos
            reply2 = QMessageBox.question(self, "Confirmación", "¿Seguro que deseas desinstalar todas las dependencias listadas en pyREPORT.txt?", QMessageBox.Yes | QMessageBox.No)
            if reply2 != QMessageBox.Yes:
                self.status_bar.showMessage("Desinstalación cancelada.", 3000)
                self.log_widget.log("Desinstalación de dependencias cancelada por el usuario.", "warn")
                return
            self.log_widget.log("Desinstalando dependencias...", "warn")
            self.status_bar.showMessage("Desinstalando dependencias...", 3000)
            try:
                uninstall_dependencies()
                self.log_widget.log("Dependencias desinstaladas.", "ok")
                self.status_bar.showMessage("Dependencias desinstaladas correctamente.", 4000)
            except Exception as e:
                self.log_widget.log(f"Error al desinstalar dependencias: {e}", "err")
                self.status_bar.showMessage("Error al desinstalar dependencias.", 4000)

        def comandos_manuales(self):
            # Imprime en el log la misma información que la función CLI manual_command
            info = [
                "\nCrear Ambiente Virtual VENV:",
                "python -m venv .venv",
                "\nActivar Ambiente Virtual VENV:",
                ".\\.venv\\Scripts\\Activate",
                "\nDesactivar Ambiente Virtual VENV:",
                "deactivate",
                "\nVerificar y manejar Politica de Ejecucion de Scripts en PowerShell:",
                "Set-ExecutionPolicy (Restricted, AllSigned, RemoteSigned, Unrestricted)"
            ]
            for line in info:
                self.log_widget.log(line, "info")
            self.status_bar.showMessage("Comandos manuales listados en el log.", 4000)
            # ...sigue mostrando el panel de comandos para copiar...
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
