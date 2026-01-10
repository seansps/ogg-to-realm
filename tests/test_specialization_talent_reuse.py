#!/usr/bin/env python3
"""
Test script for specialization talent reuse from campaign cache
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser
from data_mapper import DataMapper

def test_specialization_talent_reuse():
    """Test that talents in specialization trees reuse campaign talents when available"""
    try:
        parser = XMLParser()

        # Create a mock API client
        mock_api_client = Mock()
        mock_api_client.campaign_id = "test-campaign-123"

        # Create data mapper
        data_mapper = DataMapper(api_client=mock_api_client)

        # Create a mock specialization with talents
        spec_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Specialization>
    <Key>HEALER</Key>
    <Name>Healer</Name>
    <Description>A healer specialization</Description>
    <Source Page="71">Force and Destiny Core Rulebook</Source>
    <CareerSkills>
        <Key>DISC</Key>
        <Key>RESIL</Key>
        <Key>VIGIL</Key>
        <Key>XENCOR</Key>
    </CareerSkills>
    <TalentRows>
        <TalentRow>
            <Cost>5</Cost>
            <Talents>
                <Key>GRIT</Key>
                <Key>SURGEON</Key>
                <Key>NATDOC</Key>
                <Key>GRIT</Key>
            </Talents>
        </TalentRow>
        <TalentRow>
            <Index>1</Index>
            <Cost>10</Cost>
            <Talents>
                <Key>TOUGH</Key>
                <Key>STIM</Key>
                <Key>NATDOC</Key>
                <Key>HEALTRANCE</Key>
            </Talents>
        </TalentRow>
    </TalentRows>
</Specialization>
        '''

        root = ET.fromstring(spec_xml)

        print("Testing specialization talent reuse from campaign cache...")

        # Parse the specialization
        spec_data = parser._extract_specialization_data(root)

        if spec_data is None:
            print("  ✗ Specialization data extraction failed")
            return False

        # Verify talents are in the parsed data
        data = spec_data.get('data', {})
        talent1_1 = data.get('talent1_1', [])
        if not talent1_1 or len(talent1_1) == 0:
            print("  ✗ talent1_1 not found in parsed data")
            return False

        original_grit = talent1_1[0]
        print(f"  ✓ Found original talent: {original_grit.get('name')}")

        # Create a mock campaign talent with a portrait
        campaign_grit = {
            "_id": "campaign-grit-123",
            "name": "Grit",
            "recordType": "talents",
            "campaignId": "test-campaign-123",
            "identified": True,
            "portrait": "/images/grit-portrait.webp",
            "img": "/images/grit-icon.webp",
            "data": {
                "name": "Grit",
                "description": "<p>Custom campaign description for Grit</p>",
                "activation": "Passive",
                "ranked": True,
                "forceTalent": False,
                "tier": 1,
                "specializationTrees": ["Healer", "Other Spec"]
            },
            "unidentifiedName": "Unknown Talent",
            "icon": "IconStar"
        }

        # Populate the campaign talents cache
        data_mapper._campaign_talents_cache = {
            'grit': campaign_grit
        }
        print(f"  ✓ Populated campaign cache with 1 talent")

        # Convert the specialization using data mapper
        realm_spec = data_mapper._convert_specialization(spec_data, "test-campaign-123", "Test Category")

        # Check that the talent was replaced with the campaign version
        converted_data = realm_spec.get('data', {})
        converted_talent1_1 = converted_data.get('talent1_1', [])

        if not converted_talent1_1 or len(converted_talent1_1) == 0:
            print("  ✗ talent1_1 not found in converted data")
            return False

        converted_grit = converted_talent1_1[0]

        # Verify the talent was replaced with the campaign version
        if converted_grit.get('_id') != campaign_grit['_id']:
            print(f"  ✗ Talent was not replaced with campaign version")
            print(f"    Expected _id: {campaign_grit['_id']}")
            print(f"    Got _id: {converted_grit.get('_id')}")
            return False

        print(f"  ✓ Talent was replaced with campaign version (ID: {converted_grit.get('_id')})")

        # Verify the portrait was preserved
        if converted_grit.get('portrait') != campaign_grit['portrait']:
            print(f"  ✗ Portrait was not preserved")
            print(f"    Expected: {campaign_grit['portrait']}")
            print(f"    Got: {converted_grit.get('portrait')}")
            return False

        print(f"  ✓ Portrait was preserved: {converted_grit.get('portrait')}")

        # Verify the cost from the tree was preserved
        converted_cost = converted_grit.get('data', {}).get('cost')
        if converted_cost != 5:  # First row has cost of 5
            print(f"  ✗ Cost from tree was not preserved")
            print(f"    Expected: 5")
            print(f"    Got: {converted_cost}")
            return False

        print(f"  ✓ Cost from specialization tree was preserved: {converted_cost}")

        # Verify the campaign description was preserved
        campaign_desc = campaign_grit['data']['description']
        converted_desc = converted_grit.get('data', {}).get('description')
        if converted_desc != campaign_desc:
            print(f"  ✗ Campaign description was not preserved")
            print(f"    Expected: {campaign_desc}")
            print(f"    Got: {converted_desc}")
            return False

        print(f"  ✓ Campaign description was preserved")

        # Test that talents NOT in cache are kept as original
        converted_talent1_2 = converted_data.get('talent1_2', [])
        if not converted_talent1_2 or len(converted_talent1_2) == 0:
            print("  ✗ talent1_2 not found in converted data")
            return False

        converted_surgeon = converted_talent1_2[0]
        surgeon_name = converted_surgeon.get('name')

        # This talent should NOT have a campaign _id since it's not in the cache
        if converted_surgeon.get('_id') == campaign_grit['_id']:
            print(f"  ✗ Non-cached talent incorrectly replaced")
            return False

        print(f"  ✓ Non-cached talent '{surgeon_name}' was kept as original")

        print("  ✓ All specialization talent reuse tests passed!")
        return True

    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_specialization_talent_reuse()
    if success:
        print("\n🎉 All specialization talent reuse tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some specialization talent reuse tests failed!")
        sys.exit(1)
