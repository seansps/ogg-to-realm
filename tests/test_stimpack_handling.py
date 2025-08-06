#!/usr/bin/env python3
"""
Test script for Stimpack custom handling and Gear subtype capitalization
"""

import sys
import os
import unittest
import tempfile

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_mapper import DataMapper

class TestStimpackHandling(unittest.TestCase):
    def setUp(self):
        self.mapper = DataMapper()
    
    def test_stimpack_custom_handling(self):
        """Test that Stimpack gets custom consumable and healing properties"""
        # Create a mock Stimpack item
        stimpack_item = {
            'name': 'Stimpack',
            'recordType': 'items',
            'type': 'gear',
            'data': {
                'subtype': 'Gear',
                'description': 'A medical stimulant that provides quick healing.',
                'price': 25,
                'rarity': 1
            }
        }
        
        # Convert the item
        result = self.mapper.convert_oggdude_to_realm_vtt(stimpack_item, 'test-campaign', 'test-category')
        
        # Check that the custom properties are set
        data = result.get('data', {})
        self.assertTrue(data.get('consumable'), "Stimpack should be consumable")
        self.assertTrue(data.get('hasUseBtn'), "Stimpack should have use button")
        self.assertEqual(data.get('healing'), '5', "Stimpack should have healing value of 5")
        self.assertTrue(data.get('countsAsHealing'), "Stimpack should count as healing")
    
    def test_gear_subtype_capitalization(self):
        """Test that Gear items get proper subtype capitalization"""
        # Test case 1: Gear with no specific type (should be "General")
        generic_gear = {
            'name': 'Generic Gear',
            'recordType': 'items',
            'type': 'gear',
            'data': {
                'subtype': 'Gear',
                'description': 'Some generic gear item.'
            }
        }
        
        result = self.mapper.convert_oggdude_to_realm_vtt(generic_gear, 'test-campaign', 'test-category')
        data = result.get('data', {})
        self.assertEqual(data.get('subtype'), 'General', "Generic gear should have subtype 'General'")
        
        # Test case 2: Gear with specific type (should preserve the type)
        specific_gear = {
            'name': 'Specific Gear',
            'recordType': 'items',
            'type': 'gear',
            'data': {
                'subtype': 'Tool',
                'description': 'A specific tool item.'
            }
        }
        
        result = self.mapper.convert_oggdude_to_realm_vtt(specific_gear, 'test-campaign', 'test-category')
        data = result.get('data', {})
        self.assertEqual(data.get('subtype'), 'Tool', "Specific gear should preserve its type as subtype")
    
    def test_non_stimpack_gear_no_custom_properties(self):
        """Test that non-Stimpack gear items don't get Stimpack properties"""
        # Create a mock non-Stimpack gear item
        other_gear = {
            'name': 'Other Gear',
            'recordType': 'items',
            'type': 'gear',
            'data': {
                'subtype': 'Gear',
                'description': 'Some other gear item.',
                'price': 10,
                'rarity': 1
            }
        }
        
        # Convert the item
        result = self.mapper.convert_oggdude_to_realm_vtt(other_gear, 'test-campaign', 'test-category')
        
        # Check that the custom properties are NOT set
        data = result.get('data', {})
        self.assertFalse(data.get('consumable'), "Non-Stimpack gear should not be consumable by default")
        self.assertFalse(data.get('hasUseBtn'), "Non-Stimpack gear should not have use button by default")
        self.assertNotIn('healing', data, "Non-Stimpack gear should not have healing property")
        self.assertNotIn('countsAsHealing', data, "Non-Stimpack gear should not have countsAsHealing property")

if __name__ == '__main__':
    unittest.main() 