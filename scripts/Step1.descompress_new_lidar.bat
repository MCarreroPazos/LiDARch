@echo off
echo ========================================
echo PASO 1: Descompresion LAZ a LAS
echo ========================================
echo.

REM Crear carpeta de salida
if not exist "raw_lidar_las" mkdir raw_lidar_las

echo Descomprimiendo archivos LAZ...
C:\LASTools\bin\las2las64.exe -i raw_lidar_laz\*.laz -olas -odir raw_lidar_las

echo.
echo Descompresion completada!
echo Archivos guardados en: raw_lidar_las
pause
