#!/usr/bin/env python3
"""
Test script for source filtering functionality
"""

import sys
import os
import tempfile
import xml.etree.ElementTree as ET

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_source_extraction():
    """Test that source names are extracted correctly from XML"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing source extraction from XML...")
        
        # Create a temporary XML file with weapon data
        xml_content = '''<?xml version='1.0' encoding='utf-8'?>
<Weapons>
  <Weapon>
    <Key>TESTWEAPON1</Key>
    <Name>Test Weapon 1</Name>
    <Description>Test weapon description</Description>
    <Source Page="40">Far Horizons</Source>
    <Type>Energy Weapon</Type>
    <SkillKey>RANGLT</SkillKey>
    <Damage>5</Damage>
    <Crit>5</Crit>
    <RangeValue>wrShort</RangeValue>
  </Weapon>
  <Weapon>
    <Key>TESTWEAPON2</Key>
    <Name>Test Weapon 2</Name>
    <Description>Test weapon description 2</Description>
    <Source Page="41">Knights of Fate</Source>
    <Type>Energy Weapon</Type>
    <SkillKey>RANGLT</SkillKey>
    <Damage>6</Damage>
    <Crit>4</Crit>
    <RangeValue>wrMedium</RangeValue>
  </Weapon>
  <Weapon>
    <Key>TESTWEAPON3</Key>
    <Name>Test Weapon 3</Name>
    <Description>Test weapon description 3</Description>
    <Source Page="42">Edge of the Empire Core Rulebook</Source>
    <Type>Energy Weapon</Type>
    <SkillKey>RANGLT</SkillKey>
    <Damage>7</Damage>
    <Crit>3</Crit>
    <RangeValue>wrLong</RangeValue>
  </Weapon>
  <Weapon>
    <Key>TESTWEAPON4</Key>
    <Name>Test Weapon 4</Name>
    <Description>Test weapon with multiple sources</Description>
    <Source Page="230">Edge of the Empire Core Rulebook</Source>
    <Source Page="240">Age of Rebellion Core Rulebook</Source>
    <Type>Energy Weapon</Type>
    <SkillKey>RANGLT</SkillKey>
    <Damage>8</Damage>
    <Crit>2</Crit>
    <RangeValue>wrExtreme</RangeValue>
  </Weapon>
</Weapons>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            parser = XMLParser()
            records = parser.parse_xml_file(temp_file)
            
            # Check that we got 4 weapons
            assert len(records) == 4, f"Expected 4 weapons, got {len(records)}"
            
            # Check that all records are items type (weapons are items in Realm VTT)
            for record in records:
                assert record.get('recordType') == 'items', f"Expected recordType 'items', got '{record.get('recordType')}'"
                # Check that the type is either 'ranged weapon' or 'melee weapon' (new format)
                weapon_type = record.get('data', {}).get('type', '')
                assert weapon_type in ['ranged weapon', 'melee weapon'], f"Expected type 'ranged weapon' or 'melee weapon', got '{weapon_type}'"
            
            # Apply filtering to get categories set
            # We need to select sources that match our test data
            selected_sources = ['book:eote', 'far-horizons', 'knights-of-fate']  # Add the source keys that match our test data
            filtered_records = parser.filter_by_sources(records, selected_sources)
            
            # Check that categories are extracted correctly
            categories = [record.get('category', '') for record in filtered_records]
            expected_categories = ['Far Horizons', 'Knights of Fate', 'Edge of the Empire Core Rulebook', 'Edge of the Empire Core Rulebook']
            
            for expected in expected_categories:
                assert expected in categories, f"Expected category '{expected}' not found in {categories}"
            
            # Check multiple sources handling (should use first source as category)
            weapon4 = filtered_records[3]  # The weapon with multiple sources
            assert 'category' in weapon4, "Weapon should have 'category' field"
            assert weapon4['category'] == 'Edge of the Empire Core Rulebook', f"Expected category 'Edge of the Empire Core Rulebook', got '{weapon4['category']}'"
            
            print("✓ Source extraction test passed")
            return True
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except Exception as e:
        print(f"✗ Source extraction test failed: {e}")
        return False

def test_real_weapons_file():
    """Test with a real Weapons.xml file if available"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing with real Weapons.xml file...")
        
        # Look for Weapons.xml in common locations
        possible_paths = [
            'Weapons.xml',
            'data/Weapons.xml',
            'OggData/Weapons.xml',
            '../Weapons.xml',
            '../../Weapons.xml'
        ]
        
        weapons_file = None
        for path in possible_paths:
            if os.path.exists(path):
                weapons_file = path
                break
        
        if not weapons_file:
            print("⚠ No Weapons.xml file found, skipping real file test")
            return True
        
        parser = XMLParser()
        records = parser.parse_xml_file(weapons_file)
        
        print(f"Found {len(records)} weapons in {weapons_file}")
        
        # Check that all records are items type
        for record in records:
            assert record.get('recordType') == 'items', f"Expected recordType 'items', got '{record.get('recordType')}'"
            # Check that the type is either 'ranged weapon' or 'melee weapon' (new format)
            weapon_type = record.get('data', {}).get('type', '')
            assert weapon_type in ['ranged weapon', 'melee weapon'], f"Expected type 'ranged weapon' or 'melee weapon', got '{weapon_type}'"
        
        # Check that categories are present
        categories = set(record.get('category', '') for record in records)
        print(f"Found categories: {categories}")
        
        assert len(categories) > 0, "Should have at least one category"
        
        print("✓ Real file test passed")
        return True
        
    except Exception as e:
        print(f"✗ Real file test failed: {e}")
        return False

def test_scan_directory_categorization():
    """Test that scan_directory properly categorizes records"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing scan_directory categorization...")
        
        # Create a temporary directory with test XML files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test weapons file
            weapons_content = '''<?xml version='1.0' encoding='utf-8'?>
<Weapons>
  <Weapon>
    <Key>TESTWEAPON1</Key>
    <Name>Test Weapon 1</Name>
    <Description>Test weapon description</Description>
    <Source>Edge of the Empire Core Rulebook</Source>
    <Type>Energy Weapon</Type>
    <SkillKey>RANGLT</SkillKey>
    <Damage>5</Damage>
    <Crit>5</Crit>
    <RangeValue>wrShort</RangeValue>
  </Weapon>
</Weapons>'''
            
            weapons_file = os.path.join(temp_dir, 'test_weapons.xml')
            with open(weapons_file, 'w') as f:
                f.write(weapons_content)
            
            parser = XMLParser()
            # Pass selected sources to enable filtering and category assignment
            all_records = parser.scan_directory(temp_dir, selected_sources=['book:eote'])
            
            # Check that items key exists and contains weapons
            assert 'items' in all_records, "'items' key should be in all_records"
            assert len(all_records['items']) == 1, f"Expected 1 item, got {len(all_records['items'])}"
            
            # Check that the weapon is properly categorized
            weapon = all_records['items'][0]
            assert weapon['recordType'] == 'items', f"Expected recordType 'items', got '{weapon['recordType']}'"
            # Check that the type is either 'ranged weapon' or 'melee weapon' (new format)
            weapon_type = weapon.get('data', {}).get('type', '')
            assert weapon_type in ['ranged weapon', 'melee weapon'], f"Expected type 'ranged weapon' or 'melee weapon', got '{weapon_type}'"
            assert weapon['category'] == 'Edge of the Empire Core Rulebook', f"Expected category 'Edge of the Empire Core Rulebook', got '{weapon['category']}'"
            
            print("✓ Scan directory categorization test passed")
            return True
            
    except Exception as e:
        print(f"✗ Scan directory categorization test failed: {e}")
        return False

def main():
    """Run all source filtering tests"""
    print("Running source filtering tests")
    print("=" * 40)
    
    tests = [
        test_source_extraction,
        test_real_weapons_file,
        test_scan_directory_categorization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 40)
    print(f"Source filtering tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All source filtering tests passed!")
        print("✓ test_source_filtering.py PASSED")
        return True
    else:
        print("✗ Some source filtering tests failed.")
        print("✗ test_source_filtering.py FAILED")
        return False

if __name__ == "__main__":
    main() 