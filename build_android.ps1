# Build helper for Android using Buildozer
# This script is intended to be run from PowerShell.

param(
    [ValidateSet("debug", "release", "clean")]
    [string]$BuildType
)

$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Description,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host $Description -ForegroundColor Yellow
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Exceligrade Android Build Helper" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

# Buildozer does not support native Windows. Stop early with actionable guidance.
if ($env:OS -eq "Windows_NT" -and -not $env:WSL_DISTRO_NAME) {
    Write-Host "Buildozer does not run on native Windows." -ForegroundColor Red
    Write-Host "Use WSL (Ubuntu) and run the build there instead." -ForegroundColor Yellow
    Write-Host "" 
    Write-Host "Quick start:" -ForegroundColor Yellow
    Write-Host "  wsl --install -d Ubuntu" -ForegroundColor Cyan
    Write-Host "  wsl" -ForegroundColor Cyan
    Write-Host "  cd /mnt/c/path/to/exceligrade" -ForegroundColor Cyan
    Write-Host "  python3 -m venv .venv && source .venv/bin/activate" -ForegroundColor Cyan
    Write-Host "  pip install buildozer cython" -ForegroundColor Cyan
    Write-Host "  buildozer android debug" -ForegroundColor Cyan
    exit 1
}

$venvPython = Join-Path $repoRoot ".venv/Scripts/python.exe"
$pythonCmd = if (Test-Path $venvPython) { $venvPython } else { "python" }

if (-not (Test-Path $venvPython)) {
    Write-Host "Warning: .venv not found. Falling back to system Python." -ForegroundColor Yellow
    Write-Host "Recommended setup:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Cyan
    Write-Host "  .\\.venv\\Scripts\\Activate.ps1" -ForegroundColor Cyan
    Write-Host ""
}

Invoke-Step -Description "Installing build dependencies..." -Action {
    & $pythonCmd -m pip install -q buildozer cython
}

Invoke-Step -Description "Verifying buildozer installation..." -Action {
    & $pythonCmd -m buildozer --version | Out-Null
}

# Check for Android SDK
if (-not $env:ANDROID_SDK_ROOT) {
    Write-Host ""
    Write-Host "IMPORTANT: Android SDK not found!" -ForegroundColor Red
    Write-Host "Set ANDROID_SDK_ROOT environment variable, e.g.:" -ForegroundColor Yellow
    Write-Host '  $env:ANDROID_SDK_ROOT = "C:\Android\Sdk"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then run one of:" -ForegroundColor Yellow
    Write-Host "  .\\build_android.ps1 -BuildType debug" -ForegroundColor Cyan
    Write-Host "  .\\build_android.ps1 -BuildType release" -ForegroundColor Cyan
    Write-Host "  .\\build_android.ps1 -BuildType clean" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "Android SDK found at: $env:ANDROID_SDK_ROOT" -ForegroundColor Green

if (-not $BuildType) {
    Write-Host ""
    Write-Host "Choose build type:" -ForegroundColor Yellow
    Write-Host "1) Debug (for testing)"
    Write-Host "2) Release (for distribution)"
    Write-Host "3) Clean and rebuild"
    $choice = Read-Host "Enter 1, 2, or 3"

    switch ($choice) {
        "1" { $BuildType = "debug" }
        "2" { $BuildType = "release" }
        "3" { $BuildType = "clean" }
        default {
            Write-Host "Invalid choice" -ForegroundColor Red
            exit 1
        }
    }
}

switch ($BuildType) {
    "debug" {
        Write-Host "Building debug APK..." -ForegroundColor Green
        & $pythonCmd -m buildozer android debug
        Write-Host "APK output: bin\\exceligrade-1.0-debug.apk" -ForegroundColor Green
    }
    "release" {
        Write-Host "Building release APK..." -ForegroundColor Green
        Write-Host "You'll be prompted for keystore information" -ForegroundColor Yellow
        & $pythonCmd -m buildozer android release
        Write-Host "APK output: bin\\exceligrade-1.0-release.apk" -ForegroundColor Green
    }
    "clean" {
        Write-Host "Cleaning build cache..." -ForegroundColor Yellow
        & $pythonCmd -m buildozer android clean
        Write-Host "Building debug APK..." -ForegroundColor Green
        & $pythonCmd -m buildozer android debug
        Write-Host "APK output: bin\\exceligrade-1.0-debug.apk" -ForegroundColor Green
    }
}

if ($LASTEXITCODE -ne 0) {
    throw "Build failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To install on device:" -ForegroundColor Yellow
Write-Host "  adb install -r bin\\exceligrade-1.0-debug.apk" -ForegroundColor Cyan
