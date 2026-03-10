@echo off
echo Compiling tutorial program with PyInstaller...
echo.

set SCRIPT_DIR=%~dp0
set DIST_DIR=%SCRIPT_DIR%dist

pip install pyinstaller customtkinter

echo === PyInstaller (Tutorial) ===

set "TEMP_DIR=%SCRIPT_DIR:Kurumi's=Kurumi_s%"
set "TEMP_DIR=%TEMP_DIR:~0,-1%"

echo Copying files to temporary folder: %TEMP_DIR%
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
copy "%SCRIPT_DIR%tutorial.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%settings.py" "%TEMP_DIR%\" >nul
copy "%SCRIPT_DIR%tutorial.txt" "%TEMP_DIR%\" >nul
if exist "%SCRIPT_DIR%icon.ico" copy "%SCRIPT_DIR%icon.ico" "%TEMP_DIR%\" >nul

cd /d "%TEMP_DIR%"

pyinstaller --onedir --windowed ^
    --name "tutorial" ^
    --icon "icon.ico" ^
    --add-data "icon.ico;." ^
    --add-data "tutorial.txt;." ^
    --hidden-import customtkinter ^
    "tutorial.py"

if exist "%TEMP_DIR%\dist\tutorial\tutorial.exe" (
    if exist "%SCRIPT_DIR%tutorial" rmdir /S /Q "%SCRIPT_DIR%tutorial"
    xcopy /E /I /Y "%TEMP_DIR%\dist\tutorial" "%SCRIPT_DIR%tutorial\"
    for %%f in ("%SCRIPT_DIR%tutorial\*.*") do attrib +h "%%f"
    attrib -h "%SCRIPT_DIR%tutorial\tutorial.exe"
    echo.
    echo Success! Tutorial EXE created: %SCRIPT_DIR%tutorial\tutorial.exe
) else (
    echo.
    echo Error: Tutorial EXE not found.
)

cd /d "%SCRIPT_DIR%"
rmdir /S /Q "%TEMP_DIR%" 2>nul

echo.
pause