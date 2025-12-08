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
        ("taIncidental", "Active"),
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

def test_adversary_talent_special_handling():
    """Test special handling for Adversary talent"""
    parser = XMLParser()

    # Create a mock talent XML element for Adversary
    talent_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Talents>
        <Talent>
            <Key>ADVERSARY</Key>
            <Name>Adversary</Name>
            <Description>This is the Adversary talent description.</Description>
            <ActivationValue>taPassive</ActivationValue>
            <Ranked>true</Ranked>
            <ForceTalent>false</ForceTalent>
        </Talent>
    </Talents>
    '''

    root = ET.fromstring(talent_xml)
    talent_elem = root.find('Talent')

    print("Testing Adversary talent special handling...")
    talent_data = parser._extract_talent_data(talent_elem)

    if talent_data is None:
        print("  ✗ Adversary talent data extraction failed")
        return False

    # Check the extracted data
    data = talent_data.get('data', {})

    # Check that modifiers field is set
    modifiers = data.get('modifiers', [])
    if modifiers:
        print(f"  ✓ Modifiers field found with {len(modifiers)} modifier(s)")

        # Check the first modifier structure
        if len(modifiers) > 0:
            modifier = modifiers[0]
            expected_id = "80ec474f-faea-4179-b19b-a66a4ba4de8b"
            expected_type = "upgradeDifficultyOfAttacksTargetingYou"
            expected_value = "1"

            if modifier.get('_id') == expected_id:
                print(f"  ✓ Modifier ID is correct: {expected_id}")
            else:
                print(f"  ✗ Modifier ID is incorrect: {modifier.get('_id')} (expected: {expected_id})")
                return False

            modifier_data = modifier.get('data', {})
            if modifier_data.get('type') == expected_type:
                print(f"  ✓ Modifier type is correct: {expected_type}")
            else:
                print(f"  ✗ Modifier type is incorrect: {modifier_data.get('type')} (expected: {expected_type})")
                return False

            if modifier_data.get('value') == expected_value:
                print(f"  ✓ Modifier value is correct: {expected_value}")
            else:
                print(f"  ✗ Modifier value is incorrect: {modifier_data.get('value')} (expected: {expected_value})")
                return False
        else:
            print("  ✗ No modifiers found in the list")
            return False
    else:
        print("  ✗ Modifiers field not found")
        return False

    return True

def test_incidental_talent_tags():
    """Test that taIncidental activation creates Incidental tag"""
    parser = XMLParser()

    # Create a mock talent XML element with taIncidental activation
    talent_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Talents>
        <Talent>
            <Key>TESTINCIDENTAL</Key>
            <Name>Test Incidental</Name>
            <Description>This is an incidental talent.</Description>
            <ActivationValue>taIncidental</ActivationValue>
            <Ranked>false</Ranked>
            <ForceTalent>false</ForceTalent>
        </Talent>
    </Talents>
    '''

    root = ET.fromstring(talent_xml)
    talent_elem = root.find('Talent')

    print("Testing incidental talent tag creation...")
    talent_data = parser._extract_talent_data(talent_elem)

    if talent_data is None:
        print("  ✗ Incidental talent data extraction failed")
        return False

    # Check the extracted data
    data = talent_data.get('data', {})

    # Check tags field
    tags = data.get('tags', [])
    if tags == ["Incidental"]:
        print(f"  ✓ Tags correctly set to {tags}")
    else:
        print(f"  ✗ Tags incorrect: {tags} (expected: ['Incidental'])")
        return False

    # Check activation is still converted to Active
    activation = data.get('activation', '')
    if activation == 'Active':
        print(f"  ✓ Activation converted correctly: '{activation}'")
    else:
        print(f"  ✗ Activation conversion failed: '{activation}' (expected: 'Active')")
        return False

    return True

def test_incidental_out_of_turn_talent_tags():
    """Test that taIncidentalOOT activation creates Incidental and Out of Turn tags"""
    parser = XMLParser()

    # Create a mock talent XML element with taIncidentalOOT activation
    talent_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Talents>
        <Talent>
            <Key>TESTINCIDENTALOOT</Key>
            <Name>Test Incidental OOT</Name>
            <Description>This is an incidental out of turn talent.</Description>
            <ActivationValue>taIncidentalOOT</ActivationValue>
            <Ranked>true</Ranked>
            <ForceTalent>false</ForceTalent>
        </Talent>
    </Talents>
    '''

    root = ET.fromstring(talent_xml)
    talent_elem = root.find('Talent')

    print("Testing incidental out of turn talent tag creation...")
    talent_data = parser._extract_talent_data(talent_elem)

    if talent_data is None:
        print("  ✗ Incidental OOT talent data extraction failed")
        return False

    # Check the extracted data
    data = talent_data.get('data', {})

    # Check tags field
    tags = data.get('tags', [])
    if tags == ["Incidental", "Out of Turn"]:
        print(f"  ✓ Tags correctly set to {tags}")
    else:
        print(f"  ✗ Tags incorrect: {tags} (expected: ['Incidental', 'Out of Turn'])")
        return False

    # Check activation is still converted to Active
    activation = data.get('activation', '')
    if activation == 'Active':
        print(f"  ✓ Activation converted correctly: '{activation}'")
    else:
        print(f"  ✗ Activation conversion failed: '{activation}' (expected: 'Active')")
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

    # Test adversary talent special handling
    adversary_result = test_adversary_talent_special_handling()

    # Test incidental talent tags
    incidental_result = test_incidental_talent_tags()

    # Test incidental out of turn talent tags
    incidental_oot_result = test_incidental_out_of_turn_talent_tags()

    if (activation_result and boolean_result and extraction_result and passive_result and adversary_result and incidental_result and incidental_oot_result):
        print("\n✅ All talent conversion tests passed!")
    else:
        print("\n❌ Some talent conversion tests failed!")
        sys.exit(1) 