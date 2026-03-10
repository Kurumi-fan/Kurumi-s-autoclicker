@echo off
echo Compiling update.py with PyInstaller...
echo.

set SCRIPT_DIR=%~dp0
set DIST_DIR=%SCRIPT_DIR%dist

pip install pyinstaller

echo === PyInstaller (Update) ===

set "TEMP_DIR=%SCRIPT_DIR:Kurumi's=Kurumi_s%"
set "TEMP_DIR=%TEMP_DIR:~0,-1%"

echo Copying files to temporary folder: %TEMP_DIR%
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
copy "%SCRIPT_DIR%update.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%settings.py" "%TEMP_DIR%\" >nul
if exist "%SCRIPT_DIR%icon.ico" copy "%SCRIPT_DIR%icon.ico" "%TEMP_DIR%\" >nul

cd /d "%TEMP_DIR%"

pyinstaller --onedir --windowed ^
    --name "update" ^
    --icon "icon.ico" ^
    --hidden-import urllib.request ^
    --hidden-import json ^
    --hidden-import tempfile ^
    --hidden-import subprocess ^
    --hidden-import shutil ^
    --hidden-import argparse ^
    --hidden-import os ^
    --hidden-import sys ^
    "update.py"

if exist "%TEMP_DIR%\dist\update\update.exe" (
    if exist "%SCRIPT_DIR%update" rmdir /S /Q "%SCRIPT_DIR%update"
    xcopy /E /I /Y "%TEMP_DIR%\dist\update" "%SCRIPT_DIR%update\"
    for %%f in ("%SCRIPT_DIR%update\*.*") do attrib +h "%%f"
    attrib -h "%SCRIPT_DIR%update\update.exe"
    echo.
    echo Success! Update EXE created: %SCRIPT_DIR%update\update.exe
) else (
    echo.
    echo Error: Update EXE not found.
)

cd /d "%SCRIPT_DIR%"
rmdir /S /Q "%TEMP_DIR%" 2>nul

echo.
pause