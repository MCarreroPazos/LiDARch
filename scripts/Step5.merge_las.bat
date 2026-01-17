@echo off
echo ========================================
echo PASO 5: Merge de archivos LAS
echo ========================================
echo.

REM Crear carpeta de salida
if not exist "lidar_merged" mkdir lidar_merged

echo Mergeando todos los archivos LAS de only_terrain...
C:\LASTools\bin\lasmerge64.exe -i only_terrain\*.las -o lidar_merged\merged_cloud.las

echo.
echo Merge completado!
echo Archivo final: lidar_merged\merged_cloud.las
pause
