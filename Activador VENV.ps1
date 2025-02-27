if (Test-Path -Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "Failed to find the virtual environment in the current directory."
}

# Mantener la ventana de PowerShell abierta para interactuar con el entorno virtual activado
Write-Host "You can now interact with the virtual environment. Press Ctrl+C to exit."
while ($true) {
    Start-Sleep -Seconds 1
}