#!/usr/bin/env python3
"""
Test that Forsaken Jedi adversary gets abilities converted into features
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from json_parser import JSONParser
from data_mapper import DataMapper


def test_forsaken_jedi_features_present():
    parser = JSONParser()
    mapper = DataMapper()

    records = parser.parse_json_file('Adversaries/force-sensitives.json')
    target = next((r for r in records if r['name'] == 'Forsaken Jedi'), None)
    assert target is not None, 'Forsaken Jedi not found in source JSON'

    converted = mapper.convert_oggdude_to_realm_vtt(target, 'test_campaign', 'Force Sensitives')
    data = converted['data']

    features = data.get('features', [])
    assert isinstance(features, list)
    # Should include Force Power: Move and Force Power: Sense and the string ability 'On the Edge'
    names = [f['name'] for f in features]
    assert 'Force Power: Move' in names
    assert 'Force Power: Sense' in names
    assert 'On the Edge' in names

    # Force power flags
    move = next(f for f in features if f['name'] == 'Force Power: Move')
    sense = next(f for f in features if f['name'] == 'Force Power: Sense')
    assert move['data'].get('isForcePower') is True
    assert sense['data'].get('isForcePower') is True

    # Description should contain light pip spans and difficulty replacements
    assert '<span class="light"' in move['data'].get('description', '')
    assert '<span class="light"' in sense['data'].get('description', '')


if __name__ == '__main__':
    test_forsaken_jedi_features_present()
    print('\n✓ Forsaken Jedi features test passed!')


