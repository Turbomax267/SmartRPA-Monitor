@echo off
cd /d "%~dp0"

echo ==========================================
echo   SmartRPA Agent - Preparacion automatica
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python no esta instalado o no esta en PATH.
  echo Instala Python 3.11+ y vuelve a ejecutar este archivo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creando entorno virtual...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
  )
)

echo [INFO] Actualizando pip...
".\.venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] No se pudo actualizar pip.
  pause
  exit /b 1
)

echo [INFO] Instalando dependencias...
".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] No se pudieron instalar las dependencias.
  pause
  exit /b 1
)

echo.
echo [OK] Entorno preparado correctamente.
echo Ahora puedes ejecutar:
echo   - run-agent-001.bat
echo   - run-agent-002.bat
echo   - run-agent-003.bat
echo   - run-agent-004.bat
echo   - run-agent-005.bat
echo   - run-all-agents.bat
echo.
pause
