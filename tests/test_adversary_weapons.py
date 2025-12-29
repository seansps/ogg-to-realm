#!/usr/bin/env python3
"""
Test adversary weapon parsing from JSON format to Realm VTT format.
Tests the _create_adhoc_weapon method in data_mapper.py.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_mapper import DataMapper


def test_arc_welder_melee_weapon():
    """Test Arc welder - melee weapon with Stun Damage quality

    Arc welder on Astromech Droid (Brawn 1):
    - Adversaries JSON damage: 3 (includes Brawn)
    - Realm VTT damage: 2 (3 - 1 Brawn, since Realm adds Brawn during rolls)
    """
    mapper = DataMapper()

    weapon_data = {
        "name": "Arc welder",
        "skill": "Melee",
        "damage": 3,
        "critical": None,
        "range": "Engaged",
        "qualities": ["Stun Damage"]
    }

    # Astromech Droid has Brawn 1
    brawn = 1
    result = mapper._create_adhoc_weapon(weapon_data, brawn)

    # Check basic structure
    assert result['name'] == 'Arc welder', f"Expected name 'Arc welder', got {result['name']}"
    assert result['recordType'] == 'items', f"Expected recordType 'items', got {result['recordType']}"
    assert result['identified'] == True, "Expected identified True"
    assert '_id' in result, "Expected _id field"

    # Check data fields
    data = result.get('data', {})
    assert data.get('type') == 'melee weapon', f"Expected type 'melee weapon', got {data.get('type')}"
    assert data.get('skill') == 'Melee', f"Expected skill 'Melee', got {data.get('skill')}"
    assert data.get('weaponSkill') == 'Melee', f"Expected weaponSkill 'Melee', got {data.get('weaponSkill')}"
    # Damage should be 2 (3 - 1 Brawn) since Realm VTT adds Brawn during rolls
    assert data.get('damage') == 2, f"Expected damage 2 (3 - 1 Brawn), got {data.get('damage')}"
    assert data.get('crit') == 0, f"Expected crit 0 (null critical), got {data.get('crit')}"
    assert data.get('range') == 'Engaged', f"Expected range 'Engaged', got {data.get('range')}"
    assert data.get('carried') == 'equipped', f"Expected carried 'equipped', got {data.get('carried')}"
    assert data.get('count') == 1, f"Expected count 1, got {data.get('count')}"

    # Check Stun Damage quality - Realm VTT uses 'stun-damage' in special and 'stunDamage' as field
    assert data.get('stunDamage') == True, f"Expected stunDamage True, got {data.get('stunDamage')}"
    assert 'special' in data, "Expected 'special' list in data"
    assert 'stun-damage' in data['special'], f"Expected 'stun-damage' in special list, got {data['special']}"

    print("PASSED: test_arc_welder_melee_weapon")


def test_built_in_heavy_blasters():
    """Test Built-in heavy blasters - ranged weapon with multiple qualities"""
    mapper = DataMapper()

    weapon_data = {
        "name": "Built-in heavy blasters",
        "skill": "Gunnery",
        "damage": 12,
        "critical": 2,
        "range": "Long",
        "notes": "",
        "qualities": ["Pierce 4", "Linked 2", "Vicious 1"]
    }

    result = mapper._create_adhoc_weapon(weapon_data)

    # Check basic structure
    assert result['name'] == 'Built-in heavy blasters', f"Expected name 'Built-in heavy blasters', got {result['name']}"
    assert result['recordType'] == 'items', f"Expected recordType 'items', got {result['recordType']}"

    # Check data fields
    data = result.get('data', {})
    assert data.get('type') == 'ranged weapon', f"Expected type 'ranged weapon', got {data.get('type')}"
    assert data.get('skill') == 'Gunnery', f"Expected skill 'Gunnery', got {data.get('skill')}"
    assert data.get('weaponSkill') == 'Gunnery', f"Expected weaponSkill 'Gunnery', got {data.get('weaponSkill')}"
    assert data.get('damage') == 12, f"Expected damage 12, got {data.get('damage')}"
    assert data.get('crit') == 2, f"Expected crit 2, got {data.get('crit')}"
    assert data.get('range') == 'Long', f"Expected range 'Long', got {data.get('range')}"
    assert data.get('carried') == 'equipped', f"Expected carried 'equipped', got {data.get('carried')}"
    assert data.get('count') == 1, f"Expected count 1, got {data.get('count')}"

    # Check qualities with ratings
    assert data.get('pierce') == 4, f"Expected pierce 4, got {data.get('pierce')}"
    assert data.get('linked') == 2, f"Expected linked 2, got {data.get('linked')}"
    assert data.get('vicious') == 1, f"Expected vicious 1, got {data.get('vicious')}"

    # Check special list
    assert 'special' in data, "Expected 'special' list in data"
    special = data['special']
    assert 'pierce' in special, f"Expected 'pierce' in special list, got {special}"
    assert 'linked' in special, f"Expected 'linked' in special list, got {special}"
    assert 'vicious' in special, f"Expected 'vicious' in special list, got {special}"

    print("PASSED: test_built_in_heavy_blasters")


def test_brawl_weapon():
    """Test a Brawl skill weapon becomes melee weapon type"""
    mapper = DataMapper()

    weapon_data = {
        "name": "Claws",
        "skill": "Brawl",
        "damage": 5,
        "critical": 3,
        "range": "Engaged",
        "qualities": ["Vicious 2"]
    }

    # Creature with Brawn 2
    brawn = 2
    result = mapper._create_adhoc_weapon(weapon_data, brawn)
    data = result.get('data', {})

    assert data.get('type') == 'melee weapon', f"Expected type 'melee weapon' for Brawl, got {data.get('type')}"
    assert data.get('skill') == 'Brawl', f"Expected skill 'Brawl', got {data.get('skill')}"
    # Damage should be 3 (5 - 2 Brawn)
    assert data.get('damage') == 3, f"Expected damage 3 (5 - 2 Brawn), got {data.get('damage')}"
    assert data.get('vicious') == 2, f"Expected vicious 2, got {data.get('vicious')}"

    print("PASSED: test_brawl_weapon")


def test_captive_rancor_claws():
    """Test Captive Rancor's Massive rending claws - high brawn creature

    Captive Rancor has Brawn 6:
    - Adversaries JSON damage: 15 (includes Brawn)
    - Realm VTT damage: 9 (15 - 6 Brawn, since Realm adds Brawn during rolls)
    """
    mapper = DataMapper()

    weapon_data = {
        "name": "Massive rending claws",
        "skill": "Brawl",
        "damage": 15,
        "critical": 3,
        "range": "Engaged",
        "qualities": ["Breach 1", "Knockdown", "Vicious 3"]
    }

    # Captive Rancor has Brawn 6
    brawn = 6
    result = mapper._create_adhoc_weapon(weapon_data, brawn)
    data = result.get('data', {})

    assert data.get('type') == 'melee weapon', f"Expected type 'melee weapon' for Brawl, got {data.get('type')}"
    assert data.get('skill') == 'Brawl', f"Expected skill 'Brawl', got {data.get('skill')}"
    # Damage should be 9 (15 - 6 Brawn)
    assert data.get('damage') == 9, f"Expected damage 9 (15 - 6 Brawn), got {data.get('damage')}"
    assert data.get('crit') == 3, f"Expected crit 3, got {data.get('crit')}"
    assert data.get('breach') == 1, f"Expected breach 1, got {data.get('breach')}"
    assert data.get('knockdown') == True, f"Expected knockdown True, got {data.get('knockdown')}"
    assert data.get('vicious') == 3, f"Expected vicious 3, got {data.get('vicious')}"

    print("PASSED: test_captive_rancor_claws")


def test_lightsaber_weapon():
    """Test Lightsaber skill weapon becomes melee weapon type

    Lightsaber base damage is 6, but when wielded by a character with Brawn 4,
    the total shown in Adversaries JSON would be 10. Realm VTT expects base 6.
    """
    mapper = DataMapper()

    weapon_data = {
        "name": "Lightsaber",
        "skill": "Lightsaber",
        "damage": 10,
        "critical": 1,
        "range": "Engaged",
        "qualities": ["Breach 1", "Sunder"]
    }

    # Character with Brawn 4
    brawn = 4
    result = mapper._create_adhoc_weapon(weapon_data, brawn)
    data = result.get('data', {})

    assert data.get('type') == 'melee weapon', f"Expected type 'melee weapon' for Lightsaber, got {data.get('type')}"
    assert data.get('skill') == 'Lightsaber', f"Expected skill 'Lightsaber', got {data.get('skill')}"
    # Damage should be 6 (10 - 4 Brawn)
    assert data.get('damage') == 6, f"Expected damage 6 (10 - 4 Brawn), got {data.get('damage')}"
    assert data.get('breach') == 1, f"Expected breach 1, got {data.get('breach')}"
    assert data.get('sunder') == True, f"Expected sunder True, got {data.get('sunder')}"
    # Check special list uses hyphenated names
    assert 'breach' in data.get('special', []), f"Expected 'breach' in special list"
    assert 'sunder' in data.get('special', []), f"Expected 'sunder' in special list"

    print("PASSED: test_lightsaber_weapon")


def test_ranged_light_weapon():
    """Test Ranged: Light skill (colon format from Adversaries JSON) becomes ranged weapon type with correct skill

    Ranged weapons should NOT have brawn deducted from damage.
    """
    mapper = DataMapper()

    weapon_data = {
        "name": "Hold-out blaster",
        "skill": "Ranged: Light",  # Note: Adversaries JSON uses colon format
        "damage": 5,
        "critical": 4,
        "range": "Short",
        "qualities": ["Stun setting"]
    }

    # Even with brawn provided, ranged weapons should keep full damage
    brawn = 3
    result = mapper._create_adhoc_weapon(weapon_data, brawn)
    data = result.get('data', {})

    assert data.get('type') == 'ranged weapon', f"Expected type 'ranged weapon', got {data.get('type')}"
    # Should be normalized to "Ranged (Light)" for Realm VTT
    assert data.get('skill') == 'Ranged (Light)', f"Expected skill 'Ranged (Light)', got {data.get('skill')}"
    assert data.get('weaponSkill') == 'Ranged (Light)', f"Expected weaponSkill 'Ranged (Light)', got {data.get('weaponSkill')}"
    # Ranged weapons keep full damage (no brawn deduction)
    assert data.get('damage') == 5, f"Expected damage 5 (no brawn deduction for ranged), got {data.get('damage')}"
    assert data.get('stunSetting') == True, f"Expected stunSetting True, got {data.get('stunSetting')}"
    assert 'stun-setting' in data.get('special', []), f"Expected 'stun-setting' in special list"

    print("PASSED: test_ranged_light_weapon")


def test_ranged_heavy_weapon():
    """Test Ranged: Heavy skill (colon format from Adversaries JSON) becomes ranged weapon type with correct skill"""
    mapper = DataMapper()

    weapon_data = {
        "name": "Blaster Rifle",
        "skill": "Ranged: Heavy",  # Note: Adversaries JSON uses colon format
        "damage": 9,
        "critical": 3,
        "range": "Long",
        "qualities": ["Stun setting"]
    }

    result = mapper._create_adhoc_weapon(weapon_data)
    data = result.get('data', {})

    assert data.get('type') == 'ranged weapon', f"Expected type 'ranged weapon', got {data.get('type')}"
    # Should be normalized to "Ranged (Heavy)" for Realm VTT
    assert data.get('skill') == 'Ranged (Heavy)', f"Expected skill 'Ranged (Heavy)', got {data.get('skill')}"
    assert data.get('weaponSkill') == 'Ranged (Heavy)', f"Expected weaponSkill 'Ranged (Heavy)', got {data.get('weaponSkill')}"

    print("PASSED: test_ranged_heavy_weapon")


def test_weapon_with_no_qualities():
    """Test weapon with no qualities array"""
    mapper = DataMapper()

    weapon_data = {
        "name": "Simple blaster",
        "skill": "Ranged (Heavy)",
        "damage": 8,
        "critical": 3,
        "range": "Medium"
    }

    result = mapper._create_adhoc_weapon(weapon_data)
    data = result.get('data', {})

    assert data.get('type') == 'ranged weapon', f"Expected type 'ranged weapon', got {data.get('type')}"
    assert data.get('damage') == 8, f"Expected damage 8, got {data.get('damage')}"
    assert data.get('crit') == 3, f"Expected crit 3, got {data.get('crit')}"
    # special should not be present if no qualities
    assert 'special' not in data or len(data.get('special', [])) == 0, "Expected no special qualities"

    print("PASSED: test_weapon_with_no_qualities")


def test_weapon_with_plus_damage():
    """Test weapon that uses plus-damage instead of damage

    plus-damage weapons already represent base damage (not including brawn),
    so we still deduct brawn to get the correct Realm VTT value.
    Example: Vibro-knife with plus-damage 2 wielded by Brawn 3 character
    would show as damage 2 in JSON, and becomes -1 (clamped to 0) in Realm VTT.
    This test uses brawn 0 to verify plus-damage parsing works.
    """
    mapper = DataMapper()

    weapon_data = {
        "name": "Vibro-knife",
        "skill": "Melee",
        "plus-damage": 2,
        "critical": 2,
        "range": "Engaged",
        "qualities": ["Pierce 2", "Vicious 1"]
    }

    # With brawn 0, damage stays at 2
    brawn = 0
    result = mapper._create_adhoc_weapon(weapon_data, brawn)
    data = result.get('data', {})

    assert data.get('damage') == 2, f"Expected damage 2 (from plus-damage, no brawn), got {data.get('damage')}"
    assert data.get('pierce') == 2, f"Expected pierce 2, got {data.get('pierce')}"
    assert data.get('vicious') == 1, f"Expected vicious 1, got {data.get('vicious')}"

    print("PASSED: test_weapon_with_plus_damage")


def test_convert_adversary_inventory_with_dict_weapon():
    """Test the full _convert_adversary_inventory flow with a dict weapon

    Simulates Astromech Droid with Brawn 1.
    Arc welder damage in JSON: 3, expected Realm VTT damage: 2 (3 - 1 Brawn)
    """
    mapper = DataMapper()

    weapons = [
        {
            "name": "Arc welder",
            "skill": "Melee",
            "damage": 3,
            "critical": None,
            "range": "Engaged",
            "qualities": ["Stun Damage"]
        }
    ]
    gear = []

    # Astromech Droid has Brawn 1
    brawn = 1
    inventory = mapper._convert_adversary_inventory(weapons, gear, brawn)

    assert len(inventory) >= 1, f"Expected at least 1 item in inventory, got {len(inventory)}"

    # Find the Arc welder in the inventory
    arc_welder = None
    for item in inventory:
        if item.get('name') == 'Arc welder':
            arc_welder = item
            break

    assert arc_welder is not None, "Arc welder not found in inventory"

    data = arc_welder.get('data', {})
    assert data.get('type') == 'melee weapon', f"Expected type 'melee weapon', got {data.get('type')}"
    # Damage should be 2 (3 - 1 Brawn)
    assert data.get('damage') == 2, f"Expected damage 2 (3 - 1 Brawn), got {data.get('damage')}"
    assert data.get('skill') == 'Melee', f"Expected skill 'Melee', got {data.get('skill')}"
    assert data.get('stunDamage') == True, f"Expected stunDamage True, got {data.get('stunDamage')}"
    assert data.get('carried') == 'equipped', f"Expected carried 'equipped', got {data.get('carried')}"
    assert 'stun-damage' in data.get('special', []), f"Expected 'stun-damage' in special list"

    print("PASSED: test_convert_adversary_inventory_with_dict_weapon")


def test_convert_adversary_inventory_with_heavy_blasters():
    """Test the full _convert_adversary_inventory flow with heavy blasters

    Ranged weapons (Gunnery) should NOT have brawn deducted.
    """
    mapper = DataMapper()

    weapons = [
        {
            "name": "Built-in heavy blasters",
            "skill": "Gunnery",
            "damage": 12,
            "critical": 2,
            "range": "Long",
            "notes": "",
            "qualities": ["Pierce 4", "Linked 2", "Vicious 1"]
        }
    ]
    gear = []

    # Even with brawn provided, ranged weapons should keep full damage
    brawn = 4
    inventory = mapper._convert_adversary_inventory(weapons, gear, brawn)

    # Find the heavy blasters in the inventory
    heavy_blasters = None
    for item in inventory:
        if item.get('name') == 'Built-in heavy blasters':
            heavy_blasters = item
            break

    assert heavy_blasters is not None, "Built-in heavy blasters not found in inventory"

    data = heavy_blasters.get('data', {})
    assert data.get('type') == 'ranged weapon', f"Expected type 'ranged weapon', got {data.get('type')}"
    # Ranged weapons keep full damage (no brawn deduction)
    assert data.get('damage') == 12, f"Expected damage 12 (no brawn deduction for ranged), got {data.get('damage')}"
    assert data.get('crit') == 2, f"Expected crit 2, got {data.get('crit')}"
    assert data.get('pierce') == 4, f"Expected pierce 4, got {data.get('pierce')}"
    assert data.get('linked') == 2, f"Expected linked 2, got {data.get('linked')}"
    assert data.get('vicious') == 1, f"Expected vicious 1, got {data.get('vicious')}"
    # Check special list
    special = data.get('special', [])
    assert 'pierce' in special, f"Expected 'pierce' in special list"
    assert 'linked' in special, f"Expected 'linked' in special list"
    assert 'vicious' in special, f"Expected 'vicious' in special list"

    print("PASSED: test_convert_adversary_inventory_with_heavy_blasters")


def run_tests():
    """Run all tests"""
    test_arc_welder_melee_weapon()
    test_built_in_heavy_blasters()
    test_brawl_weapon()
    test_captive_rancor_claws()
    test_lightsaber_weapon()
    test_ranged_light_weapon()
    test_ranged_heavy_weapon()
    test_weapon_with_no_qualities()
    test_weapon_with_plus_damage()
    test_convert_adversary_inventory_with_dict_weapon()
    test_convert_adversary_inventory_with_heavy_blasters()

    print("\n✅ All adversary weapon tests passed!")


if __name__ == '__main__':
    run_tests()
