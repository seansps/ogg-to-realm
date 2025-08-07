#!/usr/bin/env python3
"""
Test conversion of adversary descriptions containing dice tags like :difficulty:
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data_mapper import DataMapper


def test_adversary_description_dice_tag_conversion():
    mapper = DataMapper()

    npc = {
        'recordType': 'npcs',
        'name': 'Test NPC',
        'description': 'Make a :difficulty: check with :boost: and :setback:.',
        'data': {
            'type': 'Rival',
            'characteristics': {
                # minimal presence; values defaulted if not provided
            },
            'derived': {
                'soak': 2,
                'wounds': 10,
                'strain': 10,
            },
        }
    }

    converted = mapper.convert_oggdude_to_realm_vtt(npc, 'test_campaign', 'Test Category')
    assert converted is not None
    html = converted['data'].get('description', '')

    # Heading added with NPC name
    assert '<h2>Test NPC</h2>' in html

    # Dice tags converted to spans
    assert '<span class="difficulty"' in html, 'Missing difficulty span'
    assert '<span class="boost"' in html, 'Missing boost span'
    assert '<span class="setback"' in html, 'Missing setback span'

    # Original tokens removed
    assert ':difficulty:' not in html
    assert ':boost:' not in html
    assert ':setback:' not in html


if __name__ == '__main__':
    test_adversary_description_dice_tag_conversion()
    print('\n✓ Adversary description dice tag conversion test passed!')


