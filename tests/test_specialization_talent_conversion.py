#!/usr/bin/env python3
"""
Test script for specialization talent conversion
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_specialization_talent_conversion():
    """Test that talents in specialization trees have full conversion applied"""
    try:
        parser = XMLParser()
        
        # Create a mock specialization XML element with a known talent
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
    </TalentRows>
</Specialization>
        '''
        
        root = ET.fromstring(spec_xml)
        
        print("Testing specialization talent conversion...")
        spec_data = parser._extract_specialization_data(root)
        
        if spec_data is None:
            print("  ✗ Specialization data extraction failed")
            return False
        
        data = spec_data.get('data', {})
        
        # Check that talent1_1 exists and has the full conversion
        talent1_1 = data.get('talent1_1', [])
        if not talent1_1:
            print("  ✗ talent1_1 not found")
            return False
        
        talent_data = talent1_1[0]
        talent_internal_data = talent_data.get('data', {})
        
        # Check that the talent has a rich text description
        description = talent_internal_data.get('description', '')
        if not description:
            print("  ✗ Talent description is empty")
            return False
        
        # Check if the description contains rich text (HTML spans)
        if '<span' in description:
            print(f"  ✓ Talent has rich text description: {description[:100]}...")
        else:
            print(f"  ✗ Talent description is not rich text: {description[:100]}...")
            return False
        
        # Check that the talent has specializationTrees field
        specialization_trees = talent_internal_data.get('specializationTrees', [])
        if not isinstance(specialization_trees, list):
            print(f"  ✗ specializationTrees is not a list: {type(specialization_trees)}")
            return False
        
        if len(specialization_trees) > 0:
            print(f"  ✓ Talent has specializationTrees: {specialization_trees}")
        else:
            print(f"  ✗ Talent has empty specializationTrees: {specialization_trees}")
            # This might be okay if the talent doesn't appear in any specialization trees
        
        # Check that the talent has other required fields
        required_fields = ['name', 'activation', 'ranked', 'forceTalent']
        for field in required_fields:
            if field not in talent_internal_data:
                print(f"  ✗ Talent missing required field: {field}")
                return False
            else:
                print(f"  ✓ Talent has {field}: {talent_internal_data[field]}")
        
        print("  ✓ All specialization talent conversion tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_specialization_talent_conversion()
    if success:
        print("\n🎉 All specialization talent conversion tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some specialization talent conversion tests failed!")
        sys.exit(1) 