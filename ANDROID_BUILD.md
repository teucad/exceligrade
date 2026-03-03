# Android APK Build Instructions for Exceligrade

## Prerequisites

> **Important:** Buildozer does not run on native Windows Python/PowerShell.
> Use WSL (Ubuntu) or a Linux machine for Android packaging.

1. **Java Development Kit (JDK)** – Java 8 or higher
   - Download from: https://www.oracle.com/java/technologies/downloads/

2. **Android SDK** – via Android Studio or cmdline-tools
   - Download from: https://developer.android.com/studio/command-line/sdkmanager

3. **Android NDK** – for compiling native libraries
   - Install via Android SDK manager or download separately

4. **Buildozer** – Python tool to package Kivy apps (Linux/WSL only)
   ```bash
   pip install buildozer cython
   ```

5. **Kivy and dependencies**
   ```bash
   pip install kivy requests openpyxl pdfminer.six python-docx flask
   ```

## Environment Setup (WSL/Linux)

Create or edit your `buildozer.spec` file (already created in the project).

### Key settings:
- `python_version = 3.11` – Python for Android uses 3.11
- `android.minapi = 21` – Minimum Android API level
- `android.targetapi = 31` – Target Android API level
- `android.permissions` – INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE (for file access)

## Build Steps

1. **Create and activate virtualenv:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install build tools:**
   ```bash
   pip install buildozer cython
   ```

3. **Navigate to project directory (inside WSL):**
   ```bash
   cd /mnt/c/your-path/exceligrade
   ```

4. **Build the APK:**
   ```bash
   buildozer android debug
   ```

   For release (requires signing):
   ```bash
   buildozer android release
   ```

5. **APK output location:**
   ```
   bin/exceligrade-1.0-debug.apk
   ```

## Troubleshooting

### Missing Java
```bash
buildozer android debug -- --help
```
Set `JAVA_HOME` environment variable:
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### Missing Android SDK
```bash
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export ANDROID_NDK_ROOT=$ANDROID_SDK_ROOT/ndk/23.1.7779620
```

### Build cache issues
```bash
buildozer android clean
buildozer android debug
```

## Testing on Device or Emulator

1. **Enable USB Debugging** on your Android device
   - Settings > Developer Options > USB Debugging

2. **Connect device via USB:**
   ```bash
   adb devices  # Should list your device
   ```

3. **Install APK:**
   ```bash
   adb install bin/exceligrade-1.0-debug.apk
   ```

4. **Run app on emulator:**
   - Launch Android Emulator from Android Studio
   - Run `adb install` command above

## Known Limitations

- File picker may have limited access on Android 11+ (use Downloads folder)
- Syllabus extraction requires internet connection to contact localhost server
- Some PDF parsing features may be limited due to Android sandboxing

## Next Steps

After building, the APK can be:
- Tested on a device via USB
- Distributed via Google Play Store (requires signing certificate)
- Side-loaded onto Android devices

For production releases, you'll need to:
1. Create a keystore and sign the APK
2. Optimize and obfuscate code
3. Test on multiple Android versions
