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

def is_venv_active() -> bool:
    """Verifica si un entorno virtual está activo."""
    return sys.prefix != sys.base_prefix

def show_environment_status():
    """Muestra el estado actual del entorno de Python con estilo."""
    env_type = "🔴 VIRTUAL ENV" if is_venv_active() else "🌐 GLOBAL ENV"
    python_version = f"Python {sys.version.split()[0]}"
    python_path = sys.executable
    
    env_table = Table(show_header=False, box=box.ROUNDED, border_style="bright_blue")
    env_table.add_column("Atributo", style="bold cyan")
    env_table.add_column("Valor", style="bright_white")
    
    env_table.add_row("🐍 Intérprete", python_version)
    env_table.add_row("📍 Ubicación", python_path)
    env_table.add_row("🌍 Tipo", env_type)
    env_table.add_row("📁 Directorio", os.getcwd())
    
    console.print(Panel(
        env_table,
        title="[bold bright_blue]🔍 Estado del Entorno Python[/bold bright_blue]",
        border_style="bright_blue"
    ))

def generate_report() -> bool:
    """Genera un reporte de dependencias instaladas con interfaz moderna."""
    with console.status("[bold green]📊 Generando reporte de dependencias...", spinner="dots"):
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                with open('pyREPORT.txt', 'w', encoding='utf-8') as report_file:
                    report_file.write(result.stdout)
                
                # Contar dependencias
                deps_count = len([line for line in result.stdout.split('\n') if line.strip()])
                
                console.print(Panel(
                    f"[bold green]✅ Reporte generado exitosamente[/bold green]\n\n"
                    f"📄 Archivo: [bold cyan]pyREPORT.txt[/bold cyan]\n"
                    f"📦 Dependencias encontradas: [bold yellow]{deps_count}[/bold yellow]",
                    title="[bold green]📊 Reporte de Dependencias[/bold green]",
                    border_style="green"
                ))
                return True
            else:
                console.print(Panel(
                    f"[bold red]❌ Error al generar reporte[/bold red]\n\n"
                    f"[red]Error: {result.stderr}[/red]",
                    title="[bold red]⚠️ Error[/bold red]",
                    border_style="red"
                ))
                return False
                
        except subprocess.TimeoutExpired:
            console.print("[bold red]⏰ Timeout al generar reporte[/bold red]")
            return False
        except Exception as e:
            console.print(f"[bold red]❌ Error inesperado: {e}[/bold red]")
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
    """Desinstala todas las dependencias de forma masiva."""
    console.print(Rule("[bold red]🧹 DESINSTALACIÓN MASIVA DE DEPENDENCIAS[/bold red]"))
    
    if not os.path.exists('pyREPORT.txt'):
        console.print("[yellow]⚠️ pyREPORT.txt no encontrado.[/yellow]")
        if Confirm.ask("¿Desea generar el reporte automáticamente?"):
            if not generate_report():
                return
        else:
            return
    
    try:
        with open('pyREPORT.txt', 'r', encoding='utf-8') as report_file:
            dependencies = [line.strip() for line in report_file.readlines() if line.strip()]
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
        "[bold red]⚠️ ADVERTENCIA ⚠️[/bold red]\n\n"
        "[yellow]Esta operación desinstalará TODAS las dependencias mostradas.\n"
        "Esta acción NO se puede deshacer.[/yellow]\n\n"
        f"[cyan]Total de paquetes a desinstalar: {len(dependencies)}[/cyan]",
        title="[bold red]🚨 Confirmación Requerida[/bold red]",
        border_style="red"
    )
    console.print(warning_panel)
    
    if not Confirm.ask("[bold red]¿Confirma la desinstalación masiva?[/bold red]"):
        console.print("[yellow]❌ Operación cancelada por el usuario.[/yellow]")
        return
    
    # Ejecutar desinstalación con progreso
    console.print(Rule("[bold green]🚀 Iniciando Desinstalación Masiva[/bold green]"))
    
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
                    [sys.executable, '-m', 'pip', 'uninstall', '-y', package_name],
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
    """Desinstala dependencias de forma selectiva con interfaz Rich moderna."""
    console.print(Rule("[bold blue]🎯 DESINSTALACIÓN SELECTIVA DE DEPENDENCIAS[/bold blue]"))
    
    # Verificar si existe el reporte, si no, generarlo
    if not os.path.exists('pyREPORT.txt'):
        console.print("[yellow]⚠️ pyREPORT.txt no encontrado.[/yellow]")
        with console.status("[bold green]Generando reporte automáticamente...", spinner="dots"):
            if not generate_report():
                return
    
    try:
        with open('pyREPORT.txt', 'r', encoding='utf-8') as report_file:
            dependencies = [line.strip() for line in report_file.readlines() if line.strip()]
    except Exception as e:
        console.print(f"[bold red]❌ Error al leer pyREPORT.txt: {e}[/bold red]")
        return
    
    if not dependencies:
        console.print(Panel(
            "[yellow]ℹ️ No se encontraron dependencias instaladas.[/yellow]",
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
        title=f"[bold cyan]📦 Dependencias Instaladas ({len(dependencies)})[/bold cyan]",
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
                "\n[bold cyan]🎯 Selecciona los paquetes a desinstalar[/bold cyan]",
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
        title=f"[bold red]🗑️ Paquetes Seleccionados para Desinstalación ({len(packages_to_uninstall)})[/bold red]",
        border_style="red"
    ))
    
    # Confirmación final estilizada
    warning_text = Text()
    warning_text.append("⚠️ ADVERTENCIA: ", style="bold red")
    warning_text.append("Esta operación NO se puede deshacer.\n", style="yellow")
    warning_text.append(f"Se desinstalarán {len(packages_to_uninstall)} paquetes.", style="cyan")
    
    console.print(Panel(
        Align.center(warning_text),
        title="[bold red]🚨 Confirmación Final[/bold red]",
        border_style="red"
    ))
    
    if not Confirm.ask("\n[bold red]¿Confirma la desinstalación de estos paquetes?[/bold red]"):
        console.print("[yellow]❌ Operación cancelada por el usuario.[/yellow]")
        return
    
    # Ejecutar desinstalación con barra de progreso avanzada
    console.print(Rule(f"[bold green]🚀 Iniciando Desinstalación de {len(packages_to_uninstall)} Paquetes[/bold green]"))
    
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
                    [sys.executable, '-m', 'pip', 'uninstall', '-y', package], 
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
    
    console.print("[bold green]✅ uninstall_dependencies_selective() ejecutado correctamente.[/bold green]")

def check_environment():
    """Verifica y muestra el entorno de Python con interfaz moderna."""
    console.print(Rule("[bold cyan]🔍 VERIFICACIÓN DEL ENTORNO PYTHON[/bold cyan]"))
    
    # Mostrar estado del entorno
    show_environment_status()
    
    # Ejecutar pip list con progreso
    with console.status("[bold green]🔍 Obteniendo lista de paquetes instalados...", spinner="dots"):
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                console.print(Panel(
                    Syntax(result.stdout, "text", theme="monokai", line_numbers=True),
                    title="[bold green]📦 Paquetes Instalados[/bold green]",
                    border_style="green"
                ))
            else:
                console.print(f"[bold red]❌ Error al verificar entorno: {result.stderr}[/bold red]")
                
        except subprocess.TimeoutExpired:
            console.print("[bold red]⏰ Timeout al verificar entorno[/bold red]")
        except Exception as e:
            console.print(f"[bold red]❌ Error inesperado: {e}[/bold red]")
    
    console.print("[bold green]✅ check_environment() ejecutado correctamente.[/bold green]")

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
        subtitle="[dim]Gestión avanzada de entornos virtuales y dependencias[/dim]",
        border_style="bright_blue",
        padding=(1, 2)
    ))
    
    # Estado del entorno actual
    show_environment_status()
    
    # Crear layout de dos columnas para opciones
    left_column = Table(show_header=False, box=None, padding=(0, 1))
    left_column.add_column("", style="bold cyan", width=3)
    left_column.add_column("", style="bright_white", min_width=25)
    
    right_column = Table(show_header=False, box=None, padding=(0, 1))
    right_column.add_column("", style="bold cyan", width=3)
    right_column.add_column("", style="bright_white", min_width=25)
    
    # Opciones del menú - Columna izquierda
    left_column.add_row("1", "⚡ Ejecutar Script Activador")
    left_column.add_row("2", "📄 Generar Reporte de Dependencias")
    left_column.add_row("3", "🧹 Desinstalar Todas las Dependencias")
    left_column.add_row("4", "🎯 Desinstalar Dependencias (Selectivo)")
    
    # Opciones del menú - Columna derecha
    right_column.add_row("5", "🔍 Verificar Entorno de Python")
    right_column.add_row("6", "🛠️ Comandos Manuales")
    right_column.add_row("7", "🚪 Salir de la aplicación")
    right_column.add_row("", "")  # Espaciado
    
    # Combinar columnas
    menu_columns = Columns([
        Panel(left_column, title="[bold yellow]🔧 Operaciones Principales[/bold yellow]", border_style="yellow"),
        Panel(right_column, title="[bold green]⚙️ Utilidades y Configuración[/bold green]", border_style="green")
    ])
    
    console.print(menu_columns)
    
    # Panel de información adicional
    info_text = Text()
    info_text.append("💡 ", style="yellow")
    info_text.append("Tip: ", style="bold yellow")
    info_text.append("Asegúrese de que el entorno virtual esté activado antes de realizar operaciones de dependencias.", style="cyan")
    
    console.print(Panel(
        info_text,
        title="[bold blue]ℹ️ Información[/bold blue]",
        border_style="blue"
    ))

def main():
    """Función principal con interfaz CLI moderna usando Rich."""
    try:
        # Mensaje de bienvenida inicial
        welcome_text = Text()
        welcome_text.append("🎉 ¡Bienvenido a ", style="bold green")
        welcome_text.append("py-cleaner", style="bold bright_blue")
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
                    choices=["1", "2", "3", "4", "5", "6", "7"],
                    default="7"
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
                    check_environment()
                elif choice == '6':
                    manual_command()
                elif choice == '7':
                    show_goodbye_message()
                    raise SystemExit
                
                # Pausa para que el usuario pueda leer la salida
                if choice in ['1', '2', '3', '4', '5']:
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
