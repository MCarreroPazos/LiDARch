import os, sys, numpy as np
import json
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

# Cargar configuración si existe
config = None
qgis_path = r'C:\Program Files\QGIS 3.40.14' # Default
config_path = 'vis_config.json'

if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
            config = data.get('config')
            qgis_path = data.get('qgis_path', qgis_path)
            print('      Configuración cargada correctamente.')
    except Exception as e:
        print(f'      Advertencia: No se pudo cargar vis_config.json: {e}')

# 0. Generar Hillshade con GDAL
hs_config = config.get('hillshade', {}) if config else {}
if hs_config.get('enabled', True):
    print('[1/6] Generando Hillshade con GDAL...')
    azim = hs_config.get('azimuth', 315)
    alt = hs_config.get('altitude', 30)
    z = hs_config.get('z_factor', 2)
    print(f'      Azimuth: {azim}°, Altitude: {alt}°, Z-factor: {z}')
    
    import subprocess
    start_time = time.time()
    try:
        # Intentar localizar gdaldem
        gdaldem = os.path.join(qgis_path, 'bin', 'gdaldem.exe')
        if not os.path.exists(gdaldem):
            gdaldem = 'gdaldem' # Fallback to PATH
            
        subprocess.run([
            gdaldem,
            'hillshade',
            input_dem,
            os.path.join(output_dir, 'hillshade.tif'),
            '-z', str(z),
            '-az', str(azim),
            '-alt', str(alt),
            '-compute_edges',
            '-co', 'COMPRESS=DEFLATE',
            '-co', 'TILED=YES'
        ], capture_output=True, text=True, check=True)
        hillshade_time = time.time() - start_time
        print(f'      COMPLETADO en {hillshade_time:.1f} segundos')
    except Exception as e:
        print(f'      ERROR: {e}')
else:
    print('[1/6] Hillshade DESACTIVADO.')

# Configurar RVT
print('')
print('[2/6] Configurando RVT...')
# Intentar localizar el plugin RVT en la ruta estándar de QGIS
rvt_plugin_path = os.path.join(os.environ.get('APPDATA', ''), r'QGIS\QGIS3\profiles\default\python\plugins\rvt-qgis')
if not os.path.exists(rvt_plugin_path):
    # Fallback path del usuario original
    rvt_plugin_path = r'C:\Users\migue\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\rvt-qgis'

if rvt_plugin_path not in sys.path: 
    sys.path.insert(0, rvt_plugin_path)

try:
    import rvt.vis
    print('      RVT importado correctamente!')
except ImportError:
    print('      ERROR: No se pudo importar rvt. Verifique la instalación del plugin RVT en QGIS.')
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
print('')
print('[3/6] Cargando MDT en memoria...')
start_time = time.time()
dem, nd, gt, pj, res = read_geotiff(input_dem)
load_time = time.time() - start_time
print(f'      Cargado en {load_time:.1f} segundos')

if nd is not None:
    dem = np.where(dem == nd, np.nan, dem)

# 1. SLRM
slrm_config = config.get('slrm', {}) if config else {}
if slrm_config.get('enabled', True):
    print('')
    print('[4/6] Generando SLRM (Local Relief Model)...')
    radius = slrm_config.get('radius', 20)
    print(f'      Radio: {radius} celdas')
    try:
        start_time = time.time()
        slrm_out = rvt.vis.slrm(dem, radius_cell=radius, ve_factor=1, no_data=np.nan)
        slrm_time = time.time() - start_time
        save_geotiff(slrm_out, f'{output_dir}/local_relief_model.tif', gt, pj)
        print(f'      COMPLETADO en {slrm_time:.1f} segundos')
    except Exception as e:
        print(f'      ERROR: {e}')
else:
    print('\n[4/6] SLRM DESACTIVADO.')

# 2. SVF
svf_config = config.get('svf', {}) if config else {}
if svf_config.get('enabled', True):
    print('')
    print('[5/6] Generando SVF (Sky View Factor)...')
    r_max = svf_config.get('radius_max', 10)
    n_dir = svf_config.get('n_dir', 16)
    print(f'      Direcciones: {n_dir}, Radio max: {r_max}m')
    try:
        start_time = time.time()
        svf_dict = rvt.vis.sky_view_factor(
            dem=dem, resolution=res, compute_svf=True, compute_asvf=False,
            compute_opns=False, svf_n_dir=n_dir, svf_r_max=r_max, svf_noise=0,
            asvf_dir=315, asvf_level=1, ve_factor=1, no_data=np.nan
        )
        svf_time = time.time() - start_time
        save_geotiff(svf_dict['svf'], f'{output_dir}/sky_view_factor.tif', gt, pj)
        print(f'      COMPLETADO en {svf_time:.1f} segundos')
    except Exception as e:
        print(f'      ERROR: {e}')
else:
    print('\n[5/6] SVF DESACTIVADO.')

# 3. Local Dominance
ld_config = config.get('local_dominance', {}) if config else {}
if ld_config.get('enabled', True):
    print('')
    print('[6/6] Generando Local Dominance...')
    min_r = ld_config.get('min_rad', 15)
    max_r = ld_config.get('max_rad', 25)
    print(f'      Radio: {min_r}-{max_r}m, Incremento: 1m')
    try:
        start_time = time.time()
        ld_out = rvt.vis.local_dominance(
            dem=dem, min_rad=min_r, max_rad=max_r, rad_inc=1,
            angular_res=15, observer_height=1.7, ve_factor=1, no_data=np.nan
        )
        ld_time = time.time() - start_time
        save_geotiff(ld_out, f'{output_dir}/local_dominance.tif', gt, pj)
        print(f'      COMPLETADO en {ld_time:.1f} segundos')
    except Exception as e:
        print(f'      ERROR: {e}')
else:
    print('\n[6/6] Local Dominance DESACTIVADO.')

print('')
print('=' * 60)
print('PROCESO COMPLETADO!')
print('=' * 60)
