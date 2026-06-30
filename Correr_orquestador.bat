@echo off
REM ============================================================
REM  Ejecuta el orquestador de notebooks mostrando su salida
REM  en TIEMPO REAL. Coloca este .bat en la RAIZ del proyecto.
REM ============================================================
setlocal

REM 1) Situarse en la carpeta del propio .bat (raiz del proyecto).
REM    El orquestador usa rutas relativas (new_source\..., data\...),
REM    asi que debe ejecutarse desde aqui.
cd /d "%~dp0"

REM 2) Consola y Python en UTF-8 (acentos y simbolos sin romperse).
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

REM 3) Salida de Python SIN buffer -> impresion linea a linea en tiempo real.
set "PYTHONUNBUFFERED=1"

REM 4) Elegir interprete: usar el venv del proyecto si existe; si no, el del sistema.
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe"  set "PYTHON=venv\Scripts\python.exe"

echo ============================================================
echo  Ejecutando orquestador de proyecto.
echo  Interprete : %PYTHON%
echo  Carpeta    : %CD%
echo  Inicio     : %DATE% %TIME%
echo ============================================================
echo.

REM 5) Ejecutar. -u refuerza la salida sin buffer (tiempo real).
"%PYTHON%" -u "Plantillas\Orquestador.py"
set "CODIGO=%ERRORLEVEL%"

echo.
echo ============================================================
if "%CODIGO%"=="0" (
    echo  [OK] Orquestador finalizado sin errores ^(codigo %CODIGO%^).
) else (
    echo  [ERROR] El orquestador termino con errores ^(codigo %CODIGO%^).
    echo  Revisa el detalle de arriba y la carpeta Salidas\.
)
echo  Fin        : %DATE% %TIME%
echo ============================================================
echo.

REM 6) Mantener la ventana abierta para poder leer la salida.
pause

REM  %CODIGO% se expande ANTES de que endlocal destruya las variables
REM  locales (expansion en fase de parsing), asi que el valor se conserva.
endlocal & exit /b %CODIGO%

REM ------------------------------------------------------------
REM  OPCIONAL: si ademas quieres GUARDAR un log con marca de
REM  tiempo y seguir viendo la salida en pantalla, sustituye la
REM  linea del paso 5 por esta (usa PowerShell como "tee"):
REM
REM  powershell -NoProfile -Command "& '%PYTHON%' -u 'Plantillas\Orquestador.py' 2>&1 | Tee-Object -FilePath ('log_' + (Get-Date -Format yyyyMMdd_HHmmss) + '.txt')"
REM
REM  Nota: al redirigir por tuberia, la barra de progreso de tqdm
REM  se vera mas "ruidosa" (escribe muchas lineas en vez de
REM  actualizar una sola). Es el compromiso normal de loguear a archivo.
REM ------------------------------------------------------------
