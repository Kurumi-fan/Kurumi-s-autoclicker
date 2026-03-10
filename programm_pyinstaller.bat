@echo off
echo Compiling main program with PyInstaller...
echo.

set SCRIPT_DIR=%~dp0
set DIST_DIR=%SCRIPT_DIR%dist

pip install pyinstaller customtkinter pynput

echo === PyInstaller (Main application) ===

set "TEMP_DIR=%SCRIPT_DIR:Kurumi's=Kurumi_s%"
set "TEMP_DIR=%TEMP_DIR:~0,-1%"

echo Copying files to temporary folder: %TEMP_DIR%
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
copy "%SCRIPT_DIR%gui.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%autoclicker.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%macro.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%recorder.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%settings.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%update.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%clicker.dll" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%about.txt" "%TEMP_DIR%\" >nul
if exist "%SCRIPT_DIR%icon.ico" copy "%SCRIPT_DIR%icon.ico" "%TEMP_DIR%\" >nul

cd /d "%TEMP_DIR%"

pyinstaller --onedir --windowed ^
    --name "Kurumis Autoclicker" ^
    --icon "icon.ico" ^
    --add-data "clicker.dll;." ^
    --add-data "about.txt;." ^
    --add-data "icon.ico;." ^
    --hidden-import customtkinter ^
    --hidden-import pynput ^
    --hidden-import pynput.mouse ^
    --hidden-import pynput.keyboard ^
    --hidden-import tkinter.colorchooser ^
    --hidden-import winshell ^
    --collect-submodules pynput ^
    "gui.py"

if exist "%TEMP_DIR%\dist\Kurumis Autoclicker\Kurumis Autoclicker.exe" (
    if exist "%SCRIPT_DIR%Kurumis Autoclicker" rmdir /S /Q "%SCRIPT_DIR%Kurumis Autoclicker"
    xcopy /E /I /Y "%TEMP_DIR%\dist\Kurumis Autoclicker" "%SCRIPT_DIR%Kurumis Autoclicker\"
    for %%f in ("%SCRIPT_DIR%Kurumis Autoclicker\*.*") do attrib +h "%%f"
    attrib -h "%SCRIPT_DIR%Kurumis Autoclicker\Kurumis Autoclicker.exe"
    echo.
    echo Success! Main EXE created: %SCRIPT_DIR%Kurumis Autoclicker\Kurumis Autoclicker.exe
) else (
    echo.
    echo Error: Main EXE not found.
)

cd /d "%SCRIPT_DIR%"
rmdir /S /Q "%TEMP_DIR%" 2>nul

echo.
pause