@echo off
setlocal enabledelayedexpansion
echo ========================================
echo PASO 3: Filtrado de puntos clase 2 (terreno)
echo ========================================
echo.

REM Crear carpeta de salida
if not exist "only_terrain" mkdir only_terrain

echo Filtrando puntos de terreno...
echo.

REM Filtrar y renombrar secuencialmente
set /a counter=1
for %%f in (ground\*.las) do (
    echo Procesando %%~nf...
    C:\LASTools\bin\las2las64.exe -i "%%f" -keep_class 2 -o "only_terrain\only_terrain_!counter!.las"
    set /a counter+=1
)

echo.
echo Filtrado completado!
echo Archivos guardados en: only_terrain
pause
