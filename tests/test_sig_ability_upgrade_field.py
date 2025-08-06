#!/usr/bin/env python3
"""
Test script for signature ability upgrade field
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_sig_ability_upgrade_field():
    """Test that signature ability upgrade talents have signatureAbilityUpgrade field"""
    try:
        parser = XMLParser()
        
        # Create a simple signature ability XML for testing
        sig_ability_xml = '''<?xml version='1.0' encoding='utf-8'?>
<SigAbility>
    <Key>NARROWESCAPE</Key>
    <Name>Narrow Escape</Name>
    <Description>Test signature ability</Description>
    <Source Page="37">Fly Casual</Source>
    <Custom>DescOnly</Custom>
    <AbilityRows>
        <AbilityRow>
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
        
        print("Testing signature ability upgrade field...")
        sig_ability_data = parser._extract_sig_ability_data(root)
        
        if sig_ability_data is None:
            print("  ✗ Signature ability data extraction failed")
            return False
        
        # Check the extracted data
        data = sig_ability_data.get('data', {})
        
        # Expected talent fields for signature ability upgrades
        expected_talent_fields = ['talent1_1', 'talent1_2', 'talent1_3', 'talent1_4', 'talent2_1', 'talent2_2', 'talent2_3', 'talent2_4']
        
        # Check that each talent has the signatureAbilityUpgrade field
        all_passed = True
        for field in expected_talent_fields:
            talent_array = data.get(field)
            if talent_array and len(talent_array) > 0:
                talent = talent_array[0]  # Get the first (and should be only) talent in the array
                talent_data = talent.get('data', {})
                upgrade_field = talent_data.get('signatureAbilityUpgrade')
                
                if upgrade_field == "yes":
                    print(f"  ✓ {field} has signatureAbilityUpgrade: yes")
                else:
                    print(f"  ✗ {field} missing or incorrect signatureAbilityUpgrade: expected 'yes', got '{upgrade_field}'")
                    all_passed = False
            else:
                print(f"  ✗ {field} talent array is missing or empty")
                all_passed = False
        
        if all_passed:
            print("  ✓ All signature ability upgrade talents have signatureAbilityUpgrade field!")
            return True
        else:
            print("  ✗ Some signature ability upgrade talents missing signatureAbilityUpgrade field!")
            return False
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sig_ability_upgrade_field()
    if success:
        print("\n🎉 All signature ability upgrade field tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some signature ability upgrade field tests failed!")
        sys.exit(1)