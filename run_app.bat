@echo off
chcp 65001 > nul
echo =====================================================================
echo    BIENVENIDO A QFAI - PLATAFORMA DE PANORAMAS LOCALES
echo    Desarrollado y Validado por FabricaWebTransaccionalSDD
echo =====================================================================
echo.

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_FILE=%SCRIPT_DIR%frontend\index.html

echo [1/2] Iniciando Servidor Backend FastAPI (Uvicorn) en http://127.0.0.1:8000 ...
cd /d "%BACKEND_DIR%"
start "Qfai Backend" cmd /k python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo [2/2] Abriendo Interfaz Frontend Premium en su navegador...
timeout /t 3 >nul
start "" "%FRONTEND_FILE%"

echo.
echo =====================================================================
echo    ¡Servicios iniciados con éxito!
echo    - Backend API: http://127.0.0.1:8000/docs (Swagger)
echo    - Frontend UI: Abierto en su navegador
echo.
echo    Para detener el servidor, cierre la ventana "Qfai Backend".
echo =====================================================================
echo.
pause