#!/usr/bin/env python3
"""
Test that attachments are correctly typed and gear subtypes are set properly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_mapper import DataMapper

def test_attachment_types():
    """Test that attachments are correctly typed and not processed as weapons"""
    print("Testing attachment type conversion...")
    
    mapper = DataMapper()
    
    # Test weapon attachment
    weapon_attachment_data = {
        'name': 'Test Weapon Attachment',
        'type': 'weapon attachment',
        'data': {
            'name': 'Test Weapon Attachment',
            'type': 'weapon attachment',
            'price': '1000',
            'rarity': 5
        }
    }
    
    converted_weapon_attachment = mapper._convert_item(weapon_attachment_data, 'test-campaign', 'Test Category')
    weapon_attachment_type = converted_weapon_attachment['data'].get('type')
    
    if weapon_attachment_type == 'weapon attachment':
        print(f"  ✓ Weapon attachment type correctly set: {weapon_attachment_type}")
    else:
        print(f"  ✗ Weapon attachment type should be 'weapon attachment', got: {weapon_attachment_type}")
        return False
    
    # Test armor attachment
    armor_attachment_data = {
        'name': 'Test Armor Attachment',
        'type': 'armor attachment',
        'data': {
            'name': 'Test Armor Attachment',
            'type': 'armor attachment',
            'price': '500',
            'rarity': 3
        }
    }
    
    converted_armor_attachment = mapper._convert_item(armor_attachment_data, 'test-campaign', 'Test Category')
    armor_attachment_type = converted_armor_attachment['data'].get('type')
    
    if armor_attachment_type == 'armor attachment':
        print(f"  ✓ Armor attachment type correctly set: {armor_attachment_type}")
    else:
        print(f"  ✗ Armor attachment type should be 'armor attachment', got: {armor_attachment_type}")
        return False
    
    # Test vehicle attachment
    vehicle_attachment_data = {
        'name': 'Test Vehicle Attachment',
        'type': 'vehicle attachment',
        'data': {
            'name': 'Test Vehicle Attachment',
            'type': 'vehicle attachment',
            'price': '2000',
            'rarity': 7
        }
    }
    
    converted_vehicle_attachment = mapper._convert_item(vehicle_attachment_data, 'test-campaign', 'Test Category')
    vehicle_attachment_type = converted_vehicle_attachment['data'].get('type')
    
    if vehicle_attachment_type == 'vehicle attachment':
        print(f"  ✓ Vehicle attachment type correctly set: {vehicle_attachment_type}")
    else:
        print(f"  ✗ Vehicle attachment type should be 'vehicle attachment', got: {vehicle_attachment_type}")
        return False
    
    print("✓ All attachment type tests passed!")
    return True

def test_gear_subtypes():
    """Test that gear subtypes are set from the original OggDude Type value"""
    print("\nTesting gear subtype conversion...")
    
    mapper = DataMapper()
    
    # Test gear with different OggDude Type values
    test_cases = [
        ('general', 'general'),
        ('medical', 'medical'),
        ('security', 'security'),
        ('survival', 'survival'),
        ('tool', 'tool'),
        ('communication', 'communication'),
        ('custom', 'custom')
    ]
    
    for oggdude_type, expected_subtype in test_cases:
        gear_data = {
            'name': f'Test {oggdude_type.title()} Gear',
            'type': 'gear',
            'data': {
                'name': f'Test {oggdude_type.title()} Gear',
                'type': oggdude_type,
                'price': '100',
                'rarity': 2
            }
        }
        
        converted_gear = mapper._convert_item(gear_data, 'test-campaign', 'Test Category')
        actual_subtype = converted_gear['data'].get('subtype')
        actual_type = converted_gear['data'].get('type')
        
        if actual_type == 'general' and actual_subtype == expected_subtype:
            print(f"  ✓ {oggdude_type.title()} gear: type='{actual_type}', subtype='{actual_subtype}'")
        else:
            print(f"  ✗ {oggdude_type.title()} gear: type should be 'general' and subtype should be '{expected_subtype}', got type='{actual_type}', subtype='{actual_subtype}'")
            return False
    
    print("✓ All gear subtype tests passed!")
    return True

def test_weapon_types_not_affected():
    """Test that weapon types are still processed correctly"""
    print("\nTesting weapon type conversion (should not be affected)...")
    
    mapper = DataMapper()
    
    # Test ranged weapon
    ranged_weapon_data = {
        'name': 'Test Blaster',
        'type': 'ranged weapon',
        'data': {
            'name': 'Test Blaster',
            'type': 'ranged weapon',
            'weaponSkill': 'Ranged (Light)',
            'damage': 6,
            'crit': 3
        }
    }
    
    converted_ranged_weapon = mapper._convert_item(ranged_weapon_data, 'test-campaign', 'Test Category')
    ranged_weapon_type = converted_ranged_weapon['data'].get('type')
    
    if ranged_weapon_type == 'ranged weapon':
        print(f"  ✓ Ranged weapon type correctly set: {ranged_weapon_type}")
    else:
        print(f"  ✗ Ranged weapon type should be 'ranged weapon', got: {ranged_weapon_type}")
        return False
    
    # Test melee weapon
    melee_weapon_data = {
        'name': 'Test Sword',
        'type': 'melee weapon',
        'data': {
            'name': 'Test Sword',
            'type': 'melee weapon',
            'weaponSkill': 'Melee',
            'damage': 5,
            'crit': 2
        }
    }
    
    converted_melee_weapon = mapper._convert_item(melee_weapon_data, 'test-campaign', 'Test Category')
    melee_weapon_type = converted_melee_weapon['data'].get('type')
    
    if melee_weapon_type == 'melee weapon':
        print(f"  ✓ Melee weapon type correctly set: {melee_weapon_type}")
    else:
        print(f"  ✗ Melee weapon type should be 'melee weapon', got: {melee_weapon_type}")
        return False
    
    print("✓ All weapon type tests passed!")
    return True

if __name__ == '__main__':
    print("Running attachment and gear type tests...")
    
    success = True
    success &= test_attachment_types()
    success &= test_gear_subtypes()
    success &= test_weapon_types_not_affected()
    
    if success:
        print("\n✓ All attachment and gear type tests passed!")
    else:
        print("\n✗ Some attachment and gear type tests failed!")
        sys.exit(1) 