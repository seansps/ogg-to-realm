#!/usr/bin/env python3
"""
Test script for Always Get My Mark signature ability parsing
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_always_get_my_mark_parsing():
    """Test Always Get My Mark signature ability parsing"""
    try:
        parser = XMLParser()
        
        # Create the Always Get My Mark signature ability XML
        sig_ability_xml = '''<?xml version='1.0' encoding='utf-8'?>
<SigAbility>
  <Key>ALWAYSGETMYMARK</Key>
  <Name>Always Get My Mark</Name>
  <Description>Once per game session, the character may choose a minion NPC to be her mark. She must know this NPC's identity and basic personal information (or have another lead of comparable quality, per the GM's discretion), and must know that the NPC is on the same planet. She spends 2 Destiny Points, and makes a [B]Hard ([DI][DI][DI]) Streetwise check[b]. If she succeeds, the character tracks down the chosen mark, and a new enounter begins as the character reaches the mark's location.</Description>
  <Source Page="39">No Disintegrations</Source>
  <Custom>DescOnly</Custom>
  <AbilityRows>
    <AbilityRow>
      <Abilities>
        <Key>ALWAYSGETMYMARKBASIC</Key>
        <Key>ALWAYSGETMYMARKBASIC</Key>
        <Key>ALWAYSGETMYMARKBASIC</Key>
        <Key>ALWAYSGETMYMARKBASIC</Key>
      </Abilities>
      <Directions>
        <Direction>
          <Down>true</Down>
        </Direction>
        <Direction />
        <Direction>
          <Down>true</Down>
        </Direction>
        <Direction />
      </Directions>
      <AbilitySpan>
        <Span>4</Span>
        <Span>0</Span>
        <Span>0</Span>
        <Span>0</Span>
        <Span>4</Span>
        <Span>0</Span>
        <Span>0</Span>
        <Span>0</Span>
        <Span>4</Span>
        <Span>0</Span>
        <Span>0</Span>
        <Span>0</Span>
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
        <Cost>30</Cost>
        <Cost>0</Cost>
        <Cost>0</Cost>
        <Cost>0</Cost>
        <Cost>30</Cost>
        <Cost>0</Cost>
        <Cost>0</Cost>
        <Cost>0</Cost>
        <Cost>30</Cost>
        <Cost>0</Cost>
        <Cost>0</Cost>
        <Cost>0</Cost>
      </Costs>
    </AbilityRow>
    <AbilityRow>
      <Abilities>
        <Key>ALWAYSGETMYMARKCHANGESKILL1</Key>
        <Key>ALWAYSGETMYMARKDESTINY</Key>
        <Key>ALWAYSGETMYMARKINCREASEEFFECT1</Key>
        <Key>ALWAYSGETMYMARKCHANGESKILL2</Key>
      </Abilities>
      <Directions>
        <Direction>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Right>true</Right>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>true</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
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
        <Key>ALWAYSGETMYMARKREDUCEDIFFICULTY</Key>
        <Key>ALWAYSGETMYMARKTAKEDOWN</Key>
        <Key>ALWAYSGETMYMARKINCREASERANGE</Key>
        <Key>ALWAYSGETMYMARKINCREASEEFFECT2</Key>
      </Abilities>
      <Directions>
        <Direction>
          <Right>true</Right>
          <Up>true</Up>
        </Direction>
        <Direction>
          <Left>true</Left>
        </Direction>
        <Direction>
          <Right>true</Right>
          <Up>true</Up>
        </Direction>
        <Direction>
          <Left>true</Left>
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
    <Key>BOUNT</Key>
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
        
        print("Testing Always Get My Mark signature ability parsing...")
        sig_ability_data = parser._extract_sig_ability_data(root)
        
        if sig_ability_data is None:
            print("  ✗ Signature ability data extraction failed")
            return False
        
        # Check the extracted data
        data = sig_ability_data.get('data', {})
        
        # Check cost field (should be 'cost' not 'baseCost', and should be 30)
        cost_value = data.get('cost')
        if cost_value == 30:
            print(f"  ✓ Cost correctly set: {cost_value}")
        else:
            print(f"  ✗ Cost failed: expected 30, got {cost_value}")
            return False
            
        # Ensure baseCost is not present
        if 'baseCost' not in data:
            print("  ✓ baseCost correctly not present")
        else:
            print(f"  ✗ baseCost should not be present, but found: {data.get('baseCost')}")
            return False
        
        # Check MatchingNodes-based connectors (should be No, Yes, Yes, No)
        expected_connectors = {
            "connector0_1": "No",   # MatchingNodes[0] = false
            "connector0_2": "Yes",  # MatchingNodes[1] = true  
            "connector0_3": "Yes",  # MatchingNodes[2] = true
            "connector0_4": "No",   # MatchingNodes[3] = false
        }
        
        for field, expected_value in expected_connectors.items():
            actual_value = data.get(field)
            if actual_value == expected_value:
                print(f"  ✓ {field} correctly set: {expected_value}")
            else:
                print(f"  ✗ {field} failed: expected '{expected_value}', got '{actual_value}'")
                return False
        
        # Check name
        if sig_ability_data.get('name') == 'Always Get My Mark':
            print("  ✓ Name correctly extracted: Always Get My Mark")
        else:
            print(f"  ✗ Name extraction failed: {sig_ability_data.get('name')}")
            return False
        
        # Check career
        career = data.get('career', '')
        if career == 'Bounty Hunter':
            print(f"  ✓ Career correctly found: {career}")
        else:
            print(f"  ✗ Career finding failed: expected 'Bounty Hunter', got '{career}'")
            return False
        
        print("  ✓ All Always Get My Mark parsing tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_always_get_my_mark_parsing()
    if success:
        print("\n🎉 All Always Get My Mark tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some Always Get My Mark tests failed!")
        sys.exit(1)