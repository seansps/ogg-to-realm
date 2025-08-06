import xml.etree.ElementTree as ET
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

class XMLParser:
    def __init__(self):
        self.field_mapping = self._load_field_mapping()
        self.sources_config = self._load_sources_config()
        self._talents = {}  # Will store talent keys to names mapping
    
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
    
    def _get_namespaced_tag(self, elem: ET.Element, tag: str) -> str:
        """
        Get the namespaced tag name for searching within an element.
        This handles both namespaced and non-namespaced XML.
        """
        # Check if the element has a namespace
        if '}' in elem.tag:
            # Extract namespace from the element's tag
            namespace = elem.tag.split('}')[0] + '}'
            return namespace + tag
        else:
            # No namespace, return the tag as-is
            return tag
    
    def _find_with_namespace(self, elem: ET.Element, tag: str) -> Optional[ET.Element]:
        """
        Find a child element, handling namespaces properly.
        """
        # Try with namespace first
        namespaced_tag = self._get_namespaced_tag(elem, tag)
        result = elem.find(namespaced_tag)
        if result is not None:
            return result
        
        # If not found with namespace, try without namespace
        return elem.find(tag)
    
    def _findall_with_namespace(self, elem: ET.Element, tag: str) -> List[ET.Element]:
        """
        Find all child elements, handling namespaces properly.
        """
        # Try with namespace first
        namespaced_tag = self._get_namespaced_tag(elem, tag)
        results = elem.findall(namespaced_tag)
        if results:
            return results
        
        # If not found with namespace, try without namespace
        return elem.findall(tag)
    
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
    
    def _get_category_from_sources(self, sources: List[str]) -> str:
        """Convert OggDude sources to Realm VTT category"""
        if not sources:
            return ""
        
        # Use the first source as the category
        source_name = sources[0]
        
        # Map source names to category names (use full names for consistency)
        category_mapping = {
            "Edge of the Empire Core Rulebook": "Edge of the Empire Core Rulebook",
            "Age of Rebellion Core Rulebook": "Age of Rebellion Core Rulebook", 
            "Force and Destiny Core Rulebook": "Force and Destiny Core Rulebook",
            "Far Horizons": "Far Horizons",
            "Dangerous Covenants": "Dangerous Covenants",
            "Fly Casual": "Fly Casual",
            "Forged in Battle": "Forged in Battle",
            "Stay on Target": "Stay on Target",
            "Unlimited Power": "Unlimited Power",
            "Disciples of Harmony": "Disciples of Harmony",
            "Lords of Nal Hutta": "Lords of Nal Hutta",
            "Suns of Fortune": "Suns of Fortune",
            "Nexus of Power": "Nexus of Power",
            "Fully Operational": "Fully Operational",
            "Cyphers and Masks": "Cyphers and Masks",
            "Rise of the Separatists": "Rise of the Separatists",
            "Collapse of the Republic": "Collapse of the Republic",
            "Dawn of Rebellion": "Dawn of Rebellion",
            "Chronicles of the Gatekeeper": "Chronicles of the Gatekeeper",
            "Savage Spirits": "Savage Spirits",
            "Endless Vigil": "Endless Vigil",
            "Lead by Example": "Lead by Example",
            "Strongholds of Resistance": "Strongholds of Resistance",
            "Special Modifications": "Special Modifications",
            "Keeping the Peace": "Keeping the Peace",
            "Knights of Fate": "Knights of Fate",
            "Ghosts of Dathomir": "Ghosts of Dathomir",
            "Mask of the Pirate Queen": "Mask of the Pirate Queen",
            "No Disintegrations": "No Disintegrations",
            "Onslaught at Arda I": "Onslaught at Arda I",
            "Under a Black Sun": "Under a Black Sun",
            "Beyond the Rim": "Beyond the Rim",
            "Long Arm of the Hutt": "Long Arm of the Hutt",
            "Jewel of Yavin": "Jewel of Yavin",
            "Desperate Allies": "Desperate Allies",
            "Friends Like These": "Friends Like These",
            "Allies and Adversaries": "Allies and Adversaries",
            "Force and Destiny Game Master's Kit": "Force and Destiny Game Master's Kit",
            "Age of Rebellion Beta Rulebook": "Age of Rebellion Beta Rulebook",
            "Force and Destiny Beta Rulebook": "Force and Destiny Beta Rulebook",
            "Unofficial Species Menagerie": "Unofficial Species Menagerie"
        }
        
        return category_mapping.get(source_name, source_name)
    
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
            
            # Handle different XML structures - check for local part of tag name to handle namespaces
            root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
            
            if root_tag == 'Weapons':
                records = self._parse_weapons(root)
            elif root_tag == 'Species':
                records = self._parse_species(root)
            elif root_tag == 'Career':
                records = self._parse_career(root)
            elif root_tag == 'Specialization':
                records = self._parse_specialization(root)
            elif root_tag == 'Talent':
                records = self._parse_talent(root)
            elif root_tag == 'Talents':
                records = self._parse_talents(root)
            elif root_tag == 'ForcePower':
                records = self._parse_force_power(root)
            elif root_tag == 'Vehicle':
                records = self._parse_vehicle(root)
            elif root_tag == 'Armor' or root_tag == 'Armors':
                records = self._parse_armor(root)
            elif root_tag == 'Gear' or root_tag == 'Gears':
                records = self._parse_gear(root)
            elif root_tag == 'Skills':
                records = self._parse_skills(root)
            elif root_tag == 'ItemAttachments' or root_tag == 'ItemAttachment':
                records = self._parse_item_attachments(root)
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
        for weapon_elem in self._findall_with_namespace(root, 'Weapon'):
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
            
            # Store original skill key and type for weapon type determination
            original_skill_key = mapped_data.get('weaponSkill', '')
            original_type = raw_data.get('Type', '')  # Store the original OggDude Type
            
            # Apply additional transformations
            if 'weaponSkill' in mapped_data and mapped_data['weaponSkill']:
                mapped_data['weaponSkill'] = self._map_skill_key(mapped_data['weaponSkill'])
            
            if 'range' in mapped_data and mapped_data['range']:
                mapped_data['range'] = self._map_range(mapped_data['range'])
            
            # Store original skill key and type for later use
            mapped_data['originalSkillKey'] = original_skill_key
            mapped_data['originalType'] = original_type
            
            # Determine weapon type based on SkillKey
            if original_skill_key in ['MELEE', 'BRAWL', 'LIGHTSABER', 'LTSABER']:
                mapped_data['type'] = 'melee weapon'
            else:
                mapped_data['type'] = 'ranged weapon'
            
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
            
            # Get sources and store them for later category determination
            sources = self._get_sources(weapon_elem)
            
            weapon = {
                'recordType': 'items',
                'name': mapped_data.get('name', 'Unknown Weapon'),
                'description': mapped_data.get('description', ''),
                'sources': sources,  # Store sources for later use
                'category': '',  # Will be determined during filtering
                'data': mapped_data,
                # 'fields': self._get_weapon_fields(),  # Commented out for now
                'fields': {},  # Set to empty dictionary for now
                'unidentifiedName': 'Unidentified Items',
                'locked': True
            }
            
            # Set animation based on weapon name and type
            weapon_name = weapon['name'].lower()
            if 'blaster' in weapon_name or 'rifle' in weapon_name:
                weapon['data']['animation'] = {
                    "animationName": "bolt_3",
                    "moveToDestination": True,
                    "stretchToDestination": False,
                    "destinationOnly": False,
                    "startAtCenter": False,
                    "scale": 0.33,
                    "opacity": 1,
                    "animationSpeed": 12,
                    "rotation": -90,
                    "hue": 360,
                    "contrast": None,
                    "brightness": None,
                    "moveSpeed": 2,
                    "sound": "laser_1",
                    "count": 1
                }
            elif 'lightsaber' in weapon_name or 'light saber' in weapon_name:
                weapon['data']['animation'] = {
                    "animationName": "slash_1",
                    "moveToDestination": False,
                    "stretchToDestination": False,
                    "destinationOnly": False,
                    "startAtCenter": False,
                    "scale": 0.5,
                    "opacity": 1,
                    "animationSpeed": 14,
                    "rotation": -74,
                    "hue": 207,
                    "contrast": 0.7,
                    "brightness": 0.3,
                    "moveSpeed": 1,
                    "sound": "laser_3",
                    "count": 1
                }
            elif 'vibro' in weapon_name:
                weapon['data']['animation'] = {
                    "animationName": "slash_1",
                    "moveToDestination": False,
                    "stretchToDestination": False,
                    "destinationOnly": False,
                    "startAtCenter": False,
                    "scale": 0.5,
                    "opacity": 1,
                    "animationSpeed": 14,
                    "rotation": -74,
                    "hue": 68,
                    "contrast": 1,
                    "brightness": 0.35,
                    "moveSpeed": 1,
                    "sound": "slash_2",
                    "count": 1
                }
            
            return weapon
            
        except Exception as e:
            print(f"Error extracting weapon data: {e}")
            return None
    
    def _parse_species(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse species from XML"""
        species = []
        
        # Check if this is a single species file (like Bith.xml)
        # where the species data is directly in the root element
        if root.tag == 'Species':
            species_data = self._extract_species_data(root)
            if species_data:
                species.append(species_data)
        else:
            # Handle multiple species in a file
            for species_elem in self._findall_with_namespace(root, 'Species'):
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
            
            # Get sources and convert to category
            sources = self._get_sources(species_elem)
            category = self._get_category_from_sources(sources)
            
            species = {
                'recordType': 'species',
                'name': mapped_data.get('name', 'Unknown Species'),
                'description': mapped_data.get('description', ''),
                'category': category,
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
            
            # Get sources and convert to category
            sources = self._get_sources(career_elem)
            category = self._get_category_from_sources(sources)
            
            career = {
                'recordType': 'careers',
                'name': mapped_data.get('name', 'Unknown Career'),
                'description': mapped_data.get('description', ''),
                'category': category,
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
            
            # Get sources and convert to category
            sources = self._get_sources(spec_elem)
            category = self._get_category_from_sources(sources)
            
            spec = {
                'recordType': 'specializations',
                'name': mapped_data.get('name', 'Unknown Specialization'),
                'description': mapped_data.get('description', ''),
                'category': category,
                'data': mapped_data,
                'unidentifiedName': 'Unknown Specialization',
                'locked': True
            }
            return spec
            
        except Exception as e:
            print(f"Error extracting specialization data: {e}")
            return None
    
    def _parse_talents(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse talents from XML (plural root tag)"""
        talents = []
        for talent_elem in self._findall_with_namespace(root, 'Talent'):
            talent = self._extract_talent_data(talent_elem)
            if talent:
                talents.append(talent)
        return talents
    
    def _parse_talent(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse talent from XML (singular root tag)"""
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
            
            # Get sources and convert to category
            sources = self._get_sources(talent_elem)
            category = self._get_category_from_sources(sources)
            
            talent = {
                'recordType': 'talents',
                'name': mapped_data.get('name', 'Unknown Talent'),
                'description': mapped_data.get('description', ''),
                'category': category,
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
            
            # Get sources and convert to category
            sources = self._get_sources(power_elem)
            category = self._get_category_from_sources(sources)
            
            power = {
                'recordType': 'force_powers',
                'name': mapped_data.get('name', 'Unknown Force Power'),
                'description': mapped_data.get('description', ''),
                'category': category,
                'data': mapped_data,
                'unidentifiedName': 'Unknown Force Power',
                'locked': True
            }
            return power
            
        except Exception as e:
            print(f"Error extracting force power data: {e}")
            return None
    
    def _parse_vehicle(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse vehicle from XML - vehicles are npcs in Realm VTT"""
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
            
            # Get sources and convert to category
            sources = self._get_sources(vehicle_elem)
            category = self._get_category_from_sources(sources)
            
            # Vehicles are npcs in Realm VTT with type = 'vehicle'
            vehicle = {
                'recordType': 'npcs',
                'name': mapped_data.get('name', 'Unknown Vehicle'),
                'description': mapped_data.get('description', ''),
                'category': category,
                'data': {
                    'type': 'vehicle',
                    **mapped_data
                },
                'unidentifiedName': 'Unknown Vehicle',
                'locked': True
            }
            return vehicle
            
        except Exception as e:
            print(f"Error extracting vehicle data: {e}")
            return None
    
    def _parse_armor(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse armor from XML"""
        armor_list = []
        
        # Handle Armors root element containing multiple Armor elements
        if root.tag == 'Armors':
            for armor_elem in self._findall_with_namespace(root, 'Armor'):
                armor = self._extract_armor_data(armor_elem)
                if armor:
                    armor_list.append(armor)
        else:
            # Handle single Armor element (fallback)
            armor = self._extract_armor_data(root)
            if armor:
                armor_list.append(armor)
        
        return armor_list
    
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
                'HP': self._get_int(armor_elem, 'HP', 0),
                'Qualities': self._extract_qualities(armor_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('armor', raw_data)
            
            # Set the type in data field
            mapped_data['type'] = 'armor'
            
            # Add default values for Realm VTT
            mapped_data.update({
                'modifiers': [],
                'equipEffect': None,
                'consumable': False,
                'hasUseBtn': False,
                'attachments': [],
                'slotsUsed': 0
            })
            
            # Get sources and convert to category
            sources = self._get_sources(armor_elem)
            category = self._get_category_from_sources(sources)
            
            armor = {
                'recordType': 'items',
                'name': mapped_data.get('name', 'Unknown Armor'),
                'description': mapped_data.get('description', ''),
                'category': category,
                'sources': sources,
                'data': mapped_data,
                # 'fields': self._get_armor_fields(),  # Commented out for now
                'fields': {},  # Set to empty dictionary for now
                'unidentifiedName': 'Unidentified Items',
                'locked': True
            }
            return armor
            
        except Exception as e:
            print(f"Error extracting armor data: {e}")
            return None
    
    def _parse_gear(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse gear from XML"""
        gear_list = []
        
        # Handle Gears root element containing multiple Gear elements - check for local part of tag name
        root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        if root_tag == 'Gears':
            for gear_elem in self._findall_with_namespace(root, 'Gear'):
                gear = self._extract_gear_data(gear_elem)
                if gear:
                    gear_list.append(gear)
        else:
            # Handle single Gear element (fallback)
            gear = self._extract_gear_data(root)
            if gear:
                gear_list.append(gear)
        
        return gear_list
    
    def _extract_gear_data(self, gear_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract gear data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(gear_elem, 'Name'),
                'Description': self._get_text(gear_elem, 'Description'),
                'Type': self._get_text(gear_elem, 'Type', 'general'),  # Read actual Type from XML
                'Encumbrance': self._get_int(gear_elem, 'Encumbrance', 0),
                'Price': self._get_text(gear_elem, 'Price', '0'),
                'Rarity': self._get_int(gear_elem, 'Rarity', 0),
                'Restricted': self._get_text(gear_elem, 'Restricted', 'no'),
                'Consumable': self._get_bool(gear_elem, 'Consumable', False)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('gear', raw_data)
            
            # Set the type in data field
            mapped_data['type'] = 'general'
            
            # Add default values for Realm VTT
            mapped_data.update({
                'modifiers': [],
                'equipEffect': None,
                'hasUseBtn': False,
                'attachments': [],
                'slotsUsed': 0
            })
            
            # Get sources and convert to category
            sources = self._get_sources(gear_elem)
            category = self._get_category_from_sources(sources)
            
            gear = {
                'recordType': 'items',
                'name': mapped_data.get('name', 'Unknown Gear'),
                'description': mapped_data.get('description', ''),
                'sources': sources,
                'category': category,
                'data': mapped_data,
                # 'fields': self._get_gear_fields(),  # Commented out for now
                'fields': {},  # Set to empty dictionary for now
                'unidentifiedName': 'Unidentified Items',
                'locked': True
            }
            return gear
            
        except Exception as e:
            print(f"Error extracting gear data: {e}")
            return None
    
    def _parse_skills(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse skills from XML"""
        skills = []
        for skill_elem in self._findall_with_namespace(root, 'Skill'):
            skill = self._extract_skill_data(skill_elem)
            if skill:
                skills.append(skill)
        return skills
    
    def _extract_skill_data(self, skill_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract skill data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(skill_elem, 'Name'),
                'Description': self._get_text(skill_elem, 'Description'),
                'Key': self._get_text(skill_elem, 'Key'),
                'CharKey': self._get_text(skill_elem, 'CharKey'),
                'TypeValue': self._get_text(skill_elem, 'TypeValue', 'general')
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('skills', raw_data)
            
            # Convert CharKey to Realm VTT characteristic values
            if 'stat' in mapped_data and mapped_data['stat']:
                mapped_data['stat'] = self._convert_char_key_to_stat(mapped_data['stat'])
            
            # Convert TypeValue to Realm VTT group format and set type to 'group'
            if 'type' in mapped_data and mapped_data['type']:
                mapped_data['group'] = self._convert_type_value_to_group(mapped_data['type'])
                mapped_data['type'] = 'group'
            else:
                mapped_data['group'] = 'general'
                mapped_data['type'] = 'group'
            
            # Get sources and convert to category
            sources = self._get_sources(skill_elem)
            category = self._get_category_from_sources(sources)
            
            skill = {
                'recordType': 'skills',
                'name': mapped_data.get('name', 'Unknown Skill'),
                'description': mapped_data.get('description', ''),
                'category': category,
                'sources': sources,  # Add sources field for filtering
                'data': mapped_data,
                'unidentifiedName': 'Unknown Skill',
                'locked': True
            }
            return skill
            
        except Exception as e:
            print(f"Error extracting skill data: {e}")
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
            
            # Get sources and convert to category
            sources = self._get_sources(elem)
            category = self._get_category_from_sources(sources)
            
            record = {
                'recordType': record_type.lower(),
                'name': mapped_data.get('name', f'Unknown {record_type}'),
                'description': mapped_data.get('description', ''),
                'category': category,
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
        child = self._find_with_namespace(elem, tag)
        if child is not None and child.text:
            return child.text.strip()
        return default
    
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
        source_elem = self._find_with_namespace(elem, 'Source')
        if source_elem is not None:
            # Prioritize the text content (source name) over the Page attribute
            return source_elem.text or source_elem.get('Page', '') or ''
        return ''
    
    def _get_sources(self, elem: ET.Element) -> List[str]:
        """Get all sources from XML element (handles multiple sources)"""
        sources = []
        
        # First, check for individual Source tags (single source)
        for source_elem in self._findall_with_namespace(elem, 'Source'):
            if source_elem.text:
                sources.append(source_elem.text.strip())
        
        # Then, check for Sources container with multiple Source tags
        sources_container = self._find_with_namespace(elem, 'Sources')
        if sources_container is not None:
            for source_elem in self._findall_with_namespace(sources_container, 'Source'):
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
            'RANGHVY': 'Ranged (Heavy)',
            'MECH': 'Mechanics',
            'GUNN': 'Gunnery',
            'GUNNERY': 'Gunnery',
            'MELEE': 'Melee',
            'BRAWL': 'Brawl',
            'LIGHTSABER': 'Lightsaber',
            'LTSABER': 'Lightsaber',
            'LIGHT': 'Ranged (Light)',
            'HEAVY': 'Ranged (Heavy)'
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
    
    def _extract_qualities(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract weapon qualities with their counts"""
        qualities = []
        qualities_elem = self._find_with_namespace(elem, 'Qualities')
        if qualities_elem:
            for quality in self._findall_with_namespace(qualities_elem, 'Quality'):
                quality_data = {}
                key_elem = self._find_with_namespace(quality, 'Key')
                if key_elem is not None and key_elem.text:
                    quality_data['Key'] = key_elem.text
                
                count_elem = self._find_with_namespace(quality, 'Count')
                if count_elem is not None and count_elem.text:
                    try:
                        quality_data['Count'] = int(count_elem.text)
                    except ValueError:
                        quality_data['Count'] = 1
                else:
                    quality_data['Count'] = 1
                
                if quality_data:
                    qualities.append(quality_data)
        return qualities
    
    def _extract_starting_chars(self, elem: ET.Element) -> Dict[str, int]:
        """Extract starting characteristics"""
        chars = {}
        chars_elem = self._find_with_namespace(elem, 'StartingChars')
        if chars_elem:
            for char in ['Brawn', 'Agility', 'Intellect', 'Cunning', 'Willpower', 'Presence']:
                chars[char.lower()] = self._get_int(chars_elem, char, 1)
        return chars
    
    def _extract_starting_attrs(self, elem: ET.Element) -> Dict[str, int]:
        """Extract starting attributes"""
        attrs = {}
        attrs_elem = self._find_with_namespace(elem, 'StartingAttrs')
        if attrs_elem:
            attrs['woundThreshold'] = self._get_int(attrs_elem, 'WoundThreshold', 10)
            attrs['strainThreshold'] = self._get_int(attrs_elem, 'StrainThreshold', 10)
            attrs['experience'] = self._get_int(attrs_elem, 'Experience', 0)
        return attrs
    
    def _extract_skill_modifiers(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract skill modifiers"""
        modifiers = []
        mods_elem = self._find_with_namespace(elem, 'SkillModifiers')
        if mods_elem:
            for mod in self._findall_with_namespace(mods_elem, 'SkillModifier'):
                modifiers.append({
                    'skill': self._get_text(mod, 'Key'),
                    'rankStart': self._get_int(mod, 'RankStart', 0),
                    'rankLimit': self._get_int(mod, 'RankLimit', 0)
                })
        return modifiers
    
    def _extract_talent_modifiers(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract talent modifiers"""
        modifiers = []
        mods_elem = self._find_with_namespace(elem, 'TalentModifiers')
        if mods_elem:
            for mod in self._findall_with_namespace(mods_elem, 'TalentModifier'):
                modifiers.append({
                    'talent': self._get_text(mod, 'Key'),
                    'rankAdd': self._get_int(mod, 'RankAdd', 0)
                })
        return modifiers
    
    def _extract_career_skills(self, elem: ET.Element) -> List[str]:
        """Extract career skills"""
        skills = []
        skills_elem = self._find_with_namespace(elem, 'CareerSkills')
        if skills_elem:
            for skill in self._findall_with_namespace(skills_elem, 'Key'):
                if skill.text:
                    skills.append(skill.text)
        return skills
    
    def _extract_specializations(self, elem: ET.Element) -> List[str]:
        """Extract specializations"""
        specs = []
        specs_elem = self._find_with_namespace(elem, 'Specializations')
        if specs_elem:
            for spec in self._findall_with_namespace(specs_elem, 'Key'):
                if spec.text:
                    specs.append(spec.text)
        return specs
    
    def _extract_spec_skills(self, elem: ET.Element) -> List[str]:
        """Extract specialization skills"""
        skills = []
        skills_elem = self._find_with_namespace(elem, 'Skills')
        if skills_elem:
            for skill in self._findall_with_namespace(skills_elem, 'Key'):
                if skill.text:
                    skills.append(skill.text)
        return skills
    
    def _extract_spec_talents(self, elem: ET.Element) -> List[str]:
        """Extract specialization talents"""
        talents = []
        talents_elem = self._find_with_namespace(elem, 'Talents')
        if talents_elem:
            for talent in self._findall_with_namespace(talents_elem, 'Key'):
                if talent.text:
                    talents.append(talent.text)
        return talents
    
    def _extract_upgrades(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract force power upgrades"""
        upgrades = []
        upgrades_elem = self._find_with_namespace(elem, 'Upgrades')
        if upgrades_elem:
            for upgrade in self._findall_with_namespace(upgrades_elem, 'Upgrade'):
                upgrades.append({
                    'name': self._get_text(upgrade, 'Name'),
                    'description': self._get_text(upgrade, 'Description'),
                    'activation': self._get_text(upgrade, 'Activation')
                })
        return upgrades
    
    def _parse_item_attachments(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse item attachments from XML"""
        attachments = []
        for attachment_elem in self._findall_with_namespace(root, 'ItemAttachment'):
            attachment = self._extract_item_attachment_data(attachment_elem)
            if attachment:
                attachments.append(attachment)
        return attachments

    def _extract_item_attachment_data(self, attachment_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract item attachment data from XML element"""
        try:
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(attachment_elem, 'Name'),
                'Description': self._get_text(attachment_elem, 'Description'),
                'Type': self._get_text(attachment_elem, 'Type', 'general'),
                'Price': self._get_text(attachment_elem, 'Price', '0'),
                'Rarity': self._get_int(attachment_elem, 'Rarity', 0),
                'HP': self._get_int(attachment_elem, 'HP', 0),
                'AddedMods': self._extract_added_mods(attachment_elem),
                'BaseMods': self._extract_base_mods(attachment_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('attachments', raw_data)
            
            # Append base modifiers to description if present
            base_mods = raw_data.get('BaseMods', '')
            if base_mods:
                description = mapped_data.get('description', '')
                if description:
                    description += f"\n\n<strong>Base Modifiers:</strong> {base_mods}"
                else:
                    description = f"<strong>Base Modifiers:</strong> {base_mods}"
                mapped_data['description'] = description
            
            # Convert type to Realm VTT format - this should be the main type, not subtype
            attachment_type = raw_data.get('Type', '').lower()
            if attachment_type == 'vehicle':
                mapped_data['type'] = 'vehicle attachment'
            elif attachment_type == 'armor':
                mapped_data['type'] = 'armor attachment'
            elif attachment_type == 'weapon':
                mapped_data['type'] = 'weapon attachment'
            else:
                mapped_data['type'] = 'weapon attachment'
            
            # Set subtype to empty for attachments
            mapped_data['subtype'] = ''
            
            # Add default values for Realm VTT
            mapped_data.update({
                'modifiers': [],
                'equipEffect': None,
                'hasUseBtn': False,
                'attachments': []
            })
            
            # Get sources and convert to category
            sources = self._get_sources(attachment_elem)
            category = self._get_category_from_sources(sources)
            
            attachment = {
                'recordType': 'items',
                'name': mapped_data.get('name', 'Unknown Item Attachment'),
                'description': mapped_data.get('description', ''),
                'category': category,
                'sources': sources,
                'data': mapped_data,
                'fields': {},
                'unidentifiedName': 'Unknown Item Attachment',
                'locked': True
            }
            return attachment
            
        except Exception as e:
            print(f"Error extracting item attachment data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
        """Filter records by selected sources and determine category"""
        if not selected_sources:
            return records
        
        filtered_records = []
        for record in records:
            # Get sources for this record
            sources = record.get('sources', [])
            
            # If the record has no sources (empty list), include it as a universal/core item
            if not sources:
                # Set a default category for universal items
                record['category'] = 'Core'
                filtered_records.append(record)
                continue
            
            # Find the first source that matches our selected sources
            matching_source = None
            for source in sources:
                for source_config in self.sources_config['sources']:
                    if source_config['key'] in selected_sources:
                        # Check if the source matches any of the oggdude_sources for this config
                        for oggdude_source in source_config.get('oggdude_sources', []):
                            if oggdude_source.lower() == source.lower():
                                matching_source = source_config['name']
                                break
                        if matching_source:
                            break
                if matching_source:
                    break
            
            # If we found a matching source, include this record
            if matching_source:
                # Set the category based on the matching source
                record['category'] = matching_source
                filtered_records.append(record)
        
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
            'npcs': [],
            'careers': [],
            'force_powers': [],
            'items': [],
            'signature_abilities': [],
            'skills': [],
            'specializations': [],
            'species': [],
            'talents': []
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
                if record_type == 'items':
                    # All items (weapons, armor, gear, item_attachments) go into the items category
                    all_records['items'].append(record)
                elif record_type in all_records:
                    all_records[record_type].append(record)
                else:
                    print(f"Unknown record type: {record_type}")
        
        # Debug: Print what we found
        print(f"DEBUG: XML parser scan_directory found:")
        for record_type, records in all_records.items():
            if len(records) > 0:
                print(f"  {record_type}: {len(records)}")
        
        return all_records

    def _extract_base_mods(self, elem: ET.Element) -> str:
        """Extract BaseMods and convert to string using ItemDescriptors and Talents"""
        try:
            base_mods_elem = self._find_with_namespace(elem, 'BaseMods')
            if base_mods_elem is None:
                return ""
            
            mods = []
            for mod_elem in self._findall_with_namespace(base_mods_elem, 'Mod'):
                key = self._get_text(mod_elem, 'Key')
                count = self._get_int(mod_elem, 'Count', 1)
                misc_desc = self._get_text(mod_elem, 'MiscDesc')
                
                if key:
                    # First check if it's a talent
                    talent_name = self._get_talent_name(key)
                    if talent_name:
                        mods.append(f"Innate Talent ({talent_name})")
                    else:
                        # Get the description from ItemDescriptors
                        description = self._get_item_descriptor_description(key, use_name=True)
                        if description:
                            # Convert OggDude format to plain text (including dice keys)
                            plain_text = self._convert_oggdude_format_to_plain_text(description)
                            # Replace {0} with the count (even if count is 1)
                            if '{0}' in plain_text:
                                plain_text = plain_text.replace('{0}', str(count))
                            mods.append(plain_text)
                        else:
                            # Fallback if no description found
                            if count > 1:
                                mods.append(f"{key} {count}")
                            else:
                                mods.append(key)
                
                # Add MiscDesc if present
                if misc_desc:
                    # Convert OggDude format to plain text (including dice keys)
                    plain_misc = self._convert_oggdude_format_to_plain_text(misc_desc)
                    mods.append(plain_misc)
            
            # Join with semicolon and clean up any extra whitespace/newlines
            result = "; ".join(mods) if mods else ""
            # Clean up any extra whitespace and newlines
            result = " ".join(result.split())
            return result
            
        except Exception as e:
            print(f"Error extracting base mods: {e}")
            return ""
    
    def _extract_added_mods(self, elem: ET.Element) -> str:
        """Extract AddedMods and convert to string using ItemDescriptors (no rich text conversion)"""
        try:
            added_mods_elem = self._find_with_namespace(elem, 'AddedMods')
            if added_mods_elem is None:
                return ""
            
            mods = []
            for mod_elem in self._findall_with_namespace(added_mods_elem, 'Mod'):
                key = self._get_text(mod_elem, 'Key')
                count = self._get_int(mod_elem, 'Count', 1)
                misc_desc = self._get_text(mod_elem, 'MiscDesc')
                
                if misc_desc:
                    # If MiscDesc is present, use it directly
                    if count > 1:
                        mods.append(f"{count} {misc_desc}")
                    else:
                        mods.append(misc_desc)
                elif key:
                    # Get the description from ItemDescriptors
                    description = self._get_item_descriptor_description(key)
                    if description:
                        # For AddedMods, we want to keep the special string replacements
                        # but NOT convert dice keys like [SE][SE] to rich text
                        # Just do basic {0} replacement
                        if '{0}' in description:
                            description = description.replace('{0}', str(count))
                        # Format as "count ModName" instead of "ModName +count"
                        if count > 1:
                            mods.append(f"{count} {description}")
                        else:
                            mods.append(description)
                    else:
                        # Fallback if no description found
                        if count > 1:
                            mods.append(f"{count} {key}")
                        else:
                            mods.append(key)
                else:
                    # No key or misc_desc, skip this mod
                    continue
            
            return "; ".join(mods) if mods else ""
            
        except Exception as e:
            print(f"Error extracting added mods: {e}")
            return ""
    
    def _get_item_descriptor_description(self, key: str, use_name: bool = False) -> Optional[str]:
        """Get description from ItemDescriptors.xml for a given key"""
        try:
            # Check if we have already loaded ItemDescriptors
            if not hasattr(self, '_item_descriptors'):
                self._load_item_descriptors()
            
            if hasattr(self, '_item_descriptors') and key in self._item_descriptors:
                descriptor = self._item_descriptors[key]
                if use_name:
                    # For BaseMods, use Name field and append ModDesc if available
                    name = descriptor.get('name', '')
                    mod_desc = descriptor.get('modDesc', '')
                    if mod_desc:
                        return f"{name} ({mod_desc})"
                    else:
                        return name
                else:
                    # Use QualDesc for attachments (supports {0} placeholder), fallback to ModDesc, then Description
                    return descriptor.get('qualDesc', descriptor.get('modDesc', descriptor.get('description', '')))
            
            return None
            
        except Exception as e:
            print(f"Error getting item descriptor description for {key}: {e}")
            return None
    
    def _load_talents(self):
        """Load Talents.xml into memory for talent key to name mapping"""
        try:
            # Look for Talents.xml in the same directory as other XML files
            talents_path = None
            
            # Check common locations
            possible_paths = [
                'OggData/Talents.xml',
                '../OggData/Talents.xml',
                './Talents.xml'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    talents_path = path
                    break
            
            if talents_path is None:
                print("Warning: Talents.xml not found, talent key resolution will not work")
                return
            
            print(f"Loading talents from {talents_path}")
            tree = ET.parse(talents_path)
            root = tree.getroot()
            
            # Parse all talents and store key -> name mapping
            for talent_elem in self._findall_with_namespace(root, 'Talent'):
                key = self._get_text(talent_elem, 'Key')
                name = self._get_text(talent_elem, 'Name')
                if key and name:
                    self._talents[key] = name
            
            print(f"Loaded {len(self._talents)} talents")
            
        except Exception as e:
            print(f"Error loading talents: {e}")
    
    def _get_talent_name(self, key: str) -> Optional[str]:
        """Get talent name from key, returns None if not found"""
        if not self._talents:
            self._load_talents()
        return self._talents.get(key)
    
    def _load_item_descriptors(self):
        """Load ItemDescriptors.xml into memory"""
        try:
            # Look for ItemDescriptors.xml in the same directory as other XML files
            item_descriptors_path = None
            
            # Check common locations
            possible_paths = [
                'ItemDescriptors.xml',
                'OggData/ItemDescriptors.xml',
                '../OggData/ItemDescriptors.xml'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    item_descriptors_path = path
                    break
            
            if not item_descriptors_path:
                print("Warning: ItemDescriptors.xml not found")
                self._item_descriptors = {}
                return
            
            tree = ET.parse(item_descriptors_path)
            root = tree.getroot()
            
            self._item_descriptors = {}
            for descriptor_elem in self._findall_with_namespace(root, 'ItemDescriptor'):
                key = self._get_text(descriptor_elem, 'Key')
                if key:
                    self._item_descriptors[key] = {
                        'name': self._get_text(descriptor_elem, 'Name'),
                        'description': self._get_text(descriptor_elem, 'Description'),
                        'modDesc': self._get_text(descriptor_elem, 'ModDesc'),
                        'qualDesc': self._get_text(descriptor_elem, 'QualDesc'),
                        'isQuality': self._get_bool(descriptor_elem, 'IsQuality', False)
                    }
            
            print(f"Loaded {len(self._item_descriptors)} item descriptors")
            
        except Exception as e:
            print(f"Error loading ItemDescriptors.xml: {e}")
            self._item_descriptors = {}
    
    def _convert_oggdude_format_to_plain_text(self, text: str) -> str:
        """Convert OggDude format to plain text"""
        if not text:
            return ""
        
        import re
        
        # Handle multiple instances first (before single replacements)
        # Count and replace multiple instances for each tag type
        di_count = text.count('[DI]')
        if di_count > 1:
            text = text.replace('[DI]' * di_count, f'{di_count} difficulty')
        
        bo_count = text.count('[BO]')
        if bo_count > 1:
            text = text.replace('[BO]' * bo_count, f'{bo_count} Boost')
        
        su_count = text.count('[SU]')
        if su_count > 1:
            text = text.replace('[SU]' * su_count, f'{su_count} success')
        
        ad_count = text.count('[AD]')
        if ad_count > 1:
            text = text.replace('[AD]' * ad_count, f'{ad_count} advantage')
        
        th_count = text.count('[TH]')
        if th_count > 1:
            text = text.replace('[TH]' * th_count, f'{th_count} threat')
        
        ab_count = text.count('[AB]')
        if ab_count > 1:
            text = text.replace('[AB]' * ab_count, f'{ab_count} ability')
        
        pr_count = text.count('[PR]')
        if pr_count > 1:
            text = text.replace('[PR]' * pr_count, f'{pr_count} proficiency')
        
        ch_count = text.count('[CH]')
        if ch_count > 1:
            text = text.replace('[CH]' * ch_count, f'{ch_count} challenge')
        
        se_count = text.count('[SE]')
        if se_count > 1:
            text = text.replace('[SE]' * se_count, f'{se_count} Setback')
        
        fa_count = text.count('[FA]')
        if fa_count > 1:
            text = text.replace('[FA]' * fa_count, f'{fa_count} failure')
        
        tr_count = text.count('[TR]')
        if tr_count > 1:
            text = text.replace('[TR]' * tr_count, f'{tr_count} triumph')
        
        de_count = text.count('[DE]')
        if de_count > 1:
            text = text.replace('[DE]' * de_count, f'{de_count} despair')
        
        # Now handle single instances
        # Convert [BO] to 'Boost'
        text = text.replace('[BO]', 'Boost')
        text = text.replace('[BOOST]', 'Boost')

        # Convert [SE] to 'Setback'
        text = text.replace('[SE]', 'Setback')
        text = text.replace('[SETBACK]', 'Setback')
        
        # Convert [DI] to 'difficulty'
        text = text.replace('[DI]', 'difficulty')
        text = text.replace('[DIFFICULTY]', 'difficulty')

        # Convert [AB] to 'ability'
        text = text.replace('[AB]', 'ability')
        text = text.replace('[ABILITY]', 'ability')

        # Convert [PR] to 'proficiency'
        text = text.replace('[PR]', 'proficiency')
        text = text.replace('[PROFICIENCY]', 'proficiency')

        # Convert [CH] to 'challenge'
        text = text.replace('[CH]', 'challenge')
        text = text.replace('[CHALLENGE]', 'challenge')
        
        # Convert [SU] to 'success'
        text = text.replace('[SU]', 'success')
        text = text.replace('[SUCCESS]', 'success')

        # Convert [FA] to 'failure'
        text = text.replace('[FA]', 'failure')
        text = text.replace('[FAILURE]', 'failure')
        
        # Convert [AD] to 'advantage'
        text = text.replace('[AD]', 'advantage')
        text = text.replace('[ADVANTAGE]', 'advantage')
        
        # Convert [TH] to 'threat'
        text = text.replace('[TH]', 'threat')
        text = text.replace('[THREAT]', 'threat')
        
        # Convert [TR] to 'triumph'
        text = text.replace('[TR]', 'triumph')
        text = text.replace('[TRIUMPH]', 'triumph')
        
        # Convert [DE] to 'despair'
        text = text.replace('[DE]', 'despair')
        text = text.replace('[DESPAIR]', 'despair')
        
        return text.strip() 

    def _convert_char_key_to_stat(self, char_key: str) -> str:
        """Convert OggDude characteristic key to Realm VTT characteristic value"""
        char_mapping = {
            'BR': 'brawn',
            'AG': 'agility', 
            'INT': 'intellect',
            'CUN': 'cunning',
            'WIL': 'willpower',
            'PR': 'presence'
        }
        return char_mapping.get(char_key.upper(), 'intellect')  # Default to intellect if unknown
    
    def _convert_type_value_to_group(self, type_value: str) -> str:
        """Convert OggDude TypeValue to Realm VTT group format"""
        if not type_value:
            return 'general'
        
        # Remove 'st' prefix if present
        if type_value.startswith('st'):
            return type_value[2:]  # Remove first 2 characters ('st')
        
        return type_value 