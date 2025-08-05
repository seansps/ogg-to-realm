#!/usr/bin/env python3
"""
Run all test_*.py scripts in the tests/ folder and report results.
"""
import os
import subprocess
import sys

def main():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)
    src_dir = os.path.join(project_root, 'src')
    
    # Set up environment with src directory in Python path
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{src_dir}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = src_dir
    
    test_files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py') and f != 'run_all_tests.py']
    test_files.sort()
    
    print("Running all tests in tests/ folder:\n")
    passed = 0
    failed = 0
    for test_file in test_files:
        print(f"=== {test_file} ===")
        result = subprocess.run([sys.executable, os.path.join(test_dir, test_file)], env=env)
        if result.returncode == 0:
            print(f"✓ {test_file} PASSED\n")
            passed += 1
        else:
            print(f"✗ {test_file} FAILED\n")
            failed += 1
    print(f"Summary: {passed} passed, {failed} failed, {passed+failed} total.")
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()