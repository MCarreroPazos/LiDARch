"""
Report Generator Module
Creates technical specification reports for processed LiDAR data
"""

import os
from datetime import datetime


class ReportGenerator:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.report_path = os.path.join(project_dir, 'technical_report.txt')
    
    def generate_report(self, stats):
        """Generate comprehensive technical report"""
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("LiDARch - Technical Processing Report")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Project Information
        report_lines.append("PROJECT INFORMATION")
        report_lines.append("-" * 80)
        report_lines.append(f"Project Directory: {self.project_dir}")
        report_lines.append(f"Input Files: {stats.get('input_files', 'N/A')}")
        report_lines.append(f"File Format: {stats.get('file_format', 'N/A')}")
        report_lines.append(f"Total Processing Time: {stats.get('total_time', 'N/A')}")
        report_lines.append("")
        
        # Step 1: Decompression
        report_lines.append("STEP 1: LAZ DECOMPRESSION")
        report_lines.append("-" * 80)
        report_lines.append("Tool: LAStools (las2las64.exe)")
        report_lines.append("Purpose: Convert compressed LAZ files to LAS format")
        report_lines.append(f"Files Processed: {stats.get('decompressed_files', 'N/A')}")
        report_lines.append(f"Processing Time: {stats.get('step1_time', 'N/A')}")
        report_lines.append("")
        
        # Step 2: Ground Classification
        report_lines.append("STEP 2: GROUND CLASSIFICATION")
        report_lines.append("-" * 80)
        report_lines.append("Tool: LAStools (lasground64.exe)")
        report_lines.append("Algorithm: Progressive TIN Densification")
        report_lines.append("Parameters:")
        report_lines.append("  - Step size: 5 meters")
        report_lines.append("  - Bulge: 0.5 meters")
        report_lines.append("  - Spike: 1.0 meters")
        report_lines.append("  - Offset: 0.05 meters")
        report_lines.append(f"Files Processed: {stats.get('classified_files', 'N/A')}")
        report_lines.append(f"Processing Time: {stats.get('step2_time', 'N/A')}")
        report_lines.append("")
        
        # Step 3: Ground Point Filtering
        report_lines.append("STEP 3: GROUND POINT FILTERING")
        report_lines.append("-" * 80)
        report_lines.append("Tool: LAStools (las2las64.exe)")
        report_lines.append("Filter: Keep only Class 2 (Ground) points")
        report_lines.append(f"Files Processed: {stats.get('filtered_files', 'N/A')}")
        report_lines.append(f"Processing Time: {stats.get('step3_time', 'N/A')}")
        report_lines.append("")
        
        # Step 4: DTM Interpolation
        report_lines.append("STEP 4: DTM INTERPOLATION")
        report_lines.append("-" * 80)
        report_lines.append("Tool: SAGA GIS (via QGIS)")
        report_lines.append("Method: PDAL Import Grid from Point Cloud")
        report_lines.append("Interpolation Parameters:")
        report_lines.append("  - Value Aggregation: Mean")
        report_lines.append("  - Cell Size: 1 meter")
        report_lines.append("  - Rounding: Enabled")
        report_lines.append("  - Fit: Cells")
        report_lines.append("")
        report_lines.append("Post-Processing:")
        report_lines.append("  - Grid to GeoTIFF conversion (GDAL)")
        report_lines.append("  - Mosaic merging with gdalbuildvrt + gdal_translate")
        report_lines.append("  - Gap filling with gdal fillnodata")
        report_lines.append(f"Output: MDT_merged.tif ({stats.get('dtm_size', 'N/A')})")
        report_lines.append(f"Processing Time: {stats.get('step4_time', 'N/A')}")
        report_lines.append("")
        
        # Step 5: LAS Merging
        report_lines.append("STEP 5: POINT CLOUD MERGING")
        report_lines.append("-" * 80)
        report_lines.append("Tool: LAStools (lasmerge64.exe)")
        report_lines.append("Purpose: Combine all ground-classified point clouds")
        report_lines.append(f"Output: merged_cloud.las ({stats.get('merged_size', 'N/A')})")
        report_lines.append(f"Processing Time: {stats.get('step5_time', 'N/A')}")
        report_lines.append("")
        
        # Step 6: Archaeological Visualizations
        report_lines.append("STEP 6: ARCHAEOLOGICAL VISUALIZATIONS")
        report_lines.append("-" * 80)
        report_lines.append("Tool: Relief Visualization Toolbox (RVT) + GDAL")
        report_lines.append("")
        
        report_lines.append("6.1 Hillshade")
        report_lines.append("  Tool: GDAL (gdaldem hillshade)")
        report_lines.append("  Parameters:")
        report_lines.append("    - Azimuth: 315°")
        report_lines.append("    - Altitude: 30°")
        report_lines.append("    - Z-factor: 2")
        report_lines.append("    - Compute edges: Yes")
        report_lines.append(f"  Output: hillshade.tif ({stats.get('hillshade_size', 'N/A')})")
        report_lines.append(f"  Processing Time: {stats.get('hillshade_time', 'N/A')}")
        report_lines.append("")
        
        report_lines.append("6.2 Simple Local Relief Model (SLRM)")
        report_lines.append("  Tool: RVT (rvt.vis.slrm)")
        report_lines.append("  Parameters:")
        report_lines.append("    - Radius: 20 cells")
        report_lines.append("    - Vertical exaggeration: 1")
        report_lines.append(f"  Output: local_relief_model.tif ({stats.get('slrm_size', 'N/A')})")
        report_lines.append(f"  Processing Time: {stats.get('slrm_time', 'N/A')}")
        report_lines.append("")
        
        report_lines.append("6.3 Sky View Factor (SVF)")
        report_lines.append("  Tool: RVT (rvt.vis.sky_view_factor)")
        report_lines.append("  Parameters:")
        report_lines.append("    - Number of directions: 16")
        report_lines.append("    - Maximum radius: 10 meters")
        report_lines.append("    - Noise removal: 0")
        report_lines.append(f"  Output: sky_view_factor.tif ({stats.get('svf_size', 'N/A')})")
        report_lines.append(f"  Processing Time: {stats.get('svf_time', 'N/A')}")
        report_lines.append("")
        
        report_lines.append("6.4 Local Dominance")
        report_lines.append("  Tool: RVT (rvt.vis.local_dominance)")
        report_lines.append("  Parameters:")
        report_lines.append("    - Minimum radius: 15 meters")
        report_lines.append("    - Maximum radius: 25 meters")
        report_lines.append("    - Radius increment: 1 meter")
        report_lines.append("    - Angular resolution: 15°")
        report_lines.append("    - Observer height: 1.7 meters")
        report_lines.append(f"  Output: local_dominance.tif ({stats.get('ld_size', 'N/A')})")
        report_lines.append(f"  Processing Time: {stats.get('ld_time', 'N/A')}")
        report_lines.append("")
        
        # Output Summary
        report_lines.append("OUTPUT SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append("Final Deliverables:")
        report_lines.append("  1. MDT_geotiff/")
        report_lines.append("     - MDT_merged.tif (1m resolution Digital Terrain Model)")
        report_lines.append("  2. RVT_visualizations/")
        report_lines.append("     - hillshade.tif")
        report_lines.append("     - local_relief_model.tif")
        report_lines.append("     - sky_view_factor.tif")
        report_lines.append("     - local_dominance.tif")
        report_lines.append("  3. lidar_merged/")
        report_lines.append("     - merged_cloud.las (Unified ground point cloud)")
        report_lines.append("")
        
        # Software Versions
        report_lines.append("SOFTWARE INFORMATION")
        report_lines.append("-" * 80)
        report_lines.append(f"LAStools: {stats.get('lastools_version', 'N/A')}")
        report_lines.append(f"QGIS: {stats.get('qgis_version', 'N/A')}")
        report_lines.append(f"SAGA GIS: {stats.get('saga_version', 'N/A')}")
        report_lines.append(f"GDAL: {stats.get('gdal_version', 'N/A')}")
        report_lines.append(f"RVT: {stats.get('rvt_version', 'N/A')}")
        report_lines.append("")
        
        # Credits
        report_lines.append("=" * 80)
        report_lines.append("LiDARch - Automated LiDAR Processing Tool")
        report_lines.append("Developed by: M. Carrero Pazos (miguel.carrero@usc.es)")
        report_lines.append("Institution: M.U. Arqueología y Ciencias de la Antigüedad")
        report_lines.append("             USC/CSIC/UDC/UVIGO")
        report_lines.append("Course: Tecnologías Geoespaciales")
        report_lines.append("=" * 80)
        
        # Write report
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        return self.report_path
