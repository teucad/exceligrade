# Build helper for Android using Buildozer
# Run this in PowerShell after setting up Android SDK and NDK

Write-Host "Exceligrade Android Build Helper" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Check if virtualenv is active
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtualenv..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Ensure buildozer and dependencies
Write-Host "Installing build dependencies..." -ForegroundColor Yellow
pip install -q buildozer cython kivy

# Check for Android SDK
if (-not $env:ANDROID_SDK_ROOT) {
    Write-Host ""
    Write-Host "IMPORTANT: Android SDK not found!" -ForegroundColor Red
    Write-Host "Set ANDROID_SDK_ROOT environment variable, e.g.:" -ForegroundColor Yellow
    Write-Host '  $env:ANDROID_SDK_ROOT = "C:\Android\Sdk"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then run:" -ForegroundColor Yellow
    Write-Host "  buildozer android debug" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "Android SDK found at: $env:ANDROID_SDK_ROOT" -ForegroundColor Green

# Choose build type
Write-Host ""
Write-Host "Choose build type:" -ForegroundColor Yellow
Write-Host "1) Debug (for testing)"
Write-Host "2) Release (for distribution)"
Write-Host "3) Clean and rebuild"
$choice = Read-Host "Enter 1, 2, or 3"

switch ($choice) {
    "1" {
        Write-Host "Building debug APK..." -ForegroundColor Green
        buildozer android debug
        Write-Host "APK output: bin\exceligrade-1.0-debug.apk" -ForegroundColor Green
    }
    "2" {
        Write-Host "Building release APK..." -ForegroundColor Green
        Write-Host "You'll be prompted for keystore information" -ForegroundColor Yellow
        buildozer android release
        Write-Host "APK output: bin\exceligrade-1.0-release.apk" -ForegroundColor Green
    }
    "3" {
        Write-Host "Cleaning build cache..." -ForegroundColor Yellow
        buildozer android clean
        Write-Host "Building debug APK..." -ForegroundColor Green
        buildozer android debug
        Write-Host "APK output: bin\exceligrade-1.0-debug.apk" -ForegroundColor Green
    }
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To install on device:" -ForegroundColor Yellow
Write-Host "  adb install -r bin\exceligrade-1.0-debug.apk" -ForegroundColor Cyan
