# --- CLI Moderno con Rich ---
import os
import subprocess
import sys
import signal
from typing import List, Optional, Tuple
from pathlib import Path
import time

# Rich imports para interfaz moderna
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich.text import Text
from rich import box
from rich.rule import Rule
from rich.tree import Tree
from rich.syntax import Syntax
from rich.markdown import Markdown

# Configuración de consola
console = Console()

# --- Gestión de Ambientes ---
class EnvironmentManager:
    """Clase para gestionar diferentes ambientes de Python de forma segura."""
    
    def __init__(self):
        self.current_env = "system"  # system, local_venv, external_venv
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
    
    def switch_to_system(self):
        """Cambia al ambiente sistema/global."""
        self.current_env = "system"
        self.python_executable = sys.base_prefix + ("/python.exe" if os.name == 'nt' else "/bin/python")
        console.print("[bold yellow]⚠️ Cambiado a ambiente SISTEMA/GLOBAL[/bold yellow]")
        return True
    
    def switch_to_local_venv(self) -> bool:
        """Cambia al venv local (.venv en directorio actual)."""
        local_venv_path = os.path.join(os.getcwd(), ".venv")
        
        if os.name == 'nt':  # Windows
            python_exe = os.path.join(local_venv_path, "Scripts", "python.exe")
        else:  # Unix/Linux/Mac
            python_exe = os.path.join(local_venv_path, "bin", "python")
            
        if os.path.exists(python_exe):
            self.current_env = "local_venv"
            self.venv_path = local_venv_path
            self.python_executable = python_exe
            console.print(f"[bold green]✅ Cambiado a VENV LOCAL: {local_venv_path}[/bold green]")
            return True
        else:
            console.print(f"[bold red]❌ No se encontró VENV local en: {local_venv_path}[/bold red]")
            return False
    
    def switch_to_external_venv(self, venv_path: str) -> bool:
        """Cambia a un venv externo especificado."""
        if not os.path.exists(venv_path):
            console.print(f"[bold red]❌ Ruta de VENV no existe: {venv_path}[/bold red]")
            return False
            
        if os.name == 'nt':  # Windows
            python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        else:  # Unix/Linux/Mac
            python_exe = os.path.join(venv_path, "bin", "python")
            
        if os.path.exists(python_exe):
            self.current_env = "external_venv"
            self.external_venv_path = venv_path
            self.python_executable = python_exe
            console.print(f"[bold green]✅ Cambiado a VENV EXTERNO: {venv_path}[/bold green]")
            return True
        else:
            console.print(f"[bold red]❌ No se encontró Python ejecutable en: {python_exe}[/bold red]")
            return False

# Instancia global del gestor de ambientes
env_manager = EnvironmentManager()

def is_venv_active() -> bool:
    """Verifica si un entorno virtual está activo."""
    return env_manager.detect_environment()["is_venv"]

def show_environment_status():
    """Muestra el estado actual del entorno de Python con estilo mejorado."""
    env_info = env_manager.detect_environment()
    
    # Mapeo de tipos de ambiente con emojis y colores
    env_types = {
        "system": ("🌐 AMBIENTE SISTEMA/GLOBAL", "red"),
        "local_venv": ("🔴 VENV LOCAL (.venv)", "green"), 
        "external_venv": ("🟠 VENV EXTERNO", "yellow")
    }
    
    env_type_display, env_color = env_types.get(env_info["env_type"], ("❓ DESCONOCIDO", "white"))
    
    env_table = Table(show_header=False, box=box.ROUNDED, border_style="bright_blue")
    env_table.add_column("Atributo", style="bold cyan", width=20)
    env_table.add_column("Valor", style="bright_white")
    
    env_table.add_row("🐍 Intérprete Python", env_info["python_version"])
    env_table.add_row("📍 Ubicación Ejecutable", env_info["python_executable"])
    env_table.add_row("🌍 Tipo de Ambiente", f"[{env_color}]{env_type_display}[/{env_color}]")
    env_table.add_row("📁 Directorio Actual", env_info["current_dir"])
    
    # Información adicional según el tipo de ambiente
    if env_info["env_type"] == "local_venv":
        env_table.add_row("📂 Ruta VENV Local", env_info["venv_path"] or "No detectado")
    elif env_info["env_type"] == "external_venv":
        env_table.add_row("📂 Ruta VENV Externo", env_info["venv_path"] or "No detectado")
    elif env_info["env_type"] == "system":
        env_table.add_row("⚠️ Advertencia", "[bold red]Trabajando en ambiente GLOBAL[/bold red]")
    
    # Información de VIRTUAL_ENV si está disponible
    if env_info["virtual_env"]:
        env_table.add_row("🔗 VIRTUAL_ENV", env_info["virtual_env"])
    
    # Gestor de ambiente activo
    env_table.add_row("⚙️ Gestor Activo", f"[bold cyan]{env_manager.current_env}[/bold cyan]")
    env_table.add_row("🔧 PIP Ejecutable", env_manager.get_pip_executable())
    
    console.print(Panel(
        env_table,
        title="[bold bright_blue]🔍 Estado del Entorno Python[/bold bright_blue]",
        border_style="bright_blue"
    ))
    
    # Advertencia de seguridad si está en ambiente global
    if env_info["env_type"] == "system":
        warning_text = Text()
        warning_text.append("⚠️ ADVERTENCIA: ", style="bold red")
        warning_text.append("Está trabajando en el ambiente GLOBAL de Python. ", style="yellow")
        warning_text.append("Se recomienda usar un entorno virtual para evitar conflictos.", style="yellow")
        
        console.print(Panel(
            warning_text,
            title="[bold red]🚨 Alerta de Seguridad[/bold red]",
            border_style="red"
        ))

def generate_report() -> bool:
    """Genera un reporte de dependencias instaladas con interfaz moderna y ambiente correcto."""
    env_info = env_manager.detect_environment()
    pip_executable = env_manager.get_pip_executable()
    
    with console.status(f"[bold green]📊 Generando reporte de dependencias ({env_info['env_type']})...", spinner="dots"):
        try:
            # Mostrar información del ambiente antes de generar el reporte
            console.print(f"[dim]🔧 Usando: {pip_executable}[/dim]")
            
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
                
                console.print(Panel(
                    f"[bold green]✅ Reporte generado exitosamente[/bold green]\n\n"
                    f"📄 Archivo: [bold cyan]pyREPORT.txt[/bold cyan]\n"
                    f"📦 Dependencias encontradas: [bold yellow]{deps_count}[/bold yellow]\n"
                    f"🌍 Ambiente: [bold cyan]{env_info['env_type'].upper()}[/bold cyan]\n"
                    f"🐍 Python: [bold green]{env_info['python_version']}[/bold green]",
                    title="[bold green]📊 Reporte de Dependencias[/bold green]",
                    border_style="green"
                ))
                return True
            else:
                console.print(Panel(
                    f"[bold red]❌ Error al generar reporte[/bold red]\n\n"
                    f"[red]Error: {result.stderr}[/red]\n"
                    f"[yellow]Ambiente: {env_info['env_type']}[/yellow]\n"
                    f"[yellow]Ejecutable: {pip_executable}[/yellow]",
                    title="[bold red]⚠️ Error[/bold red]",
                    border_style="red"
                ))
                return False
                
        except subprocess.TimeoutExpired:
            console.print(f"[bold red]⏰ Timeout al generar reporte desde {env_info['env_type']}[/bold red]")
            return False
        except Exception as e:
            console.print(f"[bold red]❌ Error inesperado: {e}[/bold red]")
            console.print(f"[dim]Ambiente: {env_info['env_type']}, Ejecutable: {pip_executable}[/dim]")
            return False

def show_packages_table(packages: List[str]) -> None:
    """Muestra una tabla estilizada de paquetes instalados."""
    if not packages:
        console.print(Panel(
            "[yellow]ℹ️ No se encontraron dependencias instaladas[/yellow]",
            title="[bold yellow]📦 Dependencias[/bold yellow]",
            border_style="yellow"
        ))
        return
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("📦 Paquete", style="cyan", no_wrap=True)
    table.add_column("📌 Versión", style="green")
    table.add_column("📊 Estado", justify="center")
    
    for i, package in enumerate(packages):
        if '==' in package:
            name, version = package.split('==', 1)
            status = "✅ Instalado"
        elif '>=' in package:
            name, version = package.split('>=', 1)
            version = f">= {version}"
            status = "⚠️ Rango"
        else:
            name, version = package, "N/A"
            status = "❓ Desconocido"
        
        # Alternar colores de fila
        style = "on dark_blue" if i % 2 == 0 else ""
        table.add_row(name, version, status, style=style)
    
    console.print(Panel(
        table,
        title=f"[bold cyan]📦 Dependencias Instaladas ({len(packages)})[/bold cyan]",
        border_style="cyan"
    ))

def parse_selection(selection: str, max_num: int) -> List[int]:
    """Parsea la selección del usuario y retorna lista de índices válidos."""
    if not selection or not selection.strip():
        return []
    
    selection = selection.strip().lower()
    
    # Casos especiales
    if selection in ['todos', 'all', 'todo', '*']:
        return list(range(1, max_num + 1))
    
    selected_indices = []
    parts = selection.replace(',', ' ').split()
    
    for part in parts:
        try:
            if '-' in part and part.count('-') == 1:
                # Rango (ej: 5-8)
                start, end = map(int, part.split('-'))
                if 1 <= start <= max_num and 1 <= end <= max_num and start <= end:
                    selected_indices.extend(range(start, end + 1))
                else:
                    console.print(f"[yellow]⚠️ Rango inválido: {part}[/yellow]")
            else:
                # Número individual
                num = int(part)
                if 1 <= num <= max_num:
                    selected_indices.append(num)
                else:
                    console.print(f"[yellow]⚠️ Número fuera de rango: {num}[/yellow]")
        except ValueError:
            console.print(f"[red]❌ Entrada inválida: {part}[/red]")
    
    # Eliminar duplicados y ordenar
    return sorted(set(selected_indices))

def uninstall_dependencies():
    """Desinstala todas las dependencias de forma masiva con verificaciones de seguridad."""
    console.print(Rule("[bold red]🧹 DESINSTALACIÓN MASIVA DE DEPENDENCIAS[/bold red]"))
    
    # Verificar ambiente actual y mostrar advertencia
    env_info = env_manager.detect_environment()
    pip_executable = env_manager.get_pip_executable()
    
    # Advertencia especial para ambiente global
    if env_info["env_type"] == "system":
        warning_panel = Panel(
            "[bold red]🚨 PELIGRO - AMBIENTE GLOBAL DETECTADO 🚨[/bold red]\n\n"
            "[yellow]Está a punto de desinstalar paquetes del ambiente GLOBAL de Python.\n"
            "Esto puede ROMPER su instalación de Python y otras aplicaciones.[/yellow]\n\n"
            "[bold cyan]Recomendación: Cambie a un entorno virtual antes de continuar.[/bold cyan]\n\n"
            f"[dim]Ambiente: {env_info['env_type']}\n"
            f"Ejecutable: {pip_executable}[/dim]",
            title="[bold red]⚠️ ADVERTENCIA CRÍTICA[/bold red]",
            border_style="red"
        )
        console.print(warning_panel)
        
        if not Confirm.ask("[bold red]¿ESTÁ SEGURO de continuar con el ambiente GLOBAL?[/bold red]"):
            console.print("[yellow]✅ Operación cancelada por seguridad.[/yellow]")
            return
    
    # Mostrar información del ambiente actual
    console.print(Panel(
        f"[bold cyan]🔧 Ambiente de trabajo:[/bold cyan] [yellow]{env_info['env_type'].upper()}[/yellow]\n"
        f"[bold cyan]🐍 Python:[/bold cyan] [green]{env_info['python_version']}[/green]\n"
        f"[bold cyan]📍 Ejecutable:[/bold cyan] [dim]{pip_executable}[/dim]",
        title="[bold blue]📋 Información del Ambiente[/bold blue]",
        border_style="blue"
    ))
    
    if not os.path.exists('pyREPORT.txt'):
        console.print("[yellow]⚠️ pyREPORT.txt no encontrado.[/yellow]")
        if Confirm.ask("¿Desea generar el reporte automáticamente?"):
            if not generate_report():
                return
        else:
            return
    
    try:
        with open('pyREPORT.txt', 'r', encoding='utf-8') as report_file:
            content = report_file.read()
            
        # Filtrar solo las líneas de dependencias (no comentarios)
        dependencies = [line.strip() for line in content.split('\n') 
                       if line.strip() and not line.startswith('#')]
    except Exception as e:
        console.print(f"[bold red]❌ Error al leer pyREPORT.txt: {e}[/bold red]")
        return
    
    if not dependencies:
        console.print("[yellow]ℹ️ No se encontraron dependencias instaladas.[/yellow]")
        return
    
    # Mostrar tabla de dependencias
    show_packages_table(dependencies)
    
    # Confirmación con advertencia
    warning_panel = Panel(
        "[bold red]⚠️ CONFIRMACIÓN FINAL ⚠️[/bold red]\n\n"
        "[yellow]Esta operación desinstalará TODAS las dependencias mostradas.\n"
        "Esta acción NO se puede deshacer.[/yellow]\n\n"
        f"[cyan]Total de paquetes a desinstalar: {len(dependencies)}[/cyan]\n"
        f"[cyan]Ambiente: {env_info['env_type'].upper()}[/cyan]\n"
        f"[cyan]Python: {env_info['python_version']}[/cyan]",
        title="[bold red]🚨 Confirmación Requerida[/bold red]",
        border_style="red"
    )
    console.print(warning_panel)
    
    if not Confirm.ask("[bold red]¿Confirma la desinstalación masiva?[/bold red]"):
        console.print("[yellow]❌ Operación cancelada por el usuario.[/yellow]")
        return
    
    # Ejecutar desinstalación con progreso
    console.print(Rule(f"[bold green]🚀 Iniciando Desinstalación Masiva en {env_info['env_type'].upper()}[/bold green]"))
    
    failed_packages = []
    successful_packages = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        
        task = progress.add_task("Desinstalando paquetes...", total=len(dependencies))
        
        for i, dep in enumerate(dependencies):
            package_name = dep.split('==')[0] if '==' in dep else dep.split('>=')[0] if '>=' in dep else dep
            progress.update(task, description=f"Desinstalando {package_name}...")
            
            try:
                result = subprocess.run(
                    [pip_executable, '-m', 'pip', 'uninstall', '-y', package_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    successful_packages.append(package_name)
                else:
                    failed_packages.append(package_name)
                    
            except subprocess.TimeoutExpired:
                failed_packages.append(package_name)
            except Exception:
                failed_packages.append(package_name)
            
            progress.advance(task)
    
    # Mostrar resumen final
    show_uninstall_summary(successful_packages, failed_packages)
    
    # Regenerar reporte
    console.print(Rule("[bold blue]🔄 Regenerando Reporte[/bold blue]"))
    generate_report()

def show_uninstall_summary(successful: List[str], failed: List[str]) -> None:
    """Muestra un resumen estilizado de la desinstalación."""
    summary_table = Table(show_header=True, header_style="bold magenta", box=box.DOUBLE_EDGE)
    summary_table.add_column("📊 Resultado", style="bold")
    summary_table.add_column("📈 Cantidad", justify="center", style="bold")
    summary_table.add_column("📦 Paquetes", style="dim")
    
    # Resultados exitosos
    success_list = ", ".join(successful[:5])
    if len(successful) > 5:
        success_list += f" ... y {len(successful) - 5} más"
    
    summary_table.add_row(
        "[green]✅ Exitosos[/green]",
        f"[green]{len(successful)}[/green]",
        f"[green]{success_list}[/green]" if successful else "[dim]Ninguno[/dim]"
    )
    
    # Resultados fallidos
    failed_list = ", ".join(failed[:5])
    if len(failed) > 5:
        failed_list += f" ... y {len(failed) - 5} más"
    
    summary_table.add_row(
        "[red]❌ Fallidos[/red]",
        f"[red]{len(failed)}[/red]",
        f"[red]{failed_list}[/red]" if failed else "[dim]Ninguno[/dim]"
    )
    
    # Mostrar panel de resumen
    success_rate = (len(successful) / (len(successful) + len(failed))) * 100 if (successful or failed) else 0
    
    console.print(Panel(
        summary_table,
        title=f"[bold cyan]📊 Resumen de Desinstalación (Éxito: {success_rate:.1f}%)[/bold cyan]",
        border_style="cyan"
    ))
    
    if failed:
        console.print(Panel(
            "[yellow]💡 Sugerencia: Intente desinstalar manualmente los paquetes fallidos o "
            "verifique si están siendo utilizados por otros procesos.[/yellow]",
            title="[bold yellow]💭 Recomendación[/bold yellow]",
            border_style="yellow"
        ))

def uninstall_dependencies_selective():
    """Desinstala dependencias de forma selectiva con interfaz Rich moderna y ambiente seguro."""
    console.print(Rule("[bold blue]🎯 DESINSTALACIÓN SELECTIVA DE DEPENDENCIAS[/bold blue]"))
    
    # Verificar ambiente actual y mostrar información
    env_info = env_manager.detect_environment()
    pip_executable = env_manager.get_pip_executable()
    
    # Advertencia para ambiente global
    if env_info["env_type"] == "system":
        warning_panel = Panel(
            "[bold red]⚠️ ADVERTENCIA - AMBIENTE GLOBAL[/bold red]\n\n"
            "[yellow]Está trabajando en el ambiente GLOBAL de Python.\n"
            "Tenga cuidado de no desinstalar paquetes críticos del sistema.[/yellow]\n\n"
            f"[dim]Ambiente: {env_info['env_type']}\n"
            f"Ejecutable: {pip_executable}[/dim]",
            title="[bold yellow]🚨 Precaución[/bold yellow]",
            border_style="yellow"
        )
        console.print(warning_panel)
    
    # Mostrar información del ambiente actual
    console.print(Panel(
        f"[bold cyan]🔧 Ambiente de trabajo:[/bold cyan] [yellow]{env_info['env_type'].upper()}[/yellow]\n"
        f"[bold cyan]🐍 Python:[/bold cyan] [green]{env_info['python_version']}[/green]\n"
        f"[bold cyan]📍 Ejecutable:[/bold cyan] [dim]{pip_executable}[/dim]",
        title="[bold blue]📋 Información del Ambiente[/bold blue]",
        border_style="blue"
    ))
    
    # Verificar si existe el reporte, si no, generarlo
    if not os.path.exists('pyREPORT.txt'):
        console.print("[yellow]⚠️ pyREPORT.txt no encontrado.[/yellow]")
        with console.status("[bold green]Generando reporte automáticamente...", spinner="dots"):
            if not generate_report():
                return
    
    try:
        with open('pyREPORT.txt', 'r', encoding='utf-8') as report_file:
            content = report_file.read()
            
        # Filtrar solo las líneas de dependencias (no comentarios)
        dependencies = [line.strip() for line in content.split('\n') 
                       if line.strip() and not line.startswith('#')]
    except Exception as e:
        console.print(f"[bold red]❌ Error al leer pyREPORT.txt: {e}[/bold red]")
        return
    
    if not dependencies:
        console.print(Panel(
            f"[yellow]ℹ️ No se encontraron dependencias instaladas en {env_info['env_type'].upper()}.[/yellow]",
            title="[bold yellow]📦 Estado[/bold yellow]",
            border_style="yellow"
        ))
        return
    
    # Mostrar dependencias con numeración en tabla moderna
    packages_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    packages_table.add_column("#", style="bold cyan", width=4, justify="right")
    packages_table.add_column("📦 Paquete", style="bright_white")
    packages_table.add_column("📌 Versión", style="green")
    packages_table.add_column("📊 Información", style="dim")
    
    for i, dep in enumerate(dependencies, 1):
        if '==' in dep:
            package_name, version = dep.split('==', 1)
            info = "Versión exacta"
        elif '>=' in dep:
            package_name, version = dep.split('>=', 1)
            version = f">= {version}"
            info = "Versión mínima"
        else:
            package_name = dep
            version = "N/A"
            info = "Sin versión"
        
        # Alternar colores
        style = "on dark_blue" if i % 2 == 0 else ""
        packages_table.add_row(str(i), package_name, version, info, style=style)
    
    console.print(Panel(
        packages_table,
        title=f"[bold cyan]📦 Dependencias en {env_info['env_type'].upper()} ({len(dependencies)})[/bold cyan]",
        border_style="cyan"
    ))
    
    # Panel de instrucciones modernas
    instructions_md = """
## 💡 Instrucciones de Selección

- **Números individuales:** `1 3 5` (desinstala paquetes 1, 3 y 5)
- **Rangos:** `1-5` o `10-15` (desinstala del 1 al 5, del 10 al 15)
- **Combinado:** `1 3 5-8 10` (desinstala 1, 3, del 5 al 8, y 10)
- **Todos:** `todos` o `all` o `*` (selecciona todos)
- **Cancelar:** Presiona `Enter` sin escribir nada

### 🎯 Ejemplos:
- `1 5 10` → Paquetes 1, 5 y 10
- `1-5` → Paquetes del 1 al 5
- `todos` → Todos los paquetes
    """
    
    console.print(Panel(
        Markdown(instructions_md),
        title="[bold yellow]📚 Guía de Uso[/bold yellow]",
        border_style="yellow"
    ))
    
    # Solicitar selección con prompt estilizado
    while True:
        try:
            selection = Prompt.ask(
                f"\n[bold cyan]🎯 Selecciona los paquetes a desinstalar de {env_info['env_type'].upper()}[/bold cyan]",
                default=""
            )
            
            if not selection:
                console.print("[yellow]❌ Operación cancelada por el usuario.[/yellow]")
                return
            
            selected_indices = parse_selection(selection, len(dependencies))
            
            if not selected_indices:
                console.print("[red]❌ No se seleccionaron paquetes válidos. Intente nuevamente.[/red]")
                continue
            
            break
            
        except KeyboardInterrupt:
            console.print("\n[yellow]❌ Operación cancelada por el usuario.[/yellow]")
            return
    
    # Mostrar paquetes seleccionados en tabla
    selected_table = Table(show_header=True, header_style="bold red", box=box.HEAVY)
    selected_table.add_column("🗑️ #", style="bold red", width=4)
    selected_table.add_column("📦 Paquete a Desinstalar", style="bright_white")
    selected_table.add_column("📌 Versión", style="yellow")
    
    packages_to_uninstall = []
    for idx in selected_indices:
        dep = dependencies[idx - 1]
        if '==' in dep:
            package_name, version = dep.split('==', 1)
        elif '>=' in dep:
            package_name, version = dep.split('>=', 1)
            version = f">= {version}"
        else:
            package_name = dep
            version = "N/A"
        
        packages_to_uninstall.append(package_name)
        selected_table.add_row(str(idx), package_name, version)
    
    console.print(Panel(
        selected_table,
        title=f"[bold red]🗑️ Paquetes Seleccionados para Desinstalación de {env_info['env_type'].upper()} ({len(packages_to_uninstall)})[/bold red]",
        border_style="red"
    ))
    
    # Confirmación final estilizada
    warning_text = Text()
    warning_text.append("⚠️ ADVERTENCIA: ", style="bold red")
    warning_text.append("Esta operación NO se puede deshacer.\n", style="yellow")
    warning_text.append(f"Se desinstalarán {len(packages_to_uninstall)} paquetes del ambiente {env_info['env_type'].upper()}.", style="cyan")
    
    console.print(Panel(
        Align.center(warning_text),
        title="[bold red]🚨 Confirmación Final[/bold red]",
        border_style="red"
    ))
    
    if not Confirm.ask(f"\n[bold red]¿Confirma la desinstalación de estos paquetes del {env_info['env_type'].upper()}?[/bold red]"):
        console.print("[yellow]❌ Operación cancelada por el usuario.[/yellow]")
        return
    
    # Ejecutar desinstalación con barra de progreso avanzada
    console.print(Rule(f"[bold green]🚀 Iniciando Desinstalación de {len(packages_to_uninstall)} Paquetes de {env_info['env_type'].upper()}[/bold green]"))
    
    failed_packages = []
    successful_packages = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("([cyan]{task.completed}[/cyan]/[cyan]{task.total}[/cyan])"),
    ) as progress:
        
        task = progress.add_task("Procesando...", total=len(packages_to_uninstall))
        
        for i, package in enumerate(packages_to_uninstall, 1):
            progress.update(task, description=f"[yellow]Desinstalando[/yellow] [bold]{package}[/bold]")
            
            try:
                result = subprocess.run(
                    [pip_executable, '-m', 'pip', 'uninstall', '-y', package], 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    successful_packages.append(package)
                    progress.update(task, description=f"[green]✅ {package}[/green]")
                else:
                    failed_packages.append(package)
                    progress.update(task, description=f"[red]❌ {package}[/red]")
                    
            except subprocess.TimeoutExpired:
                failed_packages.append(package)
                progress.update(task, description=f"[red]⏰ Timeout: {package}[/red]")
            except Exception:
                failed_packages.append(package)
                progress.update(task, description=f"[red]💥 Error: {package}[/red]")
            
            progress.advance(task)
            time.sleep(0.1)  # Pequeña pausa para mejor visualización
    
    # Mostrar resumen detallado
    show_uninstall_summary(successful_packages, failed_packages)
    
    # Regenerar reporte
    console.print(Rule("[bold blue]🔄 Regenerando Reporte de Dependencias[/bold blue]"))
    generate_report()
    
    console.print(f"[bold green]✅ uninstall_dependencies_selective() ejecutado correctamente en {env_info['env_type'].upper()}.[/bold green]")

def check_environment():
    """Verifica y muestra el entorno de Python con interfaz moderna y ambiente correcto."""
    console.print(Rule("[bold cyan]🔍 VERIFICACIÓN DEL ENTORNO PYTHON[/bold cyan]"))
    
    # Mostrar estado del entorno
    show_environment_status()
    
    # Obtener información del ambiente y ejecutable correcto
    env_info = env_manager.detect_environment()
    pip_executable = env_manager.get_pip_executable()
    
    # Ejecutar pip list con progreso
    with console.status(f"[bold green]🔍 Obteniendo lista de paquetes desde {env_info['env_type'].upper()}...", spinner="dots"):
        try:
            console.print(f"[dim]🔧 Usando: {pip_executable}[/dim]")
            
            result = subprocess.run([pip_executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Crear panel con información del ambiente
                env_details = f"[bold cyan]Ambiente:[/bold cyan] {env_info['env_type'].upper()}\n"
                env_details += f"[bold cyan]Python:[/bold cyan] {env_info['python_version']}\n"
                env_details += f"[bold cyan]Ejecutable:[/bold cyan] {pip_executable}\n"
                if env_info['venv_path']:
                    env_details += f"[bold cyan]VENV Path:[/bold cyan] {env_info['venv_path']}\n"
                
                # Contar paquetes instalados
                package_lines = [line for line in result.stdout.split('\n') if line.strip() and not line.startswith('Package') and not line.startswith('---')]
                package_count = len(package_lines)
                env_details += f"[bold cyan]Paquetes instalados:[/bold cyan] {package_count}"
                
                console.print(Panel(
                    env_details + "\n\n" + Syntax(result.stdout, "text", theme="monokai", line_numbers=True),
                    title=f"[bold green]📦 Paquetes Instalados en {env_info['env_type'].upper()}[/bold green]",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[bold red]❌ Error al verificar entorno: {result.stderr}[/bold red]\n\n"
                    f"[yellow]Ambiente: {env_info['env_type']}[/yellow]\n"
                    f"[yellow]Ejecutable: {pip_executable}[/yellow]",
                    title="[bold red]⚠️ Error de Verificación[/bold red]",
                    border_style="red"
                ))
                
        except subprocess.TimeoutExpired:
            console.print(f"[bold red]⏰ Timeout al verificar entorno {env_info['env_type']}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]❌ Error inesperado: {e}[/bold red]")
            console.print(f"[dim]Ambiente: {env_info['env_type']}, Ejecutable: {pip_executable}[/dim]")
    
    console.print(f"[bold green]✅ check_environment() ejecutado correctamente en {env_info['env_type'].upper()}.[/bold green]")

def execute_activator():
    """Ejecuta el script activador con interfaz moderna."""
    console.print(Rule("[bold blue]⚡ ACTIVADOR DE ENTORNO VIRTUAL[/bold blue]"))
    
    # Panel informativo
    info_panel = Panel(
        "[bold yellow]ℹ️ INFORMACIÓN IMPORTANTE[/bold yellow]\n\n"
        "[cyan]La activación del entorno virtual solo afecta al terminal externo.[/cyan]\n"
        "[cyan]Las operaciones posteriores se ejecutarán en ese terminal.[/cyan]\n"
        "[dim]La consola embebida no puede cambiar el entorno Python activo de la app.[/dim]\n\n"
        "[bold green]💡 Por favor, continúe en el terminal externo para trabajar con el venv activado.[/bold green]",
        title="[bold blue]📋 Limitaciones de Activación[/bold blue]",
        border_style="blue"
    )
    console.print(info_panel)
    
    # Ejecutar script con progreso
    with console.status("[bold green]⚡ Ejecutando script activador...", spinner="dots"):
        try:
            result = subprocess.run(['powershell', '-File', 'Activador-VENV.ps1'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.stdout:
                console.print(Panel(
                    result.stdout,
                    title="[bold green]📤 Salida del Script[/bold green]",
                    border_style="green"
                ))
            
            if result.stderr:
                console.print(Panel(
                    f"[red]{result.stderr}[/red]",
                    title="[bold red]⚠️ Errores del Script[/bold red]",
                    border_style="red"
                ))
                
        except subprocess.TimeoutExpired:
            console.print("[bold red]⏰ Timeout al ejecutar activador[/bold red]")
        except Exception as e:
            console.print(f"[bold red]❌ Error al ejecutar activador: {e}[/bold red]")
    
    console.print("[bold green]✅ execute_activator() ejecutado correctamente.[/bold green]")

def manual_command():
    """Muestra comandos manuales con interfaz moderna y opciones de navegación."""
    while True:
        console.clear()
        console.print(Rule("[bold cyan]🛠️ COMANDOS MANUALES DE PYTHON Y VENV[/bold cyan]"))
        
        # Crear árbol de comandos
        tree = Tree("📚 [bold cyan]Comandos Disponibles[/bold cyan]")
        
        # Rama de Entorno Virtual
        venv_branch = tree.add("🔧 [bold green]Entorno Virtual (VENV)[/bold green]")
        venv_branch.add("[cyan]python -m venv .venv[/cyan] - Crear ambiente virtual")
        venv_branch.add("[cyan].\\.venv\\Scripts\\Activate[/cyan] - Activar ambiente (Windows)")
        venv_branch.add("[cyan]source .venv/bin/activate[/cyan] - Activar ambiente (Linux/Mac)")
        venv_branch.add("[cyan]deactivate[/cyan] - Desactivar ambiente virtual")
        
        # Rama de PowerShell
        ps_branch = tree.add("⚡ [bold yellow]PowerShell (Políticas)[/bold yellow]")
        ps_branch.add("[yellow]Get-ExecutionPolicy[/yellow] - Ver política actual")
        ps_branch.add("[yellow]Set-ExecutionPolicy RemoteSigned[/yellow] - Política recomendada")
        ps_branch.add("[yellow]Set-ExecutionPolicy Restricted[/yellow] - Política restrictiva")
        ps_branch.add("[yellow]Set-ExecutionPolicy Unrestricted[/yellow] - Sin restricciones")
        
        # Rama de Pip
        pip_branch = tree.add("📦 [bold magenta]Gestión de Paquetes (Pip)[/bold magenta]")
        pip_branch.add("[magenta]pip install package[/magenta] - Instalar paquete")
        pip_branch.add("[magenta]pip uninstall package[/magenta] - Desinstalar paquete")
        pip_branch.add("[magenta]pip list[/magenta] - Listar paquetes instalados")
        pip_branch.add("[magenta]pip freeze > requirements.txt[/magenta] - Exportar dependencias")
        pip_branch.add("[magenta]pip install -r requirements.txt[/magenta] - Instalar desde archivo")
        
        # Rama de Diagnóstico
        diag_branch = tree.add("🔍 [bold red]Diagnóstico y Verificación[/bold red]")
        diag_branch.add("[red]python --version[/red] - Versión de Python")
        diag_branch.add("[red]python -c \"import sys; print(sys.executable)\"[/red] - Ruta del intérprete")
        diag_branch.add("[red]python -c \"import sys; print(sys.prefix != sys.base_prefix)\"[/red] - ¿VENV activo?")
        diag_branch.add("[red]where python[/red] - Ubicación del ejecutable Python")
        
        console.print(Panel(
            tree,
            title="[bold cyan]🛠️ Manual de Comandos Python[/bold cyan]",
            border_style="cyan"
        ))
        
        # Panel de ejemplos prácticos
        examples_md = """
## 🚀 Flujo de Trabajo Típico

1. **Crear proyecto nuevo:**
   ```bash
   mkdir mi_proyecto
   cd mi_proyecto
   python -m venv .venv
   ```

2. **Activar y configurar:**
   ```bash
   .\\.venv\\Scripts\\Activate    # Windows
   pip install --upgrade pip
   ```

3. **Instalar dependencias:**
   ```bash
   pip install requests pandas
   pip freeze > requirements.txt
   ```

4. **Compartir proyecto:**
   ```bash
   # Otros usuarios ejecutan:
   pip install -r requirements.txt
   ```
        """
        
        console.print(Panel(
            Markdown(examples_md),
            title="[bold green]💡 Ejemplos Prácticos[/bold green]",
            border_style="green"
        ))
        
        # Opciones de navegación
        options_table = Table(show_header=False, box=box.SIMPLE)
        options_table.add_column("Opción", style="bold cyan", width=8)
        options_table.add_column("Descripción", style="bright_white")
        
        options_table.add_row("1", "🔙 Volver al menú principal")
        options_table.add_row("2", "📋 Copiar comando específico")
        options_table.add_row("3", "🔄 Actualizar vista")
        options_table.add_row("4", "🚪 Salir de la aplicación")
        
        console.print(Panel(
            options_table,
            title="[bold yellow]⚙️ Opciones de Navegación[/bold yellow]",
            border_style="yellow"
        ))
        
        try:
            choice = Prompt.ask(
                "\n[bold cyan]Seleccione una opción[/bold cyan]",
                choices=["1", "2", "3", "4"],
                default="1"
            )
            
            if choice == "1":
                return
            elif choice == "2":
                copy_command_interface()
            elif choice == "3":
                continue  # Refresca la vista
            elif choice == "4":
                console.print("[bold red]🚪 Saliendo de la aplicación...[/bold red]")
                raise SystemExit
                
        except KeyboardInterrupt:
            console.print("\n[yellow]🔙 Regresando al menú principal...[/yellow]")
            return

def environment_manager_menu():
    """Menú interactivo para gestionar cambios entre ambientes Python."""
    while True:
        console.clear()
        console.print(Rule("[bold cyan]🔄 GESTIÓN DE AMBIENTES PYTHON[/bold cyan]"))
        
        # Mostrar estado actual
        env_info = env_manager.detect_environment()
        current_status = Panel(
            f"[bold cyan]🔧 Ambiente Actual:[/bold cyan] [yellow]{env_info['env_type'].upper()}[/yellow]\n"
            f"[bold cyan]🐍 Python:[/bold cyan] [green]{env_info['python_version']}[/green]\n"
            f"[bold cyan]📍 Ejecutable:[/bold cyan] [dim]{env_manager.get_pip_executable()}[/dim]\n"
            f"[bold cyan]📁 Directorio:[/bold cyan] [dim]{env_info['current_dir']}[/dim]",
            title="[bold blue]📋 Estado Actual[/bold blue]",
            border_style="blue"
        )
        console.print(current_status)
        
        # Tabla de opciones disponibles
        options_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        options_table.add_column("#", style="bold cyan", width=3)
        options_table.add_column("🔧 Acción", style="bright_white", min_width=25)
        options_table.add_column("📝 Descripción", style="bright_white")
        options_table.add_column("🎯 Estado", justify="center")
        
        # Detectar qué ambientes están disponibles
        local_venv_path = os.path.join(os.getcwd(), ".venv")
        local_available = "✅ Disponible" if os.path.exists(os.path.join(local_venv_path, "Scripts", "python.exe")) else "❌ No encontrado"
        current_indicator = "🟢 ACTIVO" if env_info['env_type'] == 'local_venv' else ""
        
        options_table.add_row(
            "1", 
            "📁 Cambiar a VENV LOCAL", 
            f"Usar .venv en directorio actual\n[dim]{local_venv_path}[/dim]",
            f"{local_available} {current_indicator}"
        )
        
        global_indicator = "🟢 ACTIVO" if env_info['env_type'] == 'system' else ""
        options_table.add_row(
            "2", 
            "🌐 Cambiar a SISTEMA/GLOBAL", 
            "Usar instalación global de Python\n[dim red]⚠️ Cuidado con paquetes críticos[/dim red]",
            f"✅ Disponible {global_indicator}"
        )
        
        external_indicator = "🟢 ACTIVO" if env_info['env_type'] == 'external_venv' else ""
        external_status = "🔗 Configurado" if env_manager.external_venv_path else "❓ No configurado"
        options_table.add_row(
            "3", 
            "📂 Configurar VENV EXTERNO", 
            "Seleccionar un venv de otra ubicación\n[dim]Útil para proyectos en otras carpetas[/dim]",
            f"{external_status} {external_indicator}"
        )
        
        options_table.add_row("4", "🔍 Verificar Ambiente Actual", "Mostrar detalles del ambiente activo", "📊 Info")
        options_table.add_row("5", "🔙 Volver al Menú Principal", "Regresar al menú principal", "↩️ Salir")
        
        console.print(Panel(
            options_table,
            title="[bold cyan]⚙️ Opciones de Gestión de Ambientes[/bold cyan]",
            border_style="cyan"
        ))
        
        # Información adicional
        info_md = """
### 💡 Información Importante

- **VENV LOCAL**: Busca `.venv` en el directorio actual del script
- **SISTEMA/GLOBAL**: Usa la instalación global de Python (⚠️ cuidado!)
- **VENV EXTERNO**: Permite seleccionar cualquier venv de otra ubicación
- Los cambios afectan todas las operaciones de pip (instalar/desinstalar/listar)
        """
        
        console.print(Panel(
            Markdown(info_md),
            title="[bold yellow]📚 Guía[/bold yellow]",
            border_style="yellow"
        ))
        
        try:
            choice = Prompt.ask(
                "\n[bold cyan]🎯 Seleccione una opción[/bold cyan]",
                choices=["1", "2", "3", "4", "5"],
                default="5"
            )
            
            if choice == "1":
                handle_switch_to_local_venv()
            elif choice == "2":
                handle_switch_to_global()
            elif choice == "3":
                handle_switch_to_external_venv()
            elif choice == "4":
                show_environment_status()
                console.print("\n[dim]Presione Enter para continuar...[/dim]")
                input()
            elif choice == "5":
                console.print("[bold green]🔙 Regresando al menú principal...[/bold green]")
                return
                
        except KeyboardInterrupt:
            console.print("\n[yellow]🔙 Regresando al menú principal...[/yellow]")
            return

def handle_switch_to_local_venv():
    """Maneja el cambio al VENV local."""
    console.print(Rule("[bold blue]📁 Cambio a VENV LOCAL[/bold blue]"))
    
    local_venv_path = os.path.join(os.getcwd(), ".venv")
    
    if not os.path.exists(local_venv_path):
        console.print(Panel(
            f"[bold red]❌ No se encontró VENV local[/bold red]\n\n"
            f"[yellow]Ruta buscada: {local_venv_path}[/yellow]\n\n"
            f"[cyan]💡 Sugerencia: Use la opción 1 del menú principal para ejecutar el script activador, "
            f"o cree un venv con:[/cyan]\n"
            f"[green]python -m venv .venv[/green]",
            title="[bold red]⚠️ VENV No Encontrado[/bold red]",
            border_style="red"
        ))
        console.print("\n[dim]Presione Enter para continuar...[/dim]")
        input()
        return
    
    if env_manager.switch_to_local_venv():
        console.print(Panel(
            f"[bold green]✅ Cambio exitoso a VENV LOCAL[/bold green]\n\n"
            f"[cyan]📂 Ruta: {local_venv_path}[/cyan]\n"
            f"[cyan]🔧 Ejecutable: {env_manager.get_pip_executable()}[/cyan]\n\n"
            f"[yellow]Todas las operaciones de pip ahora usarán este entorno.[/yellow]",
            title="[bold green]🎉 Cambio Completado[/bold green]",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "[bold red]❌ Error al cambiar al VENV local[/bold red]\n\n"
            "[yellow]Verifique que el entorno virtual esté correctamente configurado.[/yellow]",
            title="[bold red]⚠️ Error[/bold red]",
            border_style="red"
        ))
    
    console.print("\n[dim]Presione Enter para continuar...[/dim]")
    input()

def handle_switch_to_global():
    """Maneja el cambio al ambiente global/sistema."""
    console.print(Rule("[bold red]🌐 Cambio a AMBIENTE GLOBAL/SISTEMA[/bold red]"))
    
    # Advertencia de seguridad
    warning_panel = Panel(
        "[bold red]🚨 ADVERTENCIA CRÍTICA 🚨[/bold red]\n\n"
        "[yellow]Está a punto de cambiar al ambiente GLOBAL de Python.[/yellow]\n\n"
        "[red]⚠️ Riesgos:[/red]\n"
        "[red]• Puede afectar otras aplicaciones del sistema[/red]\n"
        "[red]• Desinstalar paquetes puede romper funcionalidades[/red]\n"
        "[red]• No se recomienda para desarrollo[/red]\n\n"
        "[cyan]💡 Recomendación: Use un entorno virtual en su lugar.[/cyan]",
        title="[bold red]🚨 Confirmación de Seguridad[/bold red]",
        border_style="red"
    )
    console.print(warning_panel)
    
    if not Confirm.ask("[bold red]¿Está SEGURO de cambiar al ambiente GLOBAL?[/bold red]"):
        console.print("[yellow]✅ Cambio cancelado por seguridad.[/yellow]")
        console.print("\n[dim]Presione Enter para continuar...[/dim]")
        input()
        return
    
    if env_manager.switch_to_system():
        console.print(Panel(
            f"[bold yellow]⚠️ Cambio realizado a AMBIENTE GLOBAL[/bold yellow]\n\n"
            f"[cyan]🔧 Ejecutable: {env_manager.get_pip_executable()}[/cyan]\n\n"
            f"[red]PRECAUCIÓN: Todas las operaciones afectarán el sistema global.[/red]",
            title="[bold yellow]🌐 Ambiente Global Activo[/bold yellow]",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "[bold red]❌ Error al cambiar al ambiente global[/bold red]",
            title="[bold red]⚠️ Error[/bold red]",
            border_style="red"
        ))
    
    console.print("\n[dim]Presione Enter para continuar...[/dim]")
    input()

def handle_switch_to_external_venv():
    """Maneja el cambio a un VENV externo."""
    console.print(Rule("[bold blue]📂 Configuración de VENV EXTERNO[/bold blue]"))
    
    console.print(Panel(
        "[bold cyan]� Selección de VENV Externo[/bold cyan]\n\n"
        "[yellow]Se abrirá un diálogo para seleccionar la carpeta del entorno virtual.[/yellow]\n"
        "[yellow]Busque una carpeta que contenga Scripts/python.exe (Windows) o bin/python (Linux/Mac).[/yellow]\n\n"
        "[cyan]Ejemplos de rutas típicas:[/cyan]\n"
        "[green]• C:\\Users\\usuario\\mi_proyecto\\.venv[/green]\n"
        "[green]• C:\\Python\\envs\\mi_entorno[/green]\n"
        "[green]• D:\\Proyectos\\app\\venv[/green]",
        title="[bold blue]📋 Instrucciones[/bold blue]",
        border_style="blue"
    ))
    
    # Solicitar ruta manualmente (ya que no tenemos tkinter disponible)
    try:
        venv_path = Prompt.ask(
            "\n[bold cyan]📂 Ingrese la ruta completa al directorio del VENV externo[/bold cyan]",
            default=""
        ).strip()
        
        if not venv_path:
            console.print("[yellow]❌ Operación cancelada.[/yellow]")
            console.print("\n[dim]Presione Enter para continuar...[/dim]")
            input()
            return
        
        # Verificar que la ruta existe
        if not os.path.exists(venv_path):
            console.print(Panel(
                f"[bold red]❌ La ruta no existe[/bold red]\n\n"
                f"[yellow]Ruta ingresada: {venv_path}[/yellow]\n\n"
                f"[cyan]Verifique que la ruta sea correcta y que tenga permisos de acceso.[/cyan]",
                title="[bold red]⚠️ Error de Ruta[/bold red]",
                border_style="red"
            ))
            console.print("\n[dim]Presione Enter para continuar...[/dim]")
            input()
            return
        
        # Intentar cambiar al venv externo
        if env_manager.switch_to_external_venv(venv_path):
            console.print(Panel(
                f"[bold green]✅ VENV externo configurado exitosamente[/bold green]\n\n"
                f"[cyan]📂 Ruta: {venv_path}[/cyan]\n"
                f"[cyan]🔧 Ejecutable: {env_manager.get_pip_executable()}[/cyan]\n\n"
                f"[yellow]Todas las operaciones de pip ahora usarán este entorno.[/yellow]",
                title="[bold green]🎉 VENV Externo Activo[/bold green]",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[bold red]❌ Error al configurar VENV externo[/bold red]\n\n"
                f"[yellow]Ruta: {venv_path}[/yellow]\n\n"
                f"[cyan]Verifique que:[/cyan]\n"
                f"[cyan]• Sea un directorio de entorno virtual válido[/cyan]\n"
                f"[cyan]• Contenga Scripts/python.exe (Windows) o bin/python (Linux/Mac)[/cyan]\n"
                f"[cyan]• Tenga permisos de acceso[/cyan]",
                title="[bold red]⚠️ Error de Configuración[/bold red]",
                border_style="red"
            ))
            
    except KeyboardInterrupt:
        console.print("\n[yellow]❌ Operación cancelada.[/yellow]")
    
    console.print("\n[dim]Presione Enter para continuar...[/dim]")
    input()

def copy_command_interface():
    """Interfaz para copiar comandos específicos al portapapeles."""
    commands = {
        "1": ("python -m venv .venv", "Crear entorno virtual"),
        "2": (".\\.venv\\Scripts\\Activate", "Activar VENV (Windows)"),
        "3": ("source .venv/bin/activate", "Activar VENV (Linux/Mac)"),
        "4": ("deactivate", "Desactivar VENV"),
        "5": ("Set-ExecutionPolicy RemoteSigned", "Configurar política PowerShell"),
        "6": ("pip freeze > requirements.txt", "Exportar dependencias"),
        "7": ("pip install -r requirements.txt", "Instalar desde requirements"),
        "8": ("python --version", "Ver versión de Python"),
    }
    
    cmd_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    cmd_table.add_column("#", style="bold cyan", width=3)
    cmd_table.add_column("Comando", style="green")
    cmd_table.add_column("Descripción", style="bright_white")
    
    for key, (cmd, desc) in commands.items():
        cmd_table.add_row(key, cmd, desc)
    
    console.print(Panel(
        cmd_table,
        title="[bold cyan]📋 Comandos Disponibles para Copiar[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        choice = Prompt.ask(
            "[bold cyan]Seleccione el comando a copiar (o Enter para regresar)[/bold cyan]",
            default=""
        )
        
        if choice in commands:
            command, description = commands[choice]
            try:
                # Intentar copiar al portapapeles (requiere pyperclip)
                import pyperclip
                pyperclip.copy(command)
                console.print(f"[bold green]✅ Comando copiado al portapapeles:[/bold green] [cyan]{command}[/cyan]")
            except ImportError:
                console.print(f"[bold yellow]📋 Comando seleccionado:[/bold yellow] [cyan]{command}[/cyan]")
                console.print("[dim]Tip: Instale 'pyperclip' para auto-copiar al portapapeles[/dim]")
        elif choice:
            console.print("[red]❌ Opción inválida[/red]")
            
    except KeyboardInterrupt:
        pass

def show_main_menu() -> None:
    """Muestra el menú principal con diseño moderno y atractivo."""
    console.clear()
    
    # Banner principal con arte ASCII
    banner = """
    ██████╗ ██╗   ██╗      ██████╗██╗     ███████╗ █████╗ ███╗   ██╗███████╗██████╗ 
    ██╔══██╗╚██╗ ██╔╝     ██╔════╝██║     ██╔════╝██╔══██╗████╗  ██║██╔════╝██╔══██╗
    ██████╔╝ ╚████╔╝█████╗██║     ██║     █████╗  ███████║██╔██╗ ██║█████╗  ██████╔╝
    ██╔═══╝   ╚██╔╝ ╚════╝██║     ██║     ██╔══╝  ██╔══██║██║╚██╗██║██╔══╝  ██╔══██╗
    ██║        ██║        ╚██████╗███████╗███████╗██║  ██║██║ ╚████║███████╗██║  ██║
    ╚═╝        ╚═╝         ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
    """
    
    console.print(Panel(
        Align.center(Text(banner, style="bold bright_blue")),
        title="[bold cyan]🧹 Herramienta de Limpieza de Python 🐍[/bold cyan]",
        subtitle="[dim]Gestión avanzada de entornos virtuales y dependencias - v2.1[/dim]",
        border_style="bright_blue",
        padding=(1, 2)
    ))
    
    # Estado del entorno actual
    show_environment_status()
    
    # Crear layout de dos columnas para opciones
    left_column = Table(show_header=False, box=None, padding=(0, 1))
    left_column.add_column("", style="bold cyan", width=3)
    left_column.add_column("", style="bright_white", min_width=30)
    
    right_column = Table(show_header=False, box=None, padding=(0, 1))
    right_column.add_column("", style="bold cyan", width=3)
    right_column.add_column("", style="bright_white", min_width=30)
    
    # Opciones del menú - Columna izquierda
    left_column.add_row("1", "⚡ Ejecutar Script Activador")
    left_column.add_row("2", "📄 Generar Reporte de Dependencias")
    left_column.add_row("3", "🧹 Desinstalar Todas las Dependencias")
    left_column.add_row("4", "🎯 Desinstalar Dependencias (Selectivo)")
    left_column.add_row("5", "🔄 Gestionar Ambientes Python")
    
    # Opciones del menú - Columna derecha
    right_column.add_row("6", "🔍 Verificar Entorno de Python")
    right_column.add_row("7", "🛠️ Comandos Manuales")
    right_column.add_row("8", "🚪 Salir de la aplicación")
    right_column.add_row("", "")  # Espaciado
    
    # Combinar columnas
    menu_columns = Columns([
        Panel(left_column, title="[bold yellow]🔧 Operaciones Principales[/bold yellow]", border_style="yellow"),
        Panel(right_column, title="[bold green]⚙️ Utilidades y Configuración[/bold green]", border_style="green")
    ])
    
    console.print(menu_columns)
    
    # Panel de información adicional mejorado
    env_info = env_manager.detect_environment()
    env_warning = ""
    if env_info["env_type"] == "system":
        env_warning = "\n[bold red]⚠️ ADVERTENCIA: Trabajando en ambiente GLOBAL - Usar con precaución[/bold red]"
    
    info_text = Text()
    info_text.append("💡 ", style="yellow")
    info_text.append("Tip: ", style="bold yellow")
    info_text.append(f"Ambiente actual: {env_info['env_type'].upper()}. ", style="cyan")
    info_text.append("Use la opción 5 para cambiar entre ambientes de forma segura.", style="cyan")
    if env_warning:
        info_text.append(env_warning, style="red")
    
    console.print(Panel(
        info_text,
        title="[bold blue]ℹ️ Información[/bold blue]",
        border_style="blue"
    ))

def main():
    """Función principal con interfaz CLI moderna usando Rich."""
    try:
        # Inicializar el gestor de ambientes
        env_manager.detect_environment()
        
        # Mensaje de bienvenida inicial
        welcome_text = Text()
        welcome_text.append("🎉 ¡Bienvenido a ", style="bold green")
        welcome_text.append("py-cleaner v2.1", style="bold bright_blue")
        welcome_text.append("! 🐍✨", style="bold green")
        
        console.print(Panel(
            Align.center(welcome_text),
            title="[bold bright_blue]🚀 Iniciando Aplicación[/bold bright_blue]",
            border_style="bright_blue"
        ))
        
        time.sleep(1.5)  # Pequeña pausa para mejor experiencia
        
        # Bucle principal del menú
        while True:
            show_main_menu()
            
            try:
                choice = Prompt.ask(
                    "\n[bold cyan]🎯 Seleccione una opción[/bold cyan]",
                    choices=["1", "2", "3", "4", "5", "6", "7", "8"],
                    default="8"
                )
                
                console.print(Rule(f"[bold bright_blue]Ejecutando opción {choice}[/bold bright_blue]"))
                
                # Procesamiento de opciones
                if choice == '1':
                    execute_activator()
                elif choice == '2':
                    generate_report()
                elif choice == '3':
                    uninstall_dependencies()
                elif choice == '4':
                    uninstall_dependencies_selective()
                elif choice == '5':
                    environment_manager_menu()
                elif choice == '6':
                    check_environment()
                elif choice == '7':
                    manual_command()
                elif choice == '8':
                    show_goodbye_message()
                    raise SystemExit
                
                # Pausa para que el usuario pueda leer la salida
                if choice in ['1', '2', '3', '4', '6']:
                    console.print("\n[dim]Presione Enter para continuar...[/dim]")
                    input()
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]🔄 Regresando al menú principal...[/yellow]")
                time.sleep(1)
                continue
            except Exception as e:
                console.print(f"\n[bold red]❌ Error inesperado: {e}[/bold red]")
                console.print("[dim]Presione Enter para continuar...[/dim]")
                input()
                
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 ¡Hasta luego![/yellow]")
        raise SystemExit
    except Exception as e:
        console.print(f"\n[bold red]💥 Error crítico: {e}[/bold red]")
        raise SystemExit

def show_goodbye_message():
    """Muestra un mensaje de despedida estilizado."""
    console.clear()
    
    goodbye_text = """
    ¡Gracias por usar py-cleaner! 🎉
    
    🧹 Tu entorno Python está más limpio y organizado
    🐍 Esperamos que esta herramienta te haya sido útil
    ⭐ ¡No olvides mantener tus dependencias actualizadas!
    """
    
    console.print(Panel(
        Align.center(Text(goodbye_text, style="bold bright_green")),
        title="[bold bright_blue]👋 ¡Hasta la vista![/bold bright_blue]",
        border_style="bright_green",
        padding=(2, 4)
    ))
    
    # Pequeña animación de despedida
    with console.status("[bold green]🌟 Finalizando aplicación...", spinner="dots"):
        time.sleep(2)

def signal_handler(sig, frame):
    """Maneja las señales del sistema de forma elegante."""
    console.print("\n[yellow]🔄 Regresando al menú principal...[/yellow]")
    time.sleep(1)
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

# --- Funciones de CLI ---
def show_version():
    """Muestra la versión de la aplicación con estilo."""
    version_text = Text()
    version_text.append("🧹 ", style="bright_blue")
    version_text.append("py-cleaner", style="bold bright_cyan")
    version_text.append(" v2.0.0", style="bold bright_green")
    
    console.print(Panel(
        Align.center(version_text),
        title="[bold bright_blue]📋 Información de Versión[/bold bright_blue]",
        border_style="bright_blue"
    ))
    
    # Información adicional de la versión
    info_table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
    info_table.add_column("Atributo", style="bold cyan")
    info_table.add_column("Valor", style="bright_white")
    
    info_table.add_row("🏷️ Versión", "2.0.0")
    info_table.add_row("📅 Fecha", "Agosto 2025")
    info_table.add_row("🎨 Framework UI", "Rich + Typer")
    info_table.add_row("🐍 Python mínimo", "3.8+")
    info_table.add_row("🌐 Licencia", "MIT")
    info_table.add_row("👨‍💻 Autor", "partybrasil")
    
    console.print(Panel(
        info_table,
        title="[bold cyan]ℹ️ Detalles[/bold cyan]",
        border_style="cyan"
    ))

def show_help():
    """Muestra la ayuda de uso de la aplicación con estilo."""
    # Banner de ayuda
    help_banner = Text()
    help_banner.append("🛠️ ", style="bright_yellow")
    help_banner.append("AYUDA DE USO", style="bold bright_cyan")
    help_banner.append(" - py-cleaner v2.0", style="bright_green")
    
    console.print(Panel(
        Align.center(help_banner),
        title="[bold bright_blue]📚 Manual de Usuario[/bold bright_blue]",
        border_style="bright_blue"
    ))
    
    # Tabla de comandos
    commands_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    commands_table.add_column("🔧 Comando", style="bold cyan", min_width=25)
    commands_table.add_column("📝 Descripción", style="bright_white")
    commands_table.add_column("💡 Ejemplo", style="green")
    
    commands_table.add_row(
        "python py-cleaner.py",
        "Ejecuta la interfaz CLI interactiva moderna",
        "python py-cleaner.py"
    )
    commands_table.add_row(
        "python py-cleaner.py --gui",
        "Ejecuta la interfaz gráfica (GUI) con PySide6",
        "python py-cleaner.py --gui"
    )
    commands_table.add_row(
        "python py-cleaner.py --help",
        "Muestra esta ayuda de uso y sale",
        "python py-cleaner.py --help"
    )
    commands_table.add_row(
        "python py-cleaner.py --version",
        "Muestra la versión de la aplicación y sale",
        "python py-cleaner.py --version"
    )
    
    console.print(Panel(
        commands_table,
        title="[bold cyan]⚙️ Opciones de Línea de Comandos[/bold cyan]",
        border_style="cyan"
    ))
    
    # Descripción de funcionalidades
    features_md = """
## 🎯 Funcionalidades Principales

### 🔧 **Gestión de Entornos Virtuales**
- ⚡ Activación automática de entornos virtuales
- 🆕 Creación de nuevos entornos
- 🔍 Verificación del estado del entorno activo

### 📦 **Gestión de Dependencias**
- 📊 Generación de reportes detallados de paquetes instalados
- 🧹 Desinstalación masiva de todas las dependencias
- 🎯 Desinstalación selectiva con interfaz interactiva
- 📋 Tablas estilizadas con información de versiones

### 🎨 **Interfaz Moderna**
- 🌈 Colores vibrantes y emojis contextuales
- 📊 Barras de progreso animadas
- 📋 Menús interactivos con validación
- 🎭 Arte ASCII y paneles estilizados

### 🛠️ **Herramientas Avanzadas**
- 🖥️ Interfaz gráfica opcional (--gui)
- 💻 Comandos manuales con ejemplos
- 📚 Documentación integrada
- 🔄 Regeneración automática de reportes
    """
    
    console.print(Panel(
        Markdown(features_md),
        title="[bold green]✨ Características[/bold green]",
        border_style="green"
    ))
    
    # Ejemplos de uso práctico
    examples_md = """
## 🚀 Flujo de Trabajo Típico

1. **Activar entorno virtual:**
   ```bash
   python py-cleaner.py
   # Seleccionar opción 1: ⚡ Ejecutar Script Activador
   ```

2. **Generar reporte de dependencias:**
   ```bash
   python py-cleaner.py
   # Seleccionar opción 2: 📄 Generar Reporte de Dependencias
   ```

3. **Limpieza selectiva:**
   ```bash
   python py-cleaner.py
   # Seleccionar opción 4: 🎯 Desinstalar Dependencias (Selectivo)
   ```

4. **Interfaz gráfica:**
   ```bash
   python py-cleaner.py --gui
   ```
    """
    
    console.print(Panel(
        Markdown(examples_md),
        title="[bold yellow]💡 Ejemplos de Uso[/bold yellow]",
        border_style="yellow"
    ))
    
    # Nota final
    footer_text = Text()
    footer_text.append("💡 ", style="bright_yellow")
    footer_text.append("Tip: ", style="bold yellow")
    footer_text.append("Para mejores resultados, asegúrese de activar su entorno virtual antes de usar las funciones de gestión de dependencias.", style="cyan")
    
    console.print(Panel(
        footer_text,
        title="[bold blue]📌 Recomendación[/bold blue]",
        border_style="blue"
    ))

def parse_command_line_args():
    """Parsea los argumentos de línea de comandos y ejecuta acciones correspondientes."""
    args = sys.argv[1:]  # Excluir el nombre del script
    
    # Verificar argumentos de ayuda y versión (tienen prioridad)
    if "--help" in args or "-h" in args:
        show_help()
        return "exit"
    
    if "--version" in args or "-v" in args:
        show_version()
        return "exit"
    
    # Verificar modo GUI
    if "--gui" in args:
        return "gui"
    
    # Si no hay argumentos especiales, modo CLI normal
    return "cli"

# --- Arranque híbrido CLI/GUI ---
if __name__ == "__main__":
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parsear argumentos de línea de comandos
    mode = parse_command_line_args()
    
    if mode == "exit":
        # Salir después de mostrar ayuda o versión
        sys.exit(0)
    elif mode == "gui":
        console.print("[bold green]🖥️ Iniciando interfaz gráfica...[/bold green]")
        iniciar_gui()
    else:
        # Verificar si Rich está disponible para CLI moderno
        try:
            # Mensaje inicial sobre la versión mejorada
            startup_text = Text()
            startup_text.append("🎨 ", style="bright_yellow")
            startup_text.append("Interfaz CLI mejorada con Rich", style="bold bright_cyan")
            startup_text.append(" - ¡Disfruta de la nueva experiencia visual! ✨", style="bright_green")
            
            console.print(Panel(
                Align.center(startup_text),
                title="[bold bright_blue]🚀 py-cleaner v2.0[/bold bright_blue]",
                subtitle="[dim]Herramienta de limpieza con interfaz moderna[/dim]",
                border_style="bright_blue"
            ))
            
            # Iniciar aplicación CLI moderna
            main()
            
        except ImportError:
            # Fallback a CLI clásico si Rich no está disponible
            print("⚠️ Rich no está disponible. Ejecutando en modo clásico...")
            print("💡 Instale Rich con: pip install rich")
            print("Bienvenido a la Herramienta de Limpieza de Python")
            print("Por favor, asegúrese de que el entorno virtual esté activado antes de ejecutar esta aplicación.")
            
            # Función main clásica como respaldo
            def main_classic():
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
            
            main_classic()
