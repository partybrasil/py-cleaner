param (
    [string]$venvName = ".venv"
)

# Verificar si Python está instalado
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python no está instalado. Por favor, instálalo antes de continuar."
    exit 1
}

# Crear el ambiente virtual
Write-Output "Creando ambiente virtual en la carpeta actual..."
python -m venv $venvName

if ($?) {
    Write-Output "Ambiente virtual '$venvName' creado exitosamente."
} else {
    Write-Error "Hubo un error al crear el ambiente virtual."
}

# Pausar la ventana para que el usuario pueda ver el mensaje
Write-Output "Presiona cualquier tecla para continuar..."
[void][System.Console]::ReadKey($true)
