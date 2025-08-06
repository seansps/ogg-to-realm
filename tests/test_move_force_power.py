#!/usr/bin/env python3
"""
Test script for Move Force Power parsing
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_move_force_power():
    """Test Move Force Power parsing with AbilitySpan and talent structure"""
    try:
        parser = XMLParser()
        
        # Load the actual Move Force Power XML file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        move_path = os.path.join(project_root, "OggData", "Force Powers", "Move.xml")
        
        print("Testing Move Force Power parsing...")
        
        with open(move_path, 'r') as f:
            content = f.read()
        
        root = ET.fromstring(content)
        force_power_data = parser._extract_force_power_data(root)
        
        if force_power_data is None:
            print("  ✗ Force power data extraction failed")
            return False
        
        # Check the extracted data
        data = force_power_data.get('data', {})
        fields = force_power_data.get('fields', {})
        
        # Check name
        name = force_power_data.get('name', '')
        if name == 'Move':
            print(f"  ✓ Name correctly extracted: {name}")
        else:
            print(f"  ✗ Name extraction failed: expected 'Move', got '{name}'")
            return False
        
        # Check cost field (should be from first row, highest value)
        cost = data.get('cost')
        if cost == 10:
            print(f"  ✓ Cost correctly extracted: {cost}")
        else:
            print(f"  ✗ Cost extraction failed: expected 10, got '{cost}'")
            return False
        
        # Check prerequisites
        prereqs = data.get('prereqs')
        if prereqs == "Force Rating 1+":
            print(f"  ✓ Prerequisites correctly set: {prereqs}")
        else:
            print(f"  ✗ Prerequisites failed: expected 'Force Rating 1+', got '{prereqs}'")
            return False
        
        # Check description includes base ability
        description = data.get('description', '')
        if '<strong>Base Ability:</strong>' in description:
            print("  ✓ Base ability description correctly added")
        else:
            print("  ✗ Base ability description not found in description")
            return False
        
        # Test specific talents for first upgrade row
        expected_talents = {
            'talent1_1': 'Magnitude',
            'talent1_2': 'Strength', 
            'talent1_3': 'Range',
            'talent1_4': 'Range'
        }
        
        for talent_field, expected_name in expected_talents.items():
            talent_array = data.get(talent_field)
            if talent_array and len(talent_array) > 0:
                talent = talent_array[0]
                talent_name = talent.get('name')
                talent_data = talent.get('data', {})
                
                if talent_name == expected_name:
                    print(f"  ✓ {talent_field} has correct name: {expected_name}")
                else:
                    print(f"  ✗ {talent_field} name failed: expected '{expected_name}', got '{talent_name}'")
                    return False
                
                # Check force power specific flags
                force_talent = talent_data.get('forceTalent')
                force_power_upgrade = talent_data.get('forcePowerUpgrade')
                if force_talent == 'yes' and force_power_upgrade == 'yes':
                    print(f"  ✓ {talent_field} has correct force power flags")
                else:
                    print(f"  ✗ {talent_field} missing force power flags: forceTalent='{force_talent}', forcePowerUpgrade='{force_power_upgrade}'")
                    return False
            else:
                print(f"  ✗ {talent_field} talent array is missing or empty")
                return False
        
        # Test hidden talents based on AbilitySpan
        # Row 2 should have talent2_4 hidden (span pattern: 1,1,2,0)
        if 'hide2_4' in data and data['hide2_4'] == 'Yes':
            print("  ✓ talent2_4 correctly hidden based on AbilitySpan")
        else:
            print(f"  ✗ talent2_4 should be hidden: hide2_4='{data.get('hide2_4', 'NOT_SET')}'")
            return False
        
        # Check that talent2_4 is empty array
        talent2_4 = data.get('talent2_4', [])
        if talent2_4 == []:
            print("  ✓ talent2_4 correctly set to empty array")
        else:
            print(f"  ✗ talent2_4 should be empty array, got: {talent2_4}")
            return False
        
        # Test fields structure for hiding
        if 'talent2_4' in fields and fields['talent2_4'].get('hidden') == True:
            print("  ✓ talent2_4 correctly hidden in fields structure")
        else:
            print(f"  ✗ talent2_4 not properly hidden in fields: {fields.get('talent2_4', 'NOT_SET')}")
            return False
        
        # Test connector fields
        connector_tests = {
            'connector1_1': 'Yes',
            'connector1_2': 'Yes', 
            'connector1_3': 'Yes',
            'connector1_4': 'Yes'
        }
        
        for connector_field, expected_value in connector_tests.items():
            actual_value = data.get(connector_field)
            if actual_value == expected_value:
                print(f"  ✓ {connector_field} correctly set: {expected_value}")
            else:
                print(f"  ✗ {connector_field} failed: expected '{expected_value}', got '{actual_value}'")
                return False
        
        print("  ✓ All Move Force Power parsing tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_move_force_power()
    if success:
        print("\n🎉 Move Force Power test passed!")
        sys.exit(0)
    else:
        print("\n❌ Move Force Power test failed!")
        sys.exit(1)