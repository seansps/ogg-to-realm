#!/usr/bin/env python3
"""
Test script for specialization parsing functionality
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_specialization_parsing():
    """Test specialization parsing functionality"""
    try:
        parser = XMLParser()
        
        # Create a mock specialization XML element based on Fringer
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
    </TalentRows>
</Specialization>
        '''
        
        root = ET.fromstring(spec_xml)
        
        print("Testing specialization parsing...")
        spec_data = parser._extract_specialization_data(root)
        
        if spec_data is None:
            print("  ✗ Specialization data extraction failed")
            return False
        
        # Check the extracted data
        data = spec_data.get('data', {})
        
        # Check name
        if spec_data.get('name') == 'Fringer':
            print("  ✓ Name correctly extracted: Fringer")
        else:
            print(f"  ✗ Name extraction failed: {spec_data.get('name')}")
            return False
        
        # Check skills conversion
        skills = data.get('skills', '')
        expected_skills = 'Astrogation, Coordination, Negotiation, Streetwise'
        if skills == expected_skills:
            print(f"  ✓ Skills correctly converted: {skills}")
        else:
            print(f"  ✗ Skills conversion failed: expected '{expected_skills}', got '{skills}'")
            return False
        
        # Check career
        career = data.get('career', [])
        if career == ['Explorer']:
            print(f"  ✓ Career correctly found: {career}")
        else:
            print(f"  ✗ Career finding failed: expected ['Explorer'], got '{career}'")
            return False
        
        # Check talent fields
        talent_fields = [k for k in data.keys() if k.startswith('talent')]
        expected_talent_fields = ['talent1_1', 'talent1_2', 'talent1_3', 'talent1_4', 'talent2_1', 'talent2_2', 'talent2_3', 'talent2_4']
        if set(talent_fields) == set(expected_talent_fields):
            print(f"  ✓ Talent fields correctly generated: {talent_fields}")
        else:
            print(f"  ✗ Talent fields generation failed: expected {expected_talent_fields}, got {talent_fields}")
            return False
        
        # Check talent data
        talent1_1 = data.get('talent1_1', [])
        if talent1_1 and talent1_1[0].get('name') == 'Galaxy Mapper':
            print(f"  ✓ Talent 1_1 correctly extracted: {talent1_1[0].get('name')}")
        else:
            print(f"  ✗ Talent 1_1 extraction failed: {talent1_1[0].get('name') if talent1_1 else 'None'}")
            return False
        
        # Check talent cost
        if talent1_1 and talent1_1[0].get('data', {}).get('cost') == 5:
            print(f"  ✓ Talent cost correctly set: {talent1_1[0].get('data', {}).get('cost')}")
        else:
            print(f"  ✗ Talent cost setting failed: {talent1_1[0].get('data', {}).get('cost') if talent1_1 else 'None'}")
            return False
        
        # Check connector fields
        connector_fields = [k for k in data.keys() if k.startswith('connector') or k.startswith('h_connector')]
        if len(connector_fields) > 0:
            print(f"  ✓ Connector fields generated: {len(connector_fields)} fields")
        else:
            print("  ✗ Connector fields generation failed")
            return False
        
        # Check specific connectors
        if data.get('connector2_1') == 'Yes':
            print("  ✓ Vertical connector 2_1 correctly set: Yes")
        else:
            print(f"  ✗ Vertical connector 2_1 failed: {data.get('connector2_1')}")
            return False
        
        if data.get('connector2_3') == 'Yes':
            print("  ✓ Vertical connector 2_3 correctly set: Yes")
        else:
            print(f"  ✗ Vertical connector 2_3 failed: {data.get('connector2_3')}")
            return False
        
        print("  ✓ All specialization parsing tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_specialization_parsing()
    if success:
        print("\n🎉 All specialization parsing tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some specialization parsing tests failed!")
        sys.exit(1) 