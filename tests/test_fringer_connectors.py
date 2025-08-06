#!/usr/bin/env python3
"""
Test script for Fringer specialization connectors
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_fringer_connectors():
    """Test Fringer specialization connectors"""
    try:
        parser = XMLParser()
        
        # Create the complete Fringer specialization XML
        spec_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Specialization>
    <Key>FRINGER</Key>
    <Name>Fringer</Name>
    <Description>[H4]Fringer - Discovering Possibilities[h4] Part negotiator, part astrogator, and savvy in the ways of the galaxy beyond the Core Worlds, the Fringer is a jack-of-all-trades.</Description>
    <Source Page="71">Edge of the Empire Core Rulebook</Source>
    <CareerSkills>
        <Key>ASTRO</Key>
        <Key>COORD</Key>
        <Key>NEG</Key>
        <Key>SW</Key>
    </CareerSkills>
  <TalentRows>
    <TalentRow>
      <Cost>5</Cost>
      <Talents>
        <Key>GALMAP</Key>
        <Key>STRSMART</Key>
        <Key>RAPREC</Key>
        <Key>STRSMART</Key>
      </Talents>
      <Directions>
        <Direction>
          <Down>true</Down>
        </Direction>
        <Direction />
        <Direction>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Down>true</Down>
        </Direction>
      </Directions>
    </TalentRow>
    <TalentRow>
      <Index>1</Index>
      <Cost>10</Cost>
      <Talents>
        <Key>SKILLJOCK</Key>
        <Key>GALMAP</Key>
        <Key>GRIT</Key>
        <Key>TOUGH</Key>
      </Talents>
      <Directions>
        <Direction>
          <Right>true</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Right>true</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
      </Directions>
    </TalentRow>
    <TalentRow>
      <Index>2</Index>
      <Cost>15</Cost>
      <Talents>
        <Key>MASSTAR</Key>
        <Key>DEFDRI</Key>
        <Key>RAPREC</Key>
        <Key>DURA</Key>
      </Talents>
      <Directions>
        <Direction>
          <Right>true</Right>
          <Up>true</Up>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Up>true</Up>
        </Direction>
        <Direction>
          <Right>false</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
      </Directions>
    </TalentRow>
    <TalentRow>
      <Index>3</Index>
      <Cost>20</Cost>
      <Talents>
        <Key>RAPREC</Key>
        <Key>JUMP</Key>
        <Key>GRIT</Key>
        <Key>KNOCK</Key>
      </Talents>
      <Directions>
        <Direction>
          <Right>true</Right>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>true</Right>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Up>true</Up>
        </Direction>
        <Direction>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
      </Directions>
    </TalentRow>
    <TalentRow>
      <Index>4</Index>
      <Cost>25</Cost>
      <Talents>
        <Key>DEDI</Key>
        <Key>TOUGH</Key>
        <Key>DODGE</Key>
        <Key>DODGE</Key>
      </Talents>
      <Directions>
        <Direction>
          <Right>true</Right>
          <Up>true</Up>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Up>true</Up>
        </Direction>
        <Direction>
          <Right>true</Right>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Up>true</Up>
        </Direction>
      </Directions>
    </TalentRow>
  </TalentRows>
</Specialization>
        '''
        
        root = ET.fromstring(spec_xml)
        
        print("Testing Fringer specialization connectors...")
        spec_data = parser._extract_specialization_data(root)
        
        if spec_data is None:
            print("  ✗ Specialization data extraction failed")
            return False
        
        data = spec_data.get('data', {})
        
        # Expected connector values based on the user's specification
        expected_connectors = {
            # Vertical connectors
            "connector2_1": "Yes",
            "connector2_2": "No", 
            "connector2_3": "Yes",
            "connector2_4": "Yes",
            "connector3_1": "Yes",
            "connector3_2": "Yes",
            "connector3_3": "Yes",
            "connector3_4": "Yes",
            "connector4_1": "No",
            "connector4_2": "No",
            "connector4_3": "Yes",
            "connector4_4": "Yes",
            "connector5_1": "Yes",
            "connector5_2": "Yes",
            "connector5_3": "No",
            "connector5_4": "Yes",
            # Horizontal connectors
            "h_connector1_2": "No",
            "h_connector1_3": "No",
            "h_connector1_4": "No",
            "h_connector2_2": "Yes",
            "h_connector2_3": "No",
            "h_connector2_4": "Yes",
            "h_connector3_2": "Yes",
            "h_connector3_3": "No",
            "h_connector3_4": "No",
            "h_connector4_2": "Yes",
            "h_connector4_3": "Yes",
            "h_connector4_4": "No",
            "h_connector5_2": "Yes",
            "h_connector5_3": "No",
            "h_connector5_4": "Yes"
        }
        
        # Test each expected connector
        passed = 0
        total = len(expected_connectors)
        
        for connector, expected_value in expected_connectors.items():
            actual_value = data.get(connector, "Not Found")
            if actual_value == expected_value:
                print(f"  ✓ {connector}: {actual_value}")
                passed += 1
            else:
                print(f"  ✗ {connector}: expected {expected_value}, got {actual_value}")
        
        print(f"\nResults: {passed}/{total} connectors correct")
        
        if passed == total:
            print("🎉 All Fringer connectors are correct!")
            return True
        else:
            print("❌ Some Fringer connectors are incorrect!")
            return False
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_fringer_connectors()
    if success:
        print("\n🎉 All Fringer connector tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some Fringer connector tests failed!")
        sys.exit(1) 