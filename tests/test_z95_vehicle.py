#!/usr/bin/env python3
"""
Test script for Z-95 Headhunter vehicle parsing with weapon qualities and firing arcs
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_z95_vehicle_parsing():
    """Test parsing of Z-95 Headhunter vehicle with weapon qualities"""
    try:
        parser = XMLParser()

        # Get the path to the Z-95 XML file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        vehicle_file = os.path.join(project_root, "OggData", "Vehicles", "Z-95-AF4 Headhunter.xml")

        if not os.path.exists(vehicle_file):
            print(f"❌ Z-95 vehicle file not found at {vehicle_file}")
            return False

        print("Testing Z-95 Headhunter vehicle parsing...")

        # Parse the XML
        tree = ET.parse(vehicle_file)
        root = tree.getroot()

        # Parse the vehicle
        vehicles = parser._parse_vehicle(root)

        # Should return exactly one vehicle
        assert len(vehicles) == 1, f"Expected 1 vehicle, got {len(vehicles)}"
        raw_vehicle = vehicles[0]

        # Convert through data mapper to test the final Realm VTT output
        from data_mapper import DataMapper
        data_mapper = DataMapper()
        vehicle = data_mapper.convert_oggdude_to_realm_vtt(raw_vehicle, "test_campaign_id", "Test Category")

        # Check basic structure
        assert vehicle['recordType'] == 'npcs', f"Expected recordType 'npcs', got {vehicle['recordType']}"
        assert vehicle['name'] == 'Z-95-AF4 Headhunter', f"Expected name 'Z-95-AF4 Headhunter', got {vehicle['name']}"

        # Check data fields
        data = vehicle['data']

        # Check inventory (weapons are stored as inventory items)
        inventory = data['inventory']
        assert len(inventory) == 2, f"Expected 2 inventory items (weapons), got {len(inventory)}"

        print(f"  Found {len(inventory)} weapons in inventory")

        # Check first weapon - Light Laser Cannon (Wingtip)
        laser_weapon = inventory[0]
        assert laser_weapon['recordType'] == 'items', "Expected weapon to be an item record"

        # The name should include the location in parentheses
        expected_laser_name = 'Light Laser Cannon (Wingtip)'
        assert laser_weapon['name'] == expected_laser_name, f"Expected '{expected_laser_name}', got '{laser_weapon['name']}'"
        print(f"  ✓ First weapon: {laser_weapon['name']}")

        # Check firing arcs (should only have 'fore')
        firing_arc = laser_weapon['data']['firingArc']
        assert isinstance(firing_arc, list), "firingArc should be a list"
        assert 'fore' in firing_arc, "Expected 'fore' in firing arcs"
        assert len(firing_arc) == 1, f"Expected only 'fore' arc, got {firing_arc}"
        print(f"    Firing arcs: {firing_arc}")

        # Check qualities - should have Linked 1
        special = laser_weapon['data'].get('special', [])
        assert 'Linked' in special, f"Expected 'Linked' quality, got {special}"
        assert laser_weapon['data'].get('linked', 0) == 1, f"Expected Linked count of 1, got {laser_weapon['data'].get('linked')}"
        print(f"    Qualities: {special}, linked={laser_weapon['data'].get('linked')}")

        # Check that weapon is equipped
        assert laser_weapon['data']['carried'] == 'equipped', "Expected weapon to be equipped"

        # Check second weapon - Concussion Missile Launcher (Forward)
        missile_weapon = inventory[1]
        assert missile_weapon['recordType'] == 'items', "Expected weapon to be an item record"

        # The name should include the location in parentheses
        expected_missile_name = 'Concussion Missile Launcher (Forward)'
        assert missile_weapon['name'] == expected_missile_name, f"Expected '{expected_missile_name}', got '{missile_weapon['name']}'"
        print(f"  ✓ Second weapon: {missile_weapon['name']}")

        # Check firing arcs (should only have 'fore')
        firing_arc = missile_weapon['data']['firingArc']
        assert isinstance(firing_arc, list), "firingArc should be a list"
        assert 'fore' in firing_arc, "Expected 'fore' in firing arcs"
        assert len(firing_arc) == 1, f"Expected only 'fore' arc, got {firing_arc}"
        print(f"    Firing arcs: {firing_arc}")

        # Check qualities - should have Linked 1 and Limited Ammo 6
        special = missile_weapon['data'].get('special', [])
        assert 'Linked' in special, f"Expected 'Linked' quality, got {special}"
        assert 'Limited Ammo' in special, f"Expected 'Limited Ammo' quality, got {special}"
        assert missile_weapon['data'].get('linked', 0) == 1, f"Expected Linked count of 1, got {missile_weapon['data'].get('linked')}"
        assert missile_weapon['data'].get('limitedAmmo', 0) == 6, f"Expected Limited Ammo count of 6, got {missile_weapon['data'].get('limitedAmmo')}"
        print(f"    Qualities: {special}, linked={missile_weapon['data'].get('linked')}, limitedAmmo={missile_weapon['data'].get('limitedAmmo')}")

        # Check that weapon is equipped
        assert missile_weapon['data']['carried'] == 'equipped', "Expected weapon to be equipped"

        print("✓ Z-95 Headhunter vehicle parsing test passed")
        return True

    except Exception as e:
        print(f"❌ Z-95 vehicle parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_tests():
    """Run all Z-95 vehicle tests"""
    print("Running Z-95 Vehicle Tests...")

    success = test_z95_vehicle_parsing()

    if success:
        print("\n✓ All Z-95 vehicle tests passed!")
        return True
    else:
        print("\n❌ Some Z-95 vehicle tests failed!")
        return False

if __name__ == '__main__':
    run_tests()
