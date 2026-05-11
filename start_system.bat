@echo off
echo ============================================
echo 🚀 Iniciando Sistema Neighbord
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] Inicializando sistema...
cd backend
python initialize_system.py
if %errorlevel% neq 0 (
    echo ❌ Error en inicialización del sistema
    pause
    exit /b 1
)

echo.
echo [2/4] Verificando configuración...
python pre_presentation_check.py
if %errorlevel% neq 0 (
    echo ❌ Verificación fallida
    pause
    exit /b 1
)

echo.
echo [3/4] Iniciando backend...
start "Backend Neighbord" cmd /c "cd backend && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo.
echo [4/4] Iniciando frontend...
start "Frontend Neighbord" cmd /c "cd frontend && npm run dev"

echo.
echo ========================================
echo         ¡SISTEMA LISTO!
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend:  http://localhost:8000
echo 🔐 Demo:     test@neighbord.com / test123
echo.
echo Presiona cualquier tecla para continuar...
pause > nul