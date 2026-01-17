@echo off
setlocal enabledelayedexpansion
echo ========================================
echo PASO 4: Interpolacion SAGA GIS (PDAL Import Grid)
echo ========================================
echo.

REM Crear carpetas necesarias
if not exist "MDT_geotiff" mkdir MDT_geotiff
if not exist "temp_saga" mkdir temp_saga

REM Inicializar entorno OSGeo4W (incluye todas las DLLs necesarias)
call "C:\Program Files\QGIS 3.40.14\bin\o4w_env.bat"

REM Configurar SAGA
set "SAGA_PATH=C:\Program Files\QGIS 3.40.14\apps\saga"
set "SAGA_MLB=%SAGA_PATH%\tools"
set "PATH=%SAGA_PATH%;%PATH%"

set "GDAL_BUILDVRT=C:\Program Files\QGIS 3.40.14\bin\gdalbuildvrt.exe"
set "GDAL_TRANSLATE=C:\Program Files\QGIS 3.40.14\bin\gdal_translate.exe"

echo Importando grids desde archivos LAS con SAGA PDAL...
echo Metodo: Import Grid from Point Cloud
echo Agregacion: Mean value
echo Resolucion: 1 metro
echo.

REM Procesar cada archivo LAS
set /a counter=1
for %%f in (only_terrain\*.las) do (
    echo Procesando %%~nf...
    "%SAGA_PATH%\saga_cmd.exe" io_pdal 2 -FILES "%CD%\%%f" -TARGET_DEFINITION 0 -TARGET_USER_SIZE 1 -TARGET_USER_FITS 1 -AGGREGATION 4 -GRID "%CD%\temp_saga\grid_!counter!.sgrd"
    set /a counter+=1
)

echo.
echo Convirtiendo grids SAGA a GeoTIFF...
echo.

REM Convertir cada grid a GeoTIFF
for %%f in (temp_saga\*.sgrd) do (
    echo Convirtiendo %%~nf...
    "%SAGA_PATH%\saga_cmd.exe" io_gdal 2 -GRIDS "%CD%\%%f" -FILE "%CD%\temp_saga\%%~nf.tif"
)

REM Volver al directorio de trabajo
cd /d "%~dp0"

echo.
echo Mergeando GeoTIFFs con GDAL...
echo.

REM Verificar archivos generados
set "TIF_COUNT=0"
for %%f in (temp_saga\*.tif) do set /a TIF_COUNT+=1

if %TIF_COUNT% EQU 0 (
    echo ERROR: No se generaron archivos TIF.
    echo Verifica que SAGA se ejecuto correctamente.
    pause
    exit /b 1
)

echo Se generaron %TIF_COUNT% archivos TIF
echo.

REM Crear lista de archivos
for %%f in (temp_saga\*.tif) do echo %CD%\%%f >> temp_saga\tiflist.txt

REM Mergear
"%GDAL_BUILDVRT%" -input_file_list temp_saga\tiflist.txt MDT_geotiff\MDT_temp.vrt
"%GDAL_TRANSLATE%" -of GTiff -co COMPRESS=DEFLATE -co TILED=YES MDT_geotiff\MDT_temp.vrt MDT_geotiff\MDT_raw.tif

echo.
echo Rellenando gaps con GDAL fillnodata...
echo Esto puede tardar varios minutos...
echo.

REM Rellenar areas sin datos usando Python de QGIS
echo import sys; from osgeo import gdal; import os > fill_temp.py
echo print('Rellenando gaps del MDT...'); input_path = 'MDT_geotiff/MDT_raw.tif'; output_path = 'MDT_geotiff/MDT_merged.tif' >> fill_temp.py
echo if not os.path.exists(input_path): sys.exit(1) >> fill_temp.py
echo src_ds = gdal.Open(input_path); src_band = src_ds.GetRasterBand(1) >> fill_temp.py
echo driver = gdal.GetDriverByName('GTiff'); dst_ds = driver.CreateCopy(output_path, src_ds, options=['COMPRESS=DEFLATE', 'TILED=YES']) >> fill_temp.py
echo dst_band = dst_ds.GetRasterBand(1); gdal.FillNodata(targetBand=dst_band, maskBand=None, maxSearchDist=100, smoothingIterations=1) >> fill_temp.py
echo dst_ds = None; src_ds = None >> fill_temp.py

call "C:\Program Files\QGIS 3.40.14\bin\python-qgis-ltr.bat" fill_temp.py
del fill_temp.py

if not exist "MDT_geotiff\MDT_merged.tif" (
    echo ERROR: Fillnodata fallo.
    pause
    exit /b 1
)

echo.
echo Limpiando archivos temporales...
if exist "MDT_geotiff\MDT_temp.vrt" del MDT_geotiff\MDT_temp.vrt /q
if exist "MDT_geotiff\MDT_raw.tif" del MDT_geotiff\MDT_raw.tif /q
if exist "temp_saga" rmdir /s /q temp_saga

echo.
echo ========================================
echo Interpolacion completada!
echo Archivo final: MDT_geotiff\MDT_merged.tif
echo ========================================
pause
