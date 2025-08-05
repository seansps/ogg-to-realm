#!/usr/bin/env python3
"""
Test script for sources configuration
"""

import sys
import os
import json

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_sources_loading():
    """Test that sources configuration loads correctly"""
    try:
        from src.gui import OggDudeImporterGUI
        import tkinter as tk
        
        print("Testing sources configuration loading...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        # Check that sources were loaded
        sources = app.sources_config.get('sources', [])
        print(f"Loaded {len(sources)} sources")
        
        # Should have more than the original 3 sources
        assert len(sources) > 3, f"Expected more than 3 sources, got {len(sources)}"
        
        # Check that core rulebooks are first
        first_source = sources[0]['name']
        assert "Edge of the Empire Core Rulebook" in first_source, f"First source should be Edge of the Empire Core Rulebook, got {first_source}"
        
        # Check for some specific sources
        source_names = [source['name'] for source in sources]
        expected_sources = [
            "Edge of the Empire Core Rulebook",
            "Age of Rebellion Core Rulebook", 
            "Force and Destiny Core Rulebook",
            "Far Horizons",
            "Dangerous Covenants",
            "No Disintegrations"
        ]
        
        for expected in expected_sources:
            assert expected in source_names, f"Expected source '{expected}' not found"
        
        print("✓ Sources configuration loaded correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Sources loading test failed: {e}")
        return False

def test_sources_config_file():
    """Test that the sources.json file is valid"""
    try:
        print("Testing sources.json file...")
        
        # Load the sources configuration file
        with open('config/sources.json', 'r') as f:
            config = json.load(f)
        
        sources = config.get('sources', [])
        print(f"Found {len(sources)} sources in config file")
        
        # Should have many sources
        assert len(sources) > 30, f"Expected more than 30 sources, got {len(sources)}"
        
        # Check structure
        for source in sources:
            assert 'name' in source, "Source missing 'name' field"
            assert 'key' in source, "Source missing 'key' field"
            assert 'oggdude_sources' in source, "Source missing 'oggdude_sources' field"
            assert 'adversaries_sources' in source, "Source missing 'adversaries_sources' field"
        
        print("✓ Sources.json file is valid")
        
        return True
        
    except Exception as e:
        print(f"✗ Sources config file test failed: {e}")
        return False

def main():
    """Run sources tests"""
    print("Running sources tests")
    print("=" * 40)
    
    tests = [
        test_sources_config_file,
        test_sources_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Sources tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All sources tests passed!")
        return 0
    else:
        print("✗ Some sources tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 