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

def uninstall_dependencies_selective():
    """Desinstala dependencias de forma selectiva, permitiendo al usuario elegir cuáles mantener."""
    print("\n🧹 === DESINSTALACIÓN SELECTIVA DE DEPENDENCIAS ===")
    
    # Verificar si existe el reporte, si no, generarlo
    if not os.path.exists('pyREPORT.txt'):
        print("⚠️ pyREPORT.txt no encontrado. Generando reporte automáticamente...")
        generate_report()
    
    try:
        with open('pyREPORT.txt', 'r', encoding='utf-8') as report_file:
            dependencies = [line.strip() for line in report_file.readlines() if line.strip()]
    except Exception as e:
        print(f"❌ Error al leer pyREPORT.txt: {e}")
        return
    
    if not dependencies:
        print("ℹ️ No se encontraron dependencias instaladas.")
        return
    
    print(f"\n📦 Se encontraron {len(dependencies)} dependencias instaladas:")
    print("=" * 60)
    
    # Mostrar dependencias con numeración
    packages_to_uninstall = []
    for i, dep in enumerate(dependencies, 1):
        package_name = dep.split('==')[0] if '==' in dep else dep.split('>=')[0] if '>=' in dep else dep
        print(f"{i:3d}. {dep}")
    
    print("\n" + "=" * 60)
    print("💡 Instrucciones:")
    print("   • Escribe los números de los paquetes que DESEAS DESINSTALAR")
    print("   • Separa múltiples números con espacios o comas")
    print("   • Ejemplo: 1 3 5-8 10  (desinstala paquetes 1, 3, del 5 al 8, y 10)")
    print("   • Escribe 'todos' para seleccionar todas las dependencias")
    print("   • Presiona Enter sin escribir nada para cancelar")
    
    while True:
        try:
            selection = input("\n🎯 Selecciona los paquetes a desinstalar: ").strip()
            
            if not selection:
                print("❌ Operación cancelada por el usuario.")
                return
            
            if selection.lower() in ['todos', 'all', 'todo']:
                selected_indices = list(range(1, len(dependencies) + 1))
                break
            
            # Parsear la selección
            selected_indices = []
            parts = selection.replace(',', ' ').split()
            
            for part in parts:
                if '-' in part and part.count('-') == 1:
                    # Rango (ej: 5-8)
                    try:
                        start, end = map(int, part.split('-'))
                        if 1 <= start <= len(dependencies) and 1 <= end <= len(dependencies) and start <= end:
                            selected_indices.extend(range(start, end + 1))
                        else:
                            raise ValueError()
                    except ValueError:
                        print(f"❌ Rango inválido: {part}")
                        continue
                else:
                    # Número individual
                    try:
                        num = int(part)
                        if 1 <= num <= len(dependencies):
                            selected_indices.append(num)
                        else:
                            print(f"❌ Número fuera de rango: {num}")
                    except ValueError:
                        print(f"❌ Entrada inválida: {part}")
            
            # Eliminar duplicados y ordenar
            selected_indices = sorted(set(selected_indices))
            
            if not selected_indices:
                print("❌ No se seleccionaron paquetes válidos. Intente nuevamente.")
                continue
            
            break
            
        except KeyboardInterrupt:
            print("\n❌ Operación cancelada por el usuario.")
            return
    
    # Mostrar paquetes seleccionados
    print(f"\n✅ Paquetes seleccionados para desinstalar ({len(selected_indices)}):")
    print("-" * 50)
    for idx in selected_indices:
        dep = dependencies[idx - 1]
        package_name = dep.split('==')[0] if '==' in dep else dep.split('>=')[0] if '>=' in dep else dep
        packages_to_uninstall.append(package_name)
        print(f"   🗑️  {dep}")
    
    # Confirmación final
    print("-" * 50)
    while True:
        confirm = input("¿Confirma la desinstalación de estos paquetes? (sí/s/yes/y | no/n): ").strip().lower()
        if confirm in ['sí', 'si', 's', 'yes', 'y']:
            break
        elif confirm in ['no', 'n']:
            print("❌ Operación cancelada por el usuario.")
            return
        else:
            print("❌ Respuesta inválida. Use 'sí' o 'no'.")
    
    # Ejecutar desinstalación
    print(f"\n🚀 Iniciando desinstalación de {len(packages_to_uninstall)} paquetes...")
    print("=" * 60)
    
    failed_packages = []
    successful_packages = []
    
    for i, package in enumerate(packages_to_uninstall, 1):
        try:
            print(f"[{i}/{len(packages_to_uninstall)}] Desinstalando {package}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'uninstall', '-y', package], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"   ✅ {package} desinstalado correctamente")
                successful_packages.append(package)
            else:
                print(f"   ❌ Error al desinstalar {package}: {result.stderr.strip()}")
                failed_packages.append(package)
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout al desinstalar {package}")
            failed_packages.append(package)
        except Exception as e:
            print(f"   ❌ Error inesperado al desinstalar {package}: {e}")
            failed_packages.append(package)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DESINSTALACIÓN:")
    print(f"   ✅ Exitosos: {len(successful_packages)}")
    print(f"   ❌ Fallidos: {len(failed_packages)}")
    
    if successful_packages:
        print(f"\n✅ Paquetes desinstalados correctamente:")
        for pkg in successful_packages:
            print(f"   • {pkg}")
    
    if failed_packages:
        print(f"\n❌ Paquetes que no pudieron desinstalarse:")
        for pkg in failed_packages:
            print(f"   • {pkg}")
        print("\n💡 Sugerencia: Intente desinstalar manualmente los paquetes fallidos.")
    
    print("\n🔄 Regenerando reporte de dependencias...")
    generate_report()
    print("✅ uninstall_dependencies_selective() ejecutado correctamente.")

def check_environment():
    subprocess.run([sys.executable, '-m', 'pip', 'list'])
    print("check_environment() ejecutado correctamente.")

def execute_activator():
    mensaje = (
        "ℹ️ La activación del entorno virtual solo afecta al terminal externo. "
        "Las operaciones posteriores se ejecutarán en ese terminal. "
        "La consola embebida no puede cambiar el entorno Python activo de la app. "
        "Por favor, continúe en el terminal externo para trabajar con el venv activado."
    )
    print(mensaje)
    result = subprocess.run(['powershell', '-File', 'Activador-VENV.ps1'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
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
        print("3. Desinstalar dependencias de Python (Todas)")
        print("4. Desinstalar dependencias de Python (Selectivo)")
        print("5. Verificar Entorno de Python")
        print("6. Comando Manual")
        print("7. Salir")
        choice = input("Elija una opción: ")
        if choice == '1':
            execute_activator()
        elif choice == '2':
            generate_report()
        elif choice == '3':
            uninstall_dependencies()
        elif choice == '4':
            uninstall_dependencies_selective()
        elif choice == '5':
            check_environment()
        elif choice == '6':
            manual_command()
        elif choice == '7':
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
    import signal
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

    class PackageSelectionDialog(QDialog):
        def __init__(self, packages, parent=None):
            super().__init__(parent)
            self.packages = packages
            self.selected_packages = []
            self.init_ui()
            
        def init_ui(self):
            self.setWindowTitle("🧹 Selección de Paquetes para Desinstalar")
            self.setModal(True)
            self.resize(700, 500)
            
            layout = QVBoxLayout()
            
            # Header con información
            header = QLabel(f"📦 Se encontraron {len(self.packages)} paquetes instalados")
            header.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3; padding: 10px;")
            layout.addWidget(header)
            
            # Instrucciones
            instructions = QLabel(
                "💡 Selecciona los paquetes que DESEAS DESINSTALAR.\n"
                "   Los paquetes no seleccionados permanecerán instalados."
            )
            instructions.setStyleSheet("color: #FFA726; padding: 5px; background: #2A2A2A; border-radius: 5px;")
            layout.addWidget(instructions)
            
            # Controles de selección
            controls_layout = QHBoxLayout()
            self.btn_select_all = QPushButton("✅ Seleccionar Todos")
            self.btn_select_none = QPushButton("❌ Deseleccionar Todos")
            self.btn_select_all.clicked.connect(self.select_all)
            self.btn_select_none.clicked.connect(self.select_none)
            
            controls_layout.addWidget(self.btn_select_all)
            controls_layout.addWidget(self.btn_select_none)
            controls_layout.addStretch()
            
            # Filtro de búsqueda
            self.filter_input = QLineEdit()
            self.filter_input.setPlaceholderText("🔍 Buscar paquetes...")
            self.filter_input.textChanged.connect(self.filter_packages)
            controls_layout.addWidget(QLabel("Filtro:"))
            controls_layout.addWidget(self.filter_input)
            
            layout.addLayout(controls_layout)
            
            # Lista de paquetes con checkboxes
            self.package_list = QTableWidget()
            self.package_list.setColumnCount(3)
            self.package_list.setHorizontalHeaderLabels(["Seleccionar", "Paquete", "Versión"])
            self.package_list.horizontalHeader().setStretchLastSection(True)
            self.package_list.setAlternatingRowColors(True)
            self.package_list.setSelectionBehavior(QTableWidget.SelectRows)
            
            self.populate_package_list()
            layout.addWidget(self.package_list)
            
            # Contador de seleccionados
            self.selection_label = QLabel("📊 Seleccionados: 0 paquetes")
            self.selection_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
            layout.addWidget(self.selection_label)
            
            # Botones de acción
            button_layout = QHBoxLayout()
            self.btn_ok = QPushButton("🗑️ Desinstalar Seleccionados")
            self.btn_cancel = QPushButton("❌ Cancelar")
            
            self.btn_ok.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 8px;")
            self.btn_cancel.setStyleSheet("background-color: #757575; color: white; padding: 8px;")
            
            self.btn_ok.clicked.connect(self.accept_selection)
            self.btn_cancel.clicked.connect(self.reject)
            
            button_layout.addStretch()
            button_layout.addWidget(self.btn_ok)
            button_layout.addWidget(self.btn_cancel)
            
            layout.addLayout(button_layout)
            self.setLayout(layout)
            
        def populate_package_list(self):
            self.package_list.setRowCount(len(self.packages))
            self.checkboxes = []
            
            for i, package in enumerate(self.packages):
                # Checkbox
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(self.update_selection_count)
                self.checkboxes.append(checkbox)
                self.package_list.setCellWidget(i, 0, checkbox)
                
                # Parsear nombre y versión
                if '==' in package:
                    name, version = package.split('==', 1)
                elif '>=' in package:
                    name, version = package.split('>=', 1)
                    version = f">= {version}"
                else:
                    name, version = package, "N/A"
                
                # Nombre del paquete
                name_item = QTableWidgetItem(name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.package_list.setItem(i, 1, name_item)
                
                # Versión
                version_item = QTableWidgetItem(version)
                version_item.setFlags(version_item.flags() & ~Qt.ItemIsEditable)
                self.package_list.setItem(i, 2, version_item)
            
            self.package_list.resizeColumnsToContents()
            self.package_list.setColumnWidth(0, 100)
            
        def filter_packages(self):
            filter_text = self.filter_input.text().lower()
            for i in range(self.package_list.rowCount()):
                package_name = self.package_list.item(i, 1).text().lower()
                should_show = filter_text in package_name
                self.package_list.setRowHidden(i, not should_show)
                
        def select_all(self):
            for checkbox in self.checkboxes:
                if not self.package_list.isRowHidden(self.checkboxes.index(checkbox)):
                    checkbox.setChecked(True)
                    
        def select_none(self):
            for checkbox in self.checkboxes:
                checkbox.setChecked(False)
                
        def update_selection_count(self):
            count = sum(1 for cb in self.checkboxes if cb.isChecked())
            self.selection_label.setText(f"📊 Seleccionados: {count} paquetes")
            self.btn_ok.setEnabled(count > 0)
            
        def accept_selection(self):
            self.selected_packages = []
            for i, checkbox in enumerate(self.checkboxes):
                if checkbox.isChecked():
                    package = self.packages[i]
                    # Extraer solo el nombre del paquete
                    package_name = package.split('==')[0] if '==' in package else package.split('>=')[0] if '>=' in package else package
                    self.selected_packages.append(package_name)
            
            if not self.selected_packages:
                QMessageBox.warning(self, "Advertencia", "No has seleccionado ningún paquete para desinstalar.")
                return
                
            # Confirmación final
            reply = QMessageBox.question(
                self, 
                "Confirmación de Desinstalación",
                f"¿Estás seguro de que deseas desinstalar {len(self.selected_packages)} paquetes?\n\n"
                f"Paquetes seleccionados:\n" + "\n".join(f"• {pkg}" for pkg in self.selected_packages[:10]) + 
                (f"\n... y {len(self.selected_packages) - 10} más" if len(self.selected_packages) > 10 else ""),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.accept()
            
        def get_selected_packages(self):
            return self.selected_packages

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

    class MoveCornerWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setCursor(Qt.SizeAllCursor)
            self._drag_active = False
            self._drag_pos = None
        def paintEvent(self, event):
            from PySide6.QtGui import QPainter, QPolygon, QColor
            painter = QPainter(self)
            # Triángulo visual, color azul claro
            points = [
                self.rect().bottomLeft(),
                self.rect().topLeft(),
                self.rect().bottomRight()
            ]
            triangle = QPolygon(points)
            painter.setBrush(QColor("#4FC3F7"))
            painter.setPen(QColor("#1976D2"))
            painter.drawPolygon(triangle)
        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton:
                self._drag_active = True
                self._drag_pos = event.globalPosition().toPoint()
                self._win_pos = self.window().pos()
        def mouseMoveEvent(self, event):
            if self._drag_active:
                delta = event.globalPosition().toPoint() - self._drag_pos
                self.window().move(self._win_pos + delta)
        def mouseReleaseEvent(self, event):
            self._drag_active = False

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("py-cleaner GUI")
            self.setWindowIcon(QIcon())
            self.resize(900, 600)
            # Ventana borderless
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.log_widget = LogWidget()
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.init_ui()
            self.entorno_activo = "local"  # Puede ser 'local', 'global', 'externo'
            self.python_local = sys.executable
            self.python_externo = None
            self.update_env_indicators()
            # Botón exportar log
            self.btn_export_log = QPushButton("💾 Exportar Log")
            self.status_bar.addPermanentWidget(self.btn_export_log)
            self.btn_export_log.clicked.connect(self.exportar_log)
            # Botón salir seguro
            self.btn_salir.clicked.connect(self.cerrar_seguro)
            # Triángulo para mover ventana en esquina inferior izquierda
            self.move_corner = MoveCornerWidget(self)
            self.move_corner.setFixedSize(24, 24)
            self.move_corner.setStyleSheet("background: transparent;")
            self.move_corner.setToolTip("Arrastra para mover la ventana")
            self.move_corner.raise_()
            self.move_corner.show()

        def resizeEvent(self, event):
            super().resizeEvent(event)
            # Posiciona el triángulo en la esquina inferior izquierda
            self.move_corner.move(0, self.height() - self.move_corner.height())

        def cerrar_seguro(self):
            try:
                # Aquí podrías cerrar conexiones, guardar logs, liberar recursos, etc.
                self.log_widget.log("Cerrando la aplicación de forma segura...", "info")
                self.status_bar.showMessage("Cerrando la aplicación...", 2000)
                QApplication.quit()
            except Exception as e:
                self.log_widget.log(f"Error al cerrar: {e}", "err")
                self.status_bar.showMessage("Error al cerrar la aplicación.", 4000)

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
            self.btn_uninstall = QPushButton("🧹 Desinstalar Todo")
            self.btn_uninstall_selective = QPushButton("🎯 Desinstalar Selectivo")
            self.btn_check = QPushButton("🔍 Verificar Entorno")
            self.btn_manual = QPushButton("🛠️ Comandos Manuales")
            self.btn_salir = QPushButton("🚪 Salir")
            
            # Organizar botones en dos filas para mejor distribución
            btn_layout1 = QHBoxLayout()
            btn_layout2 = QHBoxLayout()
            
            for btn in [self.btn_crear_venv, self.btn_activador, self.btn_reporte, self.btn_check]:
                btn.setMinimumHeight(40)
                btn_layout1.addWidget(btn)
                
            for btn in [self.btn_uninstall, self.btn_uninstall_selective, self.btn_manual, self.btn_salir]:
                btn.setMinimumHeight(40)
                btn_layout2.addWidget(btn)
                
            main_layout.addLayout(btn_layout1)
            main_layout.addLayout(btn_layout2)

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
            self.btn_reporte.clicked.connect(self.generar_reporte)
            self.btn_uninstall.clicked.connect(self.desinstalar_dependencias)
            self.btn_uninstall_selective.clicked.connect(self.desinstalar_dependencias_selectivo)
            self.btn_check.clicked.connect(self.verificar_entorno)
            self.btn_manual.clicked.connect(self.comandos_manuales)
            self.btn_salir.clicked.connect(self.close)
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
            self.activar_venv()

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
            mensaje = (
                "ℹ️ La creación del entorno virtual solo afecta al terminal externo. "
                "Las operaciones posteriores se ejecutarán en ese terminal. "
                "La consola embebida no puede cambiar el entorno Python activo de la app. "
                "Por favor, continúe en el terminal externo para trabajar con el venv creado."
            )
            self.log_widget.log(mensaje, "warn")
            self.status_bar.showMessage("Limitación: creación solo en terminal externo.", 6000)
            try:
                self.tab_console.console.appendPlainText(mensaje)
                self.tab_console.send_command_from_gui(f"powershell -File Creador-VENV.ps1")
                self.log_widget.log("Script de creación ejecutado.", "ok")
                self.status_bar.showMessage("VENV creado correctamente.", 4000)
                self.update_env_indicators()
            except Exception as e:
                self.log_widget.log(f"Error al crear VENV: {e}", "err")
                self.status_bar.showMessage("Error al crear VENV.", 4000)
                self.update_env_indicators()

        def activar_venv(self):
            reply = QMessageBox.question(self, "Confirmación", "¿Seguro que deseas activar el VENV local?", QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                self.status_bar.showMessage("Activación de VENV cancelada.", 3000)
                self.log_widget.log("Activación de VENV cancelada por el usuario.", "warn")
                return
            mensaje = (
                "ℹ️ La activación del entorno virtual solo afecta al terminal externo. "
                "Las operaciones posteriores se ejecutarán en ese terminal. "
                "La consola embebida no puede cambiar el entorno Python activo de la app. "
                "Por favor, continúe en el terminal externo para trabajar con el venv activado."
            )
            self.log_widget.log(mensaje, "warn")
            self.status_bar.showMessage("Limitación: activación solo en terminal externo.", 6000)
            try:
                self.tab_console.console.appendPlainText(mensaje)
                self.tab_console.send_command_from_gui(f"powershell -File Activador-VENV.ps1")
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

        def desinstalar_dependencias_selectivo(self):
            """Desinstala dependencias de forma selectiva usando un diálogo interactivo."""
            self.log_widget.log("Iniciando desinstalación selectiva de dependencias...", "info")
            self.status_bar.showMessage("Preparando lista de paquetes...", 3000)
            
            # Obtener lista de paquetes instalados
            try:
                result = subprocess.run(
                    [self.tab_console.current_python, '-m', 'pip', 'freeze'], 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.log_widget.log(f"Error al obtener lista de paquetes: {result.stderr}", "err")
                    self.status_bar.showMessage("Error al obtener lista de paquetes.", 4000)
                    QMessageBox.warning(self, "Error", "No se pudo obtener la lista de paquetes instalados.")
                    return
                
                packages = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                
                if not packages:
                    self.log_widget.log("No se encontraron paquetes instalados.", "warn")
                    self.status_bar.showMessage("No hay paquetes instalados.", 4000)
                    QMessageBox.information(self, "Información", "No se encontraron paquetes instalados en el entorno actual.")
                    return
                
                self.log_widget.log(f"Se encontraron {len(packages)} paquetes instalados.", "info")
                
            except subprocess.TimeoutExpired:
                self.log_widget.log("Timeout al obtener la lista de paquetes.", "err")
                self.status_bar.showMessage("Timeout al obtener lista de paquetes.", 4000)
                QMessageBox.warning(self, "Error", "Se agotó el tiempo de espera al obtener la lista de paquetes.")
                return
            except Exception as e:
                self.log_widget.log(f"Error inesperado al obtener paquetes: {e}", "err")
                self.status_bar.showMessage("Error inesperado.", 4000)
                QMessageBox.critical(self, "Error", f"Error inesperado: {e}")
                return
            
            # Mostrar diálogo de selección
            dialog = PackageSelectionDialog(packages, self)
            
            if dialog.exec() == QDialog.Accepted:
                selected_packages = dialog.get_selected_packages()
                
                if not selected_packages:
                    self.log_widget.log("No se seleccionaron paquetes para desinstalar.", "warn")
                    self.status_bar.showMessage("Operación cancelada - Sin selección.", 3000)
                    return
                
                self.log_widget.log(f"Iniciando desinstalación de {len(selected_packages)} paquetes seleccionados.", "warn")
                self.status_bar.showMessage(f"Desinstalando {len(selected_packages)} paquetes...", 5000)
                
                # Ejecutar desinstalación
                failed_packages = []
                successful_packages = []
                
                for i, package in enumerate(selected_packages, 1):
                    try:
                        self.log_widget.log(f"[{i}/{len(selected_packages)}] Desinstalando {package}...", "info")
                        
                        result = subprocess.run(
                            [self.tab_console.current_python, '-m', 'pip', 'uninstall', '-y', package],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if result.returncode == 0:
                            self.log_widget.log(f"✅ {package} desinstalado correctamente", "ok")
                            successful_packages.append(package)
                        else:
                            error_msg = result.stderr.strip() or "Error desconocido"
                            self.log_widget.log(f"❌ Error al desinstalar {package}: {error_msg}", "err")
                            failed_packages.append(package)
                            
                    except subprocess.TimeoutExpired:
                        self.log_widget.log(f"⏰ Timeout al desinstalar {package}", "err")
                        failed_packages.append(package)
                    except Exception as e:
                        self.log_widget.log(f"❌ Error inesperado al desinstalar {package}: {e}", "err")
                        failed_packages.append(package)
                
                # Mostrar resumen
                self.log_widget.log("=" * 50, "info")
                self.log_widget.log(f"📊 RESUMEN: Exitosos: {len(successful_packages)} | Fallidos: {len(failed_packages)}", "info")
                
                if successful_packages:
                    self.log_widget.log(f"✅ Paquetes desinstalados: {', '.join(successful_packages)}", "ok")
                    
                if failed_packages:
                    self.log_widget.log(f"❌ Paquetes fallidos: {', '.join(failed_packages)}", "err")
                
                # Mostrar notificación final
                if failed_packages:
                    QMessageBox.warning(
                        self, 
                        "Desinstalación Completada con Errores",
                        f"Desinstalación completada:\n\n"
                        f"✅ Exitosos: {len(successful_packages)}\n"
                        f"❌ Fallidos: {len(failed_packages)}\n\n"
                        f"Revisa el log para más detalles."
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Desinstalación Exitosa",
                        f"¡Todos los {len(successful_packages)} paquetes fueron desinstalados correctamente!"
                    )
                
                self.status_bar.showMessage("Desinstalación selectiva completada.", 4000)
                
                # Regenerar reporte
                self.log_widget.log("🔄 Regenerando reporte de dependencias...", "info")
                self.generar_reporte()
                
            else:
                self.log_widget.log("Desinstalación selectiva cancelada por el usuario.", "warn")
                self.status_bar.showMessage("Operación cancelada.", 3000)

        def desinstalar_dependencias(self):
            """Desinstala todas las dependencias listadas en pyREPORT.txt."""
            reply = QMessageBox.question(
                self, 
                "Confirmación", 
                "¿Seguro que deseas desinstalar TODAS las dependencias listadas en pyREPORT.txt?", 
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                self.status_bar.showMessage("Desinstalación cancelada.", 3000)
                self.log_widget.log("Desinstalación de dependencias cancelada por el usuario.", "warn")
                return
                
            self.log_widget.log("Desinstalando todas las dependencias...", "warn")
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
    # Manejo de cierre por Ctrl+C
    def cerrar_por_ctrl_c(sig, frame):
        window.cerrar_seguro()
    signal.signal(signal.SIGINT, cerrar_por_ctrl_c)
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
