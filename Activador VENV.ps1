if (Test-Path -Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated."
} else {
    Write-Host "Failed to find the virtual environment in the current directory."
}