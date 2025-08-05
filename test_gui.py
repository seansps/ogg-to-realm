#!/usr/bin/env python3
"""
Test script for GUI functionality
"""

import sys
import os
import tkinter as tk

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_creation():
    """Test that the GUI can be created without errors"""
    try:
        from src.gui import OggDudeImporterGUI
        
        print("Testing GUI creation...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        print("✓ GUI created successfully")
        
        # Test that status update methods exist
        app.update_login_status("Test message", "info")
        app.update_campaign_status("Test message", "info")
        app.update_connection_status()
        
        print("✓ Status update methods work correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI creation failed: {e}")
        return False

def test_status_methods():
    """Test the status update methods"""
    try:
        from src.gui import OggDudeImporterGUI
        
        print("Testing status update methods...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        # Test different status types
        app.update_login_status("Success message", "success")
        app.update_login_status("Error message", "error")
        app.update_login_status("Loading message", "loading")
        app.update_login_status("Info message", "info")
        
        app.update_campaign_status("Success message", "success")
        app.update_campaign_status("Error message", "error")
        app.update_campaign_status("Loading message", "loading")
        app.update_campaign_status("Info message", "info")
        
        print("✓ All status update methods work correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Status methods test failed: {e}")
        return False

def main():
    """Run GUI tests"""
    print("Running GUI tests")
    print("=" * 40)
    
    tests = [
        test_gui_creation,
        test_status_methods
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"GUI tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All GUI tests passed!")
        return 0
    else:
        print("✗ Some GUI tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 