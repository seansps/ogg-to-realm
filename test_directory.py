#!/usr/bin/env python3
"""
Test script for directory functionality
"""

import sys
import os
import tkinter as tk

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_default_directory():
    """Test that the default directory is correctly determined"""
    try:
        from src.gui import OggDudeImporterGUI
        
        print("Testing default directory functionality...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        # Test default directory
        default_dir = app.get_default_directory()
        print(f"Default directory: {default_dir}")
        
        # Should be the src directory
        expected_dir = os.path.dirname(os.path.abspath(__file__))
        assert default_dir == expected_dir, f"Default directory should be {expected_dir}, got {default_dir}"
        
        print("✓ Default directory functionality works correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Default directory test failed: {e}")
        return False

def test_window_centering():
    """Test that the window centering functionality works"""
    try:
        from src.gui import OggDudeImporterGUI
        
        print("Testing window centering functionality...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        # Test that center_window method exists and can be called
        app.center_window()
        
        print("✓ Window centering functionality works correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Window centering test failed: {e}")
        return False

def main():
    """Run directory tests"""
    print("Running directory tests")
    print("=" * 40)
    
    tests = [
        test_default_directory,
        test_window_centering
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Directory tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All directory tests passed!")
        return 0
    else:
        print("✗ Some directory tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 