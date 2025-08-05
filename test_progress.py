#!/usr/bin/env python3
"""
Test script for progress tracking functionality
"""

import sys
import os
import time
import threading

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_progress_tracking():
    """Test the progress tracking functionality"""
    try:
        from src.api_client import RealmVTTClient
        from src.import_manager import ImportManager
        
        print("Testing progress tracking functionality...")
        
        # Create import manager
        api_client = RealmVTTClient()
        import_manager = ImportManager(api_client)
        
        # Test initial state
        current, total = import_manager.get_import_progress()
        operation = import_manager.get_current_operation()
        percentage = import_manager.get_progress_percentage()
        
        print(f"Initial state: current={current}, total={total}, operation='{operation}', percentage={percentage}")
        
        # Test progress updates
        def progress_callback(message, current, total):
            print(f"Progress callback: {message} ({current}/{total})")
        
        def status_callback(message):
            print(f"Status callback: {message}")
        
        import_manager.set_progress_callback(progress_callback)
        import_manager.set_status_callback(status_callback)
        
        # Simulate progress updates
        import_manager._update_progress("Testing progress", 5, 10)
        
        current, total = import_manager.get_import_progress()
        operation = import_manager.get_current_operation()
        percentage = import_manager.get_progress_percentage()
        
        print(f"After update: current={current}, total={total}, operation='{operation}', percentage={percentage}")
        
        # Test thread safety
        def update_progress_thread():
            for i in range(10):
                import_manager._update_progress(f"Thread update {i}", i, 10)
                time.sleep(0.1)
        
        thread = threading.Thread(target=update_progress_thread)
        thread.start()
        thread.join()
        
        current, total = import_manager.get_import_progress()
        operation = import_manager.get_current_operation()
        percentage = import_manager.get_progress_percentage()
        
        print(f"After thread updates: current={current}, total={total}, operation='{operation}', percentage={percentage}")
        
        print("✓ Progress tracking test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Progress tracking test failed: {e}")
        return False

def main():
    """Run progress tracking tests"""
    print("Running progress tracking tests")
    print("=" * 40)
    
    tests = [
        test_progress_tracking
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Progress tracking tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All progress tracking tests passed!")
        return 0
    else:
        print("✗ Some progress tracking tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 