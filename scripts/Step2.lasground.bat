@echo off
setlocal enabledelayedexpansion
echo ========================================
echo PASO 2: Clasificacion de terreno con lasground
echo ========================================
echo.

REM Crear carpeta de salida
if not exist "ground" mkdir ground

echo Procesando archivos con lasground64...
echo.

REM Procesar archivos y renombrar secuencialmente
set /a counter=1
for %%f in (raw_lidar_las\*.las) do (
    echo Procesando %%~nf...
    C:\LASTools\bin\lasground64.exe -i "%%f" -step 5 -spike 1 -offset 0.05 -demo -o "ground\ground_!counter!.las"
    set /a counter+=1
)

echo.
echo Clasificacion completada!
echo Archivos guardados en: ground
pause
