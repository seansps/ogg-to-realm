#!/usr/bin/env python3
"""
Test script for adversary inventory parsing and conversion
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from json_parser import JSONParser
from data_mapper import DataMapper

def test_adversary_inventory_parsing():
    """Test adversary inventory parsing with Imperial Stormtrooper"""
    try:
        parser = JSONParser()
        data_mapper = DataMapper()
        
        # Parse Imperial Stormtrooper
        records = parser.parse_json_file('Adversaries/imperial-military.json')
        stormtrooper = None
        for record in records:
            if record['name'] == 'Imperial Stormtrooper':
                stormtrooper = record
                break
        
        assert stormtrooper is not None, "Imperial Stormtrooper not found in adversaries file"
        
        # Check raw data
        weapons = stormtrooper['data'].get('weapons', [])
        gear = stormtrooper['data'].get('gear', [])
        
        print("✓ Found Imperial Stormtrooper")
        print(f"  Weapons: {weapons}")
        print(f"  Gear: {gear}")
        
        # Expected weapons and gear
        expected_weapons = ['Blaster rifle', 'Vibroknife', 'Frag grenade', 'Light repeating blaster']
        expected_gear = ['Utility belt', 'Extra reloads', 'Stormtrooper armour (+2 Soak)', '2 Frag grenades']
        
        assert weapons == expected_weapons, f"Weapons mismatch: {weapons} != {expected_weapons}"
        assert gear == expected_gear, f"Gear mismatch: {gear} != {expected_gear}"
        
        # Convert to Realm VTT
        converted = data_mapper.convert_oggdude_to_realm_vtt(stormtrooper, 'test_campaign', 'Imperial Military')
        
        # Check basic structure
        assert converted['name'] == 'Imperial Stormtrooper'
        assert converted['recordType'] == 'npcs'
        assert converted['data']['type'] == 'minion'
        
        # Check inventory
        inventory = converted['data']['inventory']
        assert isinstance(inventory, list), "Inventory should be a list"
        assert len(inventory) == 8, f"Expected 8 inventory items, got {len(inventory)}"
        
        print(f"✓ Converted to Realm VTT with {len(inventory)} inventory items")
        
        # Test each inventory item
        item_names = [item['name'] for item in inventory]
        print(f"  Item names: {item_names}")
        
        # Check for expected items
        expected_items = [
            'Unarmed Combat',
            'Blaster Rifle',
            'Vibroknife', 
            'Frag Grenade',
            'Light Repeating Blaster',
            'Utility Belt',
            'Extra Reload',  # Should be singularized and found in OGG
            'Stormtrooper Armor'  # Ad-hoc armor item (armour → Armor conversion)
        ]
        
        for expected_item in expected_items:
            found = any(item['name'] == expected_item for item in inventory)
            assert found, f"Expected item '{expected_item}' not found in inventory"
        
        print("✓ All expected items found in inventory")
        
        # Detailed item checks and merged grenades
        frag_items = [i for i in inventory if i['name'] == 'Frag Grenade']
        assert len(frag_items) == 1, "Frag Grenade should appear once after merge"
        frag = frag_items[0]
        assert frag['data']['type'] in ['ranged weapon'], "Frag Grenade should be a ranged weapon"
        assert frag['data'].get('count', 0) == 3, f"Frag Grenade merged count should be 3, got {frag['data'].get('count')}"
        assert frag['data'].get('ammo', 0) == frag['data'].get('count'), "Ammo should equal count"

        for item in inventory:
            # All items should have required fields
            assert '_id' in item, f"Item {item['name']} missing _id field"
            assert 'recordType' in item, f"Item {item['name']} missing recordType field"
            assert item['recordType'] == 'items', f"Item {item['name']} should have recordType 'items'"
            assert 'data' in item, f"Item {item['name']} missing data field"
            assert 'type' in item['data'], f"Item {item['name']} missing type in data"
            assert 'carried' in item['data'], f"Item {item['name']} missing carried field"
            assert item['data']['carried'] == 'equipped', f"Item {item['name']} should be equipped"
            if item['name'] == 'Extra Reload':
                assert item['data']['type'] == 'general', "Extra Reload should be general type"
            if item['name'] == 'Stormtrooper Armor':
                assert item['data']['type'] == 'armor', "Stormtrooper Armor should be armor type"
                assert item['data']['soakBonus'] == 2, "Stormtrooper Armor should have +2 soak"
                assert item['data']['defense'] == 0, "Stormtrooper Armor should have 0 defense"
        
        print("✓ All inventory items have required fields and correct types")
        
        # Test singularization
        test_singularization(data_mapper)
        
        # Test credits handling
        test_credits_handling(data_mapper)
        
        # Test armor parsing
        test_armor_parsing(data_mapper)
        
        print("✓ All adversary inventory tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Adversary inventory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_singularization(data_mapper):
    """Test name singularization logic"""
    print("\nTesting singularization:")
    
    test_cases = [
        ('Extra reloads', 'Extra reload'),
        ('Frag grenades', 'Frag grenade'), 
        ('Blaster rifles', 'Blaster rifle'),
        ('Batteries', 'Battery'),
        ('Knives', 'Knife'),
        ('Credits', 'Credit'),
        ('Stories', 'Story'),
        ('Glasses', 'Glasses'),  # Should not change
    ]
    
    for plural, expected_singular in test_cases:
        actual_singular = data_mapper._singularize_name(plural)
        assert actual_singular == expected_singular, f"Singularization failed: '{plural}' -> '{actual_singular}', expected '{expected_singular}'"
        print(f"  ✓ '{plural}' -> '{actual_singular}'")

def test_credits_handling(data_mapper):
    """Test credits detection and conversion"""
    print("\nTesting credits handling:")
    
    # Test credits detection
    test_cases = [
        ('500 credits', True, 500),
        ('1000 credit', True, 1000),
        ('Credits', True, 100),
        ('credit', True, 100),
        ('normal gear', False, 0),
    ]
    
    for text, expected_is_credits, expected_amount in test_cases:
        is_credits, amount = data_mapper._is_credits_item(text)
        assert is_credits == expected_is_credits, f"Credits detection failed for '{text}'"
        if is_credits:
            assert amount == expected_amount, f"Credits amount wrong for '{text}': got {amount}, expected {expected_amount}"
        print(f"  ✓ '{text}' -> credits: {is_credits}, amount: {amount}")
    
    # Test credits item creation
    credits_item = data_mapper._create_credits_item(1500)
    assert credits_item['name'] == 'Credits'
    assert credits_item['data']['type'] == 'pack'
    assert credits_item['data']['cash'] == 1500
    print("  ✓ Credits item creation works correctly")
    
    # Test full conversion with credits
    inventory = data_mapper._convert_adversary_inventory([], ['1000 credits', 'normal gear'])
    credits_items = [item for item in inventory if item['data']['type'] == 'pack']
    assert len(credits_items) == 1, "Should have exactly one credits item"
    assert credits_items[0]['data']['cash'] == 1000, "Credits amount should be 1000"
    print("  ✓ Full credits conversion works correctly")

def test_armor_parsing(data_mapper):
    """Test armor stats parsing from parentheses"""
    print("\nTesting armor parsing:")
    
    test_cases = [
        ('Stormtrooper armour (+2 Soak)', 'Stormtrooper Armor', 2, 0),  # British -> American
        ('Padded armor (+1 Defence, +1 Soak)', 'Padded armor', 1, 1),
        ('Heavy clothing (+1 Defense)', 'Heavy clothing', 0, 1),
        ('Armoured vest (+1 Soak, +2 Defence)', 'Armored vest', 1, 2),  # British -> American
        ('Battle Armour (+3 Soak)', 'Battle Armor', 3, 0),  # Test Armour -> Armor
        ('Regular jacket', 'Regular jacket', 0, 0),
    ]
    
    for text, expected_name, expected_soak, expected_defense in test_cases:
        name, soak, defense = data_mapper._parse_armor_stats(text)
        assert name == expected_name, f"Name parsing failed for '{text}': got '{name}', expected '{expected_name}'"
        assert soak == expected_soak, f"Soak parsing failed for '{text}': got {soak}, expected {expected_soak}"
        assert defense == expected_defense, f"Defense parsing failed for '{text}': got {defense}, expected {expected_defense}"
        print(f"  ✓ '{text}' -> name: '{name}', soak: {soak}, defense: {defense}")

def test_count_parsing(data_mapper):
    """Test count parsing from item names"""
    print("\nTesting count parsing:")
    
    test_cases = [
        ('2 Frag grenades', 2, 'Frag grenade'),
        ('10 Credits', 10, 'Credit'),
        ('3 Extra reloads', 3, 'Extra reload'),
        ('Blaster rifle', 1, 'Blaster rifle'),
        ('100 credits', 100, 'credit'),
    ]
    
    for text, expected_count, expected_name in test_cases:
        count, name = data_mapper._parse_item_count(text)
        assert count == expected_count, f"Count parsing failed for '{text}': got {count}, expected {expected_count}"
        assert name == expected_name, f"Name parsing failed for '{text}': got '{name}', expected '{expected_name}'"
        print(f"  ✓ '{text}' -> count: {count}, name: '{name}'")

def run_tests():
    """Run all adversary inventory tests"""
    print("Running Adversary Inventory Tests...")
    
    success = test_adversary_inventory_parsing()
    
    if success:
        print("\n✓ All adversary inventory tests passed!")
        return True
    else:
        print("\n❌ Some adversary inventory tests failed!")
        return False

if __name__ == '__main__':
    run_tests()