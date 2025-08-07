#!/usr/bin/env python3
"""
Test adversary conversion for Force Rating handling and abilities → features parsing
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data_mapper import DataMapper


def test_force_rating_and_abilities_parsing():
    mapper = DataMapper()

    npc = {
        'recordType': 'npcs',
        'name': 'Ability Test NPC',
        'description': 'A test NPC',
        'data': {
            'type': 'Nemesis',
            'characteristics': {
                'brawn': 3,
                'agility': 3,
                'intellect': 3,
                'cunning': 3,
                'willpower': 3,
                'presence': 3,
            },
            'derived': {
                'soak': 3,
                'wounds': 12,
                'strain': 12,
            },
            'talents': ['Adversary 1', 'Force Rating 4', 'Parry 2'],
            'abilities': [
                'Darkside Force User',
                {
                    'name': 'Imperial Intimidation',
                    'description': 'As an action, Aresko may make an :average: Coercion check; if successful, characters targeting him or his allies within Short range add :setback: to their skill checks for the rest of the encounter.'
                },
                {
                    'name': 'Force Power: Enhance',
                    'description': 'When making an Athletics check, spend :forcepip: to gain :success:.'
                },
                {
                    'name': 'Tricky Flight',
                    'description': 'This makes a :easy: Piloting: Plantary check'
                }
            ]
        }
    }

    converted = mapper.convert_oggdude_to_realm_vtt(npc, 'test_campaign', 'Test Category')
    data = converted['data']

    # Force Rating captured and not a talent
    assert data.get('forceRating') == 4
    assert 'talents' in data
    talent_names = [t['name'] for t in data['talents']]
    assert 'Parry' in talent_names
    assert 'Force Rating' not in talent_names

    # Abilities converted to features
    features = data.get('features', [])
    assert isinstance(features, list) and len(features) >= 2

    # Find Imperial Intimidation feature
    intimidation = next((f for f in features if f['name'] == 'Imperial Intimidation'), None)
    assert intimidation is not None
    idata = intimidation['data']
    assert idata.get('skill') == 'Coercion'
    assert idata.get('difficulty') == 'Average'
    # Average should render as label + two difficulty spans in parentheses
    desc = idata.get('description', '')
    assert 'Average (' in desc and desc.count('class="difficulty"') >= 2
    assert ':average:' not in desc
    assert '<span class="setback"' in desc

    # Force power ability is flagged and has forcepoint span
    enhance = next((f for f in features if f['name'].startswith('Force Power: Enhance')), None)
    assert enhance is not None
    edata = enhance['data']
    assert edata.get('isForcePower') is True
    assert '<span class="forcepoint"' in edata.get('description', '')

    # Piloting colon variant and misspelling handling in ability parsing
    tricky = next((f for f in features if f['name'] == 'Tricky Flight'), None)
    assert tricky is not None
    tdata = tricky['data']
    assert tdata.get('skill') == 'Piloting (Planetary)'
    assert tdata.get('difficulty') == 'Easy'
    # Easy should render as label + one difficulty span in parentheses
    tdesc = tdata.get('description', '')
    assert 'Easy (' in tdesc and tdesc.count('class="difficulty"') >= 1


if __name__ == '__main__':
    test_force_rating_and_abilities_parsing()
    print('\n✓ Adversary force rating + abilities parsing test passed!')


