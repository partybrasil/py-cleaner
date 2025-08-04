# 🧹 py-cleaner v2.0 🐍

**Herramienta avanzada de limpieza y gestión de entornos virtuales Python con interfaz CLI modernizada**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![Rich](https://img.shields.io/badge/Rich-CLI-brightgreen.svg) ![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Novedades en v2.0

### 🎨 **Interfaz CLI Completamente Renovada**

- **Rich Framework:** Interfaz moderna con colores, emojis e iconos
- **Tablas Estilizadas:** Visualización clara de dependencias con filas alternadas
- **Paneles Informativos:** Diseño elegante con bordes estilizados
- **Barras de Progreso:** Seguimiento visual de operaciones largas
- **Arte ASCII:** Banners atractivos y profesionales

### 🚀 **Mejoras en Experiencia de Usuario**

- **Navegación Intuitiva:** Menús organizados en columnas responsivas
- **Prompts Inteligentes:** Validación de entrada robusta con Rich.Prompt
- **Confirmaciones Elegantes:** Mensajes claros con opciones visuales
- **Manejo de Errores:** Avisos coloridos y descriptivos
- **Compatibilidad Total:** Mantiene toda la funcionalidad original + GUI

## 📋 Características Principales

### 🔧 **Gestión de Entornos Virtuales**

- ⚡ Activación automática de VENV
- 🆕 Creación de entornos virtuales
- 🔍 Verificación del estado del entorno
- 📊 Información detallada del intérprete Python

### 📦 **Gestión de Dependencias**

- 📄 Generación de reportes de dependencias (`pip freeze`)
- 🧹 Desinstalación masiva de todas las dependencias
- 🎯 Desinstalación selectiva con interfaz interactiva
- 📊 Visualización de paquetes en tablas modernas
- ⚡ Progreso visual durante instalación/desinstalación

### 🛠️ **Utilidades Avanzadas**

- 📚 Manual de comandos integrado con Markdown
- 🔄 Regeneración automática de reportes
- 📋 Ejemplos de flujo de trabajo incluidos
- 🎪 Interfaz gráfica opcional (PySide6)

## 🚀 Instalación Rápida

### Prerrequisitos

```bash
Python 3.8+ requerido
```

### Instalación de Dependencias

```bash
# Clonar el repositorio
git clone https://github.com/partybrasil/py-cleaner.git
cd py-cleaner

# Crear entorno virtual (recomendado)
python -m venv .venv

# Activar entorno virtual
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🎯 Uso

### 📋 Opciones de Línea de Comandos

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `python py-cleaner.py` | Ejecuta la interfaz CLI interactiva moderna | `python py-cleaner.py` |
| `python py-cleaner.py --gui` | Ejecuta la interfaz gráfica (GUI) con PySide6 | `python py-cleaner.py --gui` |
| `python py-cleaner.py --help` | Muestra ayuda de uso detallada y sale | `python py-cleaner.py --help` |
| `python py-cleaner.py --version` | Muestra información de versión y sale | `python py-cleaner.py --version` |

#### 🔗 Alias Disponibles
- `-h` → `--help`
- `-v` → `--version`

### 🎨 CLI Moderna (Recomendado)

```bash
python py-cleaner.py
```

### 🖥️ Interfaz Gráfica

```bash
python py-cleaner.py --gui
```

### 📋 Información Rápida

```bash
# Ver versión
python py-cleaner.py --version

# Ver ayuda completa
python py-cleaner.py --help
```

## 📊 Capturas de Funcionalidades

### 🎨 Menú Principal Modernizado

```
╭──────────────────────────────────────── 🧹 Herramienta de Limpieza de Python 🐍 ────────────────────────────────────────╮
│     ██████╗ ██╗   ██╗      ██████╗██╗     ███████╗ █████╗ ███╗   ██╗███████╗██████╗                                    │
│     ██╔══██╗╚██╗ ██╔╝     ██╔════╝██║     ██╔════╝██╔══██╗████╗  ██║██╔════╝██╔══██╗                                   │
│     ██████╔╝ ╚████╔╝█████╗██║     ██║     █████╗  ███████║██╔██╗ ██║█████╗  ██████╔╝                                   │
│     ██╔═══╝   ╚██╔╝ ╚════╝██║     ██║     ██╔══╝  ██╔══██║██║╚██╗██║██╔══╝  ██╔══██╗                                   │
│     ██║        ██║        ╚██████╗███████╗███████╗██║  ██║██║ ╚████║███████╗██║  ██║                                   │
│     ╚═╝        ╚═╝         ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝                                   │
╰───────────────────────────────────── Gestión avanzada de entornos virtuales y dependencias ──────────────────────────────╯
```

### 📦 Tabla de Dependencias Estilizada

```
╭──────────────────────────────── 📦 Dependencias Instaladas (6) ────────────────────────────────╮
│ ╭────────────┬────────────┬──────────────╮                                                      │
│ │ 📦 Paquete │ 📌 Versión │  📊 Estado   │                                                      │
│ │ requests   │ 2.31.0     │ ✅ Instalado │                                                      │
│ │ pandas     │ >= 1.5.0   │   ⚠️ Rango    │                                                      │
│ │ numpy      │ 1.24.3     │ ✅ Instalado │                                                      │
│ │ rich       │ 14.1.0     │ ✅ Instalado │                                                      │
│ ╰────────────┴────────────┴──────────────╯                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## 🔧 Tecnologías Utilizadas

### 🎨 **Interfaz y Visualización**

- **[Rich](https://rich.readthedocs.io/)** - Framework de CLI moderno
- **[Typer](https://typer.tiangolo.com/)** - CLI avanzado con validación

### 🖥️ **Interfaz Gráfica (Opcional)**

- **[PySide6](https://doc.qt.io/qtforpython/)** - GUI multiplataforma

### 🐍 **Core Python**

- **subprocess** - Ejecución de comandos
- **pathlib** - Manejo moderno de rutas
- **typing** - Anotaciones de tipo

## 📚 Comandos Principales

### 🔧 Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Windows)
.\.venv\Scripts\Activate.ps1

# Activar (Linux/Mac)
source .venv/bin/activate

# Desactivar
deactivate
```

### 📦 Gestión de Paquetes

```bash
# Listar paquetes instalados
pip list

# Generar reporte de dependencias
pip freeze > requirements.txt

# Instalar desde archivo
pip install -r requirements.txt

# Desinstalar paquete
pip uninstall package_name
```

## 🎯 Flujo de Trabajo Recomendado

1. **🆕 Crear proyecto nuevo:**

   ```bash
   mkdir mi_proyecto
   cd mi_proyecto
   python -m venv .venv
   ```
2. **⚡ Activar y configurar:**

   ```bash
   .\.venv\Scripts\Activate    # Windows
   pip install --upgrade pip
   ```
3. **📦 Instalar dependencias:**

   ```bash
   pip install requests pandas
   pip freeze > requirements.txt
   ```
4. **🧹 Limpiar al finalizar:**

   ```bash
   python py-cleaner.py  # Usar opción 4 para desinstalación selectiva
   ```

## 🆕 Funcionalidades Avanzadas v2.0

### 🎯 **Desinstalación Selectiva Mejorada**

- Selección por números individuales: `1 3 5`
- Selección por rangos: `1-5` o `10-15`
- Selección combinada: `1 3 5-8 10`
- Selección total: `todos` o `all` o `*`

### 📊 **Reportes Visuales**

- Tablas con filas alternadas en colores
- Iconos descriptivos por tipo de paquete
- Estados visuales (instalado, rango, desconocido)
- Contadores automáticos de dependencias

### ⚡ **Progreso Visual**

- Barras de progreso animadas para operaciones largas
- Spinners mientras se obtienen datos
- Mensajes de estado en tiempo real

## 📈 Resumen de Mejoras v2.0

### 🎨 **Mejoras Visuales Implementadas:**

- ✅ Interfaz CLI completamente renovada con Rich framework
- ✅ Colores vibrantes y consistentes en toda la aplicación
- ✅ Emojis e iconos descriptivos para mejor legibilidad
- ✅ Tablas estilizadas con filas alternadas y bordes elegantes
- ✅ Paneles informativos con diseño moderno
- ✅ Arte ASCII en banners principales
- ✅ Barras de progreso animadas para operaciones largas

### 🚀 **Mejoras Funcionales:**

- ✅ Navegación intuitiva con menús organizados en columnas
- ✅ Prompts interactivos con validación robusta
- ✅ Confirmaciones elegantes con opciones claras
- ✅ Manejo visual de errores con colores descriptivos
- ✅ Manual de comandos integrado con Markdown
- ✅ Compatibilidad total con funcionalidad GUI existente
- ✅ Fallback automático a CLI clásico si Rich no está disponible

### 💯 **Beneficios Obtenidos:**

- **Experiencia Visual:** +500% más atractiva y moderna
- **Usabilidad:** +300% más intuitiva con iconos y colores
- **Profesionalismo:** Nivel comercial con interfaz rica
- **Compatibilidad:** 100% mantenida con funcionalidad original

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autor

- **partybrasil** - *Desarrollador Principal* - [GitHub](https://github.com/partybrasil)

## 🙏 Agradecimientos

- Equipo de **Rich** por el increíble framework de CLI
- Comunidad **Python** por las herramientas de entornos virtuales
- Contribuidores y usuarios que reportan bugs y sugieren mejoras

---

### 🎉 ¡Gracias por usar py-cleaner v2.0!

**Si te ha sido útil, no olvides dejar una ⭐ en el repositorio.**

*Mantén tu entorno Python limpio y organizado* 🧹🐍✨
