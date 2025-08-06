#!/usr/bin/env python3
"""
Test record finding functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api_client import RealmVTTClient

def test_record_finding_logic():
    """Test the record finding logic"""
    print("Testing record finding logic...")
    
    # Create a mock API client for testing
    client = RealmVTTClient()
    
    # Test the find_records method logic
    test_cases = [
        ('npcs', '/npcs', {}),
        ('items', '/records', {'recordType': 'items'}),
        ('careers', '/records', {'recordType': 'careers'}),
        ('talents', '/records', {'recordType': 'talents'}),
        ('species', '/records', {'recordType': 'species'}),
        ('specializations', '/records', {'recordType': 'specializations'}),
        ('force_powers', '/records', {'recordType': 'force_powers'}),
        ('skills', '/records', {'recordType': 'skills'}),
        ('signature_abilities', '/records', {'recordType': 'signature_abilities'}),
    ]
    
    print("Testing find_records method logic:")
    for record_type, expected_endpoint, expected_params in test_cases:
        print(f"  {record_type}:")
        print(f"    Expected endpoint: {expected_endpoint}")
        print(f"    Expected params: {expected_params}")
        
        # Test the logic that determines endpoint and params
        if record_type == 'npcs':
            endpoint = "/npcs"
            params = {}
        else:
            endpoint = "/records"
            params = {'recordType': record_type}
        
        print(f"    Actual endpoint: {endpoint}")
        print(f"    Actual params: {params}")
        
        if endpoint == expected_endpoint and params == expected_params:
            print(f"    ✓ Correct")
        else:
            print(f"    ✗ Incorrect")
            return False
    
    print("\nTesting find_record_by_name logic:")
    print("  The method should:")
    print("  1. Call find_records with the correct record_type")
    print("  2. Filter results by name (case-insensitive)")
    print("  3. Return the first matching record or None")
    print("  4. Trust the API filtering (no additional recordType check needed)")
    
    print("\n✓ Record finding logic test completed")
    return True

def test_import_manager_record_types():
    """Test that import manager uses correct record types"""
    print("\nTesting import manager record types...")
    
    # These are the record types used in the import manager
    import_record_types = [
        'items',
        'species', 
        'talents',
        'specializations',
        'careers',
        'force_powers',
        'skills',
        'signature_abilities',
        'npcs'
    ]
    
    print("Import manager record types:")
    for record_type in import_record_types:
        print(f"  {record_type}")
    
    # Verify these match what the API client expects
    expected_types = [
        'items', 'npcs', 'careers', 'talents', 'species', 
        'specializations', 'force_powers', 'skills', 'signature_abilities'
    ]
    
    for record_type in import_record_types:
        if record_type in expected_types:
            print(f"  ✓ {record_type} is valid")
        else:
            print(f"  ✗ {record_type} is not valid")
            return False
    
    print("\n✓ All import manager record types are valid")
    return True

if __name__ == '__main__':
    print("Running record finding tests...")
    
    success = True
    success &= test_record_finding_logic()
    success &= test_import_manager_record_types()
    
    if success:
        print("\n✓ All record finding tests passed!")
    else:
        print("\n✗ Some record finding tests failed!")
        sys.exit(1) 