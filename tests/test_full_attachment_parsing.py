#!/usr/bin/env python3
"""
Test full attachment parsing and conversion process
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xml_parser import XMLParser
from data_mapper import DataMapper

def test_full_attachment_parsing():
    """Test the full parsing and conversion process for attachments"""
    print("Testing full attachment parsing and conversion...")
    
    # Create the XML content for the Curved Hilt attachment
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
  <ItemAttachment>
    <Key>CURVEDHILT</Key>
    <Name>Curved Hilt</Name>
    <Description>
      [H3]Curved Hilt[h3]

The curved hilt is preferred by duelists and practitioners of the lightsaber combat form Makashi. This modification allows for both better control and better flexibility when handling the lightsaber. and for more force behind overhand strikes.

[P][B]Models Include:[b] None. </Description>
    <Source Page="196">Force and Destiny Core Rulebook</Source>
    <Custom>DescOnly</Custom>
    <Type>Weapon</Type>
    <CategoryLimit>
      <Category>Lightsaber</Category>
    </CategoryLimit>
    <Price>1000</Price>
    <Rarity>6</Rarity>
    <HP>1</HP>
    <BaseMods>
      <Mod>
        <Count>1</Count>
        <MiscDesc>Adds automatic [ADVANTAGE] to successful Lightsaber combat checks when engaged with a single opponent.</MiscDesc>
      </Mod>
    </BaseMods>
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
        # Parse with XML parser
        parser = XMLParser()
        parsed_records = parser.parse_xml_file(temp_file)
        
        print(f"Parsed {len(parsed_records)} records")
        
        if parsed_records:
            attachment = parsed_records[0]
            print(f"Record type: {attachment.get('recordType')}")
            print(f"Name: {attachment.get('name')}")
            print(f"Type in data: {attachment.get('data', {}).get('type')}")
            print(f"Top-level type: {attachment.get('type')}")
            
            # Test the exact logic from _convert_item
            data = attachment.get('data', {})
            if not isinstance(data, dict):
                data = {}
            
            # Get item type from either the top level or the data field
            item_type = attachment.get('type', data.get('type', 'gear'))
            print(f"Item type determined by _convert_item: {item_type}")
            
            # Test conversion with data mapper
            mapper = DataMapper()
            converted = mapper._convert_item(attachment, 'test-campaign', 'Test Category')
            
            print(f"\nAfter conversion:")
            print(f"Type in converted data: {converted.get('data', {}).get('type')}")
            print(f"Subtype in converted data: {converted.get('data', {}).get('subtype')}")
            
            # Check if it was processed as weapon or attachment
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

def test_multiple_attachment_types():
    """Test different attachment types to see if they're all processed correctly"""
    print("\nTesting multiple attachment types...")
    
    # Create XML with different attachment types
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ItemAttachments>
  <ItemAttachment>
    <Key>WEAPONATTACH</Key>
    <Name>Weapon Attachment</Name>
    <Type>Weapon</Type>
    <Price>100</Price>
    <Rarity>1</Rarity>
  </ItemAttachment>
  <ItemAttachment>
    <Key>ARMORATTACH</Key>
    <Name>Armor Attachment</Name>
    <Type>Armor</Type>
    <Price>200</Price>
    <Rarity>2</Rarity>
  </ItemAttachment>
  <ItemAttachment>
    <Key>VEHICLEATTACH</Key>
    <Name>Vehicle Attachment</Name>
    <Type>Vehicle</Type>
    <Price>300</Price>
    <Rarity>3</Rarity>
  </ItemAttachment>
</ItemAttachments>'''
    
    # Write to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_content)
        temp_file = f.name
    
    try:
        # Parse with XML parser
        parser = XMLParser()
        parsed_records = parser.parse_xml_file(temp_file)
        
        print(f"Parsed {len(parsed_records)} records")
        
        mapper = DataMapper()
        success = True
        
        for i, attachment in enumerate(parsed_records):
            print(f"\nAttachment {i+1}: {attachment.get('name')}")
            print(f"  OggDude Type: {attachment.get('data', {}).get('type')}")
            
            converted = mapper._convert_item(attachment, 'test-campaign', 'Test Category')
            final_type = converted.get('data', {}).get('type')
            print(f"  Final type: {final_type}")
            
            # Check if type is correct
            expected_type = None
            oggdude_type = attachment.get('data', {}).get('type', '').lower()
            if 'weapon' in oggdude_type:
                expected_type = 'weapon attachment'
            elif 'armor' in oggdude_type:
                expected_type = 'armor attachment'
            elif 'vehicle' in oggdude_type:
                expected_type = 'vehicle attachment'
            
            if final_type == expected_type:
                print(f"  ✓ Correctly processed as {expected_type}")
            else:
                print(f"  ✗ Expected {expected_type}, got {final_type}")
                success = False
        
        return success
            
    finally:
        # Clean up temp file
        os.unlink(temp_file)

if __name__ == '__main__':
    print("Running full attachment parsing tests...")
    
    success = True
    success &= test_full_attachment_parsing()
    success &= test_multiple_attachment_types()
    
    if success:
        print("\n✓ All attachment parsing tests passed!")
    else:
        print("\n✗ Some attachment parsing tests failed!")
        sys.exit(1) 