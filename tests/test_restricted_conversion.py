#!/usr/bin/env python3
"""
Test restricted field conversion from OggDude format (true/false) to Realm VTT format (yes/no)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_mapper import DataMapper

def test_restricted_conversion():
    """Test that restricted field is correctly converted from true/false to yes/no"""
    print("Testing restricted field conversion...")
    
    mapper = DataMapper()
    
    # Test cases for different input formats
    test_cases = [
        # (input, expected_output, description)
        (True, 'yes', 'Boolean True'),
        (False, 'no', 'Boolean False'),
        ('true', 'yes', 'String "true"'),
        ('false', 'no', 'String "false"'),
        ('TRUE', 'yes', 'String "TRUE"'),
        ('FALSE', 'no', 'String "FALSE"'),
        ('yes', 'yes', 'String "yes"'),
        ('no', 'no', 'String "no"'),
        (1, 'yes', 'Integer 1'),
        (0, 'no', 'Integer 0'),
        ('', 'no', 'Empty string'),
        (None, 'no', 'None value'),
    ]
    
    for input_val, expected, description in test_cases:
        result = mapper._convert_restricted_value(input_val)
        if result == expected:
            print(f"  ✓ {description}: '{input_val}' -> '{result}'")
        else:
            print(f"  ✗ {description}: '{input_val}' -> '{result}' (expected '{expected}')")
            return False
    
    print("✓ All restricted field conversion tests passed!")
    return True

def test_item_conversion_with_restricted():
    """Test that items with restricted field are converted correctly"""
    print("\nTesting item conversion with restricted field...")
    
    mapper = DataMapper()
    
    # Test weapon with restricted field
    weapon_data = {
        'name': 'Test Weapon',
        'type': 'ranged weapon',
        'restricted': True,
        'data': {
            'name': 'Test Weapon',
            'type': 'ranged weapon',
            'restricted': True
        }
    }
    
    converted_weapon = mapper._convert_item(weapon_data, 'test-campaign', 'Test Category')
    weapon_restricted = converted_weapon['data'].get('restricted')
    
    if weapon_restricted == 'yes':
        print(f"  ✓ Weapon restricted field converted: {weapon_restricted}")
    else:
        print(f"  ✗ Weapon restricted field should be 'yes', got: {weapon_restricted}")
        return False
    
    # Test armor with restricted field
    armor_data = {
        'name': 'Test Armor',
        'type': 'armor',
        'data': {
            'name': 'Test Armor',
            'type': 'armor',
            'restricted': False
        }
    }
    
    converted_armor = mapper._convert_item(armor_data, 'test-campaign', 'Test Category')
    armor_restricted = converted_armor['data'].get('restricted')
    
    if armor_restricted == 'no':
        print(f"  ✓ Armor restricted field converted: {armor_restricted}")
    else:
        print(f"  ✗ Armor restricted field should be 'no', got: {armor_restricted}")
        return False
    
    # Test gear with restricted field
    gear_data = {
        'name': 'Test Gear',
        'type': 'gear',
        'data': {
            'name': 'Test Gear',
            'type': 'gear',
            'restricted': 'true'
        }
    }
    
    converted_gear = mapper._convert_item(gear_data, 'test-campaign', 'Test Category')
    gear_restricted = converted_gear['data'].get('restricted')
    
    if gear_restricted == 'yes':
        print(f"  ✓ Gear restricted field converted: {gear_restricted}")
    else:
        print(f"  ✗ Gear restricted field should be 'yes', got: {gear_restricted}")
        return False
    
    # Test vehicle with restricted field
    vehicle_data = {
        'name': 'Test Vehicle',
        'type': 'vehicle',
        'data': {
            'name': 'Test Vehicle',
            'type': 'vehicle',
            'restricted': 'false'
        }
    }
    
    converted_vehicle = mapper._convert_vehicle(vehicle_data, 'test-campaign', 'Test Category')
    vehicle_restricted = converted_vehicle['data'].get('restricted')
    
    if vehicle_restricted == 'no':
        print(f"  ✓ Vehicle restricted field converted: {vehicle_restricted}")
    else:
        print(f"  ✗ Vehicle restricted field should be 'no', got: {vehicle_restricted}")
        return False
    
    print("✓ All item conversion restricted field tests passed!")
    return True

if __name__ == '__main__':
    print("Running restricted field conversion tests...")
    
    success = True
    success &= test_restricted_conversion()
    success &= test_item_conversion_with_restricted()
    
    if success:
        print("\n✓ All restricted field conversion tests passed!")
    else:
        print("\n✗ Some restricted field conversion tests failed!")
        sys.exit(1) 