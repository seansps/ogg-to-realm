#!/usr/bin/env python3
"""
Test script for ForceRating parsing in careers and specializations
"""

import sys
import os
import xml.etree.ElementTree as ET
from unittest.mock import Mock

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser
from data_mapper import DataMapper


def test_career_with_force_rating():
    """Test that careers with ForceRating have data.forceRating set"""
    parser = XMLParser()

    career_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Career>
  <Key>JEDI</Key>
  <Name>Jedi</Name>
  <Description>The Jedi career</Description>
  <Source Page="24">Rise of the Separatists</Source>
  <CareerSkills>
    <Key>ATHL</Key>
    <Key>COOL</Key>
  </CareerSkills>
  <Specializations>
    <Key>JEDIKNIGHT</Key>
  </Specializations>
  <Attributes>
    <ForceRating>1</ForceRating>
  </Attributes>
</Career>
    '''

    root = ET.fromstring(career_xml)
    career_data = parser._extract_career_data(root)

    assert career_data is not None, "Career data extraction failed"

    data = career_data.get('data', {})
    assert data.get('forceRating') == 1, f"Expected forceRating 1, got {data.get('forceRating')}"

    # Verify it survives conversion through data_mapper
    mock_api = Mock()
    mock_api.campaign_id = "test-campaign"
    mapper = DataMapper(api_client=mock_api)
    realm_career = mapper._convert_career(career_data, "test-campaign", "Test")
    realm_data = realm_career.get('data', {})
    assert realm_data.get('forceRating') == 1, f"Expected forceRating 1 after conversion, got {realm_data.get('forceRating')}"

    print("PASSED: test_career_with_force_rating")


def test_career_without_force_rating():
    """Test that careers without ForceRating don't have data.forceRating set"""
    parser = XMLParser()

    career_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Career>
  <Key>SMUGGLER</Key>
  <Name>Smuggler</Name>
  <Description>The Smuggler career</Description>
  <Source Page="50">Edge of the Empire Core Rulebook</Source>
  <CareerSkills>
    <Key>COORD</Key>
    <Key>DECEP</Key>
  </CareerSkills>
  <Specializations>
    <Key>PILOT</Key>
  </Specializations>
</Career>
    '''

    root = ET.fromstring(career_xml)
    career_data = parser._extract_career_data(root)

    assert career_data is not None, "Career data extraction failed"

    data = career_data.get('data', {})
    assert 'forceRating' not in data, f"Expected no forceRating, got {data.get('forceRating')}"

    print("PASSED: test_career_without_force_rating")


def test_specialization_with_force_rating():
    """Test that specializations with ForceRating have data.forceRating set"""
    parser = XMLParser()

    spec_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Specialization>
  <Key>FORCESENSITIVEEXILE</Key>
  <Name>Force Sensitive Exile</Name>
  <Description>A Force sensitive specialization</Description>
  <Source Page="276">Edge of the Empire Core Rulebook</Source>
  <TalentRows>
    <TalentRow>
      <Cost>5</Cost>
      <Talents>
        <Key>GRIT</Key>
        <Key>DODGE</Key>
        <Key>GRIT</Key>
        <Key>TOUGH</Key>
      </Talents>
    </TalentRow>
  </TalentRows>
  <Attributes>
    <ForceRating>1</ForceRating>
  </Attributes>
</Specialization>
    '''

    root = ET.fromstring(spec_xml)
    spec_data = parser._extract_specialization_data(root)

    assert spec_data is not None, "Specialization data extraction failed"

    data = spec_data.get('data', {})
    assert data.get('forceRating') == 1, f"Expected forceRating 1, got {data.get('forceRating')}"

    # Verify it survives conversion through data_mapper
    mock_api = Mock()
    mock_api.campaign_id = "test-campaign"
    mapper = DataMapper(api_client=mock_api)
    realm_spec = mapper._convert_specialization(spec_data, "test-campaign", "Test")
    realm_data = realm_spec.get('data', {})
    assert realm_data.get('forceRating') == 1, f"Expected forceRating 1 after conversion, got {realm_data.get('forceRating')}"

    print("PASSED: test_specialization_with_force_rating")


def test_specialization_without_force_rating():
    """Test that specializations without ForceRating don't have data.forceRating set"""
    parser = XMLParser()

    spec_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Specialization>
  <Key>INFILTRATOR</Key>
  <Name>Infiltrator</Name>
  <Description>An infiltrator specialization</Description>
  <Source Page="97">Age of Rebellion Core Rulebook</Source>
  <TalentRows>
    <TalentRow>
      <Cost>5</Cost>
      <Talents>
        <Key>GRIT</Key>
        <Key>DODGE</Key>
        <Key>GRIT</Key>
        <Key>TOUGH</Key>
      </Talents>
    </TalentRow>
  </TalentRows>
</Specialization>
    '''

    root = ET.fromstring(spec_xml)
    spec_data = parser._extract_specialization_data(root)

    assert spec_data is not None, "Specialization data extraction failed"

    data = spec_data.get('data', {})
    assert 'forceRating' not in data, f"Expected no forceRating, got {data.get('forceRating')}"

    print("PASSED: test_specialization_without_force_rating")


def test_real_jedi_career_file():
    """Test ForceRating parsing from the actual Jedi career XML file"""
    jedi_path = os.path.join(os.path.dirname(__file__), '..', 'OggData', 'Careers', 'Jedi.xml')
    if not os.path.exists(jedi_path):
        print("SKIPPED: test_real_jedi_career_file (Jedi.xml not found)")
        return

    parser = XMLParser()
    tree = ET.parse(jedi_path)
    root = tree.getroot()
    career_data = parser._extract_career_data(root)

    assert career_data is not None, "Jedi career data extraction failed"
    assert career_data.get('name') == 'Jedi', f"Expected name 'Jedi', got {career_data.get('name')}"

    data = career_data.get('data', {})
    assert data.get('forceRating') == 1, f"Expected forceRating 1, got {data.get('forceRating')}"

    print("PASSED: test_real_jedi_career_file")


def test_real_force_sensitive_exile_file():
    """Test ForceRating parsing from the actual Force Sensitive Exile XML file"""
    fse_path = os.path.join(os.path.dirname(__file__), '..', 'OggData', 'Force Sensitive Exile.xml')
    if not os.path.exists(fse_path):
        print("SKIPPED: test_real_force_sensitive_exile_file (file not found)")
        return

    parser = XMLParser()
    tree = ET.parse(fse_path)
    root = tree.getroot()
    spec_data = parser._extract_specialization_data(root)

    assert spec_data is not None, "Force Sensitive Exile data extraction failed"
    assert spec_data.get('name') == 'Force Sensitive Exile', f"Expected name 'Force Sensitive Exile', got {spec_data.get('name')}"

    data = spec_data.get('data', {})
    assert data.get('forceRating') == 1, f"Expected forceRating 1, got {data.get('forceRating')}"

    print("PASSED: test_real_force_sensitive_exile_file")


def run_tests():
    """Run all tests"""
    test_career_with_force_rating()
    test_career_without_force_rating()
    test_specialization_with_force_rating()
    test_specialization_without_force_rating()
    test_real_jedi_career_file()
    test_real_force_sensitive_exile_file()

    print("\n✅ All ForceRating tests passed!")


if __name__ == '__main__':
    run_tests()
