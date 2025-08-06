#!/usr/bin/env python3
"""
Test script for AddedMods dice key conversion
"""

import sys
import os
import unittest
import tempfile
import xml.etree.ElementTree as ET

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.xml_parser import XMLParser

class TestAddedModsDiceConversion(unittest.TestCase):
    def setUp(self):
        self.parser = XMLParser()
    
    def test_added_mods_dice_conversion(self):
        """Test that AddedMods correctly converts dice keys to text version"""
        # Create a mock XML element with AddedMods containing dice keys
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACHMENT</Key>
        <Name>Test Attachment</Name>
        <Description>Test attachment with dice keys</Description>
        <Type>weapon attachment</Type>
        <Price>100</Price>
        <Rarity>2</Rarity>
        <HP>1</HP>
        <AddedMods>
            <Mod>
                <Key>TESTMOD</Key>
                <Count>1</Count>
            </Mod>
        </AddedMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        # Create a temporary file with the XML content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            # Parse the XML file
            records = self.parser.parse_xml_file(temp_file)
            
            # We need to mock the ItemDescriptors to return a description with dice keys
            # Let's directly test the _extract_added_mods method
            root = ET.fromstring(xml_content)
            attachment_elem = root.find('.//ItemAttachment')
            
            # Mock the _get_item_descriptor_description method to return a description with dice keys
            original_method = self.parser._get_item_descriptor_description
            
            def mock_get_description(key):
                if key == 'TESTMOD':
                    return "Takes 1 Less [AD] to Activate"
                return None
            
            self.parser._get_item_descriptor_description = mock_get_description
            
            try:
                # Extract the added mods
                added_mods = self.parser._extract_added_mods(attachment_elem)
                
                # The dice key [AD] should be converted to "Advantage"
                expected = "Takes 1 Less Advantage to Activate"
                self.assertEqual(added_mods, expected, 
                               f"Expected '{expected}', got '{added_mods}'")
                
                print(f"✓ AddedMods dice conversion: '{added_mods}'")
                
            finally:
                # Restore the original method
                self.parser._get_item_descriptor_description = original_method
                
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)
    
    def test_added_mods_multiple_dice_keys(self):
        """Test that AddedMods correctly converts multiple dice keys"""
        # Create a mock XML element with AddedMods containing multiple dice keys
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACHMENT2</Key>
        <Name>Test Attachment 2</Name>
        <Description>Test attachment with multiple dice keys</Description>
        <Type>weapon attachment</Type>
        <Price>200</Price>
        <Rarity>3</Rarity>
        <HP>2</HP>
        <AddedMods>
            <Mod>
                <Key>TESTMOD2</Key>
                <Count>1</Count>
            </Mod>
        </AddedMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        # Create a temporary file with the XML content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            # Parse the XML file
            records = self.parser.parse_xml_file(temp_file)
            
            # We need to mock the ItemDescriptors to return a description with multiple dice keys
            root = ET.fromstring(xml_content)
            attachment_elem = root.find('.//ItemAttachment')
            
            # Mock the _get_item_descriptor_description method to return a description with multiple dice keys
            original_method = self.parser._get_item_descriptor_description
            
            def mock_get_description(key):
                if key == 'TESTMOD2':
                    return "Add [BO] and [DI] to the check"
                return None
            
            self.parser._get_item_descriptor_description = mock_get_description
            
            try:
                # Extract the added mods
                added_mods = self.parser._extract_added_mods(attachment_elem)
                
                # The dice keys [BO] and [DI] should be converted to "Boost" and "Difficulty"
                expected = "Add Boost and Difficulty to the check"
                self.assertEqual(added_mods, expected, 
                               f"Expected '{expected}', got '{added_mods}'")
                
                print(f"✓ AddedMods multiple dice conversion: '{added_mods}'")
                
            finally:
                # Restore the original method
                self.parser._get_item_descriptor_description = original_method
                
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main() 