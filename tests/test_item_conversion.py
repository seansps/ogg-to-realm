#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import xml.etree.ElementTree as ET

def test_melee_weapon_conversion():
    """Test melee weapon conversion logic"""
    try:
        from src.xml_parser import XMLParser
        from src.data_mapper import DataMapper
        
        print("Testing melee weapon conversion...")
        
        # Create test melee weapon XML
        weapon_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Weapons>
            <Weapon>
                <Name>Vibrosword</Name>
                <Description>A deadly melee weapon.</Description>
                <Type>Melee</Type>
                <SkillKey>MELEE</SkillKey>
                <Damage>4</Damage>
                <Crit>3</Crit>
                <RangeValue>wrEngaged</RangeValue>
                <Qualities>
                    <Quality>
                        <Key>VICIOUS</Key>
                        <Count>2</Count>
                    </Quality>
                </Qualities>
                <Sources>
                    <Source>Edge of the Empire Core Rulebook</Source>
                </Sources>
            </Weapon>
        </Weapons>'''
        
        # Parse the weapon
        parser = XMLParser()
        root = ET.fromstring(weapon_xml)
        weapons = parser._parse_weapons(root)
        
        if not weapons:
            print("  ✗ No weapons parsed")
            return False
        
        weapon = weapons[0]
        print(f"Extracted melee weapon:")
        print(f"  Name: {weapon['name']}")
        print(f"  Type: {weapon['data']['type']}")
        print(f"  SkillKey: {weapon['data']['weaponSkill']}")
        
        # Convert to Realm VTT format
        mapper = DataMapper()
        converted = mapper._convert_weapon_data(weapon['data'], weapon)
        
        print(f"\nConverted melee weapon:")
        print(f"  Name: {converted['name']}")
        print(f"  Type: {converted['type']}")
        print(f"  Subtype: {converted.get('subtype', 'None')}")
        print(f"  WeaponSkill: {converted['weaponSkill']}")
        print(f"  Range: {converted['range']}")
        
        # Test weapon type determination for melee
        if converted['type'] == 'melee weapon':
            print(f"  ✓ Weapon type correctly set to 'melee weapon' for MELEE SkillKey")
        else:
            print(f"  ✗ Weapon type should be 'melee weapon' for MELEE SkillKey, got '{converted['type']}'")
            return False
        
        # Test subtype for melee weapon
        if converted.get('subtype') == 'Melee':
            print(f"  ✓ Subtype correctly set to 'Melee' for melee weapon")
        else:
            print(f"  ✗ Subtype should be 'Melee' for melee weapon, got '{converted.get('subtype', 'None')}'")
            return False
        
        # Test weaponSkill mapping
        if converted['weaponSkill'] == 'Melee':
            print(f"  ✓ WeaponSkill correctly mapped to 'Melee'")
        else:
            print(f"  ✗ WeaponSkill should be 'Melee', got '{converted['weaponSkill']}'")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Melee weapon conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_weapon_conversion():
    """Test weapon conversion logic"""
    try:
        from src.xml_parser import XMLParser
        from src.data_mapper import DataMapper
        
        print("Testing weapon conversion...")
        
        # Create test weapon XML
        weapon_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Weapons>
            <Weapon>
                <Name>Auto-Blaster</Name>
                <Description>Auto blasters are rapid-fire variants of common blaster cannons.</Description>
                <Type>Vehicle</Type>
                <SkillKey>GUNN</SkillKey>
                <Damage>3</Damage>
                <Crit>5</Crit>
                <RangeValue>wrClose</RangeValue>
                <Qualities>
                    <Quality>
                        <Key>AUTOFIRE</Key>
                        <Count>1</Count>
                    </Quality>
                </Qualities>
                <Sources>
                    <Source>Edge of the Empire Core Rulebook</Source>
                </Sources>
            </Weapon>
        </Weapons>'''
        
        # Parse the weapon
        parser = XMLParser()
        root = ET.fromstring(weapon_xml)
        weapons = parser._parse_weapons(root)
        
        if not weapons:
            print("  ✗ No weapons parsed")
            return False
        
        weapon = weapons[0]
        print(f"Extracted weapon:")
        print(f"  Name: {weapon['name']}")
        print(f"  Sources: {weapon['sources']}")
        print(f"  Type: {weapon['data']['type']}")
        print(f"  SkillKey: {weapon['data']['weaponSkill']}")
        print(f"  Qualities: {weapon['data']['special']}")
        
        # Convert to Realm VTT format
        mapper = DataMapper()
        converted = mapper._convert_weapon_data(weapon['data'], weapon)
        
        print(f"\nConverted weapon:")
        print(f"  Name: {converted['name']}")
        print(f"  Type: {converted['type']}")
        print(f"  Subtype: {converted.get('subtype', 'None')}")
        print(f"  Range: {converted['range']}")
        print(f"  Special: {converted['special']}")
        print(f"  WeaponSkill: {converted['weaponSkill']}")
        print(f"  Auto-fire count: {converted.get('auto-fire', 'None')}")
        
        # Test weapon type determination
        if converted['type'] == 'ranged weapon':
            print(f"  ✓ Weapon type correctly set to 'ranged weapon' for Vehicle type")
        else:
            print(f"  ✗ Weapon type should be 'ranged weapon' for Vehicle type, got '{converted['type']}'")
            return False
        
        # Test subtype for vehicle weapon
        if converted.get('subtype') == 'Vehicle Weapon':
            print(f"  ✓ Subtype correctly set to 'Vehicle Weapon' for Vehicle type")
        else:
            print(f"  ✗ Subtype should be 'Vehicle Weapon' for Vehicle type, got '{converted.get('subtype', 'None')}'")
            return False
        
        # Test weaponSkill mapping
        if converted['weaponSkill'] == 'Gunnery':
            print(f"  ✓ WeaponSkill correctly mapped to 'Gunnery'")
        else:
            print(f"  ✗ WeaponSkill should be 'Gunnery', got '{converted['weaponSkill']}'")
            return False
        
        # Test auto-fire count
        if converted.get('auto-fire') == 1:
            print(f"  ✓ Auto-fire count field set correctly: {converted['auto-fire']}")
        else:
            print(f"  ✗ Auto-fire count should be 1, got {converted.get('auto-fire', 'None')}")
            return False
        
        # Test that no 'qualities' field exists in the final data
        if 'qualities' not in converted:
            print(f"  ✓ No 'qualities' field in final data (correct)")
        else:
            print(f"  ✗ 'qualities' field found in final data (incorrect)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Weapon conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_category_filtering():
    """Test that category is correctly set for Edge of the Empire Core Rulebook"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing category filtering...")
        
        # Create test weapon XML with Edge of the Empire Core Rulebook source
        weapon_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Weapons>
            <Weapon>
                <Name>Test Blaster</Name>
                <Description>Test weapon description</Description>
                <Type>Energy Weapon</Type>
                <SkillKey>RANGLT</SkillKey>
                <Damage>5</Damage>
                <Crit>5</Crit>
                <RangeValue>wrShort</RangeValue>
                <Sources>
                    <Source>Edge of the Empire Core Rulebook</Source>
                </Sources>
            </Weapon>
        </Weapons>'''
        
        # Parse the weapon
        parser = XMLParser()
        root = ET.fromstring(weapon_xml)
        weapons = parser._parse_weapons(root)
        
        if not weapons:
            print("  ✗ No weapons parsed")
            return False
        
        weapon = weapons[0]
        print(f"Extracted weapon:")
        print(f"  Name: {weapon['name']}")
        print(f"  Sources: {weapon['sources']}")
        print(f"  Category: {weapon.get('category', 'None')}")
        
        # Test filtering with Edge of the Empire Core Rulebook selected
        selected_sources = ['book:eote']  # This is the key for Edge of the Empire Core Rulebook
        filtered_weapons = parser.filter_by_sources(weapons, selected_sources)
        
        if not filtered_weapons:
            print("  ✗ No weapons found after filtering")
            return False
        
        filtered_weapon = filtered_weapons[0]
        print(f"Filtered weapon:")
        print(f"  Name: {filtered_weapon['name']}")
        print(f"  Category: {filtered_weapon.get('category', 'None')}")
        
        # Test that category is correctly set
        if filtered_weapon.get('category') == 'Edge of the Empire Core Rulebook':
            print(f"  ✓ Category correctly set to 'Edge of the Empire Core Rulebook'")
        else:
            print(f"  ✗ Category should be 'Edge of the Empire Core Rulebook', got '{filtered_weapon.get('category', 'None')}'")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Category filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gear_conversion():
    """Test gear conversion logic"""
    try:
        from src.xml_parser import XMLParser
        from src.data_mapper import DataMapper
        
        print("Testing gear conversion...")
        
        # Create test gear XML with correct structure
        gear_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Gears xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <Gear>
                <Key>TESTGEAR</Key>
                <Name>Test Gear</Name>
                <Description>Test gear description</Description>
                <Type>general</Type>
                <Encumbrance>1</Encumbrance>
                <Price>100</Price>
                <Rarity>2</Rarity>
                <Restricted>no</Restricted>
                <Consumable>false</Consumable>
                <Sources>
                    <Source>Edge of the Empire Core Rulebook</Source>
                </Sources>
            </Gear>
        </Gears>'''
        
        # Parse the gear
        parser = XMLParser()
        root = ET.fromstring(gear_xml)
        
        # Debug: Check the XML structure
        print(f"  XML root tag: {root.tag}")
        for child in root:
            print(f"  Child tag: {child.tag}")
            for grandchild in child:
                print(f"    Grandchild tag: {grandchild.tag}, text: {grandchild.text}")
        
        gear_list = parser._parse_gear(root)
        
        if not gear_list:
            print("  ✗ No gear parsed")
            return False
        
        gear = gear_list[0]
        print(f"Extracted gear:")
        print(f"  Name: {gear['name']}")
        print(f"  Type: {gear['data']['type']}")
        print(f"  Raw data: {gear['data']}")
        
        # Convert to Realm VTT format
        mapper = DataMapper()
        converted = mapper._convert_gear_data(gear['data'], gear)
        
        print(f"\nConverted gear:")
        print(f"  Name: {gear['name']}")  # Name is in the gear item, not the converted data
        print(f"  Type: {converted['type']}")
        print(f"  Subtype: {converted.get('subtype', 'None')}")
        
        # Test gear type determination
        if converted['type'] == 'general':
            print(f"  ✓ Gear type correctly set to 'general'")
        else:
            print(f"  ✗ Gear type should be 'general', got '{converted['type']}'")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Gear conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_armor_conversion():
    """Test armor conversion logic"""
    try:
        from src.xml_parser import XMLParser
        from src.data_mapper import DataMapper
        
        print("Testing armor conversion...")
        
        # Create test armor XML with correct structure
        armor_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Armors xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <Armor>
                <Key>HC</Key>
                <Name>Heavy Clothing</Name>
                <Description>A good leather jacket, technician's jumpsuit, or thick woolen cloak won't stop much damage, but it's certainly better than nothing.</Description>
                <Encumbrance>1</Encumbrance>
                <Price>50</Price>
                <Rarity>1</Rarity>
                <Restricted>no</Restricted>
                <Soak>1</Soak>
                <Defense>0</Defense>
                <HP>0</HP>
                <Qualities>
                    <Quality>
                        <Key>CORTOSIS</Key>
                        <Count>1</Count>
                    </Quality>
                </Qualities>
                <Sources>
                    <Source>Edge of the Empire Core Rulebook</Source>
                </Sources>
            </Armor>
        </Armors>'''
        
        # Parse the armor
        parser = XMLParser()
        root = ET.fromstring(armor_xml)
        
        # Debug: Check the XML structure
        print(f"  XML root tag: {root.tag}")
        for child in root:
            print(f"  Child tag: {child.tag}")
            for grandchild in child:
                print(f"    Grandchild tag: {grandchild.tag}, text: {grandchild.text}")
        
        armor_list = parser._parse_armor(root)
        
        if not armor_list:
            print("  ✗ No armor parsed")
            return False
        
        armor = armor_list[0]
        print(f"Extracted armor:")
        print(f"  Name: {armor['name']}")
        print(f"  Type: {armor['data']['type']}")
        print(f"  Raw data: {armor['data']}")
        
        # Convert to Realm VTT format
        mapper = DataMapper()
        converted = mapper._convert_armor_data(armor['data'], armor)
        
        print(f"\nConverted armor:")
        print(f"  Name: {armor['name']}")  # Name is in the armor item, not the converted data
        print(f"  Type: {converted['type']}")
        print(f"  Soak: {converted.get('soakBonus', 'None')}")
        print(f"  Defense: {converted.get('defense', 'None')}")
        print(f"  Hardpoints: {converted.get('hardpoints', 'None')}")
        print(f"  Special: {converted.get('special', 'None')}")
        
        # Test armor type determination
        if converted['type'] == 'armor':
            print(f"  ✓ Armor type correctly set to 'armor'")
        else:
            print(f"  ✗ Armor type should be 'armor', got '{converted['type']}'")
            return False
        
        # Test soak bonus mapping
        if converted.get('soakBonus') == 1:
            print(f"  ✓ Soak bonus correctly mapped to 'soakBonus': {converted['soakBonus']}")
        else:
            print(f"  ✗ Soak bonus should be 1, got {converted.get('soakBonus', 'None')}")
            return False
        
        # Test hardpoints mapping
        if converted.get('hardpoints') == 0:
            print(f"  ✓ Hardpoints correctly mapped from HP: {converted['hardpoints']}")
        else:
            print(f"  ✗ Hardpoints should be 0, got {converted.get('hardpoints', 'None')}")
            return False
        
        # Test qualities mapping
        if 'cortosis' in converted.get('special', []):
            print(f"  ✓ Qualities correctly mapped to 'special': {converted['special']}")
        else:
            print(f"  ✗ Qualities should contain 'cortosis', got {converted.get('special', 'None')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Armor conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_item_attachment_conversion():
    """Test item attachment conversion logic"""
    try:
        from src.xml_parser import XMLParser
        from src.data_mapper import DataMapper
        
        print("Testing item attachment conversion...")
        
        # Create test item attachment XML with correct structure
        attachment_xml = '''<?xml version="1.0" encoding="utf-8"?>
        <ItemAttachments>
            <ItemAttachment>
                <Key>AD1SBOOSTTHRUST</Key>
                <Name>(AD-1S) Sublight Boost Thrusters</Name>
                <Description>The craft's engines can be equipped with sublight boosters, which considerably increase their output.</Description>
                <Type>Vehicle</Type>
                <Price>9000</Price>
                <Rarity>7</Rarity>
                <HP>2</HP>
                <AddedMods>
                    <Mod>
                        <Key>SPEEDADD</Key>
                        <Count>1</Count>
                    </Mod>
                    <Mod>
                        <Key>HANDLINGSUB</Key>
                        <Count>1</Count>
                    </Mod>
                </AddedMods>
                <Sources>
                    <Source>Special Modifications</Source>
                </Sources>
            </ItemAttachment>
        </ItemAttachments>'''
        
        # Parse the attachment
        parser = XMLParser()
        root = ET.fromstring(attachment_xml)
        
        # Debug: Check the XML structure
        print(f"  XML root tag: {root.tag}")
        for child in root:
            print(f"  Child tag: {child.tag}")
            for grandchild in child:
                print(f"    Grandchild tag: {grandchild.tag}, text: {grandchild.text}")
        
        attachment_list = parser._parse_item_attachments(root)
        
        if not attachment_list:
            print("  ✗ No attachments parsed")
            return False
        
        attachment = attachment_list[0]
        print(f"Extracted attachment:")
        print(f"  Name: {attachment['name']}")
        print(f"  Type: {attachment['data']['type']}")
        print(f"  Raw data: {attachment['data']}")
        
        # Convert to Realm VTT format
        mapper = DataMapper()
        converted = mapper._convert_attachment_data(attachment['data'], attachment)
        
        print(f"\nConverted attachment:")
        print(f"  Name: {attachment['name']}")
        print(f"  Type: {converted['type']}")
        print(f"  Hardpoints: {converted.get('slotsUsed', 'None')}")
        print(f"  ModificationOptions: {converted.get('modificationOptions', 'None')}")
        
        # Test attachment type determination
        if converted['type'] == 'vehicle attachment':
            print(f"  ✓ Attachment type correctly set to 'vehicle attachment'")
        else:
            print(f"  ✗ Attachment type should be 'vehicle attachment', got '{converted['type']}'")
            return False
        
        # Test hardpoints mapping
        if converted.get('slotsUsed') == 2:
            print(f"  ✓ Hardpoints correctly mapped from HP: {converted['slotsUsed']}")
        else:
            print(f"  ✗ Hardpoints should be 2, got {converted.get('slotsUsed', 'None')}")
            return False
        
        # Test modificationOptions (BaseMods conversion)
        if converted.get('modificationOptions'):
            print(f"  ✓ ModificationOptions correctly extracted: {converted['modificationOptions']}")
        else:
            print(f"  ✗ ModificationOptions should be present")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Item attachment conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_item_descriptors_conversion():
    """Test ItemDescriptors conversion logic"""
    try:
        from src.xml_parser import XMLParser
        from src.data_mapper import DataMapper
        
        print("Testing ItemDescriptors conversion...")
        
        # Create test item attachment XML with BaseMods that should be converted
        attachment_xml = '''<?xml version="1.0" encoding="utf-8"?>
        <ItemAttachments>
            <ItemAttachment>
                <Key>TESTATTACHMENT</Key>
                <Name>Test Attachment</Name>
                <Description>A test attachment for ItemDescriptors conversion.</Description>
                <Type>Vehicle</Type>
                <Price>5000</Price>
                <Rarity>5</Rarity>
                <HP>1</HP>
                <AddedMods>
                    <Mod>
                        <Key>SPEEDADD</Key>
                        <Count>2</Count>
                    </Mod>
                    <Mod>
                        <Key>HANDLINGSUB</Key>
                        <Count>1</Count>
                    </Mod>
                    <Mod>
                        <Key>ACCURATE</Key>
                        <Count>1</Count>
                    </Mod>
                </AddedMods>
                <Sources>
                    <Source>Edge of the Empire Core Rulebook</Source>
                </Sources>
            </ItemAttachment>
        </ItemAttachments>'''
        
        # Parse the attachment
        parser = XMLParser()
        root = ET.fromstring(attachment_xml)
        
        attachment_list = parser._parse_item_attachments(root)
        
        if not attachment_list:
            print("  ✗ No attachments parsed")
            return False
        
        attachment = attachment_list[0]
        print(f"Extracted attachment:")
        print(f"  Name: {attachment['name']}")
        print(f"  Type: {attachment['data']['type']}")
        print(f"  ModificationOptions: {attachment['data'].get('modificationOptions', 'None')}")
        
        # Load ItemDescriptors if not already loaded
        if not hasattr(parser, '_item_descriptors'):
            parser._load_item_descriptors()
        
        # Test that ItemDescriptors were loaded
        if not hasattr(parser, '_item_descriptors'):
            print("  ✗ ItemDescriptors not loaded")
            return False
        
        print(f"  ✓ ItemDescriptors loaded ({len(parser._item_descriptors)} descriptors)")
        
        # Test specific ItemDescriptor lookups
        speedadd_desc = parser._get_item_descriptor_description('SPEEDADD')
        if speedadd_desc:
            print(f"  ✓ SPEEDADD descriptor found: {speedadd_desc}")
        else:
            print(f"  ✗ SPEEDADD descriptor not found")
            return False
        
        handlingsub_desc = parser._get_item_descriptor_description('HANDLINGSUB')
        if handlingsub_desc:
            print(f"  ✓ HANDLINGSUB descriptor found: {handlingsub_desc}")
        else:
            print(f"  ✗ HANDLINGSUB descriptor not found")
            return False
        
        accurate_desc = parser._get_item_descriptor_description('ACCURATE')
        if accurate_desc:
            print(f"  ✓ ACCURATE descriptor found: {accurate_desc}")
        else:
            print(f"  ✗ ACCURATE descriptor not found")
            return False
        
        # Test OggDude format conversion
        test_text = "Add [BO] to attack dice pools"
        converted_text = parser._convert_oggdude_format_to_plain_text(test_text)
        if converted_text == "Add Boost to attack dice pools":
            print(f"  ✓ OggDude format conversion works: '{test_text}' -> '{converted_text}'")
        else:
            print(f"  ✗ OggDude format conversion failed: '{test_text}' -> '{converted_text}'")
            return False
        
        # Test multiple dice conversion
        test_text2 = "Add [DI][DI] to difficulty"
        converted_text2 = parser._convert_oggdude_format_to_plain_text(test_text2)
        if converted_text2 == "Add 2 difficulty to difficulty":
            print(f"  ✓ Multiple dice conversion works: '{test_text2}' -> '{converted_text2}'")
        else:
            print(f"  ✗ Multiple dice conversion failed: '{test_text2}' -> '{converted_text2}'")
            return False
        
        # Test that modificationOptions contains the converted descriptions
        modification_options = attachment['data'].get('modificationOptions', '')
        if 'Increase Speed by 2' in modification_options:
            print(f"  ✓ SPEEDADD correctly converted to 'Increase Speed by 2'")
        else:
            print(f"  ✗ SPEEDADD not correctly converted, got: {modification_options}")
            return False
        
        if 'Decreases Handling by 1' in modification_options:
            print(f"  ✓ HANDLINGSUB correctly converted to 'Decreases Handling by 1'")
        else:
            print(f"  ✗ HANDLINGSUB not correctly converted, got: {modification_options}")
            return False
        
        if 'Accurate' in modification_options:
            print(f"  ✓ ACCURATE correctly converted to 'Accurate'")
        else:
            print(f"  ✗ ACCURATE not correctly converted, got: {modification_options}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ ItemDescriptors conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_item_descriptors_loading():
    """Test ItemDescriptors.xml loading functionality"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing ItemDescriptors loading...")
        
        parser = XMLParser()
        
        # Explicitly load ItemDescriptors
        parser._load_item_descriptors()
        
        # Test that ItemDescriptors are loaded
        if not hasattr(parser, '_item_descriptors'):
            print("  ✗ ItemDescriptors not loaded")
            return False
        
        item_descriptors = parser._item_descriptors
        
        if not item_descriptors:
            print("  ✗ No ItemDescriptors loaded")
            return False
        
        print(f"  ✓ Loaded {len(item_descriptors)} ItemDescriptors")
        
        # Test specific known descriptors
        test_descriptors = ['SPEEDADD', 'HANDLINGSUB', 'ACCURATE', 'AUTOFIRE']
        for descriptor_key in test_descriptors:
            if descriptor_key in item_descriptors:
                descriptor = item_descriptors[descriptor_key]
                print(f"  ✓ Found {descriptor_key}: {descriptor.get('name', 'No name')}")
                
                # Test that required fields are present
                if 'modDesc' in descriptor:
                    print(f"    - ModDesc: {descriptor['modDesc']}")
                else:
                    print(f"    - ModDesc: Missing")
                
                if 'description' in descriptor:
                    print(f"    - Description: {descriptor['description'][:50]}...")
                else:
                    print(f"    - Description: Missing")
            else:
                print(f"  ✗ Missing {descriptor_key}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ ItemDescriptors loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_oggdude_format_conversion():
    """Test OggDude format to plain text conversion"""
    try:
        from src.xml_parser import XMLParser
        
        print("Testing OggDude format conversion...")
        
        parser = XMLParser()
        
        # Test cases for OggDude format conversion
        test_cases = [
            ("Add [BO] to attack", "Add Boost to attack"),
            ("Add [DI] to difficulty", "Add difficulty to difficulty"),
            ("Add [SU] to success", "Add success to success"),
            ("Add [AD] to advantage", "Add advantage to advantage"),
            ("Add [TH] to threat", "Add threat to threat"),
            ("Add [TR] to triumph", "Add triumph to triumph"),
            ("Add [DE] to despair", "Add despair to despair"),
            ("Add [BO][BO] to attack", "Add 2 Boost to attack"),
            ("Add [DI][DI][DI] to difficulty", "Add 3 difficulty to difficulty"),
            ("Add [SU][SU] to success", "Add 2 success to success"),
            ("Add [AD][AD] to advantage", "Add 2 advantage to advantage"),
            ("Add [TH][TH] to threat", "Add 2 threat to threat"),
            ("Complex: [BO] and [DI][DI] with [SU]", "Complex: Boost and 2 difficulty with success"),
        ]
        
        for input_text, expected_output in test_cases:
            converted = parser._convert_oggdude_format_to_plain_text(input_text)
            if converted == expected_output:
                print(f"  ✓ '{input_text}' -> '{converted}'")
            else:
                print(f"  ✗ '{input_text}' -> '{converted}' (expected: '{expected_output}')")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ OggDude format conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running item conversion tests...")
    
    # Test ranged weapon conversion
    ranged_result = test_weapon_conversion()
    
    # Test melee weapon conversion
    melee_result = test_melee_weapon_conversion()
    
    # Test category filtering
    category_result = test_category_filtering()
    
    # Test gear conversion
    gear_result = test_gear_conversion()
    
    # Test armor conversion
    armor_result = test_armor_conversion()
    
    # Test item attachment conversion
    attachment_result = test_item_attachment_conversion()
    
    # Test ItemDescriptors conversion
    item_descriptors_result = test_item_descriptors_conversion()
    
    # Test ItemDescriptors loading
    item_descriptors_loading_result = test_item_descriptors_loading()
    
    # Test OggDude format conversion
    oggdude_format_result = test_oggdude_format_conversion()
    
    if (ranged_result and melee_result and category_result and gear_result and 
        armor_result and attachment_result and item_descriptors_result and 
        item_descriptors_loading_result and oggdude_format_result):
        print("\n✓ All item conversion tests passed!")
    else:
        print("\n✗ Some item conversion tests failed!")
        sys.exit(1) 