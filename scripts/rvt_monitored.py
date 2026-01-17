import os, sys, numpy as np
from osgeo import gdal
import time

print('=' * 60)
print('INICIANDO GENERACION DE VISUALIZACIONES RVT + HILLSHADE')
print('=' * 60)
print('')

# Configurar directorios
input_dem = os.path.abspath('MDT_geotiff/MDT_merged.tif')
output_dir = os.path.abspath('RVT_visualizations')
os.makedirs(output_dir, exist_ok=True)

# 0. Generar Hillshade con GDAL (rápido y estable)
print('[1/6] Generando Hillshade con GDAL...')
print('      Azimuth: 315°, Altitude: 30°, Z-factor: 2')
import subprocess
start_time = time.time()
try:
    # Usar rutas absolutas para evitar errores de directorio
    result = subprocess.run([
        r'C:\Program Files\QGIS 3.40.14\bin\gdaldem.exe',
        'hillshade',
        input_dem,
        os.path.join(output_dir, 'hillshade.tif'),
        '-z', '2',
        '-az', '315',
        '-alt', '30',
        '-compute_edges',
        '-co', 'COMPRESS=DEFLATE',
        '-co', 'TILED=YES'
    ], capture_output=True, text=True, check=True)
    hillshade_time = time.time() - start_time
    print(f'      COMPLETADO en {hillshade_time:.1f} segundos')
except Exception as e:
    print(f'      ERROR: {e}')

# Configurar RVT
print('')
print('[2/6] Configurando RVT...')
rvt_path = r'C:\Users\migue\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\rvt-qgis'
if rvt_path not in sys.path: 
    sys.path.insert(0, rvt_path)

try:
    import rvt.vis
    print('      RVT importado correctamente!')
except ImportError:
    print('      ERROR: No se pudo importar rvt.')
    sys.exit(1)

def read_geotiff(path):
    ds = gdal.Open(path)
    b = ds.GetRasterBand(1)
    a = b.ReadAsArray()
    nd = b.GetNoDataValue()
    gt = ds.GetGeoTransform()
    pj = ds.GetProjection()
    res = gt[1]
    return a, nd, gt, pj, res

def save_geotiff(arr, path, gt, pj, nd=-9999):
    d = gdal.GetDriverByName('GTiff')
    if len(arr.shape) == 3:
        nb, r, c = arr.shape
    else:
        nb = 1
        r, c = arr.shape
    
    ds = d.Create(path, c, r, nb, gdal.GDT_Float32, options=['COMPRESS=DEFLATE', 'TILED=YES'])
    ds.SetGeoTransform(gt)
    ds.SetProjection(pj)
    
    if nb > 1:
        for i in range(nb):
            b = ds.GetRasterBand(i+1)
            b.WriteArray(arr[i])
            b.SetNoDataValue(nd)
    else:
        b = ds.GetRasterBand(1)
        b.WriteArray(arr)
        b.SetNoDataValue(nd)
    
    ds = None

# Procesar MDT
# input_dem y output_dir ya definidos arriba

print('')
print('[3/6] Cargando MDT en memoria...')
print('      Archivo: MDT_geotiff/MDT_merged.tif')
start_time = time.time()
dem, nd, gt, pj, res = read_geotiff(input_dem)
load_time = time.time() - start_time
print(f'      Cargado en {load_time:.1f} segundos')
print(f'      Dimensiones: {dem.shape[0]} x {dem.shape[1]} pixeles')
print(f'      Resolucion: {res} metros')

if nd is not None:
    dem = np.where(dem == nd, np.nan, dem)

# 1. SLRM
print('')
print('[4/6] Generando SLRM (Local Relief Model)...')
print('      Radio: 20 celdas')
try:
    start_time = time.time()
    slrm_out = rvt.vis.slrm(dem, radius_cell=20, ve_factor=1, no_data=np.nan)
    slrm_time = time.time() - start_time
    save_geotiff(slrm_out, f'{output_dir}/local_relief_model.tif', gt, pj)
    print(f'      COMPLETADO en {slrm_time:.1f} segundos')
except Exception as e:
    print(f'      ERROR: {e}')

# 2. SVF
print('')
print('[5/6] Generando SVF (Sky View Factor)...')
print('      Direcciones: 16, Radio max: 10m')
try:
    start_time = time.time()
    svf_dict = rvt.vis.sky_view_factor(
        dem=dem, resolution=res, compute_svf=True, compute_asvf=False,
        compute_opns=False, svf_n_dir=16, svf_r_max=10, svf_noise=0,
        asvf_dir=315, asvf_level=1, ve_factor=1, no_data=np.nan
    )
    svf_time = time.time() - start_time
    save_geotiff(svf_dict['svf'], f'{output_dir}/sky_view_factor.tif', gt, pj)
    print(f'      COMPLETADO en {svf_time:.1f} segundos')
except Exception as e:
    print(f'      ERROR: {e}')

# 3. Local Dominance
print('')
print('[6/6] Generando Local Dominance...')
print('      Radio: 15-25m, Incremento: 1m')
try:
    start_time = time.time()
    ld_out = rvt.vis.local_dominance(
        dem=dem, min_rad=15, max_rad=25, rad_inc=1,
        angular_res=15, observer_height=1.7, ve_factor=1, no_data=np.nan
    )
    ld_time = time.time() - start_time
    save_geotiff(ld_out, f'{output_dir}/local_dominance.tif', gt, pj)
    print(f'      COMPLETADO en {ld_time:.1f} segundos')
except Exception as e:
    print(f'      ERROR: {e}')

print('')
print('=' * 60)
print('PROCESO COMPLETADO!')
print('=' * 60)
