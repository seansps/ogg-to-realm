#!/usr/bin/env python3
"""
Test script for validation functionality
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk

# Add src directory to path for imports
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_validation_methods():
    """Test the validation methods"""
    try:
        from src.gui import OggDudeImporterGUI
        
        print("Testing validation methods...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        # Clear directory paths to test "No directories selected" scenario
        app.oggdude_path_var.set("")
        app.adversaries_path_var.set("")
        
        # Test validation with empty setup (should fail)
        is_valid, issues = app.validate_setup()
        print(f"Empty setup validation: valid={is_valid}, issues={len(issues)}")
        print(f"Actual issues: {issues}")
        
        # Should have multiple issues
        assert not is_valid, "Empty setup should not be valid"
        assert len(issues) > 0, "Empty setup should have issues"
        
        # Check that expected issues are present (excluding the import button check which may not be available during testing)
        expected_issues = [
            "Not logged in to Realm VTT",
            "No campaign selected", 
            "No data sources selected",
            "No directories selected"
        ]
        
        for expected_issue in expected_issues:
            found = any(expected_issue in issue for issue in issues)
            print(f"Looking for '{expected_issue}': {'✓' if found else '✗'}")
            if not found:
                print(f"  Available issues: {issues}")
            assert found, f"Expected issue '{expected_issue}' not found"
        
        # Check that we have at least 4 issues (the core validation issues)
        assert len(issues) >= 4, f"Should have at least 4 issues, got {len(issues)}"
        
        print("✓ Validation methods work correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Validation methods test failed: {e}")
        return False

def test_validation_logic():
    """Test the validation logic with different scenarios"""
    try:
        from src.gui import OggDudeImporterGUI
        
        print("Testing validation logic...")
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        
        # Create the GUI
        app = OggDudeImporterGUI(root)
        
        # Clear directory paths to test "No directories selected" scenario
        app.oggdude_path_var.set("")
        app.adversaries_path_var.set("")
        
        # Test 1: Check that validation catches missing authentication
        is_valid, issues = app.validate_setup()
        assert "Not logged in to Realm VTT" in [issue for issue in issues if "Not logged in" in issue], "Should detect missing authentication"
        
        # Test 2: Check that validation catches missing campaign
        assert "No campaign selected" in [issue for issue in issues if "No campaign selected" in issue], "Should detect missing campaign"
        
        # Test 3: Check that validation catches missing sources
        assert "No data sources selected" in [issue for issue in issues if "No data sources selected" in issue], "Should detect missing sources"
        
        # Test 4: Check that validation catches missing directories
        assert "No directories selected" in [issue for issue in issues if "No directories selected" in issue], "Should detect missing directories"
        
        print("✓ Validation logic works correctly")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Validation logic test failed: {e}")
        return False

def main():
    """Run validation tests"""
    print("Running validation tests")
    print("=" * 40)
    
    tests = [
        test_validation_methods,
        test_validation_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Validation tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All validation tests passed!")
        return 0
    else:
        print("✗ Some validation tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 