"""
LiDARch - Automated LiDAR Processing Tool for Archaeological purposes
Main Application Entry Point

Author: M. Carrero Pazos (miguel.carrero@usc.es)
Institution: MU in Archaeology and Sciences of Antiquity
             USC/CSIC/UDC/UVIGO
Course: Geospatial Technologies in Archaeology
"""

import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
import threading
import time
import webbrowser
from datetime import datetime

from software_detector import SoftwareDetector
from workflow_engine import WorkflowEngine
from report_generator import ReportGenerator


class LiDARchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("LiDARch - Automated LiDAR Processing")
        self.geometry("900x800")
        self.resizable(True, True)
        self.minsize(900, 800)  # Minimum size to ensure all elements are visible
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.input_folder = tk.StringVar()
        self.lastools_path = tk.StringVar()
        self.processing = False
        
        # RVT Visualization Settings
        self.vis_hillshade = tk.BooleanVar(value=True)
        self.vis_slrm = tk.BooleanVar(value=True)
        self.vis_svf = tk.BooleanVar(value=True)
        self.vis_ld = tk.BooleanVar(value=True)
        
        # RVT Parameters
        self.hs_azimuth = tk.StringVar(value="315")
        self.hs_altitude = tk.StringVar(value="30")
        self.hs_zfactor = tk.StringVar(value="2")
        self.slrm_radius = tk.StringVar(value="20")
        self.svf_radius = tk.StringVar(value="10")
        self.svf_dir = tk.StringVar(value="16")
        self.ld_min_rad = tk.StringVar(value="15")
        self.ld_max_rad = tk.StringVar(value="25")
        
        # Initialize components
        self.detector = SoftwareDetector()
        self.workflow = None
        
        self.create_widgets()
        self.check_dependencies()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Header Frame
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="LiDARch",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#00d4ff"
        )
        title_label.pack(pady=(20, 5))
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Process LiDAR Data Automatically for Archaeological purposes",
            font=ctk.CTkFont(size=14),
            text_color="#a0a0a0"
        )
        subtitle_label.pack(pady=(0, 5))
        
        institution_label = ctk.CTkLabel(
            header_frame,
            text="MA in Archaeology and Sciences of Antiquity\n Geospatial Technologies in Archaeology",
            font=ctk.CTkFont(size=10),
            text_color="#707070"
        )
        institution_label.pack(pady=(0, 5))
        
        description_label = ctk.CTkLabel(
            header_frame,
            text="Uses QGIS, SAGA GIS, LASTools and RVT to generate a DTM and 4 specialized archaeological visualizations\n(local dominance, sky view factor, local relief model, and hillshade)\n Needs preinstalled QGIS, SAGA GIS, LASTools and RVT",
            font=ctk.CTkFont(size=9),
            text_color="#606060"
        )
        description_label.pack(pady=(0, 10))
        
        author_label = ctk.CTkLabel(
            header_frame,
            text="Developed by M. Carrero Pazos (miguel.carrero@usc.es)\n for educational purposes",
            font=ctk.CTkFont(size=9),
            text_color="#505050"
        )
        author_label.pack(pady=(0, 15))
        
        # Main Content Scrollable Frame
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Inner Content Frame (to maintain padding)
        content_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Input Folder Selection
        input_label = ctk.CTkLabel(
            content_frame,
            text="LiDAR Data Folder (LAS/LAZ files):",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        input_label.pack(anchor="w", pady=(10, 5))
        
        input_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        input_container.pack(fill="x", pady=(0, 15))
        
        self.input_entry = ctk.CTkEntry(
            input_container,
            textvariable=self.input_folder,
            placeholder_text="Select folder containing LAS/LAZ files...",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            input_container,
            text="Browse",
            command=self.browse_input_folder,
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        browse_btn.pack(side="right")
        
        # LAStools Path
        lastools_label = ctk.CTkLabel(
            content_frame,
            text="LAStools bin Installation Path (generally C:\\LAStools\\bin):",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        lastools_label.pack(anchor="w", pady=(10, 5))
        
        lastools_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        lastools_container.pack(fill="x", pady=(0, 15))
        
        self.lastools_entry = ctk.CTkEntry(
            lastools_container,
            textvariable=self.lastools_path,
            placeholder_text="e.g., C:\\LAStools\\bin",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.lastools_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        lastools_browse_btn = ctk.CTkButton(
            lastools_container,
            text="Browse",
            command=self.browse_lastools,
            width=100,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        lastools_browse_btn.pack(side="right")
        
        # Visualization Settings Section
        vis_label = ctk.CTkLabel(
            content_frame,
            text="Visualization Settings:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00d4ff"
        )
        vis_label.pack(anchor="w", pady=(10, 10))
        
        vis_grid = ctk.CTkFrame(content_frame, fg_color="#2b2b2b", corner_radius=10)
        vis_grid.pack(fill="x", pady=(0, 15))
        
        # Column 1: Hillshade & SLRM
        col1 = ctk.CTkFrame(vis_grid, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Hillshade
        hs_check = ctk.CTkCheckBox(col1, text="Hillshade", variable=self.vis_hillshade, font=ctk.CTkFont(size=12, weight="bold"))
        hs_check.pack(anchor="w", pady=(0, 5))
        
        hs_params = ctk.CTkFrame(col1, fg_color="transparent")
        hs_params.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(hs_params, text="Azim:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkEntry(hs_params, textvariable=self.hs_azimuth, width=40, height=20, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkLabel(hs_params, text="Alt:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkEntry(hs_params, textvariable=self.hs_altitude, width=40, height=20, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkLabel(hs_params, text="Z:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkEntry(hs_params, textvariable=self.hs_zfactor, width=30, height=20, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        
        # SLRM
        slrm_check = ctk.CTkCheckBox(col1, text="SLRM (Relief Model)", variable=self.vis_slrm, font=ctk.CTkFont(size=12, weight="bold"))
        slrm_check.pack(anchor="w", pady=(5, 5))
        
        slrm_params = ctk.CTkFrame(col1, fg_color="transparent")
        slrm_params.pack(fill="x", padx=20)
        
        ctk.CTkLabel(slrm_params, text="Radius (cells):", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkEntry(slrm_params, textvariable=self.slrm_radius, width=40, height=20, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        
        # Column 2: SVF & Local Dominance
        col2 = ctk.CTkFrame(vis_grid, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # SVF
        svf_check = ctk.CTkCheckBox(col2, text="Sky View Factor", variable=self.vis_svf, font=ctk.CTkFont(size=12, weight="bold"))
        svf_check.pack(anchor="w", pady=(0, 5))
        
        svf_params = ctk.CTkFrame(col2, fg_color="transparent")
        svf_params.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(svf_params, text="R max (m):", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkEntry(svf_params, textvariable=self.svf_radius, width=40, height=20, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkLabel(svf_params, text="Dirs:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkEntry(svf_params, textvariable=self.svf_dir, width=30, height=20, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        
        # Local Dominance
        ld_check = ctk.CTkCheckBox(col2, text="Local Dominance", variable=self.vis_ld, font=ctk.CTkFont(size=12, weight="bold"))
        ld_check.pack(anchor="w", pady=(5, 5))
        
        ld_params = ctk.CTkFrame(col2, fg_color="transparent")
        ld_params.pack(fill="x", padx=20)
        
        ctk.CTkLabel(ld_params, text="R min:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkEntry(ld_params, textvariable=self.ld_min_rad, width=35, height=20, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkLabel(ld_params, text="R max:", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        ctk.CTkEntry(ld_params, textvariable=self.ld_max_rad, width=35, height=20, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        
        # Software Status
        status_label = ctk.CTkLabel(
            content_frame,
            text="Software Dependencies:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        status_label.pack(anchor="w", pady=(15, 5))
        
        self.status_text = ctk.CTkTextbox(
            content_frame,
            height=120,
            font=ctk.CTkFont(size=11),
            fg_color="#2b2b2b"
        )
        self.status_text.pack(fill="x", pady=(0, 10))
        
        # Dependency Help Buttons
        self.help_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.help_frame.pack(fill="x", pady=(0, 15))
        
        self.qgis_help_btn = ctk.CTkButton(
            self.help_frame,
            text="Download QGIS",
            command=lambda: self.open_url(self.detector.download_urls['qgis']),
            width=120, height=28, font=ctk.CTkFont(size=11), fg_color="#3c3c3c", hover_color="#4c4c4c"
        )
        
        self.lastools_help_btn = ctk.CTkButton(
            self.help_frame,
            text="Download LAStools",
            command=lambda: self.open_url(self.detector.download_urls['lastools']),
            width=120, height=28, font=ctk.CTkFont(size=11), fg_color="#3c3c3c", hover_color="#4c4c4c"
        )
        
        # Progress Section
        progress_label = ctk.CTkLabel(
            content_frame,
            text="Processing Progress:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        progress_label.pack(anchor="w", pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(
            content_frame,
            height=25,
            corner_radius=10
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        
        # Progress Info
        progress_info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        progress_info_frame.pack(fill="x", pady=(0, 10))
        
        self.progress_label = ctk.CTkLabel(
            progress_info_frame,
            text="Ready to process",
            font=ctk.CTkFont(size=11),
            text_color="#a0a0a0"
        )
        self.progress_label.pack(side="left")
        
        self.time_label = ctk.CTkLabel(
            progress_info_frame,
            text="Time remaining: --:--",
            font=ctk.CTkFont(size=11),
            text_color="#a0a0a0"
        )
        self.time_label.pack(side="right")
        
        # Log Output
        log_label = ctk.CTkLabel(
            content_frame,
            text="Processing Log:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        log_label.pack(anchor="w", pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(
            content_frame,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color="#1a1a1a"
        )
        self.log_text.pack(fill="both", expand=True, pady=(0, 15))
        
        # Start Button
        self.start_btn = ctk.CTkButton(
            content_frame,
            text="START PROCESSING",
            command=self.start_processing,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            text_color="#000000"
        )
        self.start_btn.pack(fill="x")
    
    def check_dependencies(self):
        """Check for required software installations and provide help"""
        self.log("Checking software dependencies...")
        
        # Clear status
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        
        # Detect QGIS
        qgis_path = self.detector.find_qgis()
        if qgis_path:
            self.log(f"✓ QGIS found: {qgis_path}", "success")
            self.status_text.insert("end", f"✓ QGIS: {qgis_path}\n", "success")
            self.qgis_help_btn.pack_forget()
        else:
            self.log("✗ QGIS not found. Please install QGIS 3.x", "error")
            self.status_text.insert("end", "✗ QGIS: Not found - Required for DTM & RVT\n", "error")
            self.qgis_help_btn.pack(side="left", padx=(0, 10))
        
        # Detect SAGA GIS
        saga_path = self.detector.find_saga()
        if saga_path:
            self.log(f"✓ SAGA GIS found: {saga_path}", "success")
            self.status_text.insert("end", f"✓ SAGA GIS: {saga_path}\n", "success")
        else:
            self.log("✗ SAGA GIS not found.", "error")
            self.status_text.insert("end", "✗ SAGA GIS: Not found (included in QGIS)\n", "error")
        
        # LAStools
        self.status_text.insert("end", "⚠ LAStools: Please specify path manually\n", "warning")
        self.lastools_help_btn.pack(side="left")
        
        self.status_text.configure(state="disabled")

    def open_url(self, url):
        """Open a URL in the default web browser"""
        webbrowser.open_new_tab(url)
    
    def browse_input_folder(self):
        """Open folder browser for input data"""
        folder = filedialog.askdirectory(title="Select LiDAR Data Folder")
        if folder:
            self.input_folder.set(folder)
            self.log(f"Input folder selected: {folder}")
    
    def browse_lastools(self):
        """Open folder browser for LAStools"""
        folder = filedialog.askdirectory(title="Select LAStools bin Folder")
        if folder:
            self.lastools_path.set(folder)
            self.log(f"LAStools path set: {folder}")
            
            # Validate LAStools path and update status
            self.validate_lastools_path(folder)
    
    def validate_lastools_path(self, path):
        """Validate LAStools path and update status display"""
        if not path:
            return
        
        # Check if required executables exist
        required_tools = ["las2las64.exe", "lasground64.exe", "lasmerge64.exe"]
        path_obj = Path(path)
        
        all_found = all((path_obj / tool).exists() for tool in required_tools)
        
        # Update status text - find and replace LAStools line
        current_text = self.status_text.get("1.0", "end")
        lines = current_text.split("\n")
        
        # Find LAStools line and update it
        new_lines = []
        lastools_updated = False
        for line in lines:
            if "LAStools:" in line:
                if all_found:
                    new_lines.append(f"✓ LAStools: {path}")
                    self.log(f"✓ LAStools validated: {path}", "success")
                else:
                    new_lines.append(f"✗ LAStools: Invalid path (missing tools)")
                    self.log(f"✗ LAStools path invalid: missing required tools", "error")
                lastools_updated = True
            else:
                new_lines.append(line)
        
        # Update status text
        self.status_text.delete("1.0", "end")
        self.status_text.insert("1.0", "\n".join(new_lines))

    
    def log(self, message, level="info"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "info": "#ffffff",
            "success": "#00ff00",
            "warning": "#ffaa00",
            "error": "#ff0000"
        }
        
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.update_idletasks()
    
    def update_progress(self, percentage, message, time_remaining=None):
        """Update progress bar and labels with dynamic timer"""
        self.progress_bar.set(percentage / 100.0)
        self.progress_label.configure(text=f"{message} ({percentage}%) - This will take time, grab a coffee")
        
        if self.processing and hasattr(self, 'start_execution_time'):
            elapsed = time.time() - self.start_execution_time
            mins_e, secs_e = divmod(int(elapsed), 60)
            hrs_e, mins_e = divmod(mins_e, 60)
            
            elapsed_str = f"{hrs_e:02d}:{mins_e:02d}:{secs_e:02d}" if hrs_e > 0 else f"{mins_e:02d}:{secs_e:02d}"
            
            if percentage > 0:
                total_estimated = elapsed / (percentage / 100.0)
                remaining = total_estimated - elapsed
                
                mins_r, secs_r = divmod(int(remaining), 60)
                hrs_r, mins_r = divmod(mins_r, 60)
                remaining_str = f"~{hrs_r:02d}:{mins_r:02d}:{secs_r:02d}" if hrs_r > 0 else f"~{mins_r:02d}:{secs_r:02d}"
                
                self.time_label.configure(text=f"Elapsed: {elapsed_str} | Remaining: {remaining_str}")
            else:
                self.time_label.configure(text=f"Elapsed: {elapsed_str} | Remaining: calculating...")
        
        self.update_idletasks()
    
    def start_processing(self):
        """Start the LiDAR processing workflow"""
        if self.processing:
            return
        
        # Validate inputs
        if not self.input_folder.get():
            messagebox.showerror("Error", "Please select an input folder")
            return
        
        if not self.lastools_path.get():
            messagebox.showerror("Error", "Please specify LAStools path")
            return
        
        if not os.path.exists(self.input_folder.get()):
            messagebox.showerror("Error", "Input folder does not exist")
            return
        
        if not os.path.exists(self.lastools_path.get()):
            messagebox.showerror("Error", "LAStools path does not exist")
            return
        
        # Disable start button
        self.start_btn.configure(state="disabled", text="PROCESSING...")
        self.processing = True
        self.start_execution_time = time.time()
        
        # Run processing in separate thread
        thread = threading.Thread(target=self.run_workflow, daemon=True)
        thread.start()
    
    def run_workflow(self):
        """Execute the complete workflow"""
        try:
            # Gather visualization config
            vis_config = {
                "hillshade": {
                    "enabled": self.vis_hillshade.get(),
                    "azimuth": int(self.hs_azimuth.get()),
                    "altitude": int(self.hs_altitude.get()),
                    "z_factor": float(self.hs_zfactor.get())
                },
                "slrm": {
                    "enabled": self.vis_slrm.get(),
                    "radius": int(self.slrm_radius.get())
                },
                "svf": {
                    "enabled": self.vis_svf.get(),
                    "radius_max": int(self.svf_radius.get()),
                    "n_dir": int(self.svf_dir.get())
                },
                "local_dominance": {
                    "enabled": self.vis_ld.get(),
                    "min_rad": int(self.ld_min_rad.get()),
                    "max_rad": int(self.ld_max_rad.get())
                }
            }
            
            # Create workflow engine
            self.workflow = WorkflowEngine(
                input_folder=self.input_folder.get(),
                lastools_path=self.lastools_path.get(),
                qgis_path=self.detector.find_qgis(),
                saga_path=self.detector.find_saga(),
                progress_callback=self.update_progress,
                log_callback=self.log,
                vis_config=vis_config
            )
            
            # Execute workflow
            success = self.workflow.execute()
            
            if success:
                self.log("✓ Processing completed successfully!", "success")
                self.update_progress(100, "Complete", 0)
                
                # Generate technical report
                report_gen = ReportGenerator(self.workflow.project_dir)
                report_gen.generate_report(self.workflow.get_processing_stats())
                
                messagebox.showinfo(
                    "Success",
                    f"Processing completed!\n\nResults saved to:\n{self.workflow.project_dir}"
                )
            else:
                self.log("✗ Processing failed", "error")
                messagebox.showerror("Error", "Processing failed. Check the log for details.")
        
        except Exception as e:
            self.log(f"✗ Error: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        
        finally:
            self.processing = False
            self.start_btn.configure(state="normal", text="START PROCESSING")


def is_admin():
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Restart the application with administrator privileges"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


if __name__ == "__main__":
    # Ensure administrator privileges
    run_as_admin()
    
    # Create and run application
    app = LiDARchApp()
    app.mainloop()
