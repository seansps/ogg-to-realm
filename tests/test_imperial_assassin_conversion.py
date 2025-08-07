#!/usr/bin/env python3
"""
Comprehensive test for Imperial Assassin adversary conversion
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from json_parser import JSONParser
from data_mapper import DataMapper


def test_imperial_assassin_conversion():
    parser = JSONParser()
    data_mapper = DataMapper()

    # Parse adversaries file
    records = parser.parse_json_file('Adversaries/imperial-military.json')

    npc = next((r for r in records if r['name'] == 'Imperial Assassin'), None)
    assert npc is not None, "Imperial Assassin not found in adversaries file"

    # Sanity check extracted raw fields
    assert npc['data']['type'].lower() == 'nemesis'
    assert npc['data']['characteristics']['Brawn'] if 'Brawn' in npc['data']['characteristics'] else npc['data']['characteristics']['brawn']

    # Convert
    converted = data_mapper.convert_oggdude_to_realm_vtt(npc, 'test_campaign', 'Imperial Military')

    # Basic structure
    assert converted['name'] == 'Imperial Assassin'
    assert converted['recordType'] == 'npcs'
    assert converted['data']['type'] == 'nemesis'

    data = converted['data']

    # Characteristics
    assert data['brawn'] == 3
    assert data['agility'] == 3
    assert data['intellect'] == 3
    assert data['cunning'] == 3
    assert data['willpower'] == 3
    assert data['presence'] == 2

    # Derived
    assert data['soakValue'] == 3
    assert data['woundThreshold'] == 18
    assert data['strainThreshold'] == 20
    assert data['woundsRemaining'] == 18
    assert data['strainRemaining'] == 20

    # Skills list should include specified ranks
    def get_skill(skills, name):
        for s in skills:
            if s['name'] == name:
                return s
        return None

    skills = data['skills']
    assert get_skill(skills, 'Athletics')['data']['rank'] == 2
    assert get_skill(skills, 'Cool')['data']['rank'] == 3
    assert get_skill(skills, 'Coordination')['data']['rank'] == 3
    assert get_skill(skills, 'Discipline')['data']['rank'] == 3
    assert get_skill(skills, 'Melee')['data']['rank'] == 4
    assert get_skill(skills, 'Perception')['data']['rank'] == 4
    # Colon variant should be normalized
    assert get_skill(skills, 'Piloting (Space)')['data']['rank'] == 2
    # Colon variants for ranged should be normalized
    assert get_skill(skills, 'Ranged (Heavy)')['data']['rank'] == 4
    assert get_skill(skills, 'Stealth')['data']['rank'] == 4
    assert get_skill(skills, 'Vigilance')['data']['rank'] == 4

    # Talents should exist and include ranks
    talents = data.get('talents', [])
    assert isinstance(talents, list) and len(talents) >= 3

    def find_talent(name):
        for t in talents:
            if t.get('name') == name:
                return t
        return None

    adv = find_talent('Adversary')
    assert adv is not None
    assert adv['data'].get('rank') == 1
    # Check that Adversary modifier value matches rank
    mods = adv['data'].get('modifiers', []) or []
    if mods:
        for m in mods:
            md = m.get('data', {})
            if md.get('type') == 'upgradeDifficultyOfAttacksTargetingYou':
                assert md.get('value') == '1'
                break

    parry = find_talent('Parry')
    assert parry is not None
    assert parry['data'].get('rank') == 3

    ind = find_talent('Indistinguishable')
    assert ind is not None
    assert ind['data'].get('rank') == 2

    # Inventory: Disruptor rifle from XML and ad-hoc melee weapon
    inventory = data.get('inventory', [])
    names = [i['name'] for i in inventory]
    assert any('Disruptor' in n for n in names), f"Inventory missing Disruptor rifle: {names}"
    assert any('Combat vibroblade' in n or 'Vibroblade' in n for n in names), f"Inventory missing vibroblade: {names}"


if __name__ == '__main__':
    # Allow running the test directly
    ok = True
    try:
        test_imperial_assassin_conversion()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        ok = False
    if ok:
        print("\n✓ Imperial Assassin conversion test passed!")

