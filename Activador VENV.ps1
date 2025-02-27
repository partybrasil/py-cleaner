if (Test-Path -Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
    Write-Host "Entorno virtual activado."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "No se pudo encontrar el entorno virtual en el directorio actual."
}

# Mantener la ventana de PowerShell abierta para interactuar con el entorno virtual activado
Write-Host "Ahora puede interactuar con el entorno virtual. Presione Ctrl+C para salir."
while ($true) {
    Start-Sleep -Seconds 1
}