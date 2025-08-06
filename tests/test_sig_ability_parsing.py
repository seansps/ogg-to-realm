#!/usr/bin/env python3
"""
Test script for signature ability parsing
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_sig_ability_parsing():
    """Test signature ability parsing functionality"""
    try:
        parser = XMLParser()
        
        # Create a mock signature ability XML element based on Narrow Escape
        sig_ability_xml = '''<?xml version='1.0' encoding='utf-8'?>
<SigAbility>
    <Key>NARROWESCAPE</Key>
    <Name>Narrow Escape</Name>
    <Description>Whether a smuggling deal has gone south or the authorities see through the ship's fake transponder code, Smugglers frequently find themselves in a position where they need to make a getaway—and fast. Besides, what good is a reward if nobody gets to spend it?</Description>
    <Source Page="37">Fly Casual</Source>
    <Sources />
    <Custom>DescOnly</Custom>
    <AbilityRows>
        <AbilityRow>
            <Index>0</Index>
            <Abilities>
                <Key>NARROWESCAPEBASE</Key>
                <Key>NARROWESCAPEBASE</Key>
                <Key>NARROWESCAPEBASE</Key>
                <Key>NARROWESCAPEBASE</Key>
            </Abilities>
            <Directions>
                <Direction>
                    <Left>false</Left>
                    <Right>false</Right>
                    <Up>false</Up>
                    <Down>false</Down>
                </Direction>
                <Direction>
                    <Left>false</Left>
                    <Right>false</Right>
                    <Up>false</Up>
                    <Down>true</Down>
                </Direction>
                <Direction>
                    <Left>false</Left>
                    <Right>false</Right>
                    <Up>false</Up>
                    <Down>true</Down>
                </Direction>
                <Direction>
                    <Left>false</Left>
                    <Right>false</Right>
                    <Up>false</Up>
                    <Down>false</Down>
                </Direction>
            </Directions>
            <AbilitySpan>
                <Span>4</Span>
                <Span>0</Span>
                <Span>0</Span>
                <Span>0</Span>
            </AbilitySpan>
            <Costs>
                <Cost>30</Cost>
                <Cost>0</Cost>
                <Cost>0</Cost>
                <Cost>0</Cost>
            </Costs>
        </AbilityRow>
        <AbilityRow>
            <Index>0</Index>
            <Abilities>
                <Key>REDUCESBNE</Key>
                <Key>INCREASEEFFNE</Key>
                <Key>ADDBOOSTNE</Key>
                <Key>CHANGESCALENE</Key>
            </Abilities>
            <Directions>
                <Direction>
                    <Left>false</Left>
                    <Right>true</Right>
                    <Up>false</Up>
                    <Down>true</Down>
                </Direction>
                <Direction>
                    <Left>true</Left>
                    <Right>false</Right>
                    <Up>true</Up>
                    <Down>false</Down>
                </Direction>
                <Direction>
                    <Left>false</Left>
                    <Right>true</Right>
                    <Up>true</Up>
                    <Down>true</Down>
                </Direction>
                <Direction>
                    <Left>true</Left>
                    <Right>false</Right>
                    <Up>false</Up>
                    <Down>false</Down>
                </Direction>
            </Directions>
            <AbilitySpan>
                <Span>1</Span>
                <Span>1</Span>
                <Span>1</Span>
                <Span>1</Span>
            </AbilitySpan>
            <Costs>
                <Cost>10</Cost>
                <Cost>10</Cost>
                <Cost>10</Cost>
                <Cost>10</Cost>
            </Costs>
        </AbilityRow>
        <AbilityRow>
            <Index>0</Index>
            <Abilities>
                <Key>REDUCEDIFFNE</Key>
                <Key>INCREASEEFFNE</Key>
                <Key>CHANGESKILLNE</Key>
                <Key>DESTINYNE</Key>
            </Abilities>
            <Directions>
                <Direction>
                    <Left>false</Left>
                    <Right>true</Right>
                    <Up>true</Up>
                    <Down>false</Down>
                </Direction>
                <Direction>
                    <Left>true</Left>
                    <Right>true</Right>
                    <Up>false</Up>
                    <Down>false</Down>
                </Direction>
                <Direction>
                    <Left>true</Left>
                    <Right>true</Right>
                    <Up>true</Up>
                    <Down>false</Down>
                </Direction>
                <Direction>
                    <Left>true</Left>
                    <Right>false</Right>
                    <Up>false</Up>
                    <Down>false</Down>
                </Direction>
            </Directions>
            <AbilitySpan>
                <Span>1</Span>
                <Span>1</Span>
                <Span>1</Span>
                <Span>1</Span>
            </AbilitySpan>
            <Costs>
                <Cost>15</Cost>
                <Cost>15</Cost>
                <Cost>15</Cost>
                <Cost>15</Cost>
            </Costs>
        </AbilityRow>
    </AbilityRows>
    <Careers>
        <Key>SMUG</Key>
    </Careers>
    <MatchingNodes>
        <Node>false</Node>
        <Node>true</Node>
        <Node>true</Node>
        <Node>false</Node>
    </MatchingNodes>
</SigAbility>
        '''
        
        root = ET.fromstring(sig_ability_xml)
        
        print("Testing signature ability parsing...")
        sig_ability_data = parser._extract_sig_ability_data(root)
        
        if sig_ability_data is None:
            print("  ✗ Signature ability data extraction failed")
            return False
        
        # Check the extracted data
        data = sig_ability_data.get('data', {})
        
        # Check name
        if sig_ability_data.get('name') == 'Narrow Escape':
            print("  ✓ Name correctly extracted: Narrow Escape")
        else:
            print(f"  ✗ Name extraction failed: {sig_ability_data.get('name')}")
            return False
        
        # Check description
        description = data.get('description', '')
        if description and '<strong>Base Ability:</strong>' in description:
            print(f"  ✓ Description correctly extracted with base ability: {description[:100]}...")
        else:
            print(f"  ✗ Description extraction failed: {description[:100]}...")
            return False
        
        # Check career
        career = data.get('career', '')
        if career == 'Smuggler':
            print(f"  ✓ Career correctly found: {career}")
        else:
            print(f"  ✗ Career finding failed: expected 'Smuggler', got '{career}'")
            return False
        
        # Check talent fields (should have talent1_1 to talent2_4, but NOT talent0_*)
        talent_fields = [k for k in data.keys() if k.startswith('talent')]
        expected_talent_fields = ['talent1_1', 'talent1_2', 'talent1_3', 'talent1_4', 'talent2_1', 'talent2_2', 'talent2_3', 'talent2_4']
        
        # Check that we have the expected talent fields
        if set(talent_fields) == set(expected_talent_fields):
            print(f"  ✓ Talent fields correctly generated: {talent_fields}")
        else:
            print(f"  ✗ Talent fields generation failed: expected {expected_talent_fields}, got {talent_fields}")
            return False
        
        # Check that we DON'T have talent0_* fields
        talent0_fields = [k for k in data.keys() if k.startswith('talent0')]
        if len(talent0_fields) == 0:
            print("  ✓ No talent0_* fields generated (as expected)")
        else:
            print(f"  ✗ talent0_* fields should not be generated, but found: {talent0_fields}")
            return False
        
        # Check connector fields (should have connector0_1 to connector2_4 and h_connector1_2 to h_connector2_4)
        expected_connector_fields = [
            "connector0_1", "connector0_2", "connector0_3", "connector0_4",
            "connector1_1", "connector1_2", "connector1_3", "connector1_4",
            "connector2_1", "connector2_2", "connector2_3", "connector2_4",
            "h_connector1_2", "h_connector1_3", "h_connector1_4",
            "h_connector2_2", "h_connector2_3", "h_connector2_4"
        ]
        
        connector_fields = [k for k in data.keys() if k.startswith('connector') or k.startswith('h_connector')]
        if set(connector_fields) == set(expected_connector_fields):
            print(f"  ✓ Connector fields correctly generated: {len(connector_fields)} fields")
        else:
            missing_fields = set(expected_connector_fields) - set(connector_fields)
            extra_fields = set(connector_fields) - set(expected_connector_fields)
            print(f"  ✗ Connector fields generation failed:")
            if missing_fields:
                print(f"    Missing fields: {missing_fields}")
            if extra_fields:
                print(f"    Extra fields: {extra_fields}")
            return False
        
        # Check specific connector values
        expected_connector_values = {
            "connector0_1": "No",
            "connector0_2": "Yes", 
            "connector0_3": "Yes",
            "connector0_4": "No",
            "connector1_1": "No",
            "connector1_2": "Yes",
            "connector1_3": "Yes", 
            "connector1_4": "No",
            "connector2_1": "Yes",
            "connector2_2": "No",
            "connector2_3": "Yes",
            "connector2_4": "No",
            "h_connector1_2": "Yes",
            "h_connector1_3": "No",
            "h_connector1_4": "Yes",
            "h_connector2_2": "Yes",
            "h_connector2_3": "Yes",
            "h_connector2_4": "Yes"
        }
        
        for field, expected_value in expected_connector_values.items():
            actual_value = data.get(field)
            if actual_value == expected_value:
                print(f"  ✓ {field} correctly set: {expected_value}")
            else:
                print(f"  ✗ {field} failed: expected '{expected_value}', got '{actual_value}'")
                return False
        
        print("  ✓ All signature ability parsing tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sig_ability_parsing()
    if success:
        print("\n🎉 All signature ability parsing tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some signature ability parsing tests failed!")
        sys.exit(1)
