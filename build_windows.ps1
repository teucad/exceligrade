# Build helper for Windows using PyInstaller
# Usage (PowerShell):
# 1. Activate your virtualenv: .\.venv\Scripts\Activate.ps1
# 2. Install PyInstaller: pip install pyinstaller
# 2. Run this script: .\build_windows.ps1

Write-Host "Activating virtualenv and running PyInstaller..."
if (-Not (Test-Path .\.venv)) {
  Write-Host "Warning: .venv not found. Make sure you created a virtualenv and installed dependencies.";
}

# Expect PyInstaller to be on PATH in the venv
pyinstaller --noconfirm --clean --onefile --add-data "static;static" run_app.py
Write-Host "PyInstaller finished. See the dist\run_app.exe file." 
