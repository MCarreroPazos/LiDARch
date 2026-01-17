"""
Software Detector Module
Automatically detects installation paths for QGIS, SAGA GIS, and LAStools
"""

import os
import winreg
from pathlib import Path


class SoftwareDetector:
    def __init__(self):
        self.common_paths = {
            'qgis': [
                r'C:\Program Files\QGIS 3.40.14',
                r'C:\Program Files\QGIS 3.38',
                r'C:\Program Files\QGIS 3.36',
                r'C:\OSGeo4W64',
                r'C:\OSGeo4W',
            ],
            'saga': [
                r'C:\Program Files\QGIS 3.40.14\apps\saga',
                r'C:\Program Files\SAGA',
                r'C:\SAGA-GIS',
            ],
            'lastools': [
                r'C:\LAStools\bin',
                r'C:\Program Files\LAStools\bin',
            ]
        }
        self.download_urls = {
            'qgis': 'https://qgis.org/download/',
            'lastools': 'https://rapidlasso.de/lastools/',
            'rvt': 'https://github.com/EarthObservation/RVT_Python'
        }
    
    def find_qgis(self):
        """Find QGIS installation path"""
        # Check registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\QGIS')
            path, _ = winreg.QueryValueEx(key, 'InstallPath')
            winreg.CloseKey(key)
            if os.path.exists(path):
                return path
        except:
            pass
        
        # Check common paths
        for path in self.common_paths['qgis']:
            if os.path.exists(path):
                return path
        
        # Search Program Files
        program_files = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        ]
        
        for pf in program_files:
            if os.path.exists(pf):
                for item in os.listdir(pf):
                    if 'QGIS' in item.upper():
                        qgis_path = os.path.join(pf, item)
                        if os.path.exists(qgis_path):
                            return qgis_path
        
        return None
    
    def find_saga(self):
        """Find SAGA GIS installation path"""
        # First check within QGIS installation
        qgis_path = self.find_qgis()
        if qgis_path:
            saga_in_qgis = os.path.join(qgis_path, 'apps', 'saga')
            if os.path.exists(saga_in_qgis):
                return saga_in_qgis
        
        # Check common paths
        for path in self.common_paths['saga']:
            if os.path.exists(path):
                return path
        
        # Search Program Files
        program_files = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        ]
        
        for pf in program_files:
            if os.path.exists(pf):
                for item in os.listdir(pf):
                    if 'SAGA' in item.upper():
                        saga_path = os.path.join(pf, item)
                        if os.path.exists(saga_path):
                            return saga_path
        
        return None
    
    def find_lastools(self):
        """Find LAStools installation path"""
        # Check common paths
        for path in self.common_paths['lastools']:
            if os.path.exists(path):
                # Verify las2las.exe exists
                if os.path.exists(os.path.join(path, 'las2las.exe')) or \
                   os.path.exists(os.path.join(path, 'las2las64.exe')):
                    return path
        
        # Check C:\ root
        if os.path.exists(r'C:\LAStools'):
            bin_path = r'C:\LAStools\bin'
            if os.path.exists(bin_path):
                return bin_path
        
        return None
    
    def get_qgis_python(self):
        """Get QGIS Python executable path"""
        qgis_path = self.find_qgis()
        if qgis_path:
            python_bat = os.path.join(qgis_path, 'bin', 'python-qgis-ltr.bat')
            if os.path.exists(python_bat):
                return python_bat
            
            python_bat = os.path.join(qgis_path, 'bin', 'python-qgis.bat')
            if os.path.exists(python_bat):
                return python_bat
        
        return None
    
    def get_saga_cmd(self):
        """Get SAGA command line executable path"""
        saga_path = self.find_saga()
        if saga_path:
            saga_cmd = os.path.join(saga_path, 'saga_cmd.exe')
            if os.path.exists(saga_cmd):
                return saga_cmd
        
        return None
