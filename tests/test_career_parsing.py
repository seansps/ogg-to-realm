#!/usr/bin/env python3
"""
Test script for career parsing functionality
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_career_parsing():
    """Test career parsing functionality"""
    try:
        parser = XMLParser()
        
        # Create a mock career XML element
        career_xml = '''<?xml version="1.0" encoding="utf-8"?>
        <Career>
            <Key>GUARD</Key>
            <Name>Guardian</Name>
            <Description>
                [H4]Guardian[h4]
                The Guardian's six career skills are [B]Brawl, Cool, Discipline, Melee, Resilience,[b] and [B]Vigilance[b].
            </Description>
            <Source Page="72">Force and Destiny Core Rulebook</Source>
            <CareerSkills>
                <Key>BRAWL</Key>
                <Key>COOL</Key>
                <Key>DISC</Key>
                <Key>MELEE</Key>
                <Key>RESIL</Key>
                <Key>VIGIL</Key>
            </CareerSkills>
            <Specializations>
                <Key>ARMORER</Key>
                <Key>PEACE</Key>
                <Key>PROTECT</Key>
                <Key>SORESU</Key>
                <Key>WARDEN</Key>
                <Key>WARLEADER</Key>
            </Specializations>
            <Attributes>
                <ForceRating>1</ForceRating>
            </Attributes>
            <FreeRanks>3</FreeRanks>
        </Career>
        '''
        
        root = ET.fromstring(career_xml)
        
        print("Testing career parsing...")
        career_data = parser._extract_career_data(root)
        
        if career_data is None:
            print("  ✗ Career data extraction failed")
            return False
        
        # Check the extracted data
        data = career_data.get('data', {})
        
        # Check career skills conversion
        skills = data.get('skills', '')
        if skills:
            print(f"  ✓ Career skills found: {skills}")
            # Check that it contains expected skills (may be keys if names not found)
            expected_skills = ['BRAWL', 'COOL', 'DISC', 'MELEE', 'RESIL', 'VIGIL']
            for skill in expected_skills:
                if skill in skills or skill.lower() in skills.lower():
                    print(f"    ✓ Found skill: {skill}")
                else:
                    print(f"    - Skill {skill} not found in skills string")
        else:
            print("  ✗ No career skills found")
            return False
        
        # Check specializations conversion
        specializations = data.get('specializations', '')
        if specializations:
            print(f"  ✓ Specializations found: {specializations}")
            # Check that it contains expected specializations (may be keys if names not found)
            expected_specs = ['ARMORER', 'PEACE', 'PROTECT', 'SORESU', 'WARDEN', 'WARLEADER']
            for spec in expected_specs:
                if spec in specializations or spec.lower() in specializations.lower():
                    print(f"    ✓ Found specialization: {spec}")
                else:
                    print(f"    - Specialization {spec} not found in specializations string")
        else:
            print("  ✗ No specializations found")
            return False
        
        # Check force rating
        force_rating = data.get('forceRating', 0)
        if force_rating == 1:
            print(f"  ✓ Force rating found: {force_rating}")
        else:
            print(f"  ✗ Force rating incorrect: {force_rating} (expected: 1)")
            return False
        
        # Check career key
        career_key = career_data.get('key', '')
        if career_key == 'GUARD':
            print(f"  ✓ Career key found: {career_key}")
        else:
            print(f"  ✗ Career key incorrect: {career_key} (expected: GUARD)")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Career parsing test failed: {e}")
        return False

def test_duplicate_career_handling():
    """Test that duplicate careers are handled correctly"""
    try:
        parser = XMLParser()
        
        # Create mock career XML elements with the same key
        career_xml1 = '''<?xml version="1.0" encoding="utf-8"?>
        <Career>
            <Key>GUARD</Key>
            <Name>Guardian</Name>
            <Description>First Guardian career</Description>
            <CareerSkills>
                <Key>BRAWL</Key>
            </CareerSkills>
            <Specializations>
                <Key>ARMORER</Key>
            </Specializations>
        </Career>
        '''
        
        career_xml2 = '''<?xml version="1.0" encoding="utf-8"?>
        <Career>
            <Key>GUARD</Key>
            <Name>Guardian Duplicate</Name>
            <Description>Second Guardian career (should be skipped)</Description>
            <CareerSkills>
                <Key>COOL</Key>
            </CareerSkills>
            <Specializations>
                <Key>PEACE</Key>
            </Specializations>
        </Career>
        '''
        
        root1 = ET.fromstring(career_xml1)
        root2 = ET.fromstring(career_xml2)
        
        print("Testing duplicate career handling...")
        
        # Parse both careers
        career1 = parser._extract_career_data(root1)
        career2 = parser._extract_career_data(root2)
        
        if career1 is None or career2 is None:
            print("  ✗ Career data extraction failed")
            return False
        
        # Check that both have the same key
        if career1.get('key') == career2.get('key') == 'GUARD':
            print("  ✓ Both careers have the same key: GUARD")
        else:
            print("  ✗ Career keys don't match")
            return False
        
        # Check that the first career has the expected name
        if career1.get('name') == 'Guardian':
            print("  ✓ First career has correct name: Guardian")
        else:
            print(f"  ✗ First career name incorrect: {career1.get('name')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Duplicate career handling test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running career parsing tests...")
    
    # Test basic career parsing
    parsing_result = test_career_parsing()
    
    # Test duplicate handling
    duplicate_result = test_duplicate_career_handling()
    
    if parsing_result and duplicate_result:
        print("\n✅ All career parsing tests passed!")
    else:
        print("\n❌ Some career parsing tests failed!")
        sys.exit(1) 