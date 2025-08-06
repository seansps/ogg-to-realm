#!/usr/bin/env python3
"""
Test to debug the Curved Hilt attachment issue
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xml_parser import XMLParser
from data_mapper import DataMapper

def test_curved_hilt_attachment():
    """Test the Curved Hilt attachment specifically"""
    print("Testing Curved Hilt attachment parsing...")
    
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
            print(f"Raw data keys: {list(attachment.get('data', {}).keys())}")
            
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

if __name__ == '__main__':
    print("Running Curved Hilt attachment test...")
    
    if test_curved_hilt_attachment():
        print("\n✓ Curved Hilt attachment test passed!")
    else:
        print("\n✗ Curved Hilt attachment test failed!")
        sys.exit(1) 