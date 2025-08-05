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
            
            # Check that all records are weapons type
            for record in records:
                assert record.get('recordType') == 'weapons', f"Expected recordType 'weapons', got '{record.get('recordType')}'"
            
            # Check that sources are extracted correctly
            sources = [record.get('sources', []) for record in records]
            expected_sources = ['Far Horizons', 'Knights of Fate', 'Edge of the Empire Core Rulebook', 'Edge of the Empire Core Rulebook']
            
            for expected in expected_sources:
                found = False
                for record_sources in sources:
                    if expected in record_sources:
                        found = True
                        break
                assert found, f"Expected source '{expected}' not found in {sources}"
            
            # Check multiple sources handling
            weapon4 = records[3]  # The weapon with multiple sources
            assert 'sources' in weapon4, "Weapon should have 'sources' field"
            assert len(weapon4['sources']) == 2, f"Expected 2 sources, got {len(weapon4['sources'])}"
            assert 'Edge of the Empire Core Rulebook' in weapon4['sources'], "First source should be present"
            assert 'Age of Rebellion Core Rulebook' in weapon4['sources'], "Second source should be present"
            
            print("✓ Source extraction works correctly")
            print("✓ Multiple sources handling works correctly")
            print("✓ Weapon record type is correct")
            
            # Test filtering by sources
            selected_sources = ['far-horizons', 'knights-of-fate']
            filtered_records = parser.filter_by_sources(records, selected_sources)
            
            assert len(filtered_records) == 2, f"Expected 2 filtered weapons, got {len(filtered_records)}"
            
            filtered_names = [r.get('name') for r in filtered_records]
            assert 'Test Weapon 1' in filtered_names, "Test Weapon 1 should be included"
            assert 'Test Weapon 2' in filtered_names, "Test Weapon 2 should be included"
            assert 'Test Weapon 3' not in filtered_names, "Test Weapon 3 should NOT be included"
            assert 'Test Weapon 4' not in filtered_names, "Test Weapon 4 should NOT be included"
            
            print("✓ Source filtering works correctly")
            
            # Test filtering with multiple sources
            selected_sources = ['book:eote', 'book:aor']
            filtered_records = parser.filter_by_sources(records, selected_sources)
            
            # Should get 2 weapons: Test Weapon 3 (single source) and Test Weapon 4 (multiple sources)
            # Test Weapon 1 (Far Horizons) and Test Weapon 2 (Knights of Fate) should NOT be included
            assert len(filtered_records) == 2, f"Expected 2 filtered weapons, got {len(filtered_records)}"
            
            # Verify the correct weapons are included
            filtered_names = [r.get('name') for r in filtered_records]
            assert 'Test Weapon 3' in filtered_names, "Test Weapon 3 should be included"
            assert 'Test Weapon 4' in filtered_names, "Test Weapon 4 should be included"
            assert 'Test Weapon 1' not in filtered_names, "Test Weapon 1 should NOT be included"
            assert 'Test Weapon 2' not in filtered_names, "Test Weapon 2 should NOT be included"
            
            print("✓ Multiple source filtering works correctly")
            
            return True
            
        finally:
            os.unlink(temp_file)
        
    except Exception as e:
        print(f"✗ Source extraction test failed: {e}")
        return False

def test_real_weapons_file():
    """Test with the actual Weapons.xml file if it exists"""
    try:
        from src.xml_parser import XMLParser
        
        weapons_file = os.path.join(os.path.dirname(__file__), '..', 'OggData', 'Weapons.xml')
        
        if not os.path.exists(weapons_file):
            print("⚠ Weapons.xml not found, skipping real file test")
            return True
        
        print("Testing with real Weapons.xml file...")
        
        parser = XMLParser()
        records = parser.parse_xml_file(weapons_file)
        
        print(f"Found {len(records)} weapons in Weapons.xml")
        
        # Check that all records are weapons type
        weapon_records = [r for r in records if r.get('recordType') == 'weapons']
        assert len(weapon_records) == len(records), f"All records should be weapons type"
        
        # Get unique sources
        sources = set()
        for record in records:
            record_sources = record.get('sources', [])
            for source in record_sources:
                if source:
                    sources.add(source)
        
        print(f"Found sources: {sorted(sources)}")
        
        # Check for multiple sources
        multi_source_weapons = [r for r in records if 'sources' in r and len(r['sources']) > 1]
        print(f"Found {len(multi_source_weapons)} weapons with multiple sources")
        
        # Test filtering by a specific source
        selected_sources = ['far-horizons']
        filtered_records = parser.filter_by_sources(records, selected_sources)
        
        print(f"Filtered to {len(filtered_records)} weapons from Far Horizons")
        
        # Test Edge of the Empire filtering
        selected_sources = ['book:eote']
        filtered_records = parser.filter_by_sources(records, selected_sources)
        
        print(f"Filtered to {len(filtered_records)} weapons from Edge of the Empire Core Rulebook")
        
        if filtered_records:
            print("✓ Real file source filtering works")
            return True
        else:
            print("⚠ No weapons found for Edge of the Empire - this might be expected if the source isn't in the file")
            return True
        
    except Exception as e:
        print(f"✗ Real file test failed: {e}")
        return False

def test_scan_directory_categorization():
    """Test that scan_directory properly categorizes weapons"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing scan_directory categorization...")
        
        # Create a temporary directory with a weapons file
        with tempfile.TemporaryDirectory() as temp_dir:
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
</Weapons>'''
            
            weapons_file = os.path.join(temp_dir, 'test_weapons.xml')
            with open(weapons_file, 'w') as f:
                f.write(xml_content)
            
            parser = XMLParser()
            all_records = parser.scan_directory(temp_dir, ['far-horizons'])
            
            # Check that weapons are properly categorized
            assert 'weapons' in all_records, "'weapons' key should be in all_records"
            assert len(all_records['weapons']) == 1, f"Expected 1 weapon, got {len(all_records['weapons'])}"
            
            # Check that no "items" records are created
            assert 'items' not in all_records or len(all_records['items']) == 0, "No 'items' records should be created"
            
            print("✓ Scan directory categorization works correctly")
            return True
        
    except Exception as e:
        print(f"✗ Scan directory categorization test failed: {e}")
        return False

def main():
    """Run source filtering tests"""
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
        print()
    
    print("=" * 40)
    print(f"Source filtering tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All source filtering tests passed!")
        return 0
    else:
        print("✗ Some source filtering tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 