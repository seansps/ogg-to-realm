#!/usr/bin/env python3
"""
Test script for field mapping functionality
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json

def test_field_mapping_loading():
    """Test that field mapping loads correctly"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing field mapping loading...")
        
        parser = XMLParser()
        
        # Check that field mapping was loaded
        assert 'weapons' in parser.field_mapping, "Weapons mapping not found"
        assert 'species' in parser.field_mapping, "Species mapping not found"
        assert 'armor' in parser.field_mapping, "Armor mapping not found"
        assert 'gear' in parser.field_mapping, "Gear mapping not found"
        
        print("✓ Field mapping loaded successfully")
        return True
        
    except Exception as e:
        print(f"✗ Field mapping loading failed: {e}")
        return False

def test_field_mapping_application():
    """Test that field mapping is applied correctly"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing field mapping application...")
        
        parser = XMLParser()
        
        # Test weapon mapping
        weapon_data = {
            'Name': 'Test Blaster',
            'Description': 'A test weapon',
            'Type': 'ranged weapon',
            'Encumbrance': 2,
            'Price': '500',
            'Rarity': 3,
            'Restricted': 'yes',
            'SkillKey': 'RANGLT',
            'Damage': 6,
            'Crit': 3,
            'RangeValue': 'wrMedium',
            'Qualities': ['Accurate 1'],
            'HP': 2
        }
        
        mapped_weapon = parser._apply_field_mapping('weapons', weapon_data)
        
        # Check that fields were mapped correctly
        assert mapped_weapon['name'] == 'Test Blaster', f"Name not mapped: {mapped_weapon.get('name')}"
        assert mapped_weapon['description'] == 'A test weapon', f"Description not mapped: {mapped_weapon.get('description')}"
        assert mapped_weapon['type'] == 'ranged weapon', f"Type not mapped: {mapped_weapon.get('type')}"
        assert mapped_weapon['encumbrance'] == 2, f"Encumbrance not mapped: {mapped_weapon.get('encumbrance')}"
        assert mapped_weapon['price'] == '500', f"Price not mapped: {mapped_weapon.get('price')}"
        assert mapped_weapon['rarity'] == 3, f"Rarity not mapped: {mapped_weapon.get('rarity')}"
        assert mapped_weapon['restricted'] == 'yes', f"Restricted not mapped: {mapped_weapon.get('restricted')}"
        assert mapped_weapon['weaponSkill'] == 'RANGLT', f"WeaponSkill not mapped: {mapped_weapon.get('weaponSkill')}"
        assert mapped_weapon['damage'] == 6, f"Damage not mapped: {mapped_weapon.get('damage')}"
        assert mapped_weapon['crit'] == 3, f"Crit not mapped: {mapped_weapon.get('crit')}"
        assert mapped_weapon['range'] == 'wrMedium', f"Range not mapped: {mapped_weapon.get('range')}"
        assert mapped_weapon['special'] == ['Accurate 1'], f"Special not mapped: {mapped_weapon.get('special')}"
        assert mapped_weapon['hardpoints'] == 2, f"Hardpoints not mapped: {mapped_weapon.get('hardpoints')}"
        
        print("✓ Weapon field mapping applied correctly")
        
        # Test armor mapping
        armor_data = {
            'Name': 'Test Armor',
            'Description': 'A test armor',
            'Type': 'armor',
            'Encumbrance': 3,
            'Price': '1000',
            'Rarity': 4,
            'Restricted': 'no',
            'Soak': 2,
            'Defense': 1,
            'HP': 3
        }
        
        mapped_armor = parser._apply_field_mapping('armor', armor_data)
        
        assert mapped_armor['name'] == 'Test Armor', f"Armor name not mapped: {mapped_armor.get('name')}"
        assert mapped_armor['soak'] == 2, f"Armor soak not mapped: {mapped_armor.get('soak')}"
        assert mapped_armor['defense'] == 1, f"Armor defense not mapped: {mapped_armor.get('defense')}"
        assert mapped_armor['hardpoints'] == 3, f"Armor hardpoints not mapped: {mapped_armor.get('hardpoints')}"
        
        print("✓ Armor field mapping applied correctly")
        
        # Test gear mapping
        gear_data = {
            'Name': 'Test Gear',
            'Description': 'A test gear',
            'Type': 'gear',
            'Encumbrance': 1,
            'Price': '100',
            'Rarity': 2,
            'Restricted': 'no',
            'Consumable': True
        }
        
        mapped_gear = parser._apply_field_mapping('gear', gear_data)
        
        assert mapped_gear['name'] == 'Test Gear', f"Gear name not mapped: {mapped_gear.get('name')}"
        assert mapped_gear['consumable'] == True, f"Gear consumable not mapped: {mapped_gear.get('consumable')}"
        
        print("✓ Gear field mapping applied correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Field mapping application failed: {e}")
        return False

def test_unknown_record_type():
    """Test handling of unknown record types"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing unknown record type handling...")
        
        parser = XMLParser()
        
        # Test with unknown record type
        unknown_data = {
            'Name': 'Test Item',
            'Description': 'A test item',
            'CustomField': 'custom value'
        }
        
        mapped_data = parser._apply_field_mapping('unknown_type', unknown_data)
        
        # Should return original data unchanged
        assert mapped_data == unknown_data, f"Unknown type should return original data: {mapped_data}"
        
        print("✓ Unknown record type handled correctly")
        return True
        
    except Exception as e:
        print(f"✗ Unknown record type handling failed: {e}")
        return False

def test_missing_fields():
    """Test handling of missing fields"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing missing fields handling...")
        
        parser = XMLParser()
        
        # Test with missing fields
        incomplete_data = {
            'Name': 'Test Weapon',
            'Description': 'A test weapon'
            # Missing other fields
        }
        
        mapped_data = parser._apply_field_mapping('weapons', incomplete_data)
        
        # Should have mapped fields and None for missing ones
        assert mapped_data['name'] == 'Test Weapon', f"Name should be mapped: {mapped_data.get('name')}"
        assert mapped_data['description'] == 'A test weapon', f"Description should be mapped: {mapped_data.get('description')}"
        assert 'damage' in mapped_data, "Missing fields should be included"
        assert mapped_data.get('damage') is None, "Missing fields should be None"
        
        print("✓ Missing fields handled correctly")
        return True
        
    except Exception as e:
        print(f"✗ Missing fields handling failed: {e}")
        return False

def main():
    """Run field mapping tests"""
    print("Running field mapping tests")
    print("=" * 40)
    
    tests = [
        test_field_mapping_loading,
        test_field_mapping_application,
        test_unknown_record_type,
        test_missing_fields
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Field mapping tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All field mapping tests passed!")
        return 0
    else:
        print("✗ Some field mapping tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 