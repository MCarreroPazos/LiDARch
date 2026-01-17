"""
Workflow Engine Module
Executes the complete 6-step LiDAR processing pipeline
"""

import os
import shutil
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime


class WorkflowEngine:
    def __init__(self, input_folder, lastools_path, qgis_path, saga_path, 
                 progress_callback=None, log_callback=None, vis_config=None):
        self.input_folder = input_folder
        self.lastools_path = lastools_path
        self.qgis_path = qgis_path
        self.saga_path = saga_path
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.vis_config = vis_config
        
        # Create project directory on Desktop
        desktop = Path.home() / "Desktop"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.project_dir = desktop / f"Proyecto_LiDARch_{timestamp}"
        
        # Processing stats
        self.stats = {}
        self.start_time = None
        self.step_times = {}
    
    def log(self, message):
        """Log message via callback"""
        if self.log_callback:
            self.log_callback(message)
    
    def update_progress(self, percentage, message, time_remaining=None):
        """Update progress via callback"""
        if self.progress_callback:
            self.progress_callback(percentage, message, time_remaining)
    
    def execute(self):
        """Execute complete workflow"""
        try:
            self.start_time = time.time()
            self.log("Starting LiDAR processing workflow...")
            
            # Setup project structure
            if not self.setup_project():
                return False
            
            # Execute 6 steps
            steps = [
                (self.step1_decompress, "Step 1: Decompression", 0, 15),
                (self.step2_classify, "Step 2: Ground Classification", 15, 40),
                (self.step3_filter, "Step 3: Ground Filtering", 40, 50),
                (self.step4_interpolate, "Step 4: DTM Interpolation", 50, 75),
                (self.step5_merge, "Step 5: Point Cloud Merging", 75, 85),
                (self.step6_visualize, "Step 6: RVT Visualizations", 85, 100),
            ]
            
            for step_func, step_name, start_pct, end_pct in steps:
                self.log(f"\n{'='*60}")
                self.log(f"{step_name}")
                self.log(f"{'='*60}")
                
                step_start = time.time()
                
                if not step_func(start_pct, end_pct):
                    self.log(f"✗ {step_name} failed")
                    return False
                
                step_time = time.time() - step_start
                self.step_times[step_name] = step_time
                self.log(f"✓ {step_name} completed in {step_time:.1f}s")
            
            # Cleanup temporary files
            self.cleanup()
            
            # Calculate total time
            total_time = time.time() - self.start_time
            self.stats['total_time'] = f"{total_time:.1f} seconds"
            
            return True
            
        except Exception as e:
            self.log(f"✗ Error in workflow: {str(e)}")
            return False
    
    def setup_project(self):
        """Create project directory structure"""
        try:
            self.log(f"Creating project directory: {self.project_dir}")
            self.project_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self.project_dir / "MDT_geotiff").mkdir(exist_ok=True)
            (self.project_dir / "RVT_visualizations").mkdir(exist_ok=True)
            (self.project_dir / "lidar_merged").mkdir(exist_ok=True)
            (self.project_dir / "raw_lidar_las").mkdir(exist_ok=True)
            (self.project_dir / "ground").mkdir(exist_ok=True)
            (self.project_dir / "only_terrain").mkdir(exist_ok=True)
            
            # Detect input file format
            input_files = list(Path(self.input_folder).glob("*.laz")) + \
                         list(Path(self.input_folder).glob("*.las"))
            
            if not input_files:
                self.log("✗ No LAS/LAZ files found in input folder")
                return False
            
            self.stats['input_files'] = len(input_files)
            
            # Determine if LAZ or LAS
            laz_files = list(Path(self.input_folder).glob("*.laz"))
            if laz_files:
                self.stats['file_format'] = 'LAZ (compressed)'
                (self.project_dir / "raw_lidar_laz").mkdir(exist_ok=True)
                
                # Copy LAZ files
                self.log(f"Copying {len(laz_files)} LAZ files...")
                for laz_file in laz_files:
                    shutil.copy2(laz_file, self.project_dir / "raw_lidar_laz" / laz_file.name)
            else:
                self.stats['file_format'] = 'LAS (uncompressed)'
                # Copy LAS files directly
                las_files = list(Path(self.input_folder).glob("*.las"))
                self.log(f"Copying {len(las_files)} LAS files...")
                for las_file in las_files:
                    shutil.copy2(las_file, self.project_dir / "raw_lidar_las" / las_file.name)
            
            return True
            
        except Exception as e:
            self.log(f"✗ Error setting up project: {str(e)}")
            return False
    
    def step1_decompress(self, start_pct, end_pct):
        """Step 1: Decompress LAZ to LAS"""
        try:
            laz_folder = self.project_dir / "raw_lidar_laz"
            las_folder = self.project_dir / "raw_lidar_las"
            
            laz_files = list(laz_folder.glob("*.laz"))
            
            if not laz_files:
                self.log("No LAZ files to decompress, skipping...")
                self.stats['decompressed_files'] = 0
                return True
            
            self.log(f"Decompressing {len(laz_files)} LAZ files...")
            
            las2las = os.path.join(self.lastools_path, "las2las64.exe")
            
            for i, laz_file in enumerate(laz_files):
                output_file = las_folder / f"{laz_file.stem}.las"
                
                cmd = [las2las, "-i", str(laz_file), "-o", str(output_file)]
                subprocess.run(cmd, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Update progress
                progress = start_pct + ((i + 1) / len(laz_files)) * (end_pct - start_pct)
                self.update_progress(int(progress), f"Decompressing file {i+1}/{len(laz_files)}")
            
            self.stats['decompressed_files'] = len(laz_files)
            return True
            
        except Exception as e:
            self.log(f"✗ Decompression error: {str(e)}")
            return False
    
    def step2_classify(self, start_pct, end_pct):
        """Step 2: Ground classification with lasground"""
        try:
            las_folder = self.project_dir / "raw_lidar_las"
            ground_folder = self.project_dir / "ground"
            
            las_files = list(las_folder.glob("*.las"))
            self.log(f"Classifying {len(las_files)} LAS files...")
            
            lasground = os.path.join(self.lastools_path, "lasground64.exe")
            
            for i, las_file in enumerate(las_files):
                output_file = ground_folder / f"ground_{i+1}.las"
                
                cmd = [
                    lasground,
                    "-i", str(las_file),
                    "-o", str(output_file),
                    "-step", "5",
                    "-bulge", "0.5",
                    "-spike", "1",
                    "-offset", "0.05",
                    "-demo"
                ]
                
                result = subprocess.run(cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                # Demo mode returns exit code 1 with warnings, but file is created successfully
                if result.returncode not in [0, 1]:
                    raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
                # Update progress
                progress = start_pct + ((i + 1) / len(las_files)) * (end_pct - start_pct)
                self.update_progress(
                    int(progress),
                    f"Classifying file {i+1}/{len(las_files)}"
                )
            
            self.stats['classified_files'] = len(las_files)
            return True
            
        except Exception as e:
            self.log(f"✗ Classification error: {str(e)}")
            return False
    
    def step3_filter(self, start_pct, end_pct):
        """Step 3: Filter ground points (Class 2)"""
        try:
            ground_folder = self.project_dir / "ground"
            terrain_folder = self.project_dir / "only_terrain"
            
            ground_files = list(ground_folder.glob("*.las"))
            self.log(f"Filtering {len(ground_files)} files for ground points...")
            
            las2las = os.path.join(self.lastools_path, "las2las64.exe")
            
            for i, ground_file in enumerate(ground_files):
                output_file = terrain_folder / f"only_terrain_{i+1}.las"
                
                cmd = [
                    las2las,
                    "-i", str(ground_file),
                    "-o", str(output_file),
                    "-keep_class", "2"
                ]
                
                subprocess.run(cmd, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                progress = start_pct + ((i + 1) / len(ground_files)) * (end_pct - start_pct)
                self.update_progress(int(progress), f"Filtering file {i+1}/{len(ground_files)}")
            
            self.stats['filtered_files'] = len(ground_files)
            return True
            
        except Exception as e:
            self.log(f"✗ Filtering error: {str(e)}")
            return False
    
    def step4_interpolate(self, start_pct, end_pct):
        """Step 4: SAGA interpolation and DTM generation (original working method)"""
        try:
            self.log("Running SAGA GIS interpolation...")
            
            # Setup paths
            terrain_folder = self.project_dir / "only_terrain"
            temp_saga = self.project_dir / "temp_saga"
            mdt_folder = self.project_dir / "MDT_geotiff"
            temp_saga.mkdir(exist_ok=True)
            
            # Get tool paths
            o4w_env = os.path.join(self.qgis_path, "bin", "o4w_env.bat")
            saga_cmd = os.path.join(self.saga_path, "saga_cmd.exe")
            gdal_buildvrt = os.path.join(self.qgis_path, "bin", "gdalbuildvrt.exe")
            gdal_translate = os.path.join(self.qgis_path, "bin", "gdal_translate.exe")
            qgis_python = os.path.join(self.qgis_path, "bin", "python-qgis-ltr.bat")
            
            # Get terrain files
            terrain_files = list(terrain_folder.glob("*.las"))
            self.log(f"Interpolating {len(terrain_files)} files...")
            
            # Step 4a: Import grids from LAS using SAGA io_pdal
            self.update_progress(start_pct + 5, "Importing grids from point clouds...")
            
            for i, las_file in enumerate(terrain_files):
                grid_output = temp_saga / f"grid_{i+1}.sgrd"
                
                # Create batch script that initializes OSGeo4W environment then runs SAGA
                batch_script = self.project_dir / f"saga_import_{i+1}.bat"
                batch_content = f"""@echo off
call "{o4w_env}"
set "SAGA_PATH={self.saga_path}"
set "SAGA_MLB=%SAGA_PATH%\\tools"
set "PATH=%SAGA_PATH%;%PATH%"
"{saga_cmd}" io_pdal 2 -FILES "{las_file}" -TARGET_DEFINITION 0 -TARGET_USER_SIZE 1 -TARGET_USER_FITS 1 -AGGREGATION 4 -GRID "{grid_output}"
"""
                
                with open(batch_script, 'w') as f:
                    f.write(batch_content)
                
                # Run the batch script
                result = subprocess.run([str(batch_script)], shell=True, capture_output=True, text=True, cwd=str(self.project_dir))
                
                if result.returncode != 0:
                    self.log(f"✗ SAGA import failed for {las_file.name}")
                    self.log(f"Error: {result.stderr}")
                    continue
                
                if i % 10 == 0 or (i + 1) == len(terrain_files):
                    progress = start_pct + 5 + ((i + 1) / len(terrain_files)) * 15
                    self.update_progress(int(progress), f"Importing grid {i+1}/{len(terrain_files)}")
            
            # Step 4b: Convert SAGA grids to GeoTIFF
            self.update_progress(start_pct + 20, "Converting grids to GeoTIFF...")
            grid_files = list(temp_saga.glob("*.sgrd"))
            
            if not grid_files:
                self.log("✗ No SAGA grids were created")
                return False
            
            for i, grid_file in enumerate(grid_files):
                tif_output = temp_saga / f"{grid_file.stem}.tif"
                
                # Create batch script for conversion
                batch_script = self.project_dir / f"saga_convert_{i+1}.bat"
                batch_content = f"""@echo off
call "{o4w_env}"
set "SAGA_PATH={self.saga_path}"
set "SAGA_MLB=%SAGA_PATH%\\tools"
set "PATH=%SAGA_PATH%;%PATH%"
"{saga_cmd}" io_gdal 2 -GRIDS "{grid_file}" -FILE "{tif_output}"
"""
                
                with open(batch_script, 'w') as f:
                    f.write(batch_content)
                
                subprocess.run([str(batch_script)], shell=True, capture_output=True, cwd=str(self.project_dir))
            
            # Step 4c: Merge GeoTIFFs
            self.update_progress(start_pct + 22, "Merging GeoTIFFs...")
            tif_files = list(temp_saga.glob("*.tif"))
            
            if not tif_files:
                self.log("✗ No GeoTIFF files were created")
                return False
            
            # Create file list
            tif_list = temp_saga / "tiflist.txt"
            with open(tif_list, 'w') as f:
                for tif in tif_files:
                    f.write(f"{tif.absolute()}\n")
            
            vrt_file = mdt_folder / "MDT_temp.vrt"
            raw_dtm = mdt_folder / "MDT_raw.tif"
            
            cmd = [gdal_buildvrt, "-input_file_list", str(tif_list), str(vrt_file)]
            subprocess.run(cmd, check=True, capture_output=True)
            subprocess.run(cmd, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            cmd = [
                gdal_translate,
                "-of", "GTiff",
                "-co", "COMPRESS=DEFLATE",
                "-co", "TILED=YES",
                str(vrt_file),
                str(raw_dtm)
            ]
            subprocess.run(cmd, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Step 4d: Fill gaps
            self.update_progress(start_pct + 24, "Filling data gaps...")
            dtm_file = mdt_folder / "MDT_merged.tif"
            
            fill_script = self.project_dir / "fill_gaps.py"
            fill_code = f"""
import sys
from osgeo import gdal
import os

print('Rellenando gaps del MDT...')
input_path = r'{raw_dtm}'
output_path = r'{dtm_file}'

if not os.path.exists(input_path):
    print('Error: Input file not found')
    sys.exit(1)

src_ds = gdal.Open(input_path)
src_band = src_ds.GetRasterBand(1)

driver = gdal.GetDriverByName('GTiff')
dst_ds = driver.CreateCopy(output_path, src_ds, options=['COMPRESS=DEFLATE', 'TILED=YES'])
dst_band = dst_ds.GetRasterBand(1)

gdal.FillNodata(targetBand=dst_band, maskBand=None, maxSearchDist=100, smoothingIterations=1)

dst_ds = None
src_ds = None
print('Gap filling complete')
"""
            
            with open(fill_script, 'w') as f:
                f.write(fill_code)
            
            subprocess.run([qgis_python, str(fill_script)], check=True, capture_output=True)
            
            # Clean up temporary files
            if vrt_file.exists():
                vrt_file.unlink()
            if raw_dtm.exists():
                raw_dtm.unlink()
            
            # Verify output
            if dtm_file.exists():
                size_mb = dtm_file.stat().st_size / (1024 * 1024)
                self.stats['dtm_size'] = f"{size_mb:.1f} MB"
                self.log(f"DTM created: {size_mb:.1f} MB")
                return True
            else:
                self.log("✗ DTM file not created")
                return False
            
        except Exception as e:
            self.log(f"✗ Interpolation error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def step5_merge(self, start_pct, end_pct):
        """Step 5: Merge all LAS files"""
        try:
            terrain_folder = self.project_dir / "only_terrain"
            merged_folder = self.project_dir / "lidar_merged"
            
            terrain_files = list(terrain_folder.glob("*.las"))
            self.log(f"Merging {len(terrain_files)} LAS files...")
            
            lasmerge = os.path.join(self.lastools_path, "lasmerge64.exe")
            output_file = merged_folder / "merged_cloud.las"
            
            cmd = [lasmerge, "-i"] + [str(f) for f in terrain_files] + ["-o", str(output_file)]
            
            result = subprocess.run(cmd, capture_output=True)
            # Demo mode returns exit code 1 with warnings, but file is created successfully
            if result.returncode not in [0, 1]:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

            
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                self.stats['merged_size'] = f"{size_mb:.1f} MB"
            
            self.update_progress(end_pct, "Point cloud merging complete")
            return True
            
        except Exception as e:
            self.log(f"✗ Merging error: {str(e)}")
            return False
    
    def step6_visualize(self, start_pct, end_pct):
        """Step 6: Generate RVT visualizations"""
        try:
            self.log("Generating archaeological visualizations...")
            
            # Get RVT script from embedded resources
            import sys
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_path = sys._MEIPASS
            else:
                # Running as script
                base_path = Path(__file__).parent
            
            source_script = Path(base_path) / "rvt_monitored.py"
            rvt_script = self.project_dir / "rvt_visualizations.py"
            
            if source_script.exists():
                shutil.copy2(source_script, rvt_script)
                self.log("RVT script copied successfully")
            else:
                self.log("Warning: rvt_monitored.py not found in resources")
                return False
            
            # Create vis_config.json in project dir
            if self.vis_config:
                config_file = self.project_dir / "vis_config.json"
                with open(config_file, 'w') as f:
                    json.dump({
                        "config": self.vis_config,
                        "qgis_path": str(self.qgis_path)
                    }, f, indent=4)
                self.log("Visualization configuration saved")
            
            # Run RVT script with QGIS Python
            qgis_python = os.path.join(self.qgis_path, "bin", "python-qgis-ltr.bat")
            
            if not os.path.exists(qgis_python):
                qgis_python = os.path.join(self.qgis_path, "bin", "python-qgis.bat")
            
            self.log(f"Running RVT script with: {qgis_python}")
            self.update_progress(start_pct + 2, "Starting RVT visualizations...")
            
            process = subprocess.Popen(
                [qgis_python, str(rvt_script)],
                cwd=str(self.project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor progress with periodic updates
            update_interval = 0
            while process.poll() is None:
                time.sleep(10)
                update_interval += 10
                
                # Update every 30 seconds
                if update_interval % 30 == 0:
                    progress = start_pct + min(10, update_interval // 30)
                    self.update_progress(int(progress), "Generating visualizations...")
            
            # Check if process completed successfully
            if process.returncode != 0:
                stderr = process.stderr.read() if process.stderr else ""
                self.log(f"RVT process failed with code {process.returncode}")
                self.log(f"Error: {stderr}")
                return False
            
            # Verify outputs
            viz_folder = self.project_dir / "RVT_visualizations"
            expected_files = ["hillshade.tif", "local_relief_model.tif", 
                            "sky_view_factor.tif", "local_dominance.tif"]
            
            all_found = True
            for viz_file in expected_files:
                file_path = viz_folder / viz_file
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    self.stats[f"{viz_file.replace('.tif', '')}_size"] = f"{size_mb:.1f} MB"
                    self.log(f"  ✓ {viz_file}: {size_mb:.1f} MB")
                else:
                    self.log(f"  ✗ {viz_file}: NOT FOUND")
                    all_found = False
            
            self.update_progress(end_pct, "Visualizations complete")
            return all_found
            
        except Exception as e:
            self.log(f"✗ Visualization error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def cleanup(self):
        """Remove temporary files and folders"""
        try:
            self.log("\nCleaning up temporary files...")
            
            temp_folders = ["ground", "only_terrain", "raw_lidar_laz", "temp_saga"]
            
            for folder_name in temp_folders:
                folder_path = self.project_dir / folder_name
                if folder_path.exists():
                    shutil.rmtree(folder_path)
                    self.log(f"  Removed: {folder_name}/")
            
            # Remove temporary scripts
            for script in self.project_dir.glob("*.bat"):
                script.unlink()
                self.log(f"  Removed: {script.name}")
            
            for script in self.project_dir.glob("rvt_*.py"):
                script.unlink()
                self.log(f"  Removed: {script.name}")
            
            # Remove fill_gaps.py and SAGA scripts
            fill_gaps = self.project_dir / "fill_gaps.py"
            if fill_gaps.exists():
                fill_gaps.unlink()
                self.log(f"  Removed: fill_gaps.py")
            
            for script in self.project_dir.glob("saga_*.bat"):
                script.unlink()
                self.log(f"  Removed: {script.name}")
            
            # Remove vis_config.json
            vis_config = self.project_dir / "vis_config.json"
            if vis_config.exists():
                vis_config.unlink()
                self.log(f"  Removed: vis_config.json")
            
            self.log("✓ Cleanup complete")
            
        except Exception as e:
            self.log(f"⚠ Cleanup warning: {str(e)}")
    
    def get_processing_stats(self):
        """Return processing statistics"""
        return self.stats
