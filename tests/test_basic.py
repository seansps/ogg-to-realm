#!/usr/bin/env python3
"""
Basic test script for OggDude to Realm VTT Importer

This script tests basic functionality without requiring GUI or network access.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from api_client import RealmVTTClient
        from xml_parser import XMLParser
        from json_parser import JSONParser
        from data_mapper import DataMapper
        from import_manager import ImportManager
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_config_files():
    """Test that configuration files exist"""
    config_files = [
        'config/field_mapping.json',
        'config/sources.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✓ {config_file} exists")
        else:
            print(f"✗ {config_file} missing")
            return False
    
    return True

def test_xml_parser():
    """Test XML parser basic functionality"""
    try:
        from xml_parser import XMLParser
        parser = XMLParser()
        print("✓ XML parser created successfully")
        return True
    except Exception as e:
        print(f"✗ XML parser error: {e}")
        return False

def test_json_parser():
    """Test JSON parser basic functionality"""
    try:
        from json_parser import JSONParser
        parser = JSONParser()
        print("✓ JSON parser created successfully")
        return True
    except Exception as e:
        print(f"✗ JSON parser error: {e}")
        return False

def test_data_mapper():
    """Test data mapper basic functionality"""
    try:
        from data_mapper import DataMapper
        mapper = DataMapper()
        print("✓ Data mapper created successfully")
        return True
    except Exception as e:
        print(f"✗ Data mapper error: {e}")
        return False

def main():
    """Run all tests"""
    print("Running basic tests for OggDude to Realm VTT Importer")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_files,
        test_xml_parser,
        test_json_parser,
        test_data_mapper
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The application should work correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 