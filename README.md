# LiDARch - Automated LiDAR Processing Tool

![Version](https://img.shields.io/badge/version-1.6-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Purpose](https://img.shields.io/badge/purpose-Educational-orange.svg)

**LiDARch** is an educational tool that automates LiDAR point cloud processing workflows for archaeological applications. This project was developed as part of academic coursework to demonstrate the integration of existing geospatial tools into a streamlined processing pipeline.

> **Note:** This is an academic project that orchestrates third-party tools (QGIS, SAGA GIS, LAStools, RVT). It is provided for educational purposes only.

**Process LiDAR Data Automatically for Archaeological Purposes**  
*MA in Archaeology and Sciences of Antiquity - USC/CSIC/UDC/UVIGO*

<table>
<tr>
<td width="50%">

### 🔗 GitHub Repository

- [**View on GitHub**](https://github.com/YOUR_USERNAME/LiDARch) - Source code and releases

</td>
<td width="50%">

### 📖 Further Reading

- [**Carrero-Pazos et al. 2023**](https://www.archaeopress.com/Archaeopress/Products/9781803276328)
- [**ZRC SAZU Publication**](https://omp.zrc-sazu.si/zalozba/catalog/book/824)

</td>
</tr>
</table>

---

## 📋 Features

LiDARch automates a **6-step workflow** using industry-standard tools:

1. **LAZ Decompression** - Converts compressed LAZ to LAS format
2. **Ground Classification** - Identifies ground points using LAStools
3. **Ground Filtering** - Extracts Class 2 (ground) points
4. **DTM Interpolation** - Creates Digital Terrain Model via SAGA GIS
5. **Point Cloud Merging** - Combines processed tiles
6. **Archaeological Visualizations** - Generates 4 specialized outputs using RVT

- **Dependency Assistant** - Automatic check and direct links to download QGIS/LAStools
- **Visualization Selection** - Choose which products to generate (Hillshade, SLRM, SVF, LD)
- **Custom Parameters** - Fine-tune RVT settings directly from the GUI
- Modern dark-themed GUI with **Scrollable Interface** for small screens
- Real-time progress tracking with **Dynamic Estimated Time Remaining**
- Hidden background execution of LAStools (no popups)
- Standalone Windows executable (no Python required)

---

## 🚀 Quick Start

### Option 1: Use Pre-built Executable (Recommended)

1. Download `LiDARch.exe` from the repository root
2. Install required third-party software:
   - [**QGIS 3.28+**](https://qgis.org/download/) (includes SAGA GIS)
   - [**LAStools**](https://rapidlasso.de/lastools/)
3. Run `LiDARch.exe` with administrator privileges
4. Select your LiDAR data folder and LAStools path
5. Click "START PROCESSING"

### Option 2: Run from Source

```bash
# Clone repository
git clone https://github.com/yourusername/LiDARch.git
cd LiDARch

# Install dependencies
pip install -r requirements.txt

# Run application
python src/lidarch_main.py
```

---

## 📦 System Requirements

- **Operating System:** Windows 10/11 (64-bit)
- **RAM:** 8GB minimum, 16GB recommended
- **Disk Space:** 50GB free space for processing
- **Required Third-Party Software:**
  - QGIS 3.28+ (includes SAGA GIS)
  - LAStools (any version)

---

## 🛠️ Building from Source

To create the standalone executable:

```bash
# Install build dependencies
pip install -r requirements.txt
pip install pyinstaller

# Run build script
build_executable.bat
```

The executable will be created in the `dist/` folder.

---

## 📊 Output Files

After processing, LiDARch generates:

```
Proyecto_LiDARch_[timestamp]/
├── MDT_geotiff/
│   └── MDT_merged.tif          # Digital Terrain Model
├── RVT_visualizations/
│   ├── hillshade.tif           # Hillshade visualization
│   ├── local_relief_model.tif  # Local Relief Model (SLRM)
│   ├── sky_view_factor.tif     # Sky View Factor
│   └── local_dominance.tif     # Local Dominance
├── lidar_merged/
│   └── merged_cloud.las        # Merged point cloud
└── technical_report.txt        # Processing summary
```

---

## 🎓 Academic Context

**Project Type:** Educational coursework project  
**Institution:** MA in Archaeology and Sciences of Antiquity, USC/CSIC/UDC/UVIGO  
**Course:** Geospatial Technologies in Archaeology  
**Author:** M. Carrero Pazos (miguel.carrero@usc.es)  
**Purpose:** Demonstrate automation of archaeological LiDAR workflows

**Institutional Affiliations:**
- GEPN-AAT (Grupo de Estudios para la Prehistoria del Noroeste - Arqueología, Antigüedad y Territorio)
- CISPAC (Centro de Investigación Interuniversitario das Paisaxes Atlánticas Culturais)

---

## ⚠️ Important Notes

### Educational Use Only
This tool was created for educational purposes to demonstrate workflow automation. It is **not** official software from any institution.

### Third-Party Dependencies
LiDARch is a **wrapper/orchestrator** that automates existing tools:
- Does not replace or modify the underlying software
- Requires proper installation of all dependencies
- Subject to limitations of third-party tools

### LAStools Licensing
- LAStools demo mode has limitations (point count, slight distortion)
- For production use, purchase a [LAStools license](https://rapidlasso.de/lastools/)
- Some tools (las2las, lasmerge) are free for any use

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Third-Party Software:** This tool uses QGIS, SAGA GIS, LAStools, and RVT. Each has its own license. See LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! This is an open educational project.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

**Author:** M. Carrero Pazos  
**Email:** miguel.carrero@usc.es  
**Institution:** USC/CSIC/UDC/UVIGO

---

## 🙏 Acknowledgments

This project integrates the following excellent open-source and commercial tools:

- [**QGIS Project**](https://qgis.org) - Open-source GIS platform
- [**SAGA GIS**](http://www.saga-gis.org) - Terrain analysis tools
- [**LAStools**](https://rapidlasso.de/lastools/) - LiDAR processing utilities by rapidlasso
- [**RVT (Relief Visualization Toolbox)**](https://github.com/EarthObservation/RVT) - Archaeological visualization methods
- [**CustomTkinter**](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework

Special thanks to the developers and maintainers of these tools for making archaeological LiDAR processing accessible.

---

## 📚 Citation

If you use this tool in your research or teaching, please cite:

```
Carrero Pazos, M. (2026). LiDARch: Automated LiDAR Processing Tool for Archaeological Applications. 
Educational project, MA in Archaeology and Sciences of Antiquity, USC/CSIC/UDC/UVIGO.
GitHub: https://github.com/YOUR_USERNAME/LiDARch
```

---

## 🔍 Limitations

- **LAStools Demo Mode:** Point count limits and slight distortions in demo mode
- **Windows Only:** Currently only supports Windows 10/11
- **Manual Dependencies:** Requires manual installation of QGIS and LAStools
- **No Parameter Customization:** Uses fixed parameters for RVT visualizations
- **Educational Tool:** Not intended for production archaeological surveys

---

**Disclaimer:** This software is provided "as is" for educational purposes. Always validate results with professional tools for actual archaeological work.
