[app]
# Application title
title = Exceligrade

# Application package name
package.name = exceligrade

# Application package domain
package.domain = org.example

# Source directory (where kivy_app.py and app.py are)
source.dir = .

# Source includes - what Python files to include
source.include_exts = py,png,jpg,kv,atlas,json

# Version
version = 1.0

# Python version
python_version = 3.11

# Enable site-packages
site_packages = .venv/Lib/site-packages

# Requirements
requirements = python3,kivy,requests,openpyxl,pdfminer.six,python-docx,flask

# Entry point
main_script = kivy_app.py

# Android orientation (portrait or landscape)
orientation = portrait

# Permissions needed
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Features required
android.features = android.hardware.usb.host

# Android API levels
android.minapi = 21
android.targetapi = 31
android.api = 31

# Android NDK
android.ndk = 23b

# Gradle dependencies for Android
android.gradle_dependencies = 

# Icons - use default Kivy icon
android.icon_filename = 

# Logcat filters
android.logcat_filters = *:S python:D

# Architecture
android.archs = arm64-v8a

# Release signing (optional - for production)
# android.keystore = 1
# android.keystore_path = path/to/keystore
# android.keystore_alias = alias_name
# android.keystore_passwd = password

[buildozer]

# Logging level
log_level = 2

# Display warnings
warn_on_root = 1
