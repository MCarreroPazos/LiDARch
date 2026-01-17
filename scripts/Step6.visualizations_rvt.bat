@echo off
echo ========================================
echo PASO 6: Visualizaciones RVT y Hillshade
echo ========================================
echo.
echo Generando visualizaciones optimizadas para ARQUEOLOGIA...
echo.

REM Ejecutar script RVT mejorado (incluye Hillshade con GDAL)
"C:\Program Files\QGIS 3.40.14\bin\python-qgis-ltr.bat" rvt_monitored.py

echo.
echo Proceso completado con exito!
echo Visualizaciones disponibles en la carpeta RVT_visualizations
pause
