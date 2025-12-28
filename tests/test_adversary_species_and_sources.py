#!/usr/bin/env python3
"""
Test script for adversary species extraction from tags and adversaries_sources filtering
"""

import sys
import os
import json
import tempfile

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from json_parser import JSONParser
from data_mapper import DataMapper


def test_species_extraction_from_tags():
    """Test that species is extracted from species: tags in adversary JSON"""
    print("Testing species extraction from tags...")

    parser = JSONParser()
    data_mapper = DataMapper()

    # Create test adversary data with species tag
    test_data = [
        {
            "name": "Gamorrean Thug",
            "type": "Rival",
            "characteristics": {
                "Brawn": 3,
                "Agility": 2,
                "Intellect": 1,
                "Cunning": 1,
                "Willpower": 1,
                "Presence": 1
            },
            "derived": {
                "soak": 3,
                "wounds": 6
            },
            "skills": {"Melee": 1},
            "tags": ["book:eote", "species:Gamorrean", "thug"]
        },
        {
            "name": "Security Droid",
            "type": "Rival",
            "characteristics": {
                "Brawn": 2,
                "Agility": 2,
                "Intellect": 1,
                "Cunning": 2,
                "Willpower": 1,
                "Presence": 1
            },
            "derived": {
                "soak": 3,
                "wounds": 8
            },
            "skills": {"Ranged: Light": 3},
            "tags": ["book:eote", "species:Droid", "security"]
        },
        {
            "name": "Generic Human",
            "type": "Minion",
            "characteristics": {
                "Brawn": 2,
                "Agility": 2,
                "Intellect": 2,
                "Cunning": 2,
                "Willpower": 2,
                "Presence": 2
            },
            "derived": {
                "soak": 2,
                "wounds": 5
            },
            "skills": {},
            "tags": ["book:eote"]  # No species tag
        }
    ]

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    try:
        records = parser.parse_json_file(temp_file)
        assert len(records) == 3, f"Expected 3 records, got {len(records)}"

        # Convert each and check species
        gamorrean = next(r for r in records if r['name'] == 'Gamorrean Thug')
        converted_gamorrean = data_mapper.convert_oggdude_to_realm_vtt(gamorrean, 'test_campaign', 'Test')
        assert converted_gamorrean['data']['speciesName'] == 'Gamorrean', \
            f"Expected speciesName 'Gamorrean', got '{converted_gamorrean['data']['speciesName']}'"

        droid = next(r for r in records if r['name'] == 'Security Droid')
        converted_droid = data_mapper.convert_oggdude_to_realm_vtt(droid, 'test_campaign', 'Test')
        assert converted_droid['data']['speciesName'] == 'Droid', \
            f"Expected speciesName 'Droid', got '{converted_droid['data']['speciesName']}'"

        human = next(r for r in records if r['name'] == 'Generic Human')
        converted_human = data_mapper.convert_oggdude_to_realm_vtt(human, 'test_campaign', 'Test')
        assert converted_human['data']['speciesName'] == '', \
            f"Expected speciesName '' (empty), got '{converted_human['data']['speciesName']}'"

        print("✓ Species extraction from tags test passed")
        return True

    finally:
        os.unlink(temp_file)


def test_species_from_direct_field():
    """Test that species is extracted from direct species field if present"""
    print("Testing species extraction from direct field...")

    parser = JSONParser()
    data_mapper = DataMapper()

    test_data = [
        {
            "name": "Wookiee Warrior",
            "type": "Rival",
            "species": "Wookiee",  # Direct field
            "characteristics": {
                "Brawn": 4,
                "Agility": 2,
                "Intellect": 2,
                "Cunning": 2,
                "Willpower": 2,
                "Presence": 2
            },
            "derived": {
                "soak": 4,
                "wounds": 14
            },
            "skills": {"Melee": 2},
            "tags": ["book:eote"]
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    try:
        records = parser.parse_json_file(temp_file)
        wookiee = records[0]
        converted = data_mapper.convert_oggdude_to_realm_vtt(wookiee, 'test_campaign', 'Test')
        assert converted['data']['speciesName'] == 'Wookiee', \
            f"Expected speciesName 'Wookiee', got '{converted['data']['speciesName']}'"

        print("✓ Species extraction from direct field test passed")
        return True

    finally:
        os.unlink(temp_file)


def test_adversaries_sources_filtering():
    """Test that adversaries are filtered correctly by adversaries_sources tags"""
    print("Testing adversaries_sources filtering...")

    parser = JSONParser()

    test_data = [
        {
            "name": "EotE Core NPC",
            "type": "Rival",
            "characteristics": {"Brawn": 2, "Agility": 2, "Intellect": 2, "Cunning": 2, "Willpower": 2, "Presence": 2},
            "derived": {"soak": 2, "wounds": 10},
            "tags": ["book:eote"]
        },
        {
            "name": "Beginner Game NPC",
            "type": "Rival",
            "characteristics": {"Brawn": 2, "Agility": 2, "Intellect": 2, "Cunning": 2, "Willpower": 2, "Presence": 2},
            "derived": {"soak": 2, "wounds": 10},
            "tags": ["book:eotebg", "adventure:Escape from Mos Shuuta"]
        },
        {
            "name": "Far Horizons NPC",
            "type": "Rival",
            "characteristics": {"Brawn": 2, "Agility": 2, "Intellect": 2, "Cunning": 2, "Willpower": 2, "Presence": 2},
            "derived": {"soak": 2, "wounds": 10},
            "tags": ["book:fh"]
        },
        {
            "name": "AoR Core NPC",
            "type": "Rival",
            "characteristics": {"Brawn": 2, "Agility": 2, "Intellect": 2, "Cunning": 2, "Willpower": 2, "Presence": 2},
            "derived": {"soak": 2, "wounds": 10},
            "tags": ["book:aor"]
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    try:
        records = parser.parse_json_file(temp_file)
        assert len(records) == 4, f"Expected 4 records, got {len(records)}"

        # Filter by EotE Core only
        filtered_eote = parser.filter_by_sources(records, ['book:eote'])
        names_eote = [r['name'] for r in filtered_eote]
        assert 'EotE Core NPC' in names_eote, f"Expected 'EotE Core NPC' in filtered results: {names_eote}"
        assert 'Beginner Game NPC' not in names_eote, f"'Beginner Game NPC' should not be in book:eote filtered results"

        # Filter by Beginner Game
        filtered_bg = parser.filter_by_sources(records, ['book:eotebg'])
        names_bg = [r['name'] for r in filtered_bg]
        assert 'Beginner Game NPC' in names_bg, f"Expected 'Beginner Game NPC' in filtered results: {names_bg}"

        # Filter by Far Horizons
        filtered_fh = parser.filter_by_sources(records, ['far-horizons'])
        names_fh = [r['name'] for r in filtered_fh]
        assert 'Far Horizons NPC' in names_fh, f"Expected 'Far Horizons NPC' in filtered results: {names_fh}"

        # Filter by multiple sources
        filtered_multi = parser.filter_by_sources(records, ['book:eote', 'book:aor'])
        names_multi = [r['name'] for r in filtered_multi]
        assert 'EotE Core NPC' in names_multi, f"Expected 'EotE Core NPC' in multi-source filtered results"
        assert 'AoR Core NPC' in names_multi, f"Expected 'AoR Core NPC' in multi-source filtered results"
        assert len(filtered_multi) == 2, f"Expected 2 records with multi-source filter, got {len(filtered_multi)}"

        print("✓ Adversaries_sources filtering test passed")
        return True

    finally:
        os.unlink(temp_file)


def test_adventure_tag_filtering():
    """Test that adventure: tags work for filtering"""
    print("Testing adventure tag filtering...")

    parser = JSONParser()

    test_data = [
        {
            "name": "Escape from Mos Shuuta NPC",
            "type": "Rival",
            "characteristics": {"Brawn": 2, "Agility": 2, "Intellect": 2, "Cunning": 2, "Willpower": 2, "Presence": 2},
            "derived": {"soak": 2, "wounds": 10},
            "tags": ["adventure:Escape from Mos Shuuta", "location:Mos Shuuta"]
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    try:
        records = parser.parse_json_file(temp_file)

        # Filter by adventure source (should match via adversaries_sources in sources.json)
        filtered = parser.filter_by_sources(records, ['adventure:escape-from-mos-shuuta'])
        names = [r['name'] for r in filtered]
        assert 'Escape from Mos Shuuta NPC' in names, \
            f"Expected 'Escape from Mos Shuuta NPC' in filtered results: {names}"

        print("✓ Adventure tag filtering test passed")
        return True

    finally:
        os.unlink(temp_file)


def test_real_escapemosshuuta_file():
    """Test with real escapemosshuuta.json file if available"""
    print("Testing with real escapemosshuuta.json file...")

    possible_paths = [
        'OggData/escapemosshuuta.json',
        '../OggData/escapemosshuuta.json'
    ]

    json_file = None
    for path in possible_paths:
        if os.path.exists(path):
            json_file = path
            break

    if not json_file:
        print("⚠ No escapemosshuuta.json file found, skipping real file test")
        return True

    parser = JSONParser()
    data_mapper = DataMapper()

    records = parser.parse_json_file(json_file)
    print(f"Found {len(records)} NPCs in {json_file}")

    # Find Gamorrean Thugs - should have species:Gamorrean tag
    gamorrean = next((r for r in records if 'Gamorrean' in r['name']), None)
    if gamorrean:
        converted = data_mapper.convert_oggdude_to_realm_vtt(gamorrean, 'test_campaign', 'Test')
        species = converted['data']['speciesName']
        print(f"  Gamorrean Thugs speciesName: '{species}'")
        assert species == 'Gamorrean', f"Expected 'Gamorrean', got '{species}'"

    # Find Security Droids - should have species:Droid tag
    droid = next((r for r in records if 'Droid' in r['name']), None)
    if droid:
        converted = data_mapper.convert_oggdude_to_realm_vtt(droid, 'test_campaign', 'Test')
        species = converted['data']['speciesName']
        print(f"  Spaceport Security Droids speciesName: '{species}'")
        assert species == 'Droid', f"Expected 'Droid', got '{species}'"

    # Test filtering by book:eotebg
    filtered = parser.filter_by_sources(records, ['book:eotebg'])
    print(f"  Records matching book:eotebg: {len(filtered)}")
    assert len(filtered) > 0, "Expected some records to match book:eotebg"

    print("✓ Real escapemosshuuta.json test passed")
    return True


def test_silhouette_extraction():
    """Test that silhouette is extracted from abilities"""
    print("Testing silhouette extraction from abilities...")

    parser = JSONParser()
    data_mapper = DataMapper()

    test_data = [
        {
            "name": "Rancor",
            "type": "Nemesis",
            "characteristics": {"Brawn": 6, "Agility": 2, "Intellect": 1, "Cunning": 3, "Willpower": 3, "Presence": 2},
            "derived": {"soak": 12, "wounds": 42, "strain": 18},
            "skills": {"Brawl": 3},
            "abilities": ["Silhouette 3", "Sweep Attack"],
            "tags": ["creature", "book:aaa"]
        },
        {
            "name": "Krayt Dragon",
            "type": "Nemesis",
            "characteristics": {"Brawn": 7, "Agility": 2, "Intellect": 1, "Cunning": 2, "Willpower": 3, "Presence": 2},
            "derived": {"soak": 14, "wounds": 60, "strain": 20},
            "skills": {"Brawl": 4},
            "abilities": ["Silhouette: 4", "Terrifying"],  # With colon format
            "tags": ["creature", "book:eote"]
        },
        {
            "name": "Stormtrooper",
            "type": "Minion",
            "characteristics": {"Brawn": 2, "Agility": 2, "Intellect": 2, "Cunning": 2, "Willpower": 2, "Presence": 2},
            "derived": {"soak": 5, "wounds": 5},
            "skills": {},
            "abilities": [],  # No silhouette ability - should default to 1
            "tags": ["imperial", "book:eote"]
        },
        {
            "name": "AT-ST Pilot",
            "type": "Rival",
            "characteristics": {"Brawn": 2, "Agility": 3, "Intellect": 2, "Cunning": 2, "Willpower": 2, "Presence": 2},
            "derived": {"soak": 3, "wounds": 12},
            "skills": {"Gunnery": 2},
            "abilities": [{"name": "Silhouette 2", "description": "This creature is larger than normal."}],  # Dict format
            "tags": ["imperial", "book:aor"]
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_file = f.name

    try:
        records = parser.parse_json_file(temp_file)
        assert len(records) == 4, f"Expected 4 records, got {len(records)}"

        # Test Rancor - Silhouette 3
        rancor = next(r for r in records if r['name'] == 'Rancor')
        converted_rancor = data_mapper.convert_oggdude_to_realm_vtt(rancor, 'test_campaign', 'Test')
        assert converted_rancor['data']['silhouette'] == 3, \
            f"Expected silhouette 3 for Rancor, got {converted_rancor['data']['silhouette']}"

        # Test Krayt Dragon - Silhouette: 4 (colon format)
        krayt = next(r for r in records if r['name'] == 'Krayt Dragon')
        converted_krayt = data_mapper.convert_oggdude_to_realm_vtt(krayt, 'test_campaign', 'Test')
        assert converted_krayt['data']['silhouette'] == 4, \
            f"Expected silhouette 4 for Krayt Dragon, got {converted_krayt['data']['silhouette']}"

        # Test Stormtrooper - No silhouette, should default to 1
        stormtrooper = next(r for r in records if r['name'] == 'Stormtrooper')
        converted_stormtrooper = data_mapper.convert_oggdude_to_realm_vtt(stormtrooper, 'test_campaign', 'Test')
        assert converted_stormtrooper['data']['silhouette'] == 1, \
            f"Expected silhouette 1 (default) for Stormtrooper, got {converted_stormtrooper['data']['silhouette']}"

        # Test AT-ST Pilot - Dict format ability
        pilot = next(r for r in records if r['name'] == 'AT-ST Pilot')
        converted_pilot = data_mapper.convert_oggdude_to_realm_vtt(pilot, 'test_campaign', 'Test')
        assert converted_pilot['data']['silhouette'] == 2, \
            f"Expected silhouette 2 for AT-ST Pilot, got {converted_pilot['data']['silhouette']}"

        print("✓ Silhouette extraction test passed")
        return True

    finally:
        os.unlink(temp_file)


def main():
    """Run all adversary species and sources tests"""
    print("Running adversary species and sources tests")
    print("=" * 50)

    tests = [
        test_species_extraction_from_tags,
        test_species_from_direct_field,
        test_adversaries_sources_filtering,
        test_adventure_tag_filtering,
        test_real_escapemosshuuta_file,
        test_silhouette_extraction,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")

    print("=" * 50)
    print(f"Adversary species and sources tests passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
