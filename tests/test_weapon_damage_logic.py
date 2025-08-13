#!/usr/bin/env python3
"""
Test weapon damage logic and noAddBrawn field functionality
"""

import sys
import os
import xml.etree.ElementTree as ET

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_lightsaber_weapon_logic():
    """Test lightsaber weapon damage and noAddBrawn logic"""
    try:
        parser = XMLParser()
        
        # Create lightsaber XML from provided example
        lightsaber_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Weapons>
            <Weapon>
                <Key>LTSABER</Key>
                <Name>Lightsaber</Name>
                <Description>[H3]Lightsaber[h3]

The weapon of the Jedi is rare in [B]Edge of the Empire[b]. The rogues and scoundrels of the galaxy do not travel in the same circles as these revered knights. When such an individual is encountered, tainted souls may want to steer clear, for their weapons are made of pure energy and can slice through anything—from limbs to blast doors.

[P]Lightsabers normally require the Lightsaber skill to wield. However, since that skill is not an option for the Player Characters in this book, players must use a lightsaber untrained (selecting either Brawn or Agility as the base characteristic). This is deliberate, because there are few people in the galaxy who properly know how to fight with a lightsaber. However, if the GM feels it is warranted, he can create the Lightsaber skill as a custom skill for his players. Lightsabers cannot be sundered.</Description>
                <Custom>DescOnly</Custom>
                <SkillKey>LTSABER</SkillKey>
                <Damage>10</Damage>
                <DamageAdd>0</DamageAdd>
                <Crit>1</Crit>
                <RangeValue>wrEngaged</RangeValue>
                <Encumbrance>1</Encumbrance>
                <HP>0</HP>
                <Price>10000</Price>
                <Rarity>10</Rarity>
                <Restricted>true</Restricted>
                <Type>Lightsaber</Type>
                <Categories>
                    <Category>Lightsaber</Category>
                </Categories>
                <Qualities>
                    <Quality>
                        <Key>BREACH</Key>
                        <Count>1</Count>
                    </Quality>
                    <Quality>
                        <Key>SUNDER</Key>
                    </Quality>
                    <Quality>
                        <Key>VICIOUS</Key>
                        <Count>2</Count>
                    </Quality>
                </Qualities>
            </Weapon>
        </Weapons>'''
        
        root = ET.fromstring(lightsaber_xml)
        
        print("Testing lightsaber weapon logic...")
        weapons = parser._parse_weapons(root)
        
        if not weapons:
            print("  ✗ Lightsaber weapon extraction failed")
            return False
        
        weapon = weapons[0]
        
        # Check the extracted data
        data = weapon.get('data', {})
        
        # Check name
        if weapon.get('name') == 'Lightsaber':
            print("  ✓ Name correctly extracted: Lightsaber")
        else:
            print(f"  ✗ Name extraction failed: {weapon.get('name')}")
            return False
        
        # Check damage (should be 10 since DamageAdd is 0)
        damage = data.get('damage', 0)
        if damage == 10:
            print(f"  ✓ Damage correctly set: {damage} (used Damage field since DamageAdd is 0)")
        else:
            print(f"  ✗ Damage should be 10, got {damage}")
            return False
        
        # Check noAddBrawn (should be True since it's a lightsaber with no DamageAdd)
        no_add_brawn = data.get('noAddBrawn', False)
        if no_add_brawn is True:
            print(f"  ✓ noAddBrawn correctly set: {no_add_brawn} (lightsaber with no DamageAdd)")
        else:
            print(f"  ✗ noAddBrawn should be True, got {no_add_brawn}")
            return False
        
        print("  ✓ All lightsaber weapon tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_truncheon_weapon_logic():
    """Test truncheon weapon damage and noAddBrawn logic"""
    try:
        parser = XMLParser()
        
        # Create truncheon XML from provided example
        truncheon_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Weapons>
            <Weapon>
                <Key>TRUNCH</Key>
                <Name>Truncheon</Name>
                <Description>[H3]Truncheon[h3]

Truncheons may be made of metal, wood, bone or other materials, but all fulfill the same basic function—bruising flesh, breaking bones, and cracking skulls. Police forces around the galaxy use truncheons to intimidate and control protesters or petty thieves. Enlightened areas prefer this to lethal force.</Description>
                <Custom>DescOnly</Custom>
                <SkillKey>MELEE</SkillKey>
                <Damage>0</Damage>
                <DamageAdd>2</DamageAdd>
                <Crit>5</Crit>
                <RangeValue>wrEngaged</RangeValue>
                <Encumbrance>2</Encumbrance>
                <HP>0</HP>
                <Price>15</Price>
                <Rarity>1</Rarity>
                <Type>Melee</Type>
                <Categories>
                    <Category>Bludgeoning Melee</Category>
                </Categories>
                <Qualities>
                    <Quality>
                        <Key>DISORIENT</Key>
                        <Count>2</Count>
                    </Quality>
                </Qualities>
            </Weapon>
        </Weapons>'''
        
        root = ET.fromstring(truncheon_xml)
        
        print("Testing truncheon weapon logic...")
        weapons = parser._parse_weapons(root)
        
        if not weapons:
            print("  ✗ Truncheon weapon extraction failed")
            return False
        
        weapon = weapons[0]
        
        # Check the extracted data
        data = weapon.get('data', {})
        
        # Check name
        if weapon.get('name') == 'Truncheon':
            print("  ✓ Name correctly extracted: Truncheon")
        else:
            print(f"  ✗ Name extraction failed: {weapon.get('name')}")
            return False
        
        # Check damage (should be 2 since DamageAdd is 2)
        damage = data.get('damage', 0)
        if damage == 2:
            print(f"  ✓ Damage correctly set: {damage} (used DamageAdd field since it's set)")
        else:
            print(f"  ✗ Damage should be 2, got {damage}")
            return False
        
        # Check noAddBrawn (should be False since it has DamageAdd set)
        no_add_brawn = data.get('noAddBrawn', False)
        if no_add_brawn is False:
            print(f"  ✓ noAddBrawn correctly set: {no_add_brawn} (melee weapon with DamageAdd)")
        else:
            print(f"  ✗ noAddBrawn should be False, got {no_add_brawn}")
            return False
        
        print("  ✓ All truncheon weapon tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ranged_weapon_logic():
    """Test ranged weapon damage logic (should not have noAddBrawn)"""
    try:
        parser = XMLParser()
        
        # Create ranged weapon XML
        blaster_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Weapons>
            <Weapon>
                <Key>BLASTPIST</Key>
                <Name>Blaster Pistol</Name>
                <Description>Standard blaster pistol.</Description>
                <SkillKey>RANGLT</SkillKey>
                <Damage>6</Damage>
                <DamageAdd>0</DamageAdd>
                <Crit>3</Crit>
                <RangeValue>wrMedium</RangeValue>
                <Encumbrance>1</Encumbrance>
                <HP>2</HP>
                <Price>400</Price>
                <Rarity>4</Rarity>
                <Type>Energy Weapon</Type>
            </Weapon>
        </Weapons>'''
        
        root = ET.fromstring(blaster_xml)
        
        print("Testing ranged weapon logic...")
        weapons = parser._parse_weapons(root)
        
        if not weapons:
            print("  ✗ Ranged weapon extraction failed")
            return False
        
        weapon = weapons[0]
        
        # Check the extracted data
        data = weapon.get('data', {})
        
        # Check name
        if weapon.get('name') == 'Blaster Pistol':
            print("  ✓ Name correctly extracted: Blaster Pistol")
        else:
            print(f"  ✗ Name extraction failed: {weapon.get('name')}")
            return False
        
        # Check damage (should be 6 since DamageAdd is 0)
        damage = data.get('damage', 0)
        if damage == 6:
            print(f"  ✓ Damage correctly set: {damage} (used Damage field since DamageAdd is 0)")
        else:
            print(f"  ✗ Damage should be 6, got {damage}")
            return False
        
        # Check noAddBrawn (should be False since it's not a melee weapon)
        no_add_brawn = data.get('noAddBrawn', False)
        if no_add_brawn is False:
            print(f"  ✓ noAddBrawn correctly set: {no_add_brawn} (not a melee weapon)")
        else:
            print(f"  ✗ noAddBrawn should be False, got {no_add_brawn}")
            return False
        
        print("  ✓ All ranged weapon tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running weapon damage logic tests...\n")
    
    # Test lightsaber
    lightsaber_result = test_lightsaber_weapon_logic()
    
    print()
    
    # Test truncheon
    truncheon_result = test_truncheon_weapon_logic()
    
    print()
    
    # Test ranged weapon
    ranged_result = test_ranged_weapon_logic()
    
    if lightsaber_result and truncheon_result and ranged_result:
        print("\n🎉 All weapon damage logic tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some weapon damage logic tests failed!")
        sys.exit(1)