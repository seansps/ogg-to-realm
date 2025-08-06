#!/usr/bin/env python3
"""
Test script for Suppress Force Power parsing with complex AbilitySpan patterns
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_suppress_force_power():
    """Test Suppress Force Power parsing with complex AbilitySpan patterns"""
    try:
        parser = XMLParser()
        
        # Load the actual Suppress Force Power XML file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        suppress_path = os.path.join(project_root, "OggData", "Force Powers", "Suppress.xml")
        
        print("Testing Suppress Force Power parsing...")
        
        with open(suppress_path, 'r') as f:
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
        if name == 'Suppress':
            print(f"  ✓ Name correctly extracted: {name}")
        else:
            print(f"  ✗ Name extraction failed: expected 'Suppress', got '{name}'")
            return False
        
        # Check cost field (should be from first row, highest value - 10)
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
        
        # Test specific hidden talents based on AbilitySpan patterns
        expected_hidden = {
            'hide1_2': 'Yes',  # span=0 in row 1, col 2
            'hide2_2': 'Yes',  # span=0 in row 2, col 2
            'hide2_3': 'Yes',  # span=0 in row 2, col 3 (part of span 2)
            'hide3_2': 'Yes',  # span=0 in row 3, col 2
            'hide4_2': 'Yes',  # span=0 in row 4, col 2
            'hide4_4': 'Yes'   # span=0 in row 4, col 4
        }
        
        for hide_field, expected_value in expected_hidden.items():
            actual_value = data.get(hide_field)
            if actual_value == expected_value:
                print(f"  ✓ {hide_field} correctly set: {expected_value}")
            else:
                print(f"  ✗ {hide_field} failed: expected '{expected_value}', got '{actual_value}'")
                return False
        
        # Test that hidden talents are empty arrays
        hidden_talent_fields = ['talent1_2', 'talent2_2', 'talent2_3', 'talent3_2', 'talent4_2', 'talent4_4']
        for talent_field in hidden_talent_fields:
            talent_array = data.get(talent_field, 'NOT_SET')
            if talent_array == []:
                print(f"  ✓ {talent_field} correctly set to empty array")
            else:
                print(f"  ✗ {talent_field} should be empty array, got: {talent_array}")
                return False
        
        # Test connector fields - based on directions and hiding logic
        expected_connectors = {
            'connector1_3': 'Yes',  # Row 1 has down=true in position 3
            'connector2_1': 'Yes',  # Row 2 has down=true in position 1
            'connector2_3': 'Yes',  # Row 2 has down=true in position 3 
            'connector3_1': 'Yes',  # Row 3 has down=true in position 1
            'connector3_3': 'Yes',  # Row 3 has down=true in position 3
            'connector4_1': 'Yes',  # Row 4 has down=true in position 1
            'connector4_3': 'Yes'   # Row 4 has down=true in position 3
        }
        
        for connector_field, expected_value in expected_connectors.items():
            actual_value = data.get(connector_field)
            if actual_value == expected_value:
                print(f"  ✓ {connector_field} correctly set: {expected_value}")
            else:
                print(f"  ✗ {connector_field} failed: expected '{expected_value}', got '{actual_value}'")
                return False
        
        # Test horizontal connectors
        expected_h_connectors = {
            'h_connector1_3': 'Yes',
            'h_connector1_4': 'Yes',
            'h_connector2_4': 'Yes',
            'h_connector3_4': 'Yes'
        }
        
        for connector_field, expected_value in expected_h_connectors.items():
            actual_value = data.get(connector_field)
            if actual_value == expected_value:
                print(f"  ✓ {connector_field} correctly set: {expected_value}")
            else:
                print(f"  ✗ {connector_field} failed: expected '{expected_value}', got '{actual_value}'")
                return False
        
        # Test fields structure for hiding talents and connectors
        expected_field_hidden = [
            'talent1_2', 'talent2_2', 'talent2_3', 'talent3_2', 'talent4_2', 'talent4_4',
            'h_connector1_2', 'h_connector2_2', 'h_connector2_3', 'h_connector3_2', 'h_connector4_2', 'h_connector4_4'
        ]
        
        for field_name in expected_field_hidden:
            field_config = fields.get(field_name, {})
            if field_config.get('hidden') == True:
                print(f"  ✓ {field_name} correctly hidden in fields structure")
            else:
                print(f"  ✗ {field_name} not properly hidden in fields: {field_config}")
                return False
        
        # Test fields structure for showing no_talent placeholders
        expected_no_talent_shown = [
            'no_talent1_2', 'no_talent2_2', 'no_talent2_3', 'no_talent3_2', 'no_talent4_2', 'no_talent4_4'
        ]
        
        for field_name in expected_no_talent_shown:
            field_config = fields.get(field_name, {})
            if field_config.get('hidden') == False:
                print(f"  ✓ {field_name} correctly shown in fields structure")
            else:
                print(f"  ✗ {field_name} should be shown in fields: {field_config}")
                return False
        
        print("  ✓ All Suppress Force Power parsing tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_suppress_force_power()
    if success:
        print("\n🎉 Suppress Force Power test passed!")
        sys.exit(0)
    else:
        print("\n❌ Suppress Force Power test failed!")
        sys.exit(1)