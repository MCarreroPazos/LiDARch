@echo off
echo ========================================
echo Building LiDARch Executable
echo ========================================
echo.

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building executable with PyInstaller...
pyinstaller --name="LiDARch" ^
    --onefile ^
    --windowed ^
    --icon=assets\icon.ico ^
    --add-data="Step1.descompress_new_lidar.bat;." ^
    --add-data="Step2.lasground.bat;." ^
    --add-data="Step3.las2lasfilt.bat;." ^
    --add-data="Step4.saga_interpolation.bat;." ^
    --add-data="Step5.merge_las.bat;." ^
    --add-data="Step6.visualizations_rvt.bat;." ^
    --add-data="rvt_monitored.py;." ^
    --add-data="gepn_logo.png;." ^
    --add-data="cispac_logo.png;." ^
    --uac-admin ^
    lidarch_main.py

echo.
echo ========================================
echo Build complete!
echo Executable: dist\LiDARch.exe
echo ========================================
pause
