#!/usr/bin/env python3
"""
Test talent conversion functionality
"""
import sys
import os
import xml.etree.ElementTree as ET
from unittest.mock import Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xml_parser import XMLParser

def test_activation_value_conversion():
    """Test activation value conversion"""
    parser = XMLParser()
    
    # Test cases for activation value conversion
    test_cases = [
        ("taPassive", "Passive"),
        ("taAction", "Active"),
        ("taIncidental", "Incidental"),
        ("taManeuver", "Maneuver"),
        ("taOutOfTurn", "OutOfTurn"),
        ("", ""),
        ("SomeOtherValue", "SomeOtherValue"),
    ]
    
    print("Testing activation value conversion...")
    for input_value, expected_output in test_cases:
        result = parser._convert_activation_value(input_value)
        if result == expected_output:
            print(f"  ✓ '{input_value}' -> '{result}'")
        else:
            print(f"  ✗ '{input_value}' -> '{result}' (expected: '{expected_output}')")
            return False
    
    return True

def test_boolean_to_yes_no_conversion():
    """Test boolean to yes/no conversion"""
    parser = XMLParser()
    
    # Test cases for boolean conversion
    test_cases = [
        (True, "yes"),
        (False, "no"),
        ("true", "yes"),
        ("false", "no"),
        ("TRUE", "yes"),
        ("FALSE", "no"),
        ("yes", "yes"),
        ("no", "no"),
        (1, "yes"),
        (0, "no"),
        ("", "no"),
        (None, "no"),
    ]
    
    print("Testing boolean to yes/no conversion...")
    for input_value, expected_output in test_cases:
        result = parser._convert_boolean_to_yes_no(input_value)
        if result == expected_output:
            print(f"  ✓ {input_value} -> '{result}'")
        else:
            print(f"  ✗ {input_value} -> '{result}' (expected: '{expected_output}')")
            return False
    
    return True

def test_talent_data_extraction():
    """Test talent data extraction with conversions"""
    parser = XMLParser()
    
    # Create a mock talent XML element
    talent_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Talents>
        <Talent>
            <Key>TESTTALENT</Key>
            <Name>Test Talent</Name>
            <Description>This is a test talent description.</Description>
            <ActivationValue>taAction</ActivationValue>
            <Ranked>true</Ranked>
            <ForceTalent>false</ForceTalent>
        </Talent>
    </Talents>
    '''
    
    root = ET.fromstring(talent_xml)
    talent_elem = root.find('Talent')
    
    print("Testing talent data extraction...")
    talent_data = parser._extract_talent_data(talent_elem)
    
    if talent_data is None:
        print("  ✗ Talent data extraction failed")
        return False
    
    # Check the extracted data
    data = talent_data.get('data', {})
    
    # Check activation conversion
    activation = data.get('activation', '')
    if activation == 'Active':
        print(f"  ✓ Activation converted correctly: '{activation}'")
    else:
        print(f"  ✗ Activation conversion failed: '{activation}' (expected: 'Active')")
        return False
    
    # Check ranked conversion
    ranked = data.get('ranked', '')
    if ranked == 'yes':
        print(f"  ✓ Ranked converted correctly: '{ranked}'")
    else:
        print(f"  ✗ Ranked conversion failed: '{ranked}' (expected: 'yes')")
        return False
    
    # Check forceTalent conversion
    force_talent = data.get('forceTalent', '')
    if force_talent == 'no':
        print(f"  ✓ ForceTalent converted correctly: '{force_talent}'")
    else:
        print(f"  ✗ ForceTalent conversion failed: '{force_talent}' (expected: 'no')")
        return False
    
    return True

def test_talent_data_extraction_passive():
    """Test talent data extraction with passive activation"""
    parser = XMLParser()
    
    # Create a mock talent XML element with passive activation
    talent_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Talents>
        <Talent>
            <Key>PASSIVETALENT</Key>
            <Name>Passive Talent</Name>
            <Description>This is a passive talent description.</Description>
            <ActivationValue>taPassive</ActivationValue>
            <Ranked>false</Ranked>
            <ForceTalent>true</ForceTalent>
        </Talent>
    </Talents>
    '''
    
    root = ET.fromstring(talent_xml)
    talent_elem = root.find('Talent')
    
    print("Testing passive talent data extraction...")
    talent_data = parser._extract_talent_data(talent_elem)
    
    if talent_data is None:
        print("  ✗ Passive talent data extraction failed")
        return False
    
    # Check the extracted data
    data = talent_data.get('data', {})
    
    # Check activation conversion
    activation = data.get('activation', '')
    if activation == 'Passive':
        print(f"  ✓ Passive activation converted correctly: '{activation}'")
    else:
        print(f"  ✗ Passive activation conversion failed: '{activation}' (expected: 'Passive')")
        return False
    
    # Check ranked conversion
    ranked = data.get('ranked', '')
    if ranked == 'no':
        print(f"  ✓ Ranked converted correctly: '{ranked}'")
    else:
        print(f"  ✗ Ranked conversion failed: '{ranked}' (expected: 'no')")
        return False
    
    # Check forceTalent conversion
    force_talent = data.get('forceTalent', '')
    if force_talent == 'yes':
        print(f"  ✓ ForceTalent converted correctly: '{force_talent}'")
    else:
        print(f"  ✗ ForceTalent conversion failed: '{force_talent}' (expected: 'yes')")
        return False
    
    return True

if __name__ == "__main__":
    print("Running talent conversion tests...")
    
    # Test activation value conversion
    activation_result = test_activation_value_conversion()
    
    # Test boolean to yes/no conversion
    boolean_result = test_boolean_to_yes_no_conversion()
    
    # Test talent data extraction
    extraction_result = test_talent_data_extraction()
    
    # Test passive talent data extraction
    passive_result = test_talent_data_extraction_passive()
    
    if (activation_result and boolean_result and extraction_result and passive_result):
        print("\n✅ All talent conversion tests passed!")
    else:
        print("\n❌ Some talent conversion tests failed!")
        sys.exit(1) 