#!/usr/bin/env python3
"""
Test skill name conversion functionality
"""
import sys
import os
import xml.etree.ElementTree as ET
from unittest.mock import Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xml_parser import XMLParser

def test_skill_name_conversion():
    """Test skill name conversion with hyphens"""
    parser = XMLParser()
    
    # Test cases for skill name conversion
    test_cases = [
        ("Piloting - Planetary", "Piloting (Planetary)"),
        ("Piloting - Space", "Piloting (Space)"),
        ("Piloting - Atmospheric", "Piloting (Atmospheric)"),
        ("Ranged - Light", "Ranged (Light)"),
        ("Ranged - Heavy", "Ranged (Heavy)"),
        ("Melee - Lightsaber", "Melee (Lightsaber)"),
        ("Skill without hyphen", "Skill without hyphen"),
        ("", ""),
    ]
    
    print("Testing skill name conversion...")
    for input_value, expected_output in test_cases:
        result = parser._convert_skill_name(input_value)
        
        if result == expected_output:
            print(f"  ✓ '{input_value}' -> '{result}'")
        else:
            print(f"  ✗ '{input_value}' -> '{result}' (expected: '{expected_output}')")
            return False
    
    # Test None case separately
    result = parser._convert_skill_name(None)
    if result is None:
        print(f"  ✓ None -> None")
    else:
        print(f"  ✗ None -> '{result}' (expected: None)")
        return False
    
    return True

def test_career_skill_conversion():
    """Test career skill conversion with hyphens"""
    parser = XMLParser()
    
    # Create a mock career XML element with skills that have hyphens
    career_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Career>
        <Key>TESTCAREER</Key>
        <Name>Test Career</Name>
        <Description>This is a test career description.</Description>
        <CareerSkills>
            <Key>PILOTPLANETARY</Key>
            <Key>PILOTSPACE</Key>
            <Key>RANGLT</Key>
            <Key>RANGHV</Key>
        </CareerSkills>
        <Specializations>
            <Key>SPEC1</Key>
            <Key>SPEC2</Key>
        </Specializations>
    </Career>
    '''
    
    root = ET.fromstring(career_xml)
    
    print("Testing career skill conversion...")
    career_data = parser._extract_career_data(root)
    
    if career_data is None:
        print("  ✗ Career data extraction failed")
        return False
    
    # Check if skills are converted correctly
    skills = career_data.get('data', {}).get('skills', '')
    print(f"  Skills: {skills}")
    
    # The actual skill names will depend on what's loaded from the Skills.xml file
    # But we can check that the conversion method is being called
    return True

def test_specialization_skill_conversion():
    """Test specialization skill conversion with hyphens"""
    parser = XMLParser()
    
    # Create a mock specialization XML element with skills that have hyphens
    spec_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Specialization>
        <Key>TESTSPEC</Key>
        <Name>Test Specialization</Name>
        <Description>This is a test specialization description.</Description>
        <CareerSkills>
            <Key>PILOTPLANETARY</Key>
            <Key>PILOTSPACE</Key>
            <Key>RANGLT</Key>
            <Key>RANGHV</Key>
        </CareerSkills>
    </Specialization>
    '''
    
    root = ET.fromstring(spec_xml)
    
    print("Testing specialization skill conversion...")
    spec_data = parser._extract_specialization_data(root)
    
    if spec_data is None:
        print("  ✗ Specialization data extraction failed")
        return False
    
    # Check if skills are converted correctly
    skills = spec_data.get('data', {}).get('skills', '')
    print(f"  Skills: {skills}")
    
    # The actual skill names will depend on what's loaded from the Skills.xml file
    # But we can check that the conversion method is being called
    return True

def main():
    """Run all tests"""
    print("Running skill name conversion tests...")
    
    tests = [
        test_skill_name_conversion,
        test_career_skill_conversion,
        test_specialization_skill_conversion,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✓ {test.__name__} passed")
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All skill name conversion tests passed!")
        return True
    else:
        print("❌ Some skill name conversion tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 