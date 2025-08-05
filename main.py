#!/usr/bin/env python3
"""
OggDude to Realm VTT Importer

A Python GUI application that imports Star Wars RPG data from OggDude's Character Creator 
XML files and Adversaries JSON files into Realm VTT.

Usage:
    python main.py
"""

import tkinter as tk
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui import OggDudeImporterGUI

def main():
    """Main entry point for the application"""
    try:
        # Create the main window
        root = tk.Tk()
        
        # Create the application
        app = OggDudeImporterGUI(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 