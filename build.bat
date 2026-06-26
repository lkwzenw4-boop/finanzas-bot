@echo off
echo ============================================
echo  CONSTRUYENDO EJECUTABLE - Finanzas Personales
echo ============================================
echo.

:: Verificar que el modelo ONNX exista
if not exist "ai\model_onnx\model.onnx" (
    echo [Error] No se encontro el modelo ONNX.
    echo Ejecuta primero: python ai/export_model.py
    pause
    exit /b 1
)

:: Verificar que PyInstaller este instalado
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [Info] Instalando PyInstaller...
    pip install pyinstaller
)

echo.
echo [1/2] Limpiando builds anteriores...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [2/2] Generando ejecutable...
python -m PyInstaller finanzas.spec --noconfirm

echo.
if exist "dist\FinanzasPersonales\FinanzasPersonales.exe" (
    echo ============================================
    echo  [OK] Ejecutable generado exitosamente!
    echo  Ubicacion: dist\FinanzasPersonales\
    echo ============================================
) else (
    echo [Error] No se pudo generar el ejecutable.
)

pause
