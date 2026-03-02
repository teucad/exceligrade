# Exceligrade

Small fullstack app that converts class syllabi (JSON) into an Excel workbook where students can enter marks and see per-student weighted averages and the class average.

Available as:
- **Windows Desktop (Tkinter)** – `dist/run_app.exe`
- **Android APK** – Kivy-based mobile app
- **Python source** – Run locally with Flask web server

Quick start

1. Create a Python virtual env and activate it.

   Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

2. Open http://localhost:5000 in your browser. Edit the example JSON or paste your syllabus JSON. Click "Generate Excel" to download `gradebook.xlsx`.

Running the Application

### Windows Desktop (Recommended)

**Pre-built executable** – No dependencies needed:

```powershell
dist\run_app.exe
```

This launches a native Tkinter window with the full desktop app.

**From source** – Requires Python 3.13+:

```powershell
.\.venv\Scripts\Activate.ps1
python run_app.py
```

### Android Mobile App

Requires Android SDK, NDK, and Buildozer. See [ANDROID_BUILD.md](ANDROID_BUILD.md) for full setup.

```powershell
.\.venv\Scripts\Activate.ps1
pip install buildozer cython kivy
buildozer android debug
# Output: bin/exceligrade-1.0-debug.apk
```

Or use the helper script:

```powershell
.\.venv\Scripts\Activate.ps1
.\build_android.ps1
```

### Web Browser (Development)

For testing in a browser:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

Building Windows Executable (PyInstaller)

1. Activate virtualenv and install build tools:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pyinstaller
```

2. Run build script:

```powershell
.\build_windows.ps1
```

3. Output: `dist\run_app.exe`

Note: The executable still launches a lightweight HTTP server in the background; the window loads `http://127.0.0.1:5000/` locally.

JSON shape

```json
{
  "classes": [
    {
      "name": "Class Name",
      "assignments": [{ "name": "HW", "weight": 20, "count": 4 }, ...]
    }
  ]
}
```

Worksheet layout

- **Row 1 (Headers):** Assignment names plus a "TOTAL" column
  - if an assignment has a `count` > 1, it will be split into numbered
    columns with equal weight (e.g. "Lab 1", "Lab 2", …)
- **Row 2 (WEIGHT):** Percentage weight of each assignment; TOTAL column uses `=SUM()` formula
- **Row 3 (SCORE):** User enters actual class scores (initialized to 0); TOTAL calculates weighted average
- **Row 4 (GRADE):** User enters grades (initialized to 0); TOTAL calculates weighted average  
- **Row 6 (AVGSCORE):** User enters average scores for each assignment (initialized to 0); TOTAL calculates weighted average
- **Row 7 (AVGGRADE):** Shows weighted average based on AVGSCORE

### Syllabus extraction

You can optionally upload a syllabus file (PDF, DOCX or plain text) and click
"Extract Weights". The server will attempt to parse assignment names and
weights from the document; detected values populate the assignment list for the
last class. The parser handles common patterns like:

- `Homework - 20%`
- `Midterm: 30%`
- `Final (50%)`
- `20% Project`

Files encoded in UTF‑16 (common on Windows) are automatically decoded. If
extraction fails, you can always enter weights manually or adjust the syllabus
format.

Notes

- Each class becomes a sheet (max 31 chars due to Excel limits).
- Weighted averages use Excel formulas so students can edit scores directly in the downloaded file.
- Class average is placed below the data.
