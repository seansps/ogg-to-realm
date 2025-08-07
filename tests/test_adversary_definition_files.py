#!/usr/bin/env python3
"""
Tests that adversary definition files (talents.json, abilities.json, force-powers.json)
are discovered and used to enrich string abilities and provide talent fallbacks.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from json_parser import JSONParser
from data_mapper import DataMapper


def test_string_ability_enriched_from_abilities_definitions():
    parser = JSONParser()
    defs = parser._load_adversary_definitions(Path('Adversaries'))
    assert 'abilities' in defs and isinstance(defs['abilities'], dict)

    npc = {
        'recordType': 'npcs',
        'name': 'Defs Ability NPC',
        'data': {
            'type': 'Rival',
            'characteristics': {},
            'derived': {'soak': 2, 'wounds': 10, 'strain': 10},
            'abilities': ['Advanced Language Module'],
            'definitions': defs,
        }
    }

    mapper = DataMapper()
    converted = mapper.convert_oggdude_to_realm_vtt(npc, 'test_campaign', 'Test')
    features = converted['data'].get('features', [])
    abl = next((f for f in features if f['name'] == 'Advanced Language Module'), None)
    assert abl is not None
    desc = abl['data'].get('description', '')
    # Description should be populated and difficulty converted to label + spans
    assert desc and 'Easy (' in desc and desc.count('class="difficulty"') >= 1
    # Skill parsed
    assert abl['data'].get('skill') == 'Education'


def test_string_force_power_enriched_from_force_powers_definitions():
    parser = JSONParser()
    defs = parser._load_adversary_definitions(Path('Adversaries'))

    npc = {
        'recordType': 'npcs',
        'name': 'Defs Force Power NPC',
        'data': {
            'type': 'Rival',
            'characteristics': {},
            'derived': {'soak': 2, 'wounds': 10, 'strain': 10},
            'abilities': ['Force Power: Move'],
            'definitions': defs,
        }
    }

    mapper = DataMapper()
    converted = mapper.convert_oggdude_to_realm_vtt(npc, 'test_campaign', 'Test')
    features = converted['data'].get('features', [])
    abl = next((f for f in features if f['name'].startswith('Force Power: Move')), None)
    assert abl is not None
    # Should be marked as force power
    assert abl['data'].get('isForcePower') is True
    # Description enriched (contains something non-empty)
    assert abl['data'].get('description', '')


def test_talent_fallback_from_talents_definitions():
    parser = JSONParser()
    defs = parser._load_adversary_definitions(Path('Adversaries'))

    npc = {
        'recordType': 'npcs',
        'name': 'Defs Talent NPC',
        'data': {
            'type': 'Rival',
            'characteristics': {},
            'derived': {'soak': 2, 'wounds': 10, 'strain': 10},
            'talents': ['All the Luck in the Galaxy 1'],
            'definitions': defs,
        }
    }

    mapper = DataMapper()
    converted = mapper.convert_oggdude_to_realm_vtt(npc, 'test_campaign', 'Test')
    talents = converted['data'].get('talents', [])
    tal = next((t for t in talents if t['name'] == 'All the Luck in the Galaxy'), None)
    assert tal is not None
    # Rank carried through
    assert tal['data'].get('rank') == 1
    # Description enriched from definitions
    assert tal['data'].get('description', '') is not None


if __name__ == '__main__':
    test_string_ability_enriched_from_abilities_definitions()
    test_string_force_power_enriched_from_force_powers_definitions()
    test_talent_fallback_from_talents_definitions()
    print('\n✓ Adversary definition files tests passed!')


