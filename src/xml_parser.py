import xml.etree.ElementTree as ET
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

class XMLParser:
    def __init__(self):
        self.field_mapping = self._load_field_mapping()
        self.sources_config = self._load_sources_config()
    
    def _load_field_mapping(self) -> Dict[str, Any]:
        """Load field mapping configuration"""
        try:
            with open('config/field_mapping.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: field_mapping.json not found, using default mappings")
            return {}
    
    def _load_sources_config(self) -> Dict[str, Any]:
        """Load sources configuration"""
        try:
            with open('config/sources.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: sources.json not found, using default sources")
            return {"sources": []}
    
    def _apply_field_mapping(self, record_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply field mapping to transform OggDude field names to Realm VTT field names
        
        Args:
            record_type: Type of record (weapons, species, careers, etc.)
            data: Data dictionary with OggDude field names
            
        Returns:
            Dictionary with Realm VTT field names
        """
        if record_type not in self.field_mapping:
            return data
        
        mapping = self.field_mapping[record_type]
        mapped_data = {}
        
        # First, add all mapped fields (with None for missing ones)
        for oggdude_field, realm_field in mapping.items():
            mapped_data[realm_field] = data.get(oggdude_field, None)
        
        # Then add any fields that weren't in the mapping
        for field, value in data.items():
            if field not in mapping:
                mapped_data[field] = value
        
        return mapped_data
    
    def parse_xml_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a single XML file and extract records
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            List of dictionaries containing parsed records
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            records = []
            
            # Handle different XML structures
            if root.tag == 'Weapons':
                records = self._parse_weapons(root)
            elif root.tag == 'Species':
                records = self._parse_species(root)
            elif root.tag == 'Career':
                records = self._parse_career(root)
            elif root.tag == 'Specialization':
                records = self._parse_specialization(root)
            elif root.tag == 'Talent':
                records = self._parse_talent(root)
            elif root.tag == 'ForcePower':
                records = self._parse_force_power(root)
            elif root.tag == 'Vehicle':
                records = self._parse_vehicle(root)
            elif root.tag == 'Armor':
                records = self._parse_armor(root)
            elif root.tag == 'Gear':
                records = self._parse_gear(root)
            else:
                # Generic parsing for other types
                records = self._parse_generic(root)
            
            return records
            
        except ET.ParseError as e:
            print(f"Error parsing XML file {file_path}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error parsing {file_path}: {e}")
            return []
    
    def _parse_weapons(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse weapons from XML"""
        weapons = []
        for weapon_elem in root.findall('Weapon'):
            weapon = self._extract_weapon_data(weapon_elem)
            if weapon:
                weapons.append(weapon)
        return weapons
    
    def _extract_weapon_data(self, weapon_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract weapon data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(weapon_elem, 'Name'),
                'Description': self._get_text(weapon_elem, 'Description'),
                'Type': self._get_text(weapon_elem, 'Type', 'ranged weapon'),
                'Encumbrance': self._get_int(weapon_elem, 'Encumbrance', 0),
                'Price': self._get_text(weapon_elem, 'Price', '0'),
                'Rarity': self._get_int(weapon_elem, 'Rarity', 0),
                'Restricted': self._get_text(weapon_elem, 'Restricted', 'no'),
                'SkillKey': self._get_text(weapon_elem, 'SkillKey'),
                'Damage': self._get_int(weapon_elem, 'Damage', 0),
                'Crit': self._get_int(weapon_elem, 'Crit', 0),
                'RangeValue': self._get_text(weapon_elem, 'RangeValue'),
                'Qualities': self._extract_qualities(weapon_elem),
                'HP': self._get_int(weapon_elem, 'HP', 0)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('weapons', raw_data)
            
            # Apply additional transformations
            if 'weaponSkill' in mapped_data and mapped_data['weaponSkill']:
                mapped_data['weaponSkill'] = self._map_skill_key(mapped_data['weaponSkill'])
            
            if 'range' in mapped_data and mapped_data['range']:
                mapped_data['range'] = self._map_range(mapped_data['range'])
            
            # Add default values for Realm VTT
            mapped_data.update({
                'modifiers': [],
                'equipEffect': None,
                'stun': 0,
                'consumable': False,
                'hasUseBtn': False,
                'attachments': [],
                'slotsUsed': 0
            })
            
            weapon = {
                'recordType': 'weapons',
                'type': 'weapon',
                'name': mapped_data.get('name', 'Unknown Weapon'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(weapon_elem),
                'data': mapped_data,
                'fields': self._get_weapon_fields(),
                'unidentifiedName': 'Unidentified Items',
                'locked': True
            }
            
            # Set animation based on weapon type
            weapon_type = weapon['data']['type'].lower()
            if 'blaster' in weapon_type:
                weapon['data']['animation'] = 'blaster'
            elif 'lightsaber' in weapon_type or 'saber' in weapon_type:
                weapon['data']['animation'] = 'lightsaber'
            
            return weapon
            
        except Exception as e:
            print(f"Error extracting weapon data: {e}")
            return None
    
    def _parse_species(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse species from XML"""
        species = []
        for species_elem in root.findall('Species'):
            species_data = self._extract_species_data(species_elem)
            if species_data:
                species.append(species_data)
        return species
    
    def _extract_species_data(self, species_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract species data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(species_elem, 'Name'),
                'Description': self._get_text(species_elem, 'Description'),
                'StartingChars': self._extract_starting_chars(species_elem),
                'StartingAttrs': self._extract_starting_attrs(species_elem),
                'SkillModifiers': self._extract_skill_modifiers(species_elem),
                'TalentModifiers': self._extract_talent_modifiers(species_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('species', raw_data)
            
            species = {
                'recordType': 'species',
                'name': mapped_data.get('name', 'Unknown Species'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(species_elem),
                'data': mapped_data,
                'unidentifiedName': 'Unknown Species',
                'locked': True
            }
            return species
            
        except Exception as e:
            print(f"Error extracting species data: {e}")
            return None
    
    def _parse_career(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse career from XML"""
        career = self._extract_career_data(root)
        return [career] if career else []
    
    def _extract_career_data(self, career_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract career data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(career_elem, 'Name'),
                'Description': self._get_text(career_elem, 'Description'),
                'CareerSkills': self._extract_career_skills(career_elem),
                'Specializations': self._extract_specializations(career_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('careers', raw_data)
            
            career = {
                'recordType': 'careers',
                'name': mapped_data.get('name', 'Unknown Career'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(career_elem),
                'data': mapped_data,
                'unidentifiedName': 'Unknown Career',
                'locked': True
            }
            return career
            
        except Exception as e:
            print(f"Error extracting career data: {e}")
            return None
    
    def _parse_specialization(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse specialization from XML"""
        spec = self._extract_specialization_data(root)
        return [spec] if spec else []
    
    def _extract_specialization_data(self, spec_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract specialization data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(spec_elem, 'Name'),
                'Description': self._get_text(spec_elem, 'Description'),
                'CareerKey': self._get_text(spec_elem, 'CareerKey'),
                'Skills': self._extract_spec_skills(spec_elem),
                'Talents': self._extract_spec_talents(spec_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('specializations', raw_data)
            
            spec = {
                'recordType': 'specializations',
                'name': mapped_data.get('name', 'Unknown Specialization'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(spec_elem),
                'data': mapped_data,
                'unidentifiedName': 'Unknown Specialization',
                'locked': True
            }
            return spec
            
        except Exception as e:
            print(f"Error extracting specialization data: {e}")
            return None
    
    def _parse_talent(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse talent from XML"""
        talent = self._extract_talent_data(root)
        return [talent] if talent else []
    
    def _extract_talent_data(self, talent_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract talent data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(talent_elem, 'Name'),
                'Description': self._get_text(talent_elem, 'Description'),
                'Activation': self._get_text(talent_elem, 'Activation'),
                'Ranked': self._get_bool(talent_elem, 'Ranked', False),
                'Trees': []  # Will be populated later
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('talents', raw_data)
            
            talent = {
                'recordType': 'talents',
                'name': mapped_data.get('name', 'Unknown Talent'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(talent_elem),
                'data': mapped_data,
                'unidentifiedName': 'Unknown Talent',
                'locked': True
            }
            return talent
            
        except Exception as e:
            print(f"Error extracting talent data: {e}")
            return None
    
    def _parse_force_power(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse force power from XML"""
        power = self._extract_force_power_data(root)
        return [power] if power else []
    
    def _extract_force_power_data(self, power_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract force power data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(power_elem, 'Name'),
                'Description': self._get_text(power_elem, 'Description'),
                'Activation': self._get_text(power_elem, 'Activation'),
                'ForcePowerType': self._get_text(power_elem, 'ForcePowerType'),
                'Upgrades': self._extract_upgrades(power_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('force_powers', raw_data)
            
            power = {
                'recordType': 'force_powers',
                'name': mapped_data.get('name', 'Unknown Force Power'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(power_elem),
                'data': mapped_data,
                'unidentifiedName': 'Unknown Force Power',
                'locked': True
            }
            return power
            
        except Exception as e:
            print(f"Error extracting force power data: {e}")
            return None
    
    def _parse_vehicle(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse vehicle from XML"""
        vehicle = self._extract_vehicle_data(root)
        return [vehicle] if vehicle else []
    
    def _extract_vehicle_data(self, vehicle_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract vehicle data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(vehicle_elem, 'Name'),
                'Description': self._get_text(vehicle_elem, 'Description'),
                'Type': self._get_text(vehicle_elem, 'Type'),
                'Encumbrance': self._get_int(vehicle_elem, 'Encumbrance', 0),
                'Price': self._get_text(vehicle_elem, 'Price', '0'),
                'Rarity': self._get_int(vehicle_elem, 'Rarity', 0),
                'Restricted': self._get_text(vehicle_elem, 'Restricted', 'no'),
                'Silhouette': self._get_int(vehicle_elem, 'Silhouette', 0),
                'Speed': self._get_int(vehicle_elem, 'Speed', 0),
                'Handling': self._get_int(vehicle_elem, 'Handling', 0),
                'Armor': self._get_int(vehicle_elem, 'Armor', 0),
                'HullTrauma': self._get_int(vehicle_elem, 'HullTrauma', 0),
                'SystemStrain': self._get_int(vehicle_elem, 'SystemStrain', 0),
                'PassengerCapacity': self._get_int(vehicle_elem, 'PassengerCapacity', 0),
                'EncumbranceCapacity': self._get_int(vehicle_elem, 'EncumbranceCapacity', 0),
                'Consumables': self._get_text(vehicle_elem, 'Consumables'),
                'Hyperdrive': self._get_text(vehicle_elem, 'Hyperdrive')
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('vehicles', raw_data)
            
            vehicle = {
                'recordType': 'vehicles',
                'name': mapped_data.get('name', 'Unknown Vehicle'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(vehicle_elem),
                'data': mapped_data,
                'unidentifiedName': 'Unknown Vehicle',
                'locked': True
            }
            return vehicle
            
        except Exception as e:
            print(f"Error extracting vehicle data: {e}")
            return None
    
    def _parse_armor(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse armor from XML"""
        armor = self._extract_armor_data(root)
        return [armor] if armor else []
    
    def _extract_armor_data(self, armor_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract armor data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(armor_elem, 'Name'),
                'Description': self._get_text(armor_elem, 'Description'),
                'Type': 'armor',
                'Encumbrance': self._get_int(armor_elem, 'Encumbrance', 0),
                'Price': self._get_text(armor_elem, 'Price', '0'),
                'Rarity': self._get_int(armor_elem, 'Rarity', 0),
                'Restricted': self._get_text(armor_elem, 'Restricted', 'no'),
                'Soak': self._get_int(armor_elem, 'Soak', 0),
                'Defense': self._get_int(armor_elem, 'Defense', 0),
                'HP': self._get_int(armor_elem, 'HP', 0)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('armor', raw_data)
            
            # Add default values for Realm VTT
            mapped_data.update({
                'modifiers': [],
                'equipEffect': None,
                'consumable': False,
                'hasUseBtn': False,
                'attachments': [],
                'slotsUsed': 0
            })
            
            armor = {
                'recordType': 'items',
                'type': 'armor',
                'name': mapped_data.get('name', 'Unknown Armor'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(armor_elem),
                'data': mapped_data,
                'fields': self._get_armor_fields(),
                'unidentifiedName': 'Unidentified Items',
                'locked': True
            }
            return armor
            
        except Exception as e:
            print(f"Error extracting armor data: {e}")
            return None
    
    def _parse_gear(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse gear from XML"""
        gear = self._extract_gear_data(root)
        return [gear] if gear else []
    
    def _extract_gear_data(self, gear_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract gear data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(gear_elem, 'Name'),
                'Description': self._get_text(gear_elem, 'Description'),
                'Type': 'gear',
                'Encumbrance': self._get_int(gear_elem, 'Encumbrance', 0),
                'Price': self._get_text(gear_elem, 'Price', '0'),
                'Rarity': self._get_int(gear_elem, 'Rarity', 0),
                'Restricted': self._get_text(gear_elem, 'Restricted', 'no'),
                'Consumable': self._get_bool(gear_elem, 'Consumable', False)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('gear', raw_data)
            
            # Add default values for Realm VTT
            mapped_data.update({
                'modifiers': [],
                'equipEffect': None,
                'hasUseBtn': False,
                'attachments': [],
                'slotsUsed': 0
            })
            
            gear = {
                'recordType': 'items',
                'type': 'gear',
                'name': mapped_data.get('name', 'Unknown Gear'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(gear_elem),
                'data': mapped_data,
                'fields': self._get_gear_fields(),
                'unidentifiedName': 'Unidentified Items',
                'locked': True
            }
            return gear
            
        except Exception as e:
            print(f"Error extracting gear data: {e}")
            return None
    
    def _parse_generic(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Generic parsing for other XML types"""
        records = []
        for child in root:
            if child.tag.endswith('s'):  # Plural tags like 'Weapons', 'Species'
                for item in child:
                    record = self._extract_generic_data(item, child.tag[:-1])  # Remove 's'
                    if record:
                        records.append(record)
            else:
                record = self._extract_generic_data(child, child.tag)
                if record:
                    records.append(record)
        return records
    
    def _extract_generic_data(self, elem: ET.Element, record_type: str) -> Optional[Dict[str, Any]]:
        """Extract generic data from XML element"""
        try:
            # Extract all fields from the element
            raw_data = {}
            for child in elem:
                if child.tag not in ['Name', 'Description', 'Source']:
                    raw_data[child.tag] = self._get_element_value(child)
            
            # Add name and description
            raw_data['Name'] = self._get_text(elem, 'Name')
            raw_data['Description'] = self._get_text(elem, 'Description')
            
            # Apply field mapping if available
            if record_type.lower() in self.field_mapping:
                mapped_data = self._apply_field_mapping(record_type.lower(), raw_data)
            else:
                mapped_data = raw_data
            
            record = {
                'recordType': record_type.lower(),
                'name': mapped_data.get('name', f'Unknown {record_type}'),
                'description': mapped_data.get('description', ''),
                'sources': self._get_sources(elem),
                'data': mapped_data,
                'unidentifiedName': f'Unknown {record_type}',
                'locked': True
            }
            
            return record
            
        except Exception as e:
            print(f"Error extracting generic data: {e}")
            return None
    
    def _get_text(self, elem: ET.Element, tag: str, default: str = '') -> str:
        """Get text content from XML element"""
        child = elem.find(tag)
        return child.text if child is not None and child.text else default
    
    def _get_int(self, elem: ET.Element, tag: str, default: int = 0) -> int:
        """Get integer content from XML element"""
        text = self._get_text(elem, tag)
        try:
            return int(text) if text else default
        except ValueError:
            return default
    
    def _get_bool(self, elem: ET.Element, tag: str, default: bool = False) -> bool:
        """Get boolean content from XML element"""
        text = self._get_text(elem, tag)
        return text.lower() == 'true' if text else default
    
    def _get_source(self, elem: ET.Element) -> str:
        """Get source from XML element"""
        source_elem = elem.find('Source')
        if source_elem is not None:
            # Prioritize the text content (source name) over the Page attribute
            return source_elem.text or source_elem.get('Page', '') or ''
        return ''
    
    def _get_sources(self, elem: ET.Element) -> List[str]:
        """Get all sources from XML element (handles multiple sources)"""
        sources = []
        
        # First, check for individual Source tags (single source)
        for source_elem in elem.findall('Source'):
            if source_elem.text:
                sources.append(source_elem.text.strip())
        
        # Then, check for Sources container with multiple Source tags
        sources_container = elem.find('Sources')
        if sources_container is not None:
            for source_elem in sources_container.findall('Source'):
                if source_elem.text:
                    sources.append(source_elem.text.strip())
        
        return sources
    
    def _get_element_value(self, elem: ET.Element) -> Any:
        """Get value from XML element, handling different types"""
        if elem.text:
            return elem.text
        elif len(elem) > 0:
            return [self._get_element_value(child) for child in elem]
        else:
            return elem.attrib if elem.attrib else ''
    
    def _map_skill_key(self, skill_key: str) -> str:
        """Map OggDude skill keys to Realm VTT skill names"""
        skill_mapping = {
            'RANGLT': 'Ranged (Light)',
            'RANGHV': 'Ranged (Heavy)',
            'GUNN': 'Gunnery',
            'MELEE': 'Melee',
            'BRAWL': 'Brawl',
            'LIGHT': 'Light',
            'HEAVY': 'Heavy',
            'GUNNERY': 'Gunnery'
        }
        return skill_mapping.get(skill_key, skill_key)
    
    def _map_range(self, range_value: str) -> str:
        """Map OggDude range values to Realm VTT range names"""
        range_mapping = {
            'wrEngaged': 'Engaged',
            'wrShort': 'Short',
            'wrMedium': 'Medium',
            'wrLong': 'Long',
            'wrExtreme': 'Extreme'
        }
        return range_mapping.get(range_value, range_value)
    
    def _extract_qualities(self, elem: ET.Element) -> List[str]:
        """Extract weapon qualities"""
        qualities = []
        qualities_elem = elem.find('Qualities')
        if qualities_elem:
            for quality in qualities_elem.findall('Quality'):
                key = quality.find('Key')
                if key is not None and key.text:
                    qualities.append(key.text)
        return qualities
    
    def _extract_starting_chars(self, elem: ET.Element) -> Dict[str, int]:
        """Extract starting characteristics"""
        chars = {}
        chars_elem = elem.find('StartingChars')
        if chars_elem:
            for char in ['Brawn', 'Agility', 'Intellect', 'Cunning', 'Willpower', 'Presence']:
                chars[char.lower()] = self._get_int(chars_elem, char, 1)
        return chars
    
    def _extract_starting_attrs(self, elem: ET.Element) -> Dict[str, int]:
        """Extract starting attributes"""
        attrs = {}
        attrs_elem = elem.find('StartingAttrs')
        if attrs_elem:
            attrs['woundThreshold'] = self._get_int(attrs_elem, 'WoundThreshold', 10)
            attrs['strainThreshold'] = self._get_int(attrs_elem, 'StrainThreshold', 10)
            attrs['experience'] = self._get_int(attrs_elem, 'Experience', 0)
        return attrs
    
    def _extract_skill_modifiers(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract skill modifiers"""
        modifiers = []
        mods_elem = elem.find('SkillModifiers')
        if mods_elem:
            for mod in mods_elem.findall('SkillModifier'):
                modifiers.append({
                    'skill': self._get_text(mod, 'Key'),
                    'rankStart': self._get_int(mod, 'RankStart', 0),
                    'rankLimit': self._get_int(mod, 'RankLimit', 0)
                })
        return modifiers
    
    def _extract_talent_modifiers(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract talent modifiers"""
        modifiers = []
        mods_elem = elem.find('TalentModifiers')
        if mods_elem:
            for mod in mods_elem.findall('TalentModifier'):
                modifiers.append({
                    'talent': self._get_text(mod, 'Key'),
                    'rankAdd': self._get_int(mod, 'RankAdd', 0)
                })
        return modifiers
    
    def _extract_career_skills(self, elem: ET.Element) -> List[str]:
        """Extract career skills"""
        skills = []
        skills_elem = elem.find('CareerSkills')
        if skills_elem:
            for skill in skills_elem.findall('Key'):
                if skill.text:
                    skills.append(skill.text)
        return skills
    
    def _extract_specializations(self, elem: ET.Element) -> List[str]:
        """Extract specializations"""
        specs = []
        specs_elem = elem.find('Specializations')
        if specs_elem:
            for spec in specs_elem.findall('Key'):
                if spec.text:
                    specs.append(spec.text)
        return specs
    
    def _extract_spec_skills(self, elem: ET.Element) -> List[str]:
        """Extract specialization skills"""
        skills = []
        skills_elem = elem.find('Skills')
        if skills_elem:
            for skill in skills_elem.findall('Key'):
                if skill.text:
                    skills.append(skill.text)
        return skills
    
    def _extract_spec_talents(self, elem: ET.Element) -> List[str]:
        """Extract specialization talents"""
        talents = []
        talents_elem = elem.find('Talents')
        if talents_elem:
            for talent in talents_elem.findall('Key'):
                if talent.text:
                    talents.append(talent.text)
        return talents
    
    def _extract_upgrades(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract force power upgrades"""
        upgrades = []
        upgrades_elem = elem.find('Upgrades')
        if upgrades_elem:
            for upgrade in upgrades_elem.findall('Upgrade'):
                upgrades.append({
                    'name': self._get_text(upgrade, 'Name'),
                    'description': self._get_text(upgrade, 'Description'),
                    'activation': self._get_text(upgrade, 'Activation')
                })
        return upgrades
    
    def _get_weapon_fields(self) -> Dict[str, Any]:
        """Get weapon field configuration"""
        return {
            "animationProps": {"hidden": False},
            "armorAttachmentProperties": {"hidden": True},
            "armorProperties": {"hidden": True},
            "attackDividerBox": {"hidden": False},
            "autoFireBtn": {"hidden": True},
            "consumable": {"hidden": True},
            "consumableProperties": {"hidden": True},
            "generalWeaponProperties": {"hidden": False},
            "hardpoints": {"hidden": False},
            "hasUseBtn": {"hidden": False},
            "itemQualities": {"hidden": False},
            "packProperties": {"hidden": True},
            "stunBtn": {"hidden": True},
            "weaponAttached": {"hidden": True},
            "weaponAttachedLabel": {"hidden": True},
            "weaponAttachmentProperties": {"hidden": False},
            "weaponProperties": {"hidden": False},
            "weaponType": {"hidden": True},
            "weaponAttachmentsProperties": {"hidden": False},
            "attachmentsProperties": {"hidden": False}
        }
    
    def _get_armor_fields(self) -> Dict[str, Any]:
        """Get armor field configuration"""
        return {
            "animationProps": {"hidden": True},
            "armorAttachmentProperties": {"hidden": False},
            "armorProperties": {"hidden": False},
            "attackDividerBox": {"hidden": True},
            "autoFireBtn": {"hidden": True},
            "consumable": {"hidden": True},
            "consumableProperties": {"hidden": True},
            "generalWeaponProperties": {"hidden": True},
            "hardpoints": {"hidden": False},
            "hasUseBtn": {"hidden": False},
            "itemQualities": {"hidden": False},
            "packProperties": {"hidden": True},
            "stunBtn": {"hidden": True},
            "weaponAttached": {"hidden": True},
            "weaponAttachedLabel": {"hidden": True},
            "weaponAttachmentProperties": {"hidden": True},
            "weaponProperties": {"hidden": True},
            "weaponType": {"hidden": True}
        }
    
    def _get_gear_fields(self) -> Dict[str, Any]:
        """Get gear field configuration"""
        return {
            "animationProps": {"hidden": True},
            "armorAttachmentProperties": {"hidden": True},
            "armorProperties": {"hidden": True},
            "attackDividerBox": {"hidden": True},
            "autoFireBtn": {"hidden": True},
            "consumable": {"hidden": False},
            "consumableProperties": {"hidden": False},
            "generalWeaponProperties": {"hidden": True},
            "hardpoints": {"hidden": True},
            "hasUseBtn": {"hidden": False},
            "itemQualities": {"hidden": False},
            "packProperties": {"hidden": False},
            "stunBtn": {"hidden": True},
            "weaponAttached": {"hidden": True},
            "weaponAttachedLabel": {"hidden": True},
            "weaponAttachmentProperties": {"hidden": True},
            "weaponProperties": {"hidden": True},
            "weaponType": {"hidden": True}
        }
    
    def filter_by_sources(self, records: List[Dict[str, Any]], selected_sources: List[str]) -> List[Dict[str, Any]]:
        """Filter records by selected sources"""
        if not selected_sources:
            return records
        
        filtered_records = []
        for record in records:
            # Get all sources for this record
            record_sources = record.get('sources', [])
            
            # Check if any of the record's sources match any selected source
            for record_source in record_sources:
                for source_config in self.sources_config['sources']:
                    if source_config['key'] in selected_sources:
                        for oggdude_source in source_config['oggdude_sources']:
                            if oggdude_source.lower() in record_source.lower():
                                filtered_records.append(record)
                                break
                        else:
                            continue
                        break
                else:
                    continue
                break  # Found a match, no need to check other record sources
        
        return filtered_records
    
    def scan_directory(self, directory_path: str, selected_sources: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan directory for XML files and parse them
        
        Args:
            directory_path: Path to directory to scan
            selected_sources: List of selected source keys to filter by
            
        Returns:
            Dictionary mapping record types to lists of records
        """
        all_records = {
            'weapons': [],
            'species': [],
            'careers': [],
            'specializations': [],
            'talents': [],
            'force_powers': [],
            'vehicles': [],
            'armor': [],
            'gear': [],
            'npcs': []
        }
        
        directory = Path(directory_path)
        if not directory.exists():
            print(f"Directory {directory_path} does not exist")
            return all_records
        
        # Scan for XML files recursively
        xml_files = list(directory.rglob('*.xml'))
        print(f"Found {len(xml_files)} XML files in {directory_path}")
        
        for xml_file in xml_files:
            print(f"Parsing {xml_file}")
            records = self.parse_xml_file(str(xml_file))
            
            # Filter by sources if specified
            if selected_sources:
                records = self.filter_by_sources(records, selected_sources)
            
            # Categorize records by type
            for record in records:
                record_type = record.get('recordType', 'unknown')
                if record_type in all_records:
                    all_records[record_type].append(record)
                else:
                    print(f"Unknown record type: {record_type}")
        
        return all_records 