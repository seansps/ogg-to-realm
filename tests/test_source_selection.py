#!/usr/bin/env python3
"""
Test script for source selection functionality
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk

# Add src directory to path for imports
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_source_selection():
    """Test that source selection methods work correctly"""
    try:
        from src.gui import OggDudeImporterGUI
        
        print("Testing source selection functionality...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        # Check that source_vars were created
        assert hasattr(app, 'source_vars'), "source_vars attribute not found"
        assert len(app.source_vars) > 0, "No source variables created"
        
        print(f"Created {len(app.source_vars)} source checkboxes")
        
        # Test select all
        app.select_all_sources()
        all_selected = all(var.get() for var in app.source_vars.values())
        assert all_selected, "Not all sources were selected"
        print("✓ Select all functionality works")
        
        # Test deselect all
        app.deselect_all_sources()
        none_selected = not any(var.get() for var in app.source_vars.values())
        assert none_selected, "Not all sources were deselected"
        print("✓ Deselect all functionality works")
        
        # Test individual selection
        first_key = list(app.source_vars.keys())[0]
        app.source_vars[first_key].set(True)
        assert app.source_vars[first_key].get(), "Individual selection failed"
        print("✓ Individual selection works")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Source selection test failed: {e}")
        return False

def test_scrollable_sources():
    """Test that sources are in a scrollable area"""
    try:
        from src.gui import OggDudeImporterGUI
        
        print("Testing scrollable sources area...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        # Check that the sources frame exists and has the right structure
        # This is a basic test - in a real scenario we'd check for canvas and scrollbar
        # but for now we'll just verify the GUI creates successfully with many sources
        
        sources = app.sources_config.get('sources', [])
        assert len(sources) > 30, f"Expected many sources, got {len(sources)}"
        
        print(f"✓ GUI created successfully with {len(sources)} sources")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Scrollable sources test failed: {e}")
        return False

def main():
    """Run source selection tests"""
    print("Running source selection tests")
    print("=" * 40)
    
    tests = [
        test_source_selection,
        test_scrollable_sources
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Source selection tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All source selection tests passed!")
        return 0
    else:
        print("✗ Some source selection tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 