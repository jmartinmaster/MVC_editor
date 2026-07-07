# build.py - Build script for MVC Sync Editor
# Copyright (C) 2026 Jamie Martin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import subprocess
import shutil

def main():
    print("=== MVC Editor Build System ===")
    
    # 1. Determine active python executable (check for .venv)
    venv_dir = os.path.join(os.path.abspath("."), ".venv")
    if os.path.exists(venv_dir):
        if os.name == 'nt':  # Windows
            python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        else:  # macOS/Linux
            python_exe = os.path.join(venv_dir, "bin", "python")
        print(f"Virtual environment detected. Using: {python_exe}")
    else:
        python_exe = sys.executable
        print(f"Using current Python environment: {python_exe}")
        
    if not os.path.exists(python_exe):
        print(f"Error: Python executable not found at {python_exe}")
        sys.exit(1)

    # 2. Install dependencies
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        print("\n[1/3] Installing requirements...")
        try:
            subprocess.run([python_exe, "-m", "pip", "install", "-r", req_file], check=True)
            print("Requirements installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            sys.exit(1)
    else:
        print("\n[1/3] No requirements.txt found. Skipping installation.")

    # 3. Run PyInstaller
    print("\n[2/3] Building executable with PyInstaller...")
    # Using python -m PyInstaller is the most robust way to call it inside virtual environments
    build_cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", "MVC_Editor",
        "main.py"
    ]
    
    try:
        subprocess.run(build_cmd, check=True)
        print("\nBuild compiled successfully!")
        
        # Display executable path
        dist_dir = os.path.join(".", "dist")
        exe_name = "MVC_Editor.exe" if os.name == 'nt' else "MVC_Editor"
        exe_path = os.path.join(dist_dir, exe_name)
        if os.path.exists(exe_path):
            print(f"Executable created: {os.path.abspath(exe_path)}")
        else:
            print("Warning: Executable not found in 'dist' directory.")
            
        # 4. Clean up build artifacts
        print("\n[3/3] Cleaning up build artifacts...")
        import time
        time.sleep(0.5)  # Let OS release file locks
        
        spec_file = "MVC_Editor.spec"
        if os.path.exists(spec_file):
            try:
                os.remove(spec_file)
                print(f"Removed {spec_file}")
            except Exception as e:
                print(f"Notice: Could not remove spec file: {e}")
            
        build_folder = os.path.join(".", "build")
        if os.path.exists(build_folder):
            try:
                shutil.rmtree(build_folder, ignore_errors=True)
                print("Removed temporary build directory.")
            except Exception as e:
                print(f"Notice: Could not remove build folder: {e}")
            
        print("\n=== Build Complete ===")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError: Build failed: {e}")
        print("Please verify that PyInstaller is installed in the environment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
