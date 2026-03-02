# Android APK Build Instructions for Exceligrade

## Prerequisites

1. **Java Development Kit (JDK)** – Java 8 or higher
   - Download from: https://www.oracle.com/java/technologies/downloads/

2. **Android SDK** – via Android Studio or cmdline-tools
   - Download from: https://developer.android.com/studio/command-line/sdkmanager

3. **Android NDK** – for compiling native libraries
   - Install via Android SDK manager or download separately

4. **Buildozer** – Python tool to package Kivy apps
   ```bash
   pip install buildozer cython
   ```

5. **Kivy and dependencies**
   ```bash
   pip install kivy requests openpyxl pdfminer.six python-docx flask
   ```

## Environment Setup (Windows)

Create or edit your `buildozer.spec` file (already created in the project).

### Key settings:
- `python_version = 3.11` – Python for Android uses 3.11
- `android.minapi = 21` – Minimum Android API level
- `android.targetapi = 31` – Target Android API level
- `android.permissions` – INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE (for file access)

## Build Steps

1. **Activate virtualenv:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install Kivy and build tools:**
   ```bash
   pip install -r requirements_android.txt
   pip install buildozer cython
   ```

3. **Navigate to project directory:**
   ```bash
   cd C:\your-path\exceligrade
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
```
set JAVA_HOME=C:\Program Files\Java\jdk-21
```

### Missing Android SDK
```
set ANDROID_SDK_ROOT=C:\Android\Sdk
set ANDROID_NDK_ROOT=C:\Android\ndk\23.1.7779620
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
