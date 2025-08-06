#!/usr/bin/env python3

import unittest
import tempfile
import os
import xml.etree.ElementTree as ET
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.xml_parser import XMLParser

class TestBaseModsParsing(unittest.TestCase):
    def setUp(self):
        self.parser = XMLParser()
    
    def test_base_mods_with_talent_key(self):
        """Test that talent keys in BaseMods are converted to 'Innate Talent (Name)'"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <BaseMods>
            <Mod>
                <Key>QUICKDR</Key>
                <Count>1</Count>
            </Mod>
        </BaseMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            base_mods = attachment.get('data', {}).get('baseModifiers', '')
            
            # Should convert QUICKDR to "Innate Talent (Quick Draw)"
            self.assertIn("Innate Talent (Quick Draw)", base_mods)
            
        finally:
            os.unlink(temp_file)
    
    def test_base_mods_with_skill_key(self):
        """Test that skill keys in BaseMods are converted to '1 Skill (Name) Mod'"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <BaseMods>
            <Mod>
                <Key>VIGIL</Key>
                <Count>1</Count>
            </Mod>
        </BaseMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            base_mods = attachment.get('data', {}).get('baseModifiers', '')
            
            # Should convert VIGIL to "1 Skill (Vigilance) Mod"
            self.assertIn("1 Skill (Vigilance) Mod", base_mods)
            
        finally:
            os.unlink(temp_file)
    
    def test_base_mods_with_skill_key_multiple_count(self):
        """Test that skill keys with count > 1 are handled correctly"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <BaseMods>
            <Mod>
                <Key>VIGIL</Key>
                <Count>2</Count>
            </Mod>
        </BaseMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            base_mods = attachment.get('data', {}).get('baseModifiers', '')
            
            # Should convert VIGIL with count 2 to "2 Skill (Vigilance) Mod"
            self.assertIn("2 Skill (Vigilance) Mod", base_mods)
            
        finally:
            os.unlink(temp_file)
    
    def test_base_mods_with_dice_keys(self):
        """Test that dice keys in BaseMods are converted to rich text"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <BaseMods>
            <Mod>
                <Key>DAMADD</Key>
                <Count>1</Count>
            </Mod>
            <Mod>
                <MiscDesc>Add [SE][SE] to difficulty checks</MiscDesc>
            </Mod>
        </BaseMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            base_mods = attachment.get('data', {}).get('baseModifiers', '')
            
            # Should convert [SE][SE] to "2 Setback"
            self.assertIn("2 Setback", base_mods)
            
        finally:
            os.unlink(temp_file)
    
    def test_base_mods_cleanup_newlines(self):
        """Test that BaseMods text is cleaned up properly without random newlines"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <BaseMods>
            <Mod>
                <MiscDesc>Increases the difficulty of combat checks to hit targets at

ranges beyond Short range by one.</MiscDesc>
            </Mod>
        </BaseMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            base_mods = attachment.get('data', {}).get('baseModifiers', '')
            
            # Should not contain newlines
            self.assertNotIn('\n', base_mods)
            self.assertNotIn('\r', base_mods)
            
            # Should be a clean single line
            self.assertIn("Increases the difficulty of combat checks to hit targets at ranges beyond Short range by one", base_mods)
            
        finally:
            os.unlink(temp_file)
    
    def test_added_mods_no_rich_text_conversion(self):
        """Test that AddedMods does NOT convert dice keys to rich text"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <AddedMods>
            <Mod>
                <Key>DAMADD</Key>
                <Count>2</Count>
            </Mod>
        </AddedMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            mod_options = attachment.get('data', {}).get('modificationOptions', '')
            
            # Should keep the original format with [SE] keys, not convert to "Setback"
            # The exact format depends on what's in ItemDescriptors, but it should NOT be converted
            # to rich text like "Setback"
            self.assertNotIn("Setback", mod_options)
            
        finally:
            os.unlink(temp_file)
    
    def test_added_mods_with_talent_key(self):
        """Test that talent keys in AddedMods are converted to 'Innate Talent (Name)'"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <AddedMods>
            <Mod>
                <Key>QUICKDR</Key>
                <Count>1</Count>
            </Mod>
        </AddedMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            mod_options = attachment.get('data', {}).get('modificationOptions', '')
            
            # Should convert QUICKDR to "Innate Talent (Quick Draw)"
            self.assertIn("Innate Talent (Quick Draw)", mod_options)
            
        finally:
            os.unlink(temp_file)
    
    def test_added_mods_with_skill_key(self):
        """Test that skill keys in AddedMods are converted to '1 Skill (Name) Mod'"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <AddedMods>
            <Mod>
                <Key>VIGIL</Key>
                <Count>1</Count>
            </Mod>
        </AddedMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            mod_options = attachment.get('data', {}).get('modificationOptions', '')
            
            # Should convert VIGIL to "1 Skill (Vigilance) Mod"
            self.assertIn("1 Skill (Vigilance) Mod", mod_options)
            
        finally:
            os.unlink(temp_file)
    
    def test_added_mods_with_skill_key_multiple_count(self):
        """Test that skill keys with count > 1 in AddedMods are handled correctly"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <AddedMods>
            <Mod>
                <Key>VIGIL</Key>
                <Count>2</Count>
            </Mod>
        </AddedMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            mod_options = attachment.get('data', {}).get('modificationOptions', '')
            
            # Should convert VIGIL with count 2 to "2 Skill (Vigilance) Mod"
            self.assertIn("2 Skill (Vigilance) Mod", mod_options)
            
        finally:
            os.unlink(temp_file)
    
    def test_added_mods_with_misc_desc(self):
        """Test that AddedMods uses MiscDesc when no Key is present"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <AddedMods>
            <Mod>
                <Count>1</Count>
                <MiscDesc>Decreases the difficulty of checks to conceal the weapon by one.</MiscDesc>
            </Mod>
        </AddedMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            mod_options = attachment.get('data', {}).get('modificationOptions', '')
            
            # Should use the MiscDesc directly
            self.assertIn("Decreases the difficulty of checks to conceal the weapon by one", mod_options)
            
        finally:
            os.unlink(temp_file)
    
    def test_added_mods_with_misc_desc_and_count(self):
        """Test that AddedMods uses MiscDesc with count when no Key is present"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
    <ItemAttachment>
        <Key>TESTATTACH</Key>
        <Name>Test Attachment</Name>
        <Description>Test description</Description>
        <AddedMods>
            <Mod>
                <Count>2</Count>
                <MiscDesc>Add [SE] to difficulty checks</MiscDesc>
            </Mod>
        </AddedMods>
    </ItemAttachment>
</ItemAttachments>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            records = self.parser.parse_xml_file(temp_file)
            self.assertEqual(len(records), 1)
            
            attachment = records[0]
            mod_options = attachment.get('data', {}).get('modificationOptions', '')
            
            # Should use the MiscDesc with count prefix
            self.assertIn("2 Add [SE] to difficulty checks", mod_options)
            
        finally:
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main() 