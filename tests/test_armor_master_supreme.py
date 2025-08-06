#!/usr/bin/env python3
"""
Test script for Armor Master (Supreme) talent with taIncidentalOOT activation
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_armor_master_supreme():
    """Test that Armor Master (Supreme) with taIncidentalOOT converts to Active"""
    try:
        parser = XMLParser()
        
        print("Testing Armor Master (Supreme) talent activation conversion...")
        
        # Create XML for Armor Master (Supreme) talent
        talent_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Talent>
    <Key>ARMSUP</Key>
    <Name>Armor Master (Supreme)</Name>
    <Description>Once per round, when the character suffers a Critical Injury, he may suffer 3 strain to take the Armor Master incidental. If he does he reduces the Critical Injury result that he suffers by 10 per point of his soak, to a minimum of 1.</Description>
    <Source Page="30">Keeping the Peace</Source>
    <Custom>DescOnly</Custom>
    <ActivationValue>taIncidentalOOT</ActivationValue>
</Talent>'''
        
        root = ET.fromstring(talent_xml)
        
        # Extract the talent data
        talent_data = parser._extract_talent_data(root)
        
        if talent_data is None:
            print("  ✗ Talent data extraction failed")
            return False
        
        # Check the extracted data
        data = talent_data.get('data', {})
        activation = data.get('activation', 'NOT_SET')
        name = talent_data.get('name', 'UNKNOWN')
        
        print(f"  Talent: {name}")
        print(f"  Original activation: taIncidentalOOT")
        print(f"  Converted activation: {activation}")
        
        if activation == 'Active':
            print("  ✓ Activation correctly converted to Active!")
            return True
        else:
            print(f"  ✗ Activation conversion failed: expected 'Active', got '{activation}'")
            return False
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_armor_master_supreme()
    if success:
        print("\n🎉 Armor Master (Supreme) test passed!")
        sys.exit(0)
    else:
        print("\n❌ Armor Master (Supreme) test failed!")
        sys.exit(1)