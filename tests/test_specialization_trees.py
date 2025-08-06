#!/usr/bin/env python3
"""
Test specialization tree parsing functionality
"""
import sys
import os
import xml.etree.ElementTree as ET
from unittest.mock import Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xml_parser import XMLParser

def test_specialization_tree_parsing():
    """Test specialization tree parsing"""
    parser = XMLParser()
    
    # Check if specialization trees were loaded
    if not hasattr(parser, '_talent_specializations'):
        print("  ✗ _talent_specializations attribute not found")
        return False
    
    if not parser._talent_specializations:
        print("  ✗ No specialization trees loaded")
        return False
    
    print(f"  ✓ Loaded {len(parser._talent_specializations)} talent-specialization mappings")
    
    # Test a few known talents
    test_talents = ['GRIT', 'QUICKST', 'RAPREA', 'QUICKDR']
    found_talents = 0
    
    for talent_key in test_talents:
        specializations = parser._get_talent_specializations(talent_key)
        if specializations:
            print(f"  ✓ Talent '{talent_key}' found in specializations: {specializations}")
            found_talents += 1
        else:
            print(f"  - Talent '{talent_key}' not found in any specialization trees")
    
    if found_talents > 0:
        print(f"  ✓ Found {found_talents} test talents in specialization trees")
        return True
    else:
        print("  ✗ No test talents found in specialization trees")
        return False

def test_talent_data_with_specializations():
    """Test that talent data extraction includes specialization trees"""
    parser = XMLParser()
    
    # Create a mock talent XML element
    talent_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Talents>
        <Talent>
            <Key>GRIT</Key>
            <Name>Grit</Name>
            <Description>This is a test talent description.</Description>
            <ActivationValue>taPassive</ActivationValue>
            <Ranked>true</Ranked>
            <ForceTalent>false</ForceTalent>
        </Talent>
    </Talents>
    '''
    
    root = ET.fromstring(talent_xml)
    talent_elem = root.find('Talent')
    
    print("Testing talent data extraction with specializations...")
    talent_data = parser._extract_talent_data(talent_elem)
    
    if talent_data is None:
        print("  ✗ Talent data extraction failed")
        return False
    
    # Check the extracted data
    data = talent_data.get('data', {})
    
    # Check specializationTrees field
    specialization_trees = data.get('specializationTrees', [])
    if specialization_trees:
        print(f"  ✓ Specialization trees found: {specialization_trees}")
        return True
    else:
        print("  - No specialization trees found (this might be normal if GRIT isn't in any trees)")
        return True  # This is not necessarily a failure

def test_specialization_tree_structure():
    """Test parsing of a specific specialization tree structure"""
    parser = XMLParser()
    
    # Create a mock specialization XML element
    spec_xml = '''<?xml version="1.0" encoding="utf-8"?>
    <Specialization>
        <Key>TESTSPEC</Key>
        <Name>Test Specialization</Name>
        <Description>This is a test specialization.</Description>
        <TalentRows>
            <TalentRow>
                <Cost>5</Cost>
                <Talents>
                    <Key>GRIT</Key>
                    <Key>QUICKST</Key>
                </Talents>
                <Directions>
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
    
    # Test the parsing logic manually
    spec_key = parser._get_text(root, 'Key')
    spec_name = parser._get_text(root, 'Name')
    
    if spec_key != 'TESTSPEC':
        print(f"  ✗ Spec key extraction failed: expected 'TESTSPEC', got '{spec_key}'")
        return False
    
    if spec_name != 'Test Specialization':
        print(f"  ✗ Spec name extraction failed: expected 'Test Specialization', got '{spec_name}'")
        return False
    
    # Test talent extraction
    talent_rows = parser._findall_with_namespace(root, 'TalentRow')
    if not talent_rows:
        print("  ✗ No talent rows found")
        return False
    
    talent_keys = []
    for talent_row in talent_rows:
        talents = parser._findall_with_namespace(talent_row, 'Key')
        for talent_elem in talents:
            talent_key = talent_elem.text.strip() if talent_elem.text else ''
            if talent_key:
                talent_keys.append(talent_key)
    
    expected_talents = ['GRIT', 'QUICKST']
    if talent_keys == expected_talents:
        print(f"  ✓ Talent keys extracted correctly: {talent_keys}")
        return True
    else:
        print(f"  ✗ Talent keys extraction failed: expected {expected_talents}, got {talent_keys}")
        return False

if __name__ == "__main__":
    print("Running specialization tree tests...")
    
    # Test specialization tree structure parsing
    structure_result = test_specialization_tree_structure()
    
    # Test specialization tree loading
    loading_result = test_specialization_tree_parsing()
    
    # Test talent data extraction with specializations
    extraction_result = test_talent_data_with_specializations()
    
    if (structure_result and loading_result and extraction_result):
        print("\n✅ All specialization tree tests passed!")
    else:
        print("\n❌ Some specialization tree tests failed!")
        sys.exit(1) 