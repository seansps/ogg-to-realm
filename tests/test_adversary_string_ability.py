#!/usr/bin/env python3
"""
Test that string abilities (non-object) are converted into one-off features
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data_mapper import DataMapper


def test_string_ability_becomes_feature():
    mapper = DataMapper()

    npc = {
        'recordType': 'npcs',
        'name': 'String Ability NPC',
        'description': 'A test NPC',
        'data': {
            'type': 'Rival',
            'characteristics': {},
            'derived': {'soak': 2, 'wounds': 10, 'strain': 10},
            'abilities': [
                {
                    'name': 'Force Power: Move',
                    'description': ':forcepip:: Move one object Silhouette 1 at Short range.'
                },
                'On the Edge',
            ]
        }
    }

    converted = mapper.convert_oggdude_to_realm_vtt(npc, 'test_campaign', 'Test Category')
    data = converted['data']
    features = data.get('features', [])
    assert isinstance(features, list)
    # Find the string ability converted to a feature
    f = next((x for x in features if x['name'] == 'On the Edge'), None)
    assert f is not None
    fdata = f.get('data', {})
    assert fdata.get('isForcePower') is False
    # String ability has no description provided
    assert fdata.get('description', '') == ''


if __name__ == '__main__':
    test_string_ability_becomes_feature()
    print('\n✓ String ability conversion test passed!')


