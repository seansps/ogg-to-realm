#!/usr/bin/env python3
"""
Debug test to trace attachment type processing
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xml_parser import XMLParser
from data_mapper import DataMapper

def debug_attachment_type():
    """Debug the attachment type processing step by step"""
    print("Debugging attachment type processing...")
    
    # Create the XML content for the Curved Hilt attachment
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
  <ItemAttachment>
    <Key>CURVEDHILT</Key>
    <Name>Curved Hilt</Name>
    <Description>Test description</Description>
    <Source Page="196">Force and Destiny Core Rulebook</Source>
    <Type>Weapon</Type>
    <Price>1000</Price>
    <Rarity>6</Rarity>
    <HP>1</HP>
    <AddedMods>
      <Mod>
        <Key>DEFENSIVE</Key>
        <Count>1</Count>
      </Mod>
    </AddedMods>
  </ItemAttachment>
</ItemAttachments>'''
    
    # Write to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_content)
        temp_file = f.name
    
    try:
        # Step 1: Parse with XML parser
        print("\n=== STEP 1: XML Parsing ===")
        parser = XMLParser()
        parsed_records = parser.parse_xml_file(temp_file)
        
        if parsed_records:
            attachment = parsed_records[0]
            print(f"Record type: {attachment.get('recordType')}")
            print(f"Name: {attachment.get('name')}")
            print(f"Top-level type: {attachment.get('type')}")
            print(f"Data type: {attachment.get('data', {}).get('type')}")
            print(f"All data keys: {list(attachment.get('data', {}).keys())}")
            
            # Step 2: Test data mapper logic
            print("\n=== STEP 2: Data Mapper Logic ===")
            data = attachment.get('data', {})
            if not isinstance(data, dict):
                data = {}
            
            # Get item type from either the top level or the data field
            item_type = attachment.get('type', data.get('type', 'gear'))
            print(f"Item type determined: {item_type}")
            
            # Test each condition
            print(f"Is weapon? {item_type == 'weapon'}")
            print(f"Is ranged weapon? {item_type == 'ranged weapon'}")
            print(f"Is melee weapon? {item_type == 'melee weapon'}")
            print(f"Is weapon attachment? {item_type == 'weapon attachment'}")
            print(f"Is armor attachment? {item_type == 'armor attachment'}")
            print(f"Is vehicle attachment? {item_type == 'vehicle attachment'}")
            
            # Test the weapon condition
            weapon_condition = item_type == 'weapon' or (item_type in ['ranged weapon', 'melee weapon'])
            print(f"Weapon condition result: {weapon_condition}")
            
            # Test the attachment condition
            attachment_condition = item_type in ['weapon attachment', 'armor attachment', 'vehicle attachment']
            print(f"Attachment condition result: {attachment_condition}")
            
            # Step 3: Full conversion
            print("\n=== STEP 3: Full Conversion ===")
            mapper = DataMapper()
            converted = mapper._convert_item(attachment, 'test-campaign', 'Test Category')
            
            print(f"Final type: {converted.get('data', {}).get('type')}")
            print(f"Final subtype: {converted.get('data', {}).get('subtype')}")
            
            # Check if it was processed correctly
            if converted.get('data', {}).get('type') == 'weapon attachment':
                print("✓ Correctly processed as weapon attachment")
                return True
            else:
                print(f"✗ Incorrectly processed as: {converted.get('data', {}).get('type')}")
                return False
        else:
            print("✗ No records parsed")
            return False
            
    finally:
        # Clean up temp file
        os.unlink(temp_file)

if __name__ == '__main__':
    print("Running attachment type debug test...")
    
    if debug_attachment_type():
        print("\n✓ Attachment type debug test passed!")
    else:
        print("\n✗ Attachment type debug test failed!")
        sys.exit(1) 