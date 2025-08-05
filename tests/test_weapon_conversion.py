#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_mapper import DataMapper
from xml_parser import XMLParser
import xml.etree.ElementTree as ET

def test_weapon_conversion():
    """Test weapon conversion functionality"""
    try:
        parser = XMLParser()
        mapper = DataMapper()
        
        test_xml = '''<Weapon>
            <Key>AUTOBLAST</Key>
            <Name>Auto-Blaster</Name>
            <Description>Test description</Description>
            <Sources>
                <Source Page="230">Edge of the Empire Core Rulebook</Source>
            </Sources>
            <Type>Vehicle</Type>
            <SkillKey>GUNN</SkillKey>
            <Damage>3</Damage>
            <Crit>5</Crit>
            <RangeValue>wrClose</RangeValue>
            <Qualities>
                <Quality>
                    <Key>AUTOFIRE</Key>
                    <Count>1</Count>
                </Quality>
            </Qualities>
        </Weapon>'''
        
        root = ET.fromstring(test_xml)
        weapon = parser._extract_weapon_data(root)
        
        if weapon:
            print("Extracted weapon:")
            print(f"  Name: {weapon['name']}")
            print(f"  Sources: {weapon['sources']}")
            print(f"  Type: {weapon['data']['type']}")
            print(f"  Qualities: {weapon['data'].get('qualities', weapon['data'].get('special', 'None'))}")
            
            converted = mapper._convert_item(weapon, 'test-campaign', 'Edge of the Empire Core Rulebook')
            
            print("\nConverted weapon:")
            print(f"  Name: {converted['name']}")
            print(f"  Type: {converted['data']['type']}")
            print(f"  Subtype: {converted['data'].get('subtype', 'None')}")
            print(f"  Range: {converted['data']['range']}")
            print(f"  Special: {converted['data']['special']}")
            print(f"  Category: {converted['category']}")
            
            # Test quality count fields
            print(f"  Auto-fire count: {converted['data'].get('auto-fire', 'None')}")
            
            # Test that the quality count is properly set
            if 'auto-fire' in converted['data']:
                print(f"  ✓ Auto-fire count field set correctly: {converted['data']['auto-fire']}")
            else:
                print(f"  ✗ Auto-fire count field not found")
            
            # Test that no 'qualities' field exists in the final data
            if 'qualities' not in converted['data']:
                print(f"  ✓ No 'qualities' field in final data (correct)")
            else:
                print(f"  ✗ 'qualities' field found in final data (incorrect)")
            
            return True
        else:
            print("No weapon extracted")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_weapon_conversion() 