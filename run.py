#!/usr/bin/env python3
"""
Launcher script for OggDude to Realm VTT Importer

This script automatically handles virtual environment activation and runs the application.
"""

import os
import sys
import subprocess
import platform

def main():
    """Main launcher function"""
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # Already in a virtual environment, run the app directly
        print("Running in virtual environment...")
        run_app()
    else:
        # Not in a virtual environment, try to activate one
        venv_path = os.path.join(os.path.dirname(__file__), 'venv')
        
        if os.path.exists(venv_path):
            print("Activating virtual environment...")
            activate_venv_and_run(venv_path)
        else:
            print("Virtual environment not found. Creating one...")
            create_venv_and_run()

def create_venv_and_run():
    """Create virtual environment and run the app"""
    try:
        # Create virtual environment
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("Virtual environment created successfully.")
        
        # Activate and run
        venv_path = os.path.join(os.path.dirname(__file__), 'venv')
        activate_venv_and_run(venv_path)
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to create virtual environment: {e}")
        print("Please create it manually:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("  pip install -r requirements.txt")
        print("  python main.py")
        sys.exit(1)

def activate_venv_and_run(venv_path):
    """Activate virtual environment and run the app"""
    if platform.system() == "Windows":
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
        pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
    else:
        python_path = os.path.join(venv_path, 'bin', 'python')
        pip_path = os.path.join(venv_path, 'bin', 'pip')
    
    # Check if dependencies are installed
    try:
        import requests
        import xmltodict
    except ImportError:
        print("Installing dependencies...")
        try:
            subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            sys.exit(1)
    
    # Run the application
    run_app(python_path)

def run_app(python_path=None):
    """Run the main application"""
    if python_path is None:
        python_path = sys.executable
    
    try:
        subprocess.run([python_path, 'main.py'])
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 