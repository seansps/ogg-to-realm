#!/usr/bin/env python3
"""
Test script for YT-1300 Light Freighter vehicle parsing
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_yt1300_vehicle_parsing():
    """Test parsing of YT-1300 Light Freighter vehicle"""
    try:
        parser = XMLParser()
        
        # Get the path to the YT-1300 XML file
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        vehicle_file = os.path.join(project_root, "OggData", "Vehicles", "YT-1300 Light Freighter.xml")
        
        if not os.path.exists(vehicle_file):
            print(f"❌ YT-1300 vehicle file not found at {vehicle_file}")
            return False
        
        print("Testing YT-1300 Light Freighter vehicle parsing...")
        
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
        
        # Check basic structure (data mapper output)
        assert vehicle['recordType'] == 'npcs', f"Expected recordType 'npcs', got {vehicle['recordType']}"
        assert vehicle['name'] == 'YT-1300 Light Freighter', f"Expected name 'YT-1300 Light Freighter', got {vehicle['name']}"
        assert vehicle['unidentifiedName'] == 'Unknown Vehicle', f"Expected unidentifiedName 'Unknown Vehicle'"
        assert vehicle['locked'] == True, "Expected vehicle to be locked"
        assert vehicle['campaignId'] == 'test_campaign_id', f"Expected campaignId 'test_campaign_id', got {vehicle.get('campaignId')}"
        assert vehicle['category'] == 'Test Category', f"Expected category 'Test Category', got {vehicle.get('category')}"
        assert vehicle['identified'] == True, "Expected vehicle to be identified"
        assert vehicle['shared'] == True, "Expected vehicle to be shared by default"
        
        # Check data fields
        data = vehicle['data']
        
        # Basic vehicle properties
        assert data['type'] == 'vehicle', f"Expected type 'vehicle', got {data.get('type')}"
        assert data['subtype'] == 'Freighter', f"Expected subtype 'Freighter', got {data.get('subtype')}"
        assert data['sensorRange'] == 'Short', f"Expected sensorRange 'Short', got {data.get('sensorRange')}"  # 'sr' prefix removed
        assert data['hyperdrive'] == 'Class 2 (backup Class 12)', f"Expected hyperdrive format, got {data.get('hyperdrive')}"
        assert data['navicomputer'] == True, "Expected navicomputer to be True"
        assert data['restricted'] == 'no', f"Expected restricted 'no', got {data.get('restricted')}"
        assert data['crew'] == 'One Pilot, One Co-Pilot, One Engineer', f"Unexpected crew value"
        assert data['passengers'] == 6, f"Expected passengers 6, got {data.get('passengers')}"
        assert data['encumbranceCapacity'] == 165, f"Expected encumbranceCapacity 165, got {data.get('encumbranceCapacity')}"
        assert data['consumables'] == 'Two Months', f"Unexpected consumables value"
        assert data['size'] == 'Silhouette 4', f"Expected size 'Silhouette 4', got {data.get('size')}"
        assert data['speed'] == 3, f"Expected speed 3, got {data.get('speed')}"
        assert data['handling'] == -1, f"Expected handling -1, got {data.get('handling')}"
        assert data['soakValue'] == 3, f"Expected soakValue 3, got {data.get('soakValue')}"
        assert data['woundThreshold'] == 22, f"Expected woundThreshold 22, got {data.get('woundThreshold')}"
        assert data['woundsRemaining'] == 22, f"Expected woundsRemaining 22, got {data.get('woundsRemaining')}"
        assert data['strainThreshold'] == 15, f"Expected strainThreshold 15, got {data.get('strainThreshold')}"
        assert data['strainRemaining'] == 15, f"Expected strainRemaining 15, got {data.get('strainRemaining')}"
        assert data['hardpoints'] == 6, f"Expected hardpoints 6, got {data.get('hardpoints')}"
        assert data['price'] == 100000, f"Expected price 100000, got {data.get('price')}"
        assert data['rarity'] == 4, f"Expected rarity 4, got {data.get('rarity')}"
        assert data['starship'] == True, "Expected starship to be True"
        
        # Check defense zones (individual fields, 0 values should not be present)
        assert data['defFore'] == 1, f"Expected defFore 1, got {data.get('defFore')}"
        assert data['defAft'] == 1, f"Expected defAft 1, got {data.get('defAft')}"
        assert 'defPort' not in data, "defPort should not be present when value is 0"
        assert 'defStarboard' not in data, "defStarboard should not be present when value is 0"
        
        # Check inventory (weapons are stored as inventory items)
        inventory = data['inventory']
        assert len(inventory) == 2, f"Expected 2 inventory items, got {len(inventory)}"
        
        # Check first weapon (dorsal) - now as inventory item
        dorsal_weapon = inventory[0]
        assert dorsal_weapon['recordType'] == 'items', "Expected weapon to be an item record"
        assert dorsal_weapon['name'] == 'Medium Laser Cannon', f"Expected 'Medium Laser Cannon', got {dorsal_weapon['name']}"
        assert '_id' in dorsal_weapon, "Expected weapon to have UUID _id field"
        assert len(dorsal_weapon['_id']) == 36, f"Expected UUID format, got {dorsal_weapon['_id']}"
        assert '<strong>Location:</strong> Dorsal' in dorsal_weapon['data']['description'], "Expected location in description"
        assert '<strong>Turret:</strong> Yes' in dorsal_weapon['data']['description'], "Expected turret info in description"
        assert 'Firing Arcs:' not in dorsal_weapon['data']['description'], "Firing arcs should not be in description"
        assert dorsal_weapon['data']['carried'] == 'equipped', "Expected weapon to be equipped"
        assert 'fields' in dorsal_weapon, "Expected fields structure"
        
        # Check firing arcs as proper field
        firing_arc = dorsal_weapon['data']['firingArc']
        assert 'fore' in firing_arc, "Expected fore in firing arcs"
        assert 'aft' in firing_arc, "Expected aft in firing arcs"
        assert 'port' in firing_arc, "Expected port in firing arcs"
        assert 'starboard' in firing_arc, "Expected starboard in firing arcs"
        assert 'dorsal' in firing_arc, "Expected dorsal in firing arcs"
        assert 'ventral' not in firing_arc, "Did not expect ventral in dorsal weapon firing arcs"
        
        # Check animation for laser weapons (YT-1300 is not TIE, so should have hue 360)
        assert 'animation' in dorsal_weapon['data'], "Expected animation field for laser weapon"
        animation = dorsal_weapon['data']['animation']
        assert animation['animationName'] == 'bolt_3', f"Expected animationName 'bolt_3', got {animation.get('animationName')}"
        assert animation['hue'] == 360, f"Expected hue 360 for non-TIE vehicle, got {animation.get('hue')}"
        assert animation['sound'] == 'laser_2', f"Expected sound 'laser_2', got {animation.get('sound')}"
        
        # Check second weapon (ventral) - now as inventory item
        ventral_weapon = inventory[1]
        assert ventral_weapon['recordType'] == 'items', "Expected weapon to be an item record"
        assert ventral_weapon['name'] == 'Medium Laser Cannon', f"Expected 'Medium Laser Cannon', got {ventral_weapon['name']}"
        assert '<strong>Location:</strong> Ventral' in ventral_weapon['data']['description'], "Expected location in description"
        assert '<strong>Turret:</strong> Yes' in ventral_weapon['data']['description'], "Expected turret info in description"
        assert 'Firing Arcs:' not in ventral_weapon['data']['description'], "Firing arcs should not be in description"
        
        # Check firing arcs as proper field
        firing_arc = ventral_weapon['data']['firingArc']
        assert 'fore' in firing_arc, "Expected fore in firing arcs"
        assert 'aft' in firing_arc, "Expected aft in firing arcs"
        assert 'port' in firing_arc, "Expected port in firing arcs"
        assert 'starboard' in firing_arc, "Expected starboard in firing arcs"
        assert 'dorsal' not in firing_arc, "Did not expect dorsal in ventral weapon firing arcs"
        assert 'ventral' in firing_arc, "Expected ventral in firing arcs"
        
        # Check animation for laser weapons (same as dorsal)
        assert 'animation' in ventral_weapon['data'], "Expected animation field for laser weapon"
        animation = ventral_weapon['data']['animation']
        assert animation['hue'] == 360, f"Expected hue 360 for non-TIE vehicle, got {animation.get('hue')}"
        
        # Check features (should include all vehicle actions)
        features = data['features']
        assert isinstance(features, list), "Features should be a list"
        assert len(features) > 0, "Should have some features"
        
        # Check first feature has proper structure
        first_feature = features[0]
        assert '_id' in first_feature, "Feature should have UUID _id field"
        assert len(first_feature['_id']) == 36, f"Expected UUID format, got {first_feature['_id']}"
        assert first_feature['recordType'] == 'records', f"Expected recordType 'records', got {first_feature.get('recordType')}"
        assert first_feature['identified'] == True, "Expected feature to be identified"
        assert 'unidentifiedName' in first_feature, "Expected unidentifiedName field"
        assert 'data' in first_feature, "Expected data field"
        assert 'description' in first_feature['data'], "Expected description in feature data"
        
        # Each feature should have name and description in data
        for feature in features:
            assert 'name' in feature, "Feature should have name"
            assert 'data' in feature and 'description' in feature['data'], "Feature should have description in data"
            assert isinstance(feature['name'], str), "Feature name should be string"
            assert isinstance(feature['data']['description'], str), "Feature description should be string"
        
        print("✓ YT-1300 Light Freighter vehicle parsing test passed")
        return True
        
    except Exception as e:
        print(f"❌ YT-1300 vehicle parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_tests():
    """Run all vehicle tests"""
    print("Running YT-1300 Vehicle Tests...")
    
    success = test_yt1300_vehicle_parsing()
    
    if success:
        print("\n✓ All vehicle tests passed!")
        return True
    else:
        print("\n❌ Some vehicle tests failed!")
        return False

if __name__ == '__main__':
    run_tests()