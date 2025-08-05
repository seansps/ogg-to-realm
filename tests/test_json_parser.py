#!/usr/bin/env python3
"""
Test script for JSON parser functionality
"""

import sys
import os
import tempfile
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_json_parser_basic():
    """Test basic JSON parser functionality"""
    try:
        from src.json_parser import JSONParser
        
        print("Testing basic JSON parser functionality...")
        
        parser = JSONParser()
        print("✓ JSON parser created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Basic JSON parser test failed: {e}")
        return False

def test_json_parser_extraction():
    """Test JSON parser data extraction"""
    try:
        from src.json_parser import JSONParser
        
        print("Testing JSON parser data extraction...")
        
        parser = JSONParser()
        
        # Test data extraction with sample data
        sample_data = {
            'name': 'Test NPC',
            'tags': ['source:test', 'adventure:test'],
            'characteristics': {'Brawn': 3, 'Agility': 2},
            'skills': ['Athletics', 'Perception'],
            'talents': ['Test Talent'],
            'gear': ['Test Gear'],
            'weapons': ['Test Weapon'],
            'armor': ['Test Armor']
        }
        
        record = parser._extract_npc_data(sample_data)
        
        if record and record['name'] == 'Test NPC' and record['source'] == 'source:test' and record['recordType'] == 'npcs':
            print("✓ JSON parser data extraction test passed")
            return True
        else:
            print("✗ JSON parser data extraction test failed - unexpected record data")
            return False
                
    except Exception as e:
        print(f"✗ JSON parser data extraction test failed: {e}")
        return False

def test_json_parser_scan_directory():
    """Test JSON parser scan_directory functionality"""
    try:
        from src.json_parser import JSONParser
        
        print("Testing JSON parser scan_directory...")
        
        # Create a temporary directory with test JSON files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test JSON file
            json_file = os.path.join(temp_dir, 'test.json')
            data = [
                {
                    'name': 'Test NPC',
                    'tags': ['source:test', 'adventure:test'],
                    'characteristics': {'Brawn': 3, 'Agility': 2},
                    'skills': ['Athletics', 'Perception'],
                    'talents': ['Test Talent'],
                    'gear': ['Test Gear'],
                    'weapons': ['Test Weapon'],
                    'armor': ['Test Armor']
                }
            ]
            
            with open(json_file, 'w') as f:
                json.dump(data, f)
            
            # Test the parser
            parser = JSONParser()
            records = parser.scan_directory(temp_dir, [])
            
            print(f"Scanned {len(records)} records")
            
            if len(records) == 1:
                record = records[0]
                if record['name'] == 'Test NPC' and record['source'] == 'source:test' and record['recordType'] == 'npcs':
                    print("✓ JSON parser scan_directory test passed")
                    return True
                else:
                    print("✗ JSON parser scan_directory test failed - unexpected record data")
                    return False
            else:
                print(f"✗ JSON parser scan_directory test failed - expected 1 record, got {len(records)}")
                return False
                
    except Exception as e:
        print(f"✗ JSON parser scan_directory test failed: {e}")
        return False

def test_json_parser_source_filtering():
    """Test JSON parser source filtering"""
    try:
        from src.json_parser import JSONParser
        
        print("Testing JSON parser source filtering...")
        
        parser = JSONParser()
        
        # Test records with different sources
        records = [
            {'source': 'book:eote', 'name': 'EotE NPC'},
            {'source': 'book:aor', 'name': 'AoR NPC'},
            {'source': 'adventure:test', 'name': 'Test NPC'}
        ]
        
        # Test filtering by EotE source
        filtered = parser.filter_by_sources(records, ['book:eote'])
        
        if len(filtered) == 1 and filtered[0]['name'] == 'EotE NPC':
            print("✓ JSON parser source filtering test passed")
            return True
        else:
            print(f"✗ JSON parser source filtering test failed - expected 1 record, got {len(filtered)}")
            return False
                
    except Exception as e:
        print(f"✗ JSON parser source filtering test failed: {e}")
        return False

def main():
    """Run all JSON parser tests"""
    print("Running JSON parser tests")
    print("=" * 40)
    
    tests = [
        test_json_parser_basic,
        test_json_parser_extraction,
        test_json_parser_scan_directory,
        test_json_parser_source_filtering
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"JSON parser tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All JSON parser tests passed!")
        print("✓ test_json_parser.py PASSED")
        return True
    else:
        print("✗ Some JSON parser tests failed.")
        print("✗ test_json_parser.py FAILED")
        return False

if __name__ == "__main__":
    main() 