import xml.etree.ElementTree as ET
import os
import json
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path

class XMLParser:
    def __init__(self, data_dir: Optional[str] = None):
        # Use provided data_dir or fall back to default
        if data_dir:
            self.data_dir = data_dir
        else:
            self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'OggData')
        
        self.field_mapping = self._load_field_mapping()
        self.sources_config = self._load_sources_config()
        self._talents = {}  # Will store talent keys to names mapping
        self._skills = {}   # Will store skill keys to names mapping
        self._talent_specializations = {}  # Will store talent-to-specialization mapping
        self._specializations = {}  # Will store specialization keys to names mapping
        self._careers = {}  # Will store career keys to names mapping
        self._force_abilities = {}  # Will store force ability keys to data mapping
        self._vehicle_actions = {}  # Will store vehicle action keys to data mapping
        self._items_loader = None  # Shared items loader for vehicle weapon lookup
        
        # Load reference data
        self._load_talents()
        self._load_skills()
        self._load_item_descriptors()
        self._load_specialization_trees()
        self._load_specializations()
        self._load_careers()
        self._load_force_abilities()
        self._load_vehicle_actions()
        self._init_items_loader()
    
    def set_data_directory(self, data_dir: str):
        """Set the data directory and reload reference data"""
        self.data_dir = data_dir
        # Reload reference data with new directory
        self._talents = {}
        self._skills = {}
        self._talent_specializations = {}
        self._item_descriptors = {}
        self._specializations = {}
        self._careers = {}
        self._force_abilities = {}
        
        self._load_talents()
        self._load_skills()
        self._load_item_descriptors()
        self._load_specialization_trees()
        self._load_specializations()
        self._load_careers()
        self._load_force_abilities()
    
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
            "Enter the Unknown": "Enter the Unknown",
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
            elif root_tag == 'SigAbility':
                records = self._parse_sig_ability(root)
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
            # Get the weapon key for duplicate checking
            weapon_key = self._get_text(weapon_elem, 'Key')
            
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(weapon_elem, 'Name'),
                'Description': self._get_text(weapon_elem, 'Description'),
                'Type': self._get_text(weapon_elem, 'Type', 'ranged weapon'),
                'Encumbrance': self._get_int(weapon_elem, 'Encumbrance', 0),
                'Price': self._get_text(weapon_elem, 'Price', '0'),
                'Rarity': self._get_int(weapon_elem, 'Rarity', 0),
                'Restricted': self._get_bool(weapon_elem, 'Restricted', False),
                'SkillKey': self._get_text(weapon_elem, 'SkillKey'),
                'Damage': self._get_int(weapon_elem, 'Damage', 0),
                'DamageAdd': self._get_int(weapon_elem, 'DamageAdd', 0),
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
            
            # Handle damage logic: use DamageAdd if set, otherwise use Damage
            damage_add = raw_data.get('DamageAdd', 0)
            base_damage = raw_data.get('Damage', 0)
            
            if damage_add and damage_add > 0:
                mapped_data['damage'] = damage_add
            else:
                mapped_data['damage'] = base_damage
            
            # Handle noAddBrawn field for melee weapons
            # Set to true if it's a melee weapon (Melee, Lightsaber, or Brawl) and DamageAdd is not set
            is_melee_weapon = original_skill_key in ['MELEE', 'BRAWL', 'LIGHTSABER', 'LTSABER']
            has_damage_add = damage_add and damage_add > 0
            
            if is_melee_weapon and not has_damage_add:
                mapped_data['noAddBrawn'] = True
            else:
                mapped_data['noAddBrawn'] = False
            
            # Clean up the temporary damageAdd field since it's not needed in Realm
            mapped_data.pop('damageAdd', None)
            
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
                'locked': True,
                'key': weapon_key  # Store the key for duplicate checking
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
            # Get the species key for duplicate checking
            species_key = self._get_text(species_elem, 'Key')
            
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
            
            # Convert description to rich text format
            if 'description' in mapped_data and mapped_data['description']:
                mapped_data['description'] = self._convert_oggdude_format_to_rich_text(mapped_data['description'])
            
            # Map starting characteristics to individual fields
            starting_chars = raw_data.get('StartingChars', {})
            if starting_chars:
                mapped_data['brawn'] = starting_chars.get('brawn', 1)
                mapped_data['agility'] = starting_chars.get('agility', 1)
                mapped_data['intellect'] = starting_chars.get('intellect', 1)
                mapped_data['cunning'] = starting_chars.get('cunning', 1)
                mapped_data['willpower'] = starting_chars.get('willpower', 1)
                mapped_data['presence'] = starting_chars.get('presence', 1)
            
            # Map starting attributes to individual fields
            starting_attrs = raw_data.get('StartingAttrs', {})
            if starting_attrs:
                mapped_data['woundThreshold'] = starting_attrs.get('woundThreshold', 10)
                mapped_data['strainThreshold'] = starting_attrs.get('strainThreshold', 10)
                mapped_data['startingXp'] = starting_attrs.get('experience', 0)
            
            # Convert skill modifiers to text format
            skill_modifiers = raw_data.get('SkillModifiers', [])
            if skill_modifiers:
                mapped_data['startingSkills'] = self._convert_skill_modifiers_to_text(skill_modifiers)
            else:
                mapped_data['startingSkills'] = ""
            
            # Extract option choices (species abilities)
            features = self._extract_option_choices(species_elem)
            if features:
                mapped_data['features'] = features
            else:
                mapped_data['features'] = []
            
            # Get sources and convert to category
            sources = self._get_sources(species_elem)
            category = self._get_category_from_sources(sources)
            
            species = {
                'recordType': 'species',
                'name': mapped_data.get('name', 'Unknown Species'),
                'description': mapped_data.get('description', ''),
                'sources': sources,  # Store sources for filtering
                'category': category,
                'data': mapped_data,
                'unidentifiedName': 'Unknown Species',
                'locked': True,
                'key': species_key  # Store the key for duplicate checking
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
            # Get the career key for duplicate checking
            career_key = self._get_text(career_elem, 'Key')
            
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(career_elem, 'Name'),
                'Description': self._get_text(career_elem, 'Description'),
                'CareerSkills': self._extract_career_skills(career_elem),
                'Specializations': self._extract_specializations(career_elem),
                'ForceRating': self._extract_force_rating(career_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('careers', raw_data)
            
            # Convert career skills from keys to names
            career_skills = raw_data.get('CareerSkills', [])
            if career_skills:
                skill_names = []
                for skill_key in career_skills:
                    skill_name = self._get_skill_name(skill_key)
                    if skill_name:
                        # Convert skill name to handle hyphens
                        converted_skill_name = self._convert_skill_name(skill_name)
                        skill_names.append(converted_skill_name)
                    else:
                        # If we can't find the skill name, use the key
                        skill_names.append(skill_key)
                mapped_data['skills'] = ', '.join(skill_names)
            else:
                mapped_data['skills'] = ''
            
            # Convert specializations from keys to names
            specializations = raw_data.get('Specializations', [])
            if specializations:
                spec_names = []
                for spec_key in specializations:
                    spec_name = self._get_specialization_name(spec_key)
                    if spec_name:
                        spec_names.append(spec_name)
                    else:
                        # If we can't find the specialization name, use the key
                        spec_names.append(spec_key)
                mapped_data['specializations'] = ', '.join(spec_names)
            else:
                mapped_data['specializations'] = ''
            
            # Set force rating
            force_rating = raw_data.get('ForceRating', 0)
            if force_rating > 0:
                mapped_data['forceRating'] = force_rating
            
            # Get sources and convert to category
            sources = self._get_sources(career_elem)
            category = self._get_category_from_sources(sources)
            
            career = {
                'recordType': 'careers',
                'name': mapped_data.get('name', 'Unknown Career'),
                'description': mapped_data.get('description', ''),
                'sources': sources,  # Store sources for filtering
                'category': category,
                'data': mapped_data,
                'unidentifiedName': 'Unknown Career',
                'locked': True,
                'key': career_key  # Store the key for duplicate checking
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
            # Get the specialization key for duplicate checking
            spec_key = self._get_text(spec_elem, 'Key')
            
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(spec_elem, 'Name'),
                'Description': self._get_text(spec_elem, 'Description'),
                'CareerKey': self._get_text(spec_elem, 'CareerKey'),
                'CareerSkills': self._extract_career_skills_from_spec(spec_elem),
                'TalentRows': self._extract_talent_rows(spec_elem),
                'Directions': self._extract_directions(spec_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('specializations', raw_data)
            
            # Convert description to rich text format
            if 'description' in mapped_data and mapped_data['description']:
                mapped_data['description'] = self._convert_oggdude_format_to_rich_text(mapped_data['description'])
            
            # Convert career skills from keys to names
            career_skills = raw_data.get('CareerSkills', [])
            if career_skills:
                skill_names = []
                for skill_key in career_skills:
                    skill_name = self._get_skill_name(skill_key)
                    if skill_name:
                        # Convert skill name to handle hyphens
                        converted_skill_name = self._convert_skill_name(skill_name)
                        skill_names.append(converted_skill_name)
                    else:
                        # If we can't find the skill name, use the key
                        skill_names.append(skill_key)
                mapped_data['skills'] = ', '.join(skill_names)
            else:
                mapped_data['skills'] = ''
            
            # Find all careers for this specialization (some specializations work in multiple careers)
            career_names = self._find_careers_for_specialization(spec_key)
            if career_names:
                mapped_data['career'] = career_names
            else:
                mapped_data['career'] = []
            
            # Process talent rows and convert to Realm VTT format
            talent_rows = raw_data.get('TalentRows', [])
            if talent_rows:
                self._process_talent_rows(mapped_data, talent_rows)
            
            # Remove the 'talents' field that was added by field mapping since we handle talents differently
            mapped_data.pop('talents', None)
            
            # Process directions and convert to Realm VTT format
            directions = raw_data.get('Directions', [])
            if directions:
                self._process_directions(mapped_data, talent_rows)
            
            # Clean up fields that shouldn't be sent to Realm
            mapped_data.pop('CareerSkills', None)
            mapped_data.pop('TalentRows', None)
            mapped_data.pop('Directions', None)
            
            # Get sources and convert to category
            sources = self._get_sources(spec_elem)
            category = self._get_category_from_sources(sources)
            
            spec = {
                'recordType': 'specializations',
                'name': mapped_data.get('name', 'Unknown Specialization'),
                'description': mapped_data.get('description', ''),
                'sources': sources,  # Store sources for filtering
                'category': category,
                'data': mapped_data,
                'unidentifiedName': 'Unknown Specialization',
                'locked': True,
                'key': spec_key  # Store the key for duplicate checking
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
            # Get the talent key for specialization tree lookup
            talent_key = self._get_text(talent_elem, 'Key')
            
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(talent_elem, 'Name'),
                'Description': self._get_text(talent_elem, 'Description'),
                'ActivationValue': self._get_text(talent_elem, 'ActivationValue'),
                'Ranked': self._get_bool(talent_elem, 'Ranked', False),
                'ForceTalent': self._get_bool(talent_elem, 'ForceTalent', False),
                'Trees': self._get_talent_specializations(talent_key) if talent_key else []
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('talents', raw_data)

            # Apply conversions for specific fields
            # Get tags from activation value BEFORE converting it
            if 'activation' in mapped_data:
                activation_tags = self._get_tags_from_activation(mapped_data['activation'])
                if activation_tags:
                    mapped_data['tags'] = activation_tags
                mapped_data['activation'] = self._convert_activation_value(mapped_data['activation'])

            if 'ranked' in mapped_data:
                mapped_data['ranked'] = self._convert_boolean_to_yes_no(mapped_data['ranked'])

            if 'forceTalent' in mapped_data:
                mapped_data['forceTalent'] = self._convert_boolean_to_yes_no(mapped_data['forceTalent'])
            
            # Special handling for "Adversary" talent
            talent_name = mapped_data.get('name', '')
            if talent_name == 'Adversary':
                mapped_data['modifiers'] = [
                    {
                        "_id": "80ec474f-faea-4179-b19b-a66a4ba4de8b",
                        "name": "Modifier",
                        "unidentifiedName": "Modifier",
                        "recordType": "records",
                        "identified": True,
                        "data": {
                            "type": "upgradeDifficultyOfAttacksTargetingYou",
                            "valueType": "number",
                            "value": "1",
                            "active": True
                        }
                    }
                ]
            
            # Get sources and convert to category
            sources = self._get_sources(talent_elem)
            category = self._get_category_from_sources(sources)
            
            talent = {
                'recordType': 'talents',
                'name': mapped_data.get('name', 'Unknown Talent'),
                'description': mapped_data.get('description', ''),
                'sources': sources,  # Store sources for filtering
                'category': category,
                'data': mapped_data,
                'unidentifiedName': 'Unknown Talent',
                'locked': True,
                'key': talent_key  # Store the key for duplicate checking
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
        """Extract force power data from XML element with talent tree structure"""
        try:
            # Get the force power key for duplicate checking
            power_key = self._get_text(power_elem, 'Key')
            
            # Extract basic raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(power_elem, 'Name'),
                'Description': self._get_text(power_elem, 'Description'),
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('force_powers', raw_data)
            
            # Convert description to rich text format
            if 'description' in mapped_data and mapped_data['description']:
                mapped_data['description'] = self._convert_oggdude_format_to_rich_text(mapped_data['description'])
            
            # Get sources and convert to category
            sources = self._get_sources(power_elem)
            category = self._get_category_from_sources(sources)
            
            # Extract ability rows structure similar to signature abilities
            ability_rows_elem = power_elem.find('AbilityRows')
            if ability_rows_elem is not None:
                ability_rows = self._extract_ability_rows(ability_rows_elem)
                
                if ability_rows:
                    # Process first row to get base ability description and cost
                    first_row = ability_rows[0]
                    abilities = first_row.get('abilities', [])
                    costs = first_row.get('costs', [])
                    
                    
                    if abilities:
                        base_ability_key = abilities[0]  # Get the first ability key
                        base_description = self._get_force_ability_description(base_ability_key)
                        if base_description:
                            # Convert base description to rich text and add to main description
                            rich_base_description = self._convert_oggdude_format_to_rich_text(base_description)
                            if mapped_data.get('description'):
                                mapped_data['description'] += f"<br><br><strong>Base Ability:</strong> {rich_base_description}"
                            else:
                                mapped_data['description'] = f"<strong>Base Ability:</strong> {rich_base_description}"
                        
                        # Calculate base cost as the highest cost in the first row
                        if costs:
                            base_cost = max(costs)
                            mapped_data['cost'] = base_cost
                    
                    # Add MinForceRating as prerequisite
                    min_force_rating = self._get_text(power_elem, 'MinForceRating')
                    if min_force_rating and min_force_rating != '1':
                        mapped_data['prereqs'] = f"Force Rating {min_force_rating}+"
                    else:
                        mapped_data['prereqs'] = "Force Rating 1+"
                    
                    # Process talent rows (skip first row which is the base ability)
                    self._process_force_power_talent_rows(mapped_data, ability_rows[1:])
                    
                    # Generate connector fields for the force power tree
                    self._generate_force_power_connectors(mapped_data, ability_rows)
                    
                    # Generate fields structure for hiding talents and connectors
                    fields = self._generate_force_power_fields(ability_rows[1:])  # Skip first row
                else:
                    fields = {}
            else:
                fields = {}
            
            power = {
                'recordType': 'force_powers',
                'name': mapped_data.get('name', 'Unknown Force Power'),
                'description': mapped_data.get('description', ''),
                'sources': sources,  # Store sources for filtering
                'category': category,
                'data': mapped_data,
                'fields': fields,
                'unidentifiedName': 'Unknown Force Power',
                'locked': True,
                'key': power_key  # Store the key for duplicate checking
            }
            return power
            
        except Exception as e:
            print(f"Error extracting force power data: {e}")
            return None
    
    def _process_force_power_talent_rows(self, mapped_data: Dict[str, Any], talent_rows: List[Dict[str, Any]]):
        """Process force power talent rows similar to signature abilities but with AbilitySpan support"""
        try:
            for row_index, row_data in enumerate(talent_rows):
                actual_row_index = row_index + 1  # Skip row 0 which is the base ability
                abilities = row_data.get('abilities', [])
                costs = row_data.get('costs', [])
                spans = row_data.get('spans', [])
                
                # Process each ability in the row with span consideration
                for col_index, ability_key in enumerate(abilities):
                    if ability_key:  # Skip empty abilities
                        col_number = col_index + 1
                        talent_field = f"talent{actual_row_index}_{col_number}"
                        
                        # Check if this talent should be hidden based on span
                        should_hide = self._should_hide_talent_by_span(spans, col_index)
                        
                        if should_hide:
                            # Set hide field for this position
                            hide_field = f"hide{actual_row_index}_{col_number}"
                            mapped_data[hide_field] = "Yes"
                            mapped_data[talent_field] = []  # Empty array for hidden talents
                        else:
                            # Create the talent data
                            talent_data = self._create_force_power_talent(
                                ability_key, costs[col_index] if col_index < len(costs) else 0
                            )
                            if talent_data:
                                mapped_data[talent_field] = [talent_data]
        except Exception as e:
            print(f"Error processing force power talent rows: {e}")
    
    def _should_hide_talent_by_span(self, spans: List[int], col_index: int) -> bool:
        """Determine if a talent should be hidden based on AbilitySpan values"""
        if not spans or col_index >= len(spans):
            return False
        
        # If span is 0, this position should be hidden
        if spans[col_index] == 0:
            return True
        
        # If this is not the first column, check if a previous column spans into this one
        for prev_col in range(col_index):
            if prev_col < len(spans):
                prev_span = spans[prev_col]
                # If previous column spans enough to reach this column, hide this one
                if prev_span > 1 and (prev_col + prev_span > col_index):
                    return True
        
        return False
    
    def _create_force_power_talent(self, ability_key: str, cost: int) -> Optional[Dict[str, Any]]:
        """Create a force power talent object similar to signature ability talents"""
        try:
            # Get ability data from Force Abilities
            ability_data = self._force_abilities.get(ability_key)
            if not ability_data:
                print(f"Warning: Force ability '{ability_key}' not found in Force Abilities")
                return None
            
            talent_name = ability_data.get('name', 'Unknown Upgrade')
            talent_description = ability_data.get('description', '')
            
            # Convert description to rich text format
            rich_description = self._convert_oggdude_format_to_rich_text(talent_description)
            
            # Create the talent data structure
            talent_data = {
                "_id": self._generate_uuid(),
                "name": talent_name,
                "unidentifiedName": "Upgrade",
                "recordType": "talents",
                "identified": True,
                "icon": "IconStar",
                "data": {
                    "talentAccordion": None,
                    "description": rich_description,
                    "ranked": "yes",
                    "cost": cost,
                    "forceTalent": "yes",
                    "forcePowerUpgrade": "yes"
                },
                "fields": {
                    "specializationTrees": {
                        "hidden": True
                    }
                }
            }
            
            return talent_data
            
        except Exception as e:
            print(f"Error creating force power talent: {e}")
            return None
    
    def _generate_force_power_connectors(self, mapped_data: Dict[str, Any], ability_rows: List[Dict[str, Any]]):
        """Generate connector fields for force power similar to signature abilities"""
        try:
            # Generate vertical connectors - skip first row (base ability)
            for row_index in range(1, len(ability_rows)):
                row_data = ability_rows[row_index]
                directions = row_data.get('directions', [])
                
                for col_index, direction in enumerate(directions):
                    col_number = col_index + 1
                    connector_field = f"connector{row_index}_{col_number}"
                    
                    # Check if this talent has a connection up to the previous row
                    has_connection = direction.get('up', False)
                    mapped_data[connector_field] = "Yes" if has_connection else "No"
            
            # Generate horizontal connectors for all rows including first row
            for row_index in range(len(ability_rows)):
                row_data = ability_rows[row_index]
                directions = row_data.get('directions', [])
                spans = row_data.get('spans', [])
                
                for col_index, direction in enumerate(directions):
                    col_number = col_index + 1
                    
                    # Generate horizontal connector for talents that span multiple columns
                    # or connect to the right
                    if col_number < 4:  # Don't create h_connector for last column
                        h_connector_field = f"h_connector{row_index}_{col_number + 1}"
                        
                        # Check span logic - if current position has span > 1, create horizontal connector
                        current_span = spans[col_index] if col_index < len(spans) else 1
                        has_h_connection = (
                            current_span > 1 or  # Multi-column span
                            direction.get('right', False)  # Right connection
                        )
                        
                        mapped_data[h_connector_field] = "Yes" if has_h_connection else "No"
                        
        except Exception as e:
            print(f"Error generating force power connectors: {e}")
    
    def _generate_force_power_fields(self, talent_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fields structure to hide talents and connectors based on AbilitySpan"""
        fields = {}
        try:
            for row_index, row_data in enumerate(talent_rows):
                actual_row_index = row_index + 1  # Skip row 0 which is the base ability
                spans = row_data.get('spans', [])
                
                for col_index in range(4):  # Force Powers typically have 4 columns
                    col_number = col_index + 1
                    
                    # Check if this talent should be hidden
                    should_hide = self._should_hide_talent_by_span(spans, col_index)
                    
                    if should_hide:
                        # Hide the talent field
                        talent_field = f"talent{actual_row_index}_{col_number}"
                        fields[talent_field] = {"hidden": True}
                        
                        # Show the no_talent field
                        no_talent_field = f"no_talent{actual_row_index}_{col_number}"
                        fields[no_talent_field] = {"hidden": False}
                        
                        # Hide the horizontal connector field if applicable
                        if col_number > 1:  # No h_connector for column 1
                            h_connector_field = f"h_connector{actual_row_index}_{col_number}"
                            fields[h_connector_field] = {"hidden": True}
        except Exception as e:
            print(f"Error generating force power fields: {e}")
        
        return fields
    
    def _parse_vehicle(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse vehicle from XML - vehicles are npcs in Realm VTT"""
        vehicle = self._extract_vehicle_data(root)
        return [vehicle] if vehicle else []
    
    def _extract_vehicle_data(self, vehicle_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract vehicle data from XML element and convert to NPC format"""
        try:
            # Get basic info
            key = self._get_text(vehicle_elem, 'Key')
            name = self._get_text(vehicle_elem, 'Name')
            description = self._get_text(vehicle_elem, 'Description', '')
            source = self._get_text(vehicle_elem, 'Source', '')
            
            # Convert description to rich text
            if description:
                description = self._convert_oggdude_format_to_rich_text(description)
            
            # 1. Ignore Categories tag - not implemented
            
            # 2. Use Type as subtype
            subtype = self._get_text(vehicle_elem, 'Type', '')
            
            # 3. Convert SensorRangeValue (remove 'sr' prefix)
            sensor_range = self._get_text(vehicle_elem, 'SensorRangeValue', '')
            if sensor_range.startswith('sr'):
                sensor_range = sensor_range[2:]  # Remove 'sr' prefix
            
            # 4. Format hyperdrive from Primary/Backup values
            hyperdrive_primary = self._get_text(vehicle_elem, 'HyperdrivePrimary', '')
            hyperdrive_backup = self._get_text(vehicle_elem, 'HyperdriveBackup', '')
            hyperdrive = ''
            if hyperdrive_primary and hyperdrive_backup:
                hyperdrive = f"Class {hyperdrive_primary} (backup Class {hyperdrive_backup})"
            elif hyperdrive_primary:
                hyperdrive = f"Class {hyperdrive_primary}"
            
            # 5. Convert NaviComputer to boolean
            navicomputer_text = self._get_text(vehicle_elem, 'NaviComputer', 'false').lower()
            navicomputer = navicomputer_text == 'true'
            
            # Parse restricted same as items - "Yes" or "No"
            restricted_bool = self._get_text(vehicle_elem, 'Restricted', 'false').lower() == 'true'
            restricted = "yes" if restricted_bool else "no"
            
            # 6. Handle numeric conversions
            try:
                passengers = int(self._get_text(vehicle_elem, 'Passengers', '0'))
            except ValueError:
                passengers = 0
            
            try:
                encumbrance = int(self._get_text(vehicle_elem, 'EncumbranceCapacity', '0'))
            except ValueError:
                encumbrance = 0
                
            try:
                hardpoints = int(self._get_text(vehicle_elem, 'HP', '0'))
            except ValueError:
                hardpoints = 0
            
            # 7. Parse Silhouette to "Silhouette X" format
            silhouette_value = self._get_text(vehicle_elem, 'Silhouette', '0')
            silhouette = f"Silhouette {silhouette_value}"
            
            # 8. Map defense zones
            defense = {
                'fore': int(self._get_text(vehicle_elem, 'DefFore', '0')),
                'aft': int(self._get_text(vehicle_elem, 'DefAft', '0')),
                'port': int(self._get_text(vehicle_elem, 'DefPort', '0')),
                'starboard': int(self._get_text(vehicle_elem, 'DefStarboard', '0'))
            }
            
            # 9. Handle vehicle weapons as inventory items
            inventory = []
            vehicle_weapons = vehicle_elem.find('VehicleWeapons')
            if vehicle_weapons is not None:
                for weapon_element in vehicle_weapons.findall('VehicleWeapon'):
                    weapon_item = self._parse_vehicle_weapon(weapon_element)
                    if weapon_item:
                        inventory.append(weapon_item)
            
            # 10. Add all vehicle actions to features array
            features = []
            for action_key, action_data in self._vehicle_actions.items():
                features.append({
                    'name': action_data['name'],
                    'description': action_data['description']
                })
            
            # Get sources and convert to category  
            sources = self._get_sources(vehicle_elem)
            category = self._get_category_from_sources(sources)
            
            # Build the vehicle data as NPC format
            vehicle_data = {
                'recordType': 'npcs',
                'name': name,
                'description': description,
                'sources': sources,
                'category': category,
                'data': {
                    'type': 'vehicle',
                    'subtype': subtype,
                    'sensorRange': sensor_range,
                    'hyperdrive': hyperdrive,
                    'navicomputer': navicomputer,
                    'restricted': restricted,
                    'crew': self._get_text(vehicle_elem, 'Crew', ''),
                    'passengers': passengers,
                    'encumbrance': encumbrance,
                    'consumables': self._get_text(vehicle_elem, 'Consumables', ''),
                    'silhouette': silhouette,
                    'speed': int(self._get_text(vehicle_elem, 'Speed', '0')),
                    'handling': int(self._get_text(vehicle_elem, 'Handling', '0')),
                    'defense': defense,
                    'armor': int(self._get_text(vehicle_elem, 'Armor', '0')),
                    'hullTrauma': int(self._get_text(vehicle_elem, 'HullTrauma', '0')),
                    'systemStrain': int(self._get_text(vehicle_elem, 'SystemStrain', '0')),
                    'hardpoints': hardpoints,
                    'price': int(self._get_text(vehicle_elem, 'Price', '0')),
                    'rarity': int(self._get_text(vehicle_elem, 'Rarity', '0')),
                    'starship': self._get_text(vehicle_elem, 'Starship', 'false').lower() == 'true',
                    'inventory': inventory,
                    'features': features
                },
                'unidentifiedName': 'Unknown Vehicle',
                'locked': True,
                'key': key  # Store the key for duplicate checking
            }
            
            return vehicle_data
            
        except Exception as e:
            print(f"Error extracting vehicle data: {e}")
            return None

    def _parse_vehicle_weapon(self, weapon_element) -> Optional[Dict[str, Any]]:
        """Parse a vehicle weapon as an inventory item by looking up from Items cache"""
        try:
            key = self._get_text(weapon_element, 'Key', '')
            location = self._get_text(weapon_element, 'Location', '')
            is_turret = self._get_text(weapon_element, 'Turret', 'false').lower() == 'true'
            count = int(self._get_text(weapon_element, 'Count', '1'))

            # Parse firing arcs
            firing_arcs = []
            firing_arcs_element = weapon_element.find('FiringArcs')
            if firing_arcs_element is not None:
                for arc in ['Fore', 'Aft', 'Port', 'Starboard', 'Dorsal', 'Ventral']:
                    if self._get_text(firing_arcs_element, arc, 'false').lower() == 'true':
                        firing_arcs.append(arc.lower())

            # Parse vehicle-specific qualities
            vehicle_qualities = self._extract_qualities(weapon_element)

            # Look up the item from our items loader
            base_item = self._items_loader.get_item_by_key(key)
            if not base_item:
                print(f"Warning: Vehicle weapon with key '{key}' not found in items cache")
                return None

            # Make a deep copy of the item to avoid modifying the cached version
            import copy
            weapon_item = copy.deepcopy(base_item)

            # Add location to weapon name in parentheses
            if location:
                weapon_item['name'] = f"{weapon_item['name']} ({location})"

            # Merge vehicle-specific qualities with base weapon qualities
            if vehicle_qualities:
                # Get existing qualities from the raw data field
                if 'data' not in weapon_item:
                    weapon_item['data'] = {}

                # The weapon should have 'Qualities' in raw data before field mapping
                # We need to add vehicle qualities to this list
                if 'Qualities' not in weapon_item.get('data', {}):
                    weapon_item['data']['Qualities'] = []

                # Merge qualities - if a quality exists in both, keep the vehicle one
                existing_keys = {q.get('Key'): q for q in weapon_item['data']['Qualities']}
                for vehicle_quality in vehicle_qualities:
                    quality_key = vehicle_quality.get('Key')
                    if quality_key:
                        # Vehicle quality overrides base weapon quality
                        existing_keys[quality_key] = vehicle_quality

                weapon_item['data']['Qualities'] = list(existing_keys.values())

            # Add vehicle-specific information to the description (without firing arcs)
            vehicle_info_parts = []
            vehicle_info_parts.append(f"<strong>Location:</strong> {location}")
            
            if is_turret:
                vehicle_info_parts.append(f"<strong>Turret:</strong> Yes")
            else:
                vehicle_info_parts.append(f"<strong>Turret:</strong> No")
            
            # Add vehicle info to the end of the description
            if vehicle_info_parts:
                vehicle_info = "<br><br>" + "<br>".join(vehicle_info_parts)
                current_desc = weapon_item.get('description', '')
                weapon_item['description'] = current_desc + vehicle_info
            
            # Add the proper fields structure from your example
            weapon_item['fields'] = {
                "accurate": {"hidden": True},
                "blast": {"hidden": True},
                "breach": {"hidden": True},
                "burn": {"hidden": True},
                "concussive": {"hidden": True},
                "consumable": {"hidden": True},
                "cumbersome": {"hidden": True},
                "defensive": {"hidden": True},
                "deflection": {"hidden": True},
                "disorient": {"hidden": True},
                "ensnare": {"hidden": True},
                "guided": {"hidden": True},
                "hasUseBtn": {"hidden": False},
                "inaccurate": {"hidden": True},
                "limitedAmmo": {"hidden": True},
                "linked": {"hidden": True},
                "pierce": {"hidden": True},
                "prepare": {"hidden": True},
                "slowFiring": {"hidden": True},
                "stun": {"hidden": True},
                "tractor": {"hidden": True},
                "vicious": {"hidden": True},
                "animationProps": {"hidden": False},
                "armorAttachmentProperties": {"hidden": True},
                "armorProperties": {"hidden": True},
                "attackDividerBox": {"hidden": False},
                "autoFireBtn": {"hidden": False},
                "consumableProperties": {"hidden": True},
                "generalWeaponProperties": {"hidden": False},
                "hardpoints": {"hidden": False},
                "itemQualities": {"hidden": False},
                "packProperties": {"hidden": True},
                "stunBtn": {"hidden": True},
                "weaponAttached": {"hidden": True},
                "weaponAttachedLabel": {"hidden": True},
                "weaponAttachmentProperties": {"hidden": True},
                "weaponProperties": {"hidden": False},
                "weaponType": {"hidden": True},
                "attachmentsProperties": {"hidden": True},
                "useBtn": {"hidden": True},
                "attachments": {"hidden": True}
            }
            
            # Ensure proper structure for inventory items
            if 'data' not in weapon_item:
                weapon_item['data'] = {}
            
            # Set carried status for vehicle weapons
            weapon_item['data']['carried'] = 'equipped'
            weapon_item['data']['count'] = count
            
            # Add firing arcs as proper field
            weapon_item['data']['firingArc'] = firing_arcs
            
            return weapon_item
            
        except Exception as e:
            print(f"Error parsing vehicle weapon: {e}")
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
            # Get the armor key for duplicate checking
            armor_key = self._get_text(armor_elem, 'Key')
            
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(armor_elem, 'Name'),
                'Description': self._get_text(armor_elem, 'Description'),
                'Type': 'armor',
                'Encumbrance': self._get_int(armor_elem, 'Encumbrance', 0),
                'Price': self._get_text(armor_elem, 'Price', '0'),
                'Rarity': self._get_int(armor_elem, 'Rarity', 0),
                'Restricted': self._get_bool(armor_elem, 'Restricted', False),
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
                'locked': True,
                'key': armor_key  # Store the key for duplicate checking
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
            # Get the gear key for duplicate checking
            gear_key = self._get_text(gear_elem, 'Key')
            
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(gear_elem, 'Name'),
                'Description': self._get_text(gear_elem, 'Description'),
                'Type': self._get_text(gear_elem, 'Type', 'general'),  # Read actual Type from XML
                'Encumbrance': self._get_int(gear_elem, 'Encumbrance', 0),
                'Price': self._get_text(gear_elem, 'Price', '0'),
                'Rarity': self._get_int(gear_elem, 'Rarity', 0),
                'Restricted': self._get_bool(gear_elem, 'Restricted', False),
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
                'locked': True,
                'key': gear_key  # Store the key for duplicate checking
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
            # Get the skill key for duplicate checking
            skill_key = self._get_text(skill_elem, 'Key')
            
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
                'locked': True,
                'key': skill_key  # Store the key for duplicate checking
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
            # Get the key for duplicate checking
            key = self._get_text(elem, 'Key')
            
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
                'sources': sources,  # Store sources for filtering
                'category': category,
                'data': mapped_data,
                'unidentifiedName': f'Unknown {record_type}',
                'locked': True,
                'key': key  # Store the key for duplicate checking
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
    
    def _generate_uuid(self) -> str:
        """Generate a UUID string"""
        return str(uuid.uuid4())
    
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
            # Get the attachment key for duplicate checking
            attachment_key = self._get_text(attachment_elem, 'Key')
            
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
                'locked': True,
                'key': attachment_key  # Store the key for duplicate checking
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
        
        # Track seen keys to prevent duplicates for all record types
        seen_keys = {
            'npcs': set(),
            'careers': set(),
            'force_powers': set(),
            'items': set(),
            'signature_abilities': set(),
            'skills': set(),
            'specializations': set(),
            'species': set(),
            'talents': set()
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
            
            # Categorize records by type and check for duplicates
            for record in records:
                record_type = record.get('recordType', 'unknown')
                record_key = record.get('key', '')
                
                if record_type == 'items':
                    # All items (weapons, armor, gear, item_attachments) go into the items category
                    if record_key and record_key in seen_keys['items']:
                        print(f"Skipping duplicate item with key: {record_key}")
                        continue
                    if record_key:
                        seen_keys['items'].add(record_key)
                    all_records['items'].append(record)
                elif record_type in all_records:
                    # Check for duplicates based on key
                    if record_key and record_key in seen_keys[record_type]:
                        print(f"Skipping duplicate {record_type} with key: {record_key}")
                        continue
                    if record_key:
                        seen_keys[record_type].add(record_key)
                    all_records[record_type].append(record)
                else:
                    print(f"Unknown record type: {record_type}")
        
        # Print summary of what was found
        print("XML parser scan results:")
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
                        # Then check if it's a skill
                        skill_name = self._get_skill_name(key)
                        if skill_name:
                            mods.append(f"{count} Skill ({skill_name}) Mod")
                        else:
                            # Get the description from ItemDescriptors
                            description = self._get_item_descriptor_description(key, use_name=True)
                            if description:
                                # Convert OggDude format to rich text (including dice keys)
                                rich_text = self._convert_oggdude_format_to_rich_text(description)
                                # Replace {0} with the count (even if count is 1)
                                if '{0}' in rich_text:
                                    rich_text = rich_text.replace('{0}', str(count))
                                mods.append(rich_text)
                            else:
                                # Fallback if no description found
                                if count > 1:
                                    mods.append(f"{key} {count}")
                                else:
                                    mods.append(key)
                
                # Add MiscDesc if present
                if misc_desc:
                    # Convert OggDude format to rich text (including dice keys)
                    rich_misc = self._convert_oggdude_format_to_rich_text(misc_desc)
                    mods.append(rich_misc)
            
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
                    # First check if it's a talent
                    talent_name = self._get_talent_name(key)
                    if talent_name:
                        if count > 1:
                            mods.append(f"{count} Innate Talent ({talent_name})")
                        else:
                            mods.append(f"Innate Talent ({talent_name})")
                    else:
                        # Then check if it's a skill
                        skill_name = self._get_skill_name(key)
                        if skill_name:
                            if count > 1:
                                mods.append(f"{count} Skill ({skill_name}) Mod")
                            else:
                                mods.append(f"1 Skill ({skill_name}) Mod")
                        else:
                            # Get the description from ItemDescriptors
                            description = self._get_item_descriptor_description(key)
                            if description:
                                # For AddedMods, we want to convert dice keys to text version
                                # but NOT to rich text HTML spans
                                description = self._convert_oggdude_format_to_plain_text(description)
                                # Do basic {0} replacement
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
                    # Use ModDesc for attachments, fallback to qualDesc, then Description
                    return descriptor.get('modDesc', descriptor.get('qualDesc', descriptor.get('description', '')))
            
            return None
            
        except Exception as e:
            print(f"Error getting item descriptor description for {key}: {e}")
            return None
    
    def _load_talents(self):
        """Load Talents.xml into memory for talent key to name mapping"""
        try:
            oggdata_dir = self._find_oggdata_directory()
            if oggdata_dir is None:
                print("Warning: OggData directory not found, talent key resolution will not work")
                return
            
            # Find all Talents.xml files recursively
            talents_files = self._find_xml_files_recursively(oggdata_dir, 'Talents.xml')
            
            if not talents_files:
                print("Warning: Talents.xml not found in OggData directory, talent key resolution will not work")
                return
            
            print(f"Loading talents from {len(talents_files)} Talents.xml file(s)")
            
            for talents_path in talents_files:
                print(f"  Loading from: {talents_path}")
                tree = ET.parse(talents_path)
                root = tree.getroot()
                
                # Parse all talents and store key -> data mapping
                for talent_elem in self._findall_with_namespace(root, 'Talent'):
                    talent_data = self._extract_talent_data(talent_elem)
                    if talent_data:
                        key = talent_data.get('key')
                        if key:
                            self._talents[key] = talent_data
            
            print(f"Loaded {len(self._talents)} talents")
            
        except Exception as e:
            print(f"Error loading talents: {e}")
    
    def _get_talent_name(self, key: str) -> Optional[str]:
        """Get talent name from key, returns None if not found"""
        if not self._talents:
            self._load_talents()
        
        talent_data = self._talents.get(key)
        if talent_data:
            if isinstance(talent_data, dict):
                return talent_data.get('name')
            else:
                # Backward compatibility for old string format
                return talent_data
        return None
    
    def _load_skills(self):
        """Load Skills.xml into memory for skill key to name mapping"""
        try:
            oggdata_dir = self._find_oggdata_directory()
            if oggdata_dir is None:
                print("Warning: OggData directory not found, skill key resolution will not work")
                return
            
            # Find all Skills.xml files recursively
            skills_files = self._find_xml_files_recursively(oggdata_dir, 'Skills.xml')
            
            if not skills_files:
                print("Warning: Skills.xml not found in OggData directory, skill key resolution will not work")
                return
            
            print(f"Loading skills from {len(skills_files)} Skills.xml file(s)")
            
            for skills_path in skills_files:
                print(f"  Loading from: {skills_path}")
                tree = ET.parse(skills_path)
                root = tree.getroot()
                
                # Parse all skills and store key -> name mapping
                for skill_elem in self._findall_with_namespace(root, 'Skill'):
                    key = self._get_text(skill_elem, 'Key')
                    name = self._get_text(skill_elem, 'Name')
                    if key and name:
                        self._skills[key] = name
            
            print(f"Loaded {len(self._skills)} skills")
            
        except Exception as e:
            print(f"Error loading skills: {e}")
    
    def _get_skill_name(self, key: str) -> Optional[str]:
        """Get skill name from key, returns None if not found"""
        if not self._skills:
            self._load_skills()
        return self._skills.get(key)
    
    def _load_item_descriptors(self):
        """Load ItemDescriptors.xml into memory"""
        try:
            oggdata_dir = self._find_oggdata_directory()
            if oggdata_dir is None:
                print("Warning: OggData directory not found, item descriptor resolution will not work")
                self._item_descriptors = {}
                return
            
            # Find all ItemDescriptors.xml files recursively
            item_descriptors_files = self._find_xml_files_recursively(oggdata_dir, 'ItemDescriptors.xml')
            
            if not item_descriptors_files:
                print("Warning: ItemDescriptors.xml not found in OggData directory")
                self._item_descriptors = {}
                return
            
            print(f"Loading item descriptors from {len(item_descriptors_files)} ItemDescriptors.xml file(s)")
            
            self._item_descriptors = {}
            for item_descriptors_path in item_descriptors_files:
                print(f"  Loading from: {item_descriptors_path}")
                tree = ET.parse(item_descriptors_path)
                root = tree.getroot()
                
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
        # Count and replace multiple instances for each tag type, including alternate spellings
        
        # Difficulty: [DI] and [DIFFICULTY]
        di_count = text.count('[DI]')
        difficulty_count = text.count('[DIFFICULTY]')
        total_di = di_count + difficulty_count
        if total_di > 1:
            text = text.replace('[DI]' * di_count, f'{total_di} Difficulty')
            text = text.replace('[DIFFICULTY]' * difficulty_count, '')
        elif total_di == 1:
            if di_count == 1:
                text = text.replace('[DI]', 'Difficulty')
            else:
                text = text.replace('[DIFFICULTY]', 'Difficulty')
        
        # Boost: [BO] and [BOOST]
        bo_count = text.count('[BO]')
        boost_count = text.count('[BOOST]')
        total_bo = bo_count + boost_count
        if total_bo > 1:
            text = text.replace('[BO]' * bo_count, f'{total_bo} Boost')
            text = text.replace('[BOOST]' * boost_count, '')
        elif total_bo == 1:
            if bo_count == 1:
                text = text.replace('[BO]', 'Boost')
            else:
                text = text.replace('[BOOST]', 'Boost')
        
        # Success: [SU] and [SUCCESS]
        su_count = text.count('[SU]')
        success_count = text.count('[SUCCESS]')
        total_su = su_count + success_count
        if total_su > 1:
            text = text.replace('[SU]' * su_count, f'{total_su} Success')
            text = text.replace('[SUCCESS]' * success_count, '')
        elif total_su == 1:
            if su_count == 1:
                text = text.replace('[SU]', 'Success')
            else:
                text = text.replace('[SUCCESS]', 'Success')
        
        # Advantage: [AD] and [ADVANTAGE]
        ad_count = text.count('[AD]')
        advantage_count = text.count('[ADVANTAGE]')
        total_ad = ad_count + advantage_count
        if total_ad > 1:
            text = text.replace('[AD]' * ad_count, f'{total_ad} Advantage')
            text = text.replace('[ADVANTAGE]' * advantage_count, '')
        elif total_ad == 1:
            if ad_count == 1:
                text = text.replace('[AD]', 'Advantage')
            else:
                text = text.replace('[ADVANTAGE]', 'Advantage')
        
        # Threat: [TH] and [THREAT]
        th_count = text.count('[TH]')
        threat_count = text.count('[THREAT]')
        total_th = th_count + threat_count
        if total_th > 1:
            text = text.replace('[TH]' * th_count, f'{total_th} Threat')
            text = text.replace('[THREAT]' * threat_count, '')
        elif total_th == 1:
            if th_count == 1:
                text = text.replace('[TH]', 'Threat')
            else:
                text = text.replace('[THREAT]', 'Threat')
        
        # Ability: [AB] and [ABILITY]
        ab_count = text.count('[AB]')
        ability_count = text.count('[ABILITY]')
        total_ab = ab_count + ability_count
        if total_ab > 1:
            text = text.replace('[AB]' * ab_count, f'{total_ab} Ability')
            text = text.replace('[ABILITY]' * ability_count, '')
        elif total_ab == 1:
            if ab_count == 1:
                text = text.replace('[AB]', 'Ability')
            else:
                text = text.replace('[ABILITY]', 'Ability')
        
        # Proficiency: [PR] and [PROFICIENCY]
        pr_count = text.count('[PR]')
        proficiency_count = text.count('[PROFICIENCY]')
        total_pr = pr_count + proficiency_count
        if total_pr > 1:
            text = text.replace('[PR]' * pr_count, f'{total_pr} Proficiency')
            text = text.replace('[PROFICIENCY]' * proficiency_count, '')
        elif total_pr == 1:
            if pr_count == 1:
                text = text.replace('[PR]', 'Proficiency')
            else:
                text = text.replace('[PROFICIENCY]', 'Proficiency')
        
        # Challenge: [CH] and [CHALLENGE]
        ch_count = text.count('[CH]')
        challenge_count = text.count('[CHALLENGE]')
        total_ch = ch_count + challenge_count
        if total_ch > 1:
            text = text.replace('[CH]' * ch_count, f'{total_ch} Challenge')
            text = text.replace('[CHALLENGE]' * challenge_count, '')
        elif total_ch == 1:
            if ch_count == 1:
                text = text.replace('[CH]', 'Challenge')
            else:
                text = text.replace('[CHALLENGE]', 'Challenge')
        
        # Setback: [SE] and [SETBACK] (already handled above, but keeping for consistency)
        se_count = text.count('[SE]')
        setback_count = text.count('[SETBACK]')
        total_se = se_count + setback_count
        if total_se > 1:
            text = text.replace('[SE]' * se_count, f'{total_se} Setback')
            text = text.replace('[SETBACK]' * setback_count, '')
        elif total_se == 1:
            if se_count == 1:
                text = text.replace('[SE]', 'Setback')
            else:
                text = text.replace('[SETBACK]', 'Setback')
        
        # Failure: [FA] and [FAILURE]
        fa_count = text.count('[FA]')
        failure_count = text.count('[FAILURE]')
        total_fa = fa_count + failure_count
        if total_fa > 1:
            text = text.replace('[FA]' * fa_count, f'{total_fa} Failure')
            text = text.replace('[FAILURE]' * failure_count, '')
        elif total_fa == 1:
            if fa_count == 1:
                text = text.replace('[FA]', 'Failure')
            else:
                text = text.replace('[FAILURE]', 'Failure')
        
        # Triumph: [TR] and [TRIUMPH]
        tr_count = text.count('[TR]')
        triumph_count = text.count('[TRIUMPH]')
        total_tr = tr_count + triumph_count
        if total_tr > 1:
            text = text.replace('[TR]' * tr_count, f'{total_tr} Triumph')
            text = text.replace('[TRIUMPH]' * triumph_count, '')
        elif total_tr == 1:
            if tr_count == 1:
                text = text.replace('[TR]', 'Triumph')
            else:
                text = text.replace('[TRIUMPH]', 'Triumph')
        
        # Despair: [DE] and [DESPAIR]
        de_count = text.count('[DE]')
        despair_count = text.count('[DESPAIR]')
        total_de = de_count + despair_count
        if total_de > 1:
            text = text.replace('[DE]' * de_count, f'{total_de} Despair')
            text = text.replace('[DESPAIR]' * despair_count, '')
        elif total_de == 1:
            if de_count == 1:
                text = text.replace('[DE]', 'Despair')
            else:
                text = text.replace('[DESPAIR]', 'Despair')
        return text.strip()

    def _convert_oggdude_format_to_rich_text(self, text: str) -> str:
        """Convert OggDude format to rich text with HTML spans"""
        if not text:
            return ""
        
        import re
        
        # Convert each dice tag to individual spans (no counting, just direct replacement)
        # Difficulty: [DI] and [DIFFICULTY]
        text = text.replace('[DI]', '<span class="difficulty" data-dice-type="difficulty" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[DIFFICULTY]', '<span class="difficulty" data-dice-type="difficulty" contenteditable="false" style="display: inline-block;"></span>')
        
        # Boost: [BO] and [BOOST]
        text = text.replace('[BO]', '<span class="boost" data-dice-type="boost" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[BOOST]', '<span class="boost" data-dice-type="boost" contenteditable="false" style="display: inline-block;"></span>')
        
        # Success: [SU] and [SUCCESS]
        text = text.replace('[SU]', '<span class="success" data-dice-type="success" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[SUCCESS]', '<span class="success" data-dice-type="success" contenteditable="false" style="display: inline-block;"></span>')
        
        # Advantage: [AD] and [ADVANTAGE]
        text = text.replace('[AD]', '<span class="advantage" data-dice-type="advantage" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[ADVANTAGE]', '<span class="advantage" data-dice-type="advantage" contenteditable="false" style="display: inline-block;"></span>')
        
        # Threat: [TH] and [THREAT]
        text = text.replace('[TH]', '<span class="threat" data-dice-type="threat" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[THREAT]', '<span class="threat" data-dice-type="threat" contenteditable="false" style="display: inline-block;"></span>')
        
        # Ability: [AB] and [ABILITY]
        text = text.replace('[AB]', '<span class="ability" data-dice-type="ability" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[ABILITY]', '<span class="ability" data-dice-type="ability" contenteditable="false" style="display: inline-block;"></span>')
        
        # Proficiency: [PR] and [PROFICIENCY]
        text = text.replace('[PR]', '<span class="proficiency" data-dice-type="proficiency" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[PROFICIENCY]', '<span class="proficiency" data-dice-type="proficiency" contenteditable="false" style="display: inline-block;"></span>')
        
        # Challenge: [CH] and [CHALLENGE]
        text = text.replace('[CH]', '<span class="challenge" data-dice-type="challenge" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[CHALLENGE]', '<span class="challenge" data-dice-type="challenge" contenteditable="false" style="display: inline-block;"></span>')
        
        # Setback: [SE] and [SETBACK]
        text = text.replace('[SE]', '<span class="setback" data-dice-type="setback" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[SETBACK]', '<span class="setback" data-dice-type="setback" contenteditable="false" style="display: inline-block;"></span>')
        
        # Failure: [FA] and [FAILURE]
        text = text.replace('[FA]', '<span class="failure" data-dice-type="failure" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[FAILURE]', '<span class="failure" data-dice-type="failure" contenteditable="false" style="display: inline-block;"></span>')
        
        # Triumph: [TR] and [TRIUMPH]
        text = text.replace('[TR]', '<span class="triumph" data-dice-type="triumph" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[TRIUMPH]', '<span class="triumph" data-dice-type="triumph" contenteditable="false" style="display: inline-block;"></span>')
        
        # Despair: [DE] and [DESPAIR]
        text = text.replace('[DE]', '<span class="despair" data-dice-type="despair" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[DESPAIR]', '<span class="despair" data-dice-type="despair" contenteditable="false" style="display: inline-block;"></span>')
        
        # Force Point tags
        text = text.replace('[FP]', '<span class="forcepoint" data-dice-type="forcepoint" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[FORCEPOINT]', '<span class="forcepoint" data-dice-type="forcepoint" contenteditable="false" style="display: inline-block;"></span>')
        
        # Dark Side Force Point tags
        text = text.replace('[DARKSIDE]', '<span class="dark" data-dice-type="dark" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[DARKSIDEPOINT]', '<span class="dark" data-dice-type="dark" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[DARKPOINT]', '<span class="dark" data-dice-type="dark" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[DA]', '<span class="dark" data-dice-type="dark" contenteditable="false" style="display: inline-block;"></span>')
        
        # Light Side Force Point tags
        text = text.replace('[LIGHTSIDE]', '<span class="light" data-dice-type="light" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[LIGHTSIDEPOINT]', '<span class="light" data-dice-type="light" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[LIGHTPOINT]', '<span class="light" data-dice-type="light" contenteditable="false" style="display: inline-block;"></span>')
        text = text.replace('[LI]', '<span class="light" data-dice-type="light" contenteditable="false" style="display: inline-block;"></span>')
        
        # Text formatting tags
        text = text.replace('[H4]', '<h4>')
        text = text.replace('[h4]', '</h4>')
        text = text.replace('[H3]', '<h3>')
        text = text.replace('[h3]', '</h3>')
        text = text.replace('[H2]', '<h2>')
        text = text.replace('[h2]', '</h2>')
        text = text.replace('[H1]', '<h1>')
        text = text.replace('[h1]', '</h1>')
        
        # Bold tags - handle case-insensitive matching for OggDude inconsistencies
        # Match [B] or [b] followed by content followed by [B] or [b] (any case combination)
        text = re.sub(r'\[B\](.*?)\[b\]', r'<strong>\1</strong>', text, flags=re.IGNORECASE)
        text = re.sub(r'\[b\](.*?)\[B\]', r'<strong>\1</strong>', text, flags=re.IGNORECASE)
        # Handle remaining simple cases
        text = text.replace('[B]', '<strong>')
        text = text.replace('[b]', '</strong>')
        
        # Italic tags - handle case-insensitive matching for OggDude inconsistencies  
        text = re.sub(r'\[I\](.*?)\[i\]', r'<em>\1</em>', text, flags=re.IGNORECASE)
        text = re.sub(r'\[i\](.*?)\[I\]', r'<em>\1</em>', text, flags=re.IGNORECASE)
        # Handle remaining simple cases
        text = text.replace('[I]', '<em>')
        text = text.replace('[i]', '</em>')
        
        # Paragraph tags
        text = text.replace('[P]', '<p>')
        text = text.replace('[p]', '</p>')
        
        # Line break
        text = text.replace('[BR]', '<br>')
        
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

    def _convert_activation_value(self, activation_value: str) -> str:
        """Convert OggDude activation value to Realm VTT format"""
        if not activation_value:
            return ""

        # Handle the activation value conversions
        if activation_value == "taPassive":
            return "Passive"
        elif activation_value == "taAction":
            return "Active"
        elif activation_value.startswith("taIncidental") or activation_value.startswith("Incidental"):
            return "Active"
        elif activation_value.startswith("ta"):
            # Remove "ta" prefix for any other values
            return activation_value[2:]
        else:
            return activation_value

    def _get_tags_from_activation(self, activation_value: str) -> List[str]:
        """Convert OggDude activation value to Realm VTT tags

        Args:
            activation_value: The OggDude activation value (e.g., 'taIncidental', 'taIncidentalOOT')

        Returns:
            List of tags for the talent (e.g., ['Incidental'], ['Incidental', 'Out of Turn'])
        """
        tags = []

        if not activation_value:
            return tags

        # Check for incidental types
        if activation_value == "taIncidental":
            tags.append("Incidental")
        elif activation_value == "taIncidentalOOT":
            tags.append("Incidental")
            tags.append("Out of Turn")

        return tags

    def _convert_boolean_to_yes_no(self, value: Any) -> str:
        """Convert boolean value to 'yes' or 'no' string"""
        if isinstance(value, str):
            value = value.lower()
        
        if value in [True, 'true', 'yes', 1]:
            return 'yes'
        else:
            return 'no'
    
    def _load_specialization_trees(self):
        """Load specialization trees and build talent-to-specialization mapping"""
        self._talent_specializations = {}
        
        oggdata_dir = self._find_oggdata_directory()
        if oggdata_dir is None:
            print("Warning: OggData directory not found, specialization tree mapping will not work")
            return
        
        # Find all specialization XML files recursively
        specialization_files = []
        for root, dirs, files in os.walk(oggdata_dir):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    try:
                        # Check if this is a specialization file by looking at the root element
                        tree = ET.parse(file_path)
                        root_elem = tree.getroot()
                        if root_elem.tag.endswith('Specialization') or 'Specialization' in root_elem.tag:
                            specialization_files.append(file_path)
                    except Exception:
                        # Skip files that can't be parsed as XML
                        continue
        
        if not specialization_files:
            print("Warning: No specialization files found in OggData directory")
            return
        
        print(f"Loading specialization trees from {len(specialization_files)} specialization file(s)")
        
        for file_path in specialization_files:
            try:
                self._parse_specialization_tree(file_path)
            except Exception as e:
                print(f"Error parsing specialization tree {file_path}: {e}")
        
        print(f"Loaded {len(self._talent_specializations)} talent-specialization mappings")
    
    def _parse_specialization_tree(self, file_path: str):
        """Parse a single specialization tree XML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Get specialization key and name
            spec_key = self._get_text(root, 'Key')
            spec_name = self._get_text(root, 'Name')
            
            if not spec_key or not spec_name:
                print(f"Missing Key or Name in specialization file: {file_path}")
                return
            
            # Find the TalentRows element first
            talent_rows_elem = self._find_with_namespace(root, 'TalentRows')
            if talent_rows_elem is None:
                print(f"No TalentRows element found in specialization file: {file_path}")
                return
            
            # Find all talent rows within the TalentRows element
            talent_rows = self._findall_with_namespace(talent_rows_elem, 'TalentRow')
            if not talent_rows:
                print(f"No talent rows found in specialization file: {file_path}")
                return
            
            for talent_row in talent_rows:
                # Find the Talents element within this TalentRow
                talents_elem = self._find_with_namespace(talent_row, 'Talents')
                if talents_elem is not None:
                    # Find all Key elements within the Talents element
                    talent_keys = self._findall_with_namespace(talents_elem, 'Key')
                    for talent_key_elem in talent_keys:
                        talent_key = talent_key_elem.text.strip() if talent_key_elem.text else ''
                        if talent_key:
                            # Add this specialization to the talent's list
                            if talent_key not in self._talent_specializations:
                                self._talent_specializations[talent_key] = []
                            if spec_name not in self._talent_specializations[talent_key]:
                                self._talent_specializations[talent_key].append(spec_name)
            
        except Exception as e:
            print(f"Error parsing specialization tree {file_path}: {e}")
    
    def _get_talent_specializations(self, talent_key: str) -> List[str]:
        """Get the list of specialization trees that contain this talent"""
        return self._talent_specializations.get(talent_key, [])
    
    def _find_xml_files_recursively(self, directory: str, filename: str = None) -> List[str]:
        """Recursively find XML files in the given directory and its subdirectories"""
        xml_files = []
        
        if not os.path.exists(directory):
            return xml_files
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.xml'):
                    if filename is None or file == filename:
                        xml_files.append(os.path.join(root, file))
        
        return xml_files
    
    def _find_oggdata_directory(self) -> Optional[str]:
        """Find the OggData directory from the configured data_dir"""
        if hasattr(self, 'data_dir') and self.data_dir:
            if os.path.exists(self.data_dir) and os.path.isdir(self.data_dir):
                return os.path.abspath(self.data_dir)
        
        # Fallback to common locations if data_dir is not set or doesn't exist
        possible_paths = [
            'OggData',
            '../OggData',
            './OggData',
            os.path.join(os.path.dirname(__file__), '..', '..', 'OggData'),
            os.path.join(os.path.dirname(__file__), '..', 'OggData')
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                return os.path.abspath(path)
        
        return None
    
    def _extract_force_rating(self, elem: ET.Element) -> int:
        """Extract force rating from career element"""
        try:
            # First try to find the Attributes element
            attrs_elem = self._find_with_namespace(elem, 'Attributes')
            if attrs_elem:
                # Try to find ForceRating directly in the Attributes element
                for child in attrs_elem:
                    if child.tag.endswith('ForceRating') or child.tag == 'ForceRating':
                        if child.text:
                            return int(child.text.strip())
            
            # If not found in Attributes, try direct search
            for child in elem:
                if child.tag.endswith('ForceRating') or child.tag == 'ForceRating':
                    if child.text:
                        return int(child.text.strip())
                
        except (ValueError, AttributeError) as e:
            print(f"Error extracting force rating: {e}")
        return 0
    
    def _get_specialization_name(self, spec_key: str) -> Optional[str]:
        """Get specialization name from key, returns None if not found"""
        # Load specializations if not already loaded
        if not hasattr(self, '_specializations'):
            self._load_specializations()
        return self._specializations.get(spec_key)
    
    def _load_specializations(self):
        """Load specializations into memory for key to name mapping"""
        try:
            oggdata_dir = self._find_oggdata_directory()
            if oggdata_dir is None:
                print("Warning: OggData directory not found, specialization key resolution will not work")
                return
            
            # Find all specialization XML files recursively
            spec_files = self._find_xml_files_recursively(oggdata_dir)
            
            if not spec_files:
                print("Warning: No specialization files found in OggData directory")
                return
            
            self._specializations = {}
            
            for spec_path in spec_files:
                try:
                    tree = ET.parse(spec_path)
                    root = tree.getroot()
                    
                    # Check if this is a specialization file by looking for the Specialization root tag
                    root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
                    if root_tag == 'Specialization':
                        spec_key = self._get_text(root, 'Key')
                        spec_name = self._get_text(root, 'Name')
                        if spec_key and spec_name:
                            self._specializations[spec_key] = spec_name
                    
                except Exception as e:
                    # Skip files that can't be parsed
                    continue
            
            print(f"Loaded {len(self._specializations)} specializations")
            
        except Exception as e:
            print(f"Error loading specializations: {e}")
            self._specializations = {}
    
    def _extract_option_choices(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract option choices (species abilities) from XML element"""
        import uuid
        features = []
        choices_elem = self._find_with_namespace(elem, 'OptionChoices')
        if choices_elem:
            for choice in self._findall_with_namespace(choices_elem, 'OptionChoice'):
                choice_name = self._get_text(choice, 'Name')
                options_elem = self._find_with_namespace(choice, 'Options')
                if options_elem:
                    for option in self._findall_with_namespace(options_elem, 'Option'):
                        option_name = self._get_text(option, 'Name')
                        option_description = self._get_text(option, 'Description')
                        
                        # Convert description to rich text format
                        if option_description:
                            option_description = self._convert_oggdude_format_to_rich_text(option_description)
                        
                        feature = {
                            "_id": str(uuid.uuid4()),
                            "name": option_name or choice_name,
                            "unidentifiedName": "Feature",
                            "recordType": "records",
                            "identified": True,
                            "data": {
                                "description": f"<p>{option_description}</p>" if option_description else "<p></p>"
                            }
                        }
                        features.append(feature)
        return features
    
    def _convert_skill_modifiers_to_text(self, skill_modifiers: List[Dict[str, Any]]) -> str:
        """Convert skill modifiers to text format for species"""
        if not skill_modifiers:
            return ""
        
        descriptions = []
        for modifier in skill_modifiers:
            skill_key = modifier.get('skill', '')
            rank_start = modifier.get('rankStart', 0)
            rank_limit = modifier.get('rankLimit', 0)
            
            if skill_key:
                skill_name = self._get_skill_name(skill_key) or skill_key
                
                if rank_start > 0 and rank_limit > 0:
                    descriptions.append(f"Begin the game with {rank_start} rank{'s' if rank_start > 1 else ''} in {skill_name}. They still may not train {skill_name} above rank {rank_limit} during character creation.")
                elif rank_start > 0:
                    descriptions.append(f"Begin the game with {rank_start} rank{'s' if rank_start > 1 else ''} in {skill_name}.")
                elif rank_limit > 0:
                    descriptions.append(f"They still may not train {skill_name} above rank {rank_limit} during character creation.")
        
        return " ".join(descriptions)
    
    def _extract_career_skills_from_spec(self, elem: ET.Element) -> List[str]:
        """Extract career skills from specialization XML"""
        skills = []
        skills_elem = self._find_with_namespace(elem, 'CareerSkills')
        if skills_elem:
            for skill in self._findall_with_namespace(skills_elem, 'Key'):
                if skill.text:
                    skills.append(skill.text)
        return skills
    
    def _extract_talent_rows(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract talent rows from specialization XML"""
        talent_rows = []
        talent_rows_elem = self._find_with_namespace(elem, 'TalentRows')
        if talent_rows_elem:
            for row_elem in self._findall_with_namespace(talent_rows_elem, 'TalentRow'):
                row_data = {
                    'index': self._get_int(row_elem, 'Index', 0),
                    'cost': self._get_int(row_elem, 'Cost', 0),
                    'talents': [],
                    'directions': []
                }
                
                # Extract talents
                talents_elem = self._find_with_namespace(row_elem, 'Talents')
                if talents_elem:
                    for talent in self._findall_with_namespace(talents_elem, 'Key'):
                        if talent.text:
                            row_data['talents'].append(talent.text)
                
                # Extract directions
                directions_elem = self._find_with_namespace(row_elem, 'Directions')
                if directions_elem:
                    for direction in self._findall_with_namespace(directions_elem, 'Direction'):
                        direction_data = {
                            'up': self._get_bool(direction, 'Up', False),
                            'down': self._get_bool(direction, 'Down', False),
                            'left': self._get_bool(direction, 'Left', False),
                            'right': self._get_bool(direction, 'Right', False)
                        }
                        row_data['directions'].append(direction_data)
                
                talent_rows.append(row_data)
        
        # Sort talent rows by index (0 comes first, then 1, 2, etc.)
        talent_rows.sort(key=lambda x: x['index'])
        return talent_rows
    
    def _extract_directions(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract directions from specialization XML"""
        directions = []
        talent_rows_elem = self._find_with_namespace(elem, 'TalentRows')
        if talent_rows_elem:
            for row_elem in self._findall_with_namespace(talent_rows_elem, 'TalentRow'):
                directions_elem = self._find_with_namespace(row_elem, 'Directions')
                if directions_elem:
                    for direction in self._findall_with_namespace(directions_elem, 'Direction'):
                        direction_data = {
                            'up': self._get_bool(direction, 'Up', False),
                            'down': self._get_bool(direction, 'Down', False),
                            'left': self._get_bool(direction, 'Left', False),
                            'right': self._get_bool(direction, 'Right', False)
                        }
                        directions.append(direction_data)
        return directions
    
    def _load_careers(self):
        """Load careers into memory for key to name mapping"""
        try:
            oggdata_dir = self._find_oggdata_directory()
            if oggdata_dir is None:
                print("Warning: OggData directory not found, career key resolution will not work")
                return
            
            # Find all career XML files recursively
            career_files = self._find_xml_files_recursively(oggdata_dir)
            
            if not career_files:
                print("Warning: No career files found in OggData directory")
                return
            
            self._careers = {}
            
            for career_path in career_files:
                try:
                    tree = ET.parse(career_path)
                    root = tree.getroot()
                    
                    # Check if this is a career file by looking for the Career root tag
                    root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
                    if root_tag == 'Career':
                        career_key = self._get_text(root, 'Key')
                        career_name = self._get_text(root, 'Name')
                        if career_key and career_name:
                            self._careers[career_key] = career_name
                    
                except Exception as e:
                    # Skip files that can't be parsed
                    continue
            
            print(f"Loaded {len(self._careers)} careers")
            
        except Exception as e:
            print(f"Error loading careers: {e}")
            self._careers = {}
    
    def _load_force_abilities(self):
        """Load force abilities into memory for key to ability data mapping"""
        try:
            force_abilities_file = os.path.join(self.data_dir, 'Force Abilities.xml')
            if not os.path.exists(force_abilities_file):
                print(f"Warning: Force Abilities.xml not found at {force_abilities_file}")
                return
                
            tree = ET.parse(force_abilities_file)
            root = tree.getroot()
            
            self._force_abilities = {}
            
            for ability_elem in root.findall('.//ForceAbility'):
                key = self._get_text(ability_elem, 'Key')
                if key:
                    ability_data = {
                        'name': self._get_text(ability_elem, 'Name'),
                        'description': self._get_text(ability_elem, 'Description')
                    }
                    self._force_abilities[key] = ability_data
            
            print(f"Loading force abilities from 1 Force Abilities.xml file(s)")
            print(f"  Loading from: {force_abilities_file}")
            print(f"Loaded {len(self._force_abilities)} force abilities")
            
        except Exception as e:
            print(f"Error loading force abilities: {e}")
            self._force_abilities = {}
    
    def _load_vehicle_actions(self):
        """Load vehicle actions into memory for adding to all vehicles"""
        try:
            vehicle_actions_file = os.path.join(self.data_dir, 'VehActions.xml')
            if not os.path.exists(vehicle_actions_file):
                print(f"Warning: VehActions.xml not found at {vehicle_actions_file}")
                return
                
            tree = ET.parse(vehicle_actions_file)
            root = tree.getroot()
            
            self._vehicle_actions = {}
            
            for action_elem in root.findall('.//VehAction'):
                key = self._get_text(action_elem, 'Key')
                if key:
                    # Parse additional metadata for human-readable format
                    action_type = self._get_text(action_elem, 'ActionTypeValue', '')
                    pilot_only = self._get_text(action_elem, 'PilotOnly', 'false')
                    requires_speed = self._get_text(action_elem, 'RequiresSpeed', 'false')
                    
                    # Build human-readable metadata
                    metadata_parts = []
                    if action_type:
                        # Convert action type to readable format
                        if action_type == 'vaManeuver':
                            metadata_parts.append('Maneuver')
                        elif action_type == 'vaAction':
                            metadata_parts.append('Action')
                        else:
                            metadata_parts.append(action_type.replace('va', ''))
                    
                    if pilot_only.lower() == 'true':
                        metadata_parts.append('Pilot Only')
                    
                    if requires_speed.lower() == 'true':
                        metadata_parts.append('Requires Speed')
                    
                    # Get description and add metadata
                    description = self._get_text(action_elem, 'Description', '')
                    if metadata_parts:
                        metadata_text = f"<br><strong>Requirements:</strong> {', '.join(metadata_parts)}"
                        description += metadata_text
                    
                    action_data = {
                        'name': self._get_text(action_elem, 'Name'),
                        'description': description
                    }
                    self._vehicle_actions[key] = action_data
            
            print(f"Loading vehicle actions from 1 VehActions.xml file(s)")
            print(f"  Loading from: {vehicle_actions_file}")
            print(f"Loaded {len(self._vehicle_actions)} vehicle actions")
            
        except Exception as e:
            print(f"Error loading vehicle actions: {e}")
            self._vehicle_actions = {}
    
    def _init_items_loader(self):
        """Initialize the shared items loader for vehicle weapon lookup"""
        from items_loader import ItemsLoader
        self._items_loader = ItemsLoader(self)  # Pass self as xml_parser_instance
        # Pre-load items during initialization
        self._items_loader.load_all_items()
    
    def _get_force_ability_description(self, key: str) -> Optional[str]:
        """Get force ability description from key"""
        if not self._force_abilities:
            self._load_force_abilities()
        
        ability_data = self._force_abilities.get(key)
        if ability_data and isinstance(ability_data, dict):
            return ability_data.get('description')
        return None
    
    def _find_careers_for_specialization(self, spec_key: str) -> List[str]:
        """Find all careers that contain this specialization"""
        try:
            # Load careers if not already loaded
            if not hasattr(self, '_careers') or not self._careers:
                self._load_careers()
            
            career_names = []
            
            # Look through all career XML files to find which ones contain this specialization
            oggdata_dir = self._find_oggdata_directory()
            if oggdata_dir is None:
                return career_names
            
            # Find all career XML files recursively
            career_files = self._find_xml_files_recursively(oggdata_dir)
            
            for career_path in career_files:
                try:
                    tree = ET.parse(career_path)
                    root = tree.getroot()
                    
                    # Check if this is a career file by looking for the Career root tag
                    root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
                    if root_tag == 'Career':
                        # Check if this career contains the specialization
                        specializations_elem = self._find_with_namespace(root, 'Specializations')
                        if specializations_elem:
                            for spec in self._findall_with_namespace(specializations_elem, 'Key'):
                                if spec.text == spec_key:
                                    # Found the career! Get its name
                                    career_name = self._get_text(root, 'Name')
                                    if career_name and career_name not in career_names:
                                        career_names.append(career_name)
                                    break  # Move to next career file
                    
                except Exception as e:
                    # Skip files that can't be parsed
                    continue
            
            return career_names
            
        except Exception as e:
            print(f"Error finding careers for specialization {spec_key}: {e}")
            return []
    
    def _process_talent_rows(self, mapped_data: Dict[str, Any], talent_rows: List[Dict[str, Any]]):
        """Process talent rows and convert to Realm VTT format"""
        try:
            # Check if all rows have the same index (especially index 0)
            # If so, use the order in which they appear in the XML
            all_same_index = len(set(row.get('index', 0) for row in talent_rows)) == 1
            
            for row_index, row_data in enumerate(talent_rows, 1):
                if all_same_index:
                    # Use the order in XML when all rows have the same index
                    realm_row_index = row_index
                else:
                    # Use the index from the XML
                    # If no index specified, it's row 1
                    # If index is specified, it's row (index + 1)
                    xml_index = row_data.get('index', 0)
                    if xml_index == 0:
                        # No index specified, this is row 1
                        realm_row_index = 1
                    else:
                        # Index specified, this is row (index + 1)
                        realm_row_index = xml_index + 1
                
                row_cost = row_data.get('cost', 0)
                talents = row_data.get('talents', [])
                
                for col_index, talent_key in enumerate(talents, 1):
                    # Get the talent data
                    talent_data = self._get_talent_data_by_key(talent_key)
                    if talent_data:
                        # Create a copy of the talent data to avoid sharing references
                        talent_data_copy = talent_data.copy()
                        if 'data' in talent_data_copy and isinstance(talent_data_copy['data'], dict):
                            talent_data_copy['data'] = talent_data_copy['data'].copy()
                            talent_data_copy['data']['cost'] = row_cost
                        
                        # Set the talent in the correct position
                        talent_field = f"talent{realm_row_index}_{col_index}"
                        mapped_data[talent_field] = [talent_data_copy]
                    else:
                        # If talent not found, create a placeholder
                        placeholder_talent = {
                            "_id": f"placeholder-{talent_key}",
                            "name": talent_key,
                            "recordType": "talents",
                            "identified": True,
                            "data": {
                                "name": talent_key,
                                "description": f"Talent {talent_key} not found",
                                "cost": row_cost
                            },
                            "unidentifiedName": "Unknown Talent",
                            "icon": "IconStar"
                        }
                        talent_field = f"talent{realm_row_index}_{col_index}"
                        mapped_data[talent_field] = [placeholder_talent]
                        
        except Exception as e:
            print(f"Error processing talent rows: {e}")
    
    def _get_talent_data_by_key(self, talent_key: str) -> Optional[Dict[str, Any]]:
        """Get talent data by key with full conversion applied"""
        try:
            # Load talents if not already loaded
            if not hasattr(self, '_talents') or not self._talents:
                self._load_talents()
            
            # Check if we have the talent data stored
            talent_data = self._talents.get(talent_key)
            if talent_data and isinstance(talent_data, dict):
                # Get the full talent data including data subdictionary
                talent_name = talent_data.get('name', talent_key)
                talent_description = talent_data.get('description', '')
                talent_data_dict = talent_data.get('data', {})
                
                # Convert description to rich text if it exists
                if talent_description:
                    talent_description = self._convert_oggdude_format_to_rich_text(talent_description)
                
                # Get specialization trees for this talent
                specialization_trees = self._get_talent_specializations(talent_key) if talent_key else []
                
                # Create the full talent structure with all conversions applied
                full_talent_data = {
                    "_id": f"talent-{talent_key}",
                    "name": talent_name,
                    "recordType": "talents",
                    "identified": True,
                    "data": {
                        "name": talent_name,
                        "description": talent_description,
                        "activation": talent_data_dict.get('activation', 'Passive'),
                        "ranked": talent_data_dict.get('ranked', 'no'),
                        "forceTalent": talent_data_dict.get('forceTalent', 'no'),
                        "specializationTrees": specialization_trees
                    },
                    "unidentifiedName": "Unknown Talent",
                    "icon": "IconStar"
                }
                
                # Apply any additional data from the stored talent
                if talent_data_dict:
                    for key, value in talent_data_dict.items():
                        if key not in full_talent_data['data']:
                            full_talent_data['data'][key] = value
                
                return full_talent_data
            
            # Fallback: create a basic talent structure
            talent_name = self._get_talent_name(talent_key) or talent_key
            
            # Get specialization trees for this talent
            specialization_trees = self._get_talent_specializations(talent_key) if talent_key else []
            
            # Create a basic talent structure
            talent_data = {
                "_id": f"talent-{talent_key}",
                "name": talent_name,
                "recordType": "talents",
                "identified": True,
                "data": {
                    "name": talent_name,
                    "description": f"Description for {talent_name}",
                    "activation": "Passive",
                    "ranked": "no",
                    "forceTalent": "no",
                    "specializationTrees": specialization_trees
                },
                "unidentifiedName": "Unknown Talent",
                "icon": "IconStar"
            }
            
            return talent_data
            
        except Exception as e:
            print(f"Error getting talent data for key {talent_key}: {e}")
            return None
    
    def _process_directions(self, mapped_data: Dict[str, Any], talent_rows: List[Dict[str, Any]]):
        """Process directions and convert to Realm VTT format"""
        try:
            # Process vertical connectors (connector{row}_{col})
            for row_index in range(2, 6):  # Rows 2-5
                for col_index in range(1, 5):  # Columns 1-4
                    connector_field = f"connector{row_index}_{col_index}"
                    
                    # Check if there's a direction pointing down from the previous row
                    if row_index > 1 and row_index - 2 < len(talent_rows):
                        prev_row = talent_rows[row_index - 2]
                        prev_directions = prev_row.get('directions', [])
                        if col_index <= len(prev_directions):
                            prev_direction = prev_directions[col_index - 1]
                            if prev_direction.get('down', False):
                                mapped_data[connector_field] = "Yes"
                            else:
                                mapped_data[connector_field] = "No"
                        else:
                            mapped_data[connector_field] = "No"
                    else:
                        mapped_data[connector_field] = "No"
                           
            # Process horizontal connectors (h_connector{row}_2 to h_connector{row}_4)
            # Generate connectors for all talent rows starting from row 1
            max_row = len(talent_rows)
            for row_index in range(1, max_row + 1):  # Rows 1 to max_row
                for col_index in range(2, 5):  # Columns 2-4
                    h_connector_field = f"h_connector{row_index}_{col_index}"
                    
                    # Check if there's a direction pointing right from the previous column or left from the current column
                    # For h_connector{row}_*, use row {row} (index {row-1})
                    actual_row_index = row_index - 1
                    if actual_row_index < len(talent_rows):
                        current_row = talent_rows[actual_row_index]
                        current_directions = current_row.get('directions', [])
                        
                        # Check if previous column (col_index - 1) has right direction
                        prev_col_index = col_index - 2  # Convert to 0-based index for previous column
                        current_col_index = col_index - 1  # Convert to 0-based index for current column
                        
                        has_connection = False
                        # A horizontal connection exists only if the previous column has right=True
                        if prev_col_index >= 0 and prev_col_index < len(current_directions):
                            prev_directions = current_directions[prev_col_index]
                            if prev_directions.get('right', False):
                                has_connection = True
                        
                        mapped_data[h_connector_field] = "Yes" if has_connection else "No"
                        
        except Exception as e:
            print(f"Error processing directions: {e}")

    def _convert_skill_name(self, skill_name: str) -> str:
        """Convert skill name to handle hyphens (e.g., 'Piloting - Planetary' -> 'Piloting (Planetary)')"""
        if skill_name is None:
            return None
        if ' - ' in skill_name:
            # Split on ' - ' and convert to parentheses format
            parts = skill_name.split(' - ', 1)
            if len(parts) == 2:
                return f"{parts[0]} ({parts[1]})"
        return skill_name
    
    def _parse_skill_check_from_description(self, description: str) -> tuple[str, str]:
        """Parse skill check from signature ability description
        
        Returns:
            tuple: (skill, difficulty) - both as Realm VTT values or ("None", "None") if not found
        """
        if not description:
            return ("None", "None")
        
        import re
        
        # First, clean BBCode tags from the description
        clean_description = re.sub(r'\[/?[BbIiUu]\]', '', description)
        clean_description = re.sub(r'\[DI\]', '', clean_description)
        
        
        # Pattern to match skill checks - more flexible approach
        # Look for patterns like "make/makes a [difficulty] (...) [skill] check"
        patterns = [
            # Pattern 1: "makes a Hard (...) Streetwise check"
            r'makes?\s+an?\s+(\w+)\s+\([^)]*\)\s+([^c]+?)\s+check',
            # Pattern 2: "make a Hard (...) Knowledge (Education) check"  
            r'makes?\s+an?\s+(\w+)\s+\([^)]*\)\s+(Knowledge\s*\([^)]+\))\s+check',
            # Pattern 3: "make a Hard Knowledge (Education) check" (without difficulty parentheses)
            r'makes?\s+an?\s+(\w+)\s+(Knowledge\s*\([^)]+\))\s+check',
            # Pattern 4: "make a Hard Streetwise check" (simple format without difficulty parentheses)
            r'makes?\s+an?\s+(\w+)\s+([A-Za-z]+)\s+check',
            # Pattern 5: "Make an Easy (-) Perception check" (with difficulty parentheses)
            r'makes?\s+an?\s+(\w+)\s+\([^)]*\)\s+([A-Za-z]+)\s+check',
            # Pattern 6: "Requires an Average (--) Coordination check"
            r'requires?\s+an?\s+(\w+)\s+\([^)]*\)\s+([A-Za-z]+)\s+check',
            # Pattern 7: "Must make a Formidable (-----) Discipline check"
            r'must\s+makes?\s+an?\s+(\w+)\s+\([^)]*\)\s+([A-Za-z]+)\s+check'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_description, re.IGNORECASE)
            if match:
                difficulty_text = match.group(1).strip()
                skill_text = match.group(2).strip()
                break
        else:
            return ("None", "None")
        
        # Map difficulty to Realm VTT format
        difficulty_mapping = {
            "easy": "Easy",
            "average": "Average", 
            "hard": "Hard",
            "daunting": "Daunting",
            "formidable": "Formidable"
        }
        difficulty = difficulty_mapping.get(difficulty_text.lower(), "None")
        
        # Map skill to Realm VTT format
        # Handle skills like "Knowledge (Education)" -> "Education"
        knowledge_match = re.search(r'Knowledge\s*\(([^)]+)\)', skill_text, re.IGNORECASE)
        if knowledge_match:
            knowledge_type = knowledge_match.group(1).strip()
            # Map knowledge types to Realm skills
            knowledge_mapping = {
                "core worlds": "Core Worlds",
                "education": "Education", 
                "lore": "Lore",
                "outer rim": "Outer Rim",
                "underworld": "Underworld",
                "xenology": "Xenology"
            }
            skill = knowledge_mapping.get(knowledge_type.lower(), "None")
        else:
            # Handle regular skills
            skill_mapping = {
                "astrogation": "Astrogation",
                "athletics": "Athletics", 
                "brawl": "Brawl",
                "charm": "Charm",
                "coercion": "Coercion",
                "computers": "Computers",
                "cool": "Cool",
                "coordination": "Coordination",
                "deception": "Deception",
                "discipline": "Discipline",
                "gunnery": "Gunnery",
                "leadership": "Leadership",
                "lightsaber": "Lightsaber",
                "mechanics": "Mechanics",
                "medicine": "Medicine",
                "melee": "Melee",
                "negotiation": "Negotiation",
                "perception": "Perception",
                "piloting - planetary": "Piloting (Planetary)",
                "piloting - space": "Piloting (Space)",
                "piloting (planetary)": "Piloting (Planetary)",
                "piloting (space)": "Piloting (Space)",
                "ranged - heavy": "Ranged (Heavy)",
                "ranged - light": "Ranged (Light)",
                "ranged (heavy)": "Ranged (Heavy)",
                "ranged (light)": "Ranged (Light)",
                "resilience": "Resilience",
                "skulduggery": "Skulduggery",
                "stealth": "Stealth",
                "streetwise": "Streetwise",
                "survival": "Survival",
                "vigilance": "Vigilance"
            }
            skill = skill_mapping.get(skill_text.lower(), "None")
        
        return (skill, difficulty)
    
    def _parse_sig_ability(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse signature ability from XML"""
        sig_ability = self._extract_sig_ability_data(root)
        return [sig_ability] if sig_ability else []
    
    def _extract_sig_ability_data(self, sig_ability_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract signature ability data from XML element"""
        try:
            # Get the signature ability key for duplicate checking
            sig_ability_key = self._get_text(sig_ability_elem, 'Key')
            
            # Extract raw data using OggDude field names
            raw_data = {
                'Name': self._get_text(sig_ability_elem, 'Name'),
                'Description': self._get_text(sig_ability_elem, 'Description'),
                'AbilityRows': self._extract_ability_rows(sig_ability_elem),
                'Careers': self._extract_careers_from_sig_ability(sig_ability_elem),
                'MatchingNodes': self._extract_matching_nodes(sig_ability_elem)
            }
            
            # Apply field mapping
            mapped_data = self._apply_field_mapping('signature_abilities', raw_data)
            
            # Parse skill check from original description BEFORE converting to rich text
            original_description = mapped_data.get('description', '')
            skill, difficulty = ("None", "None")
            
            # Get the base ability description and cost from the first ability row
            ability_rows = raw_data.get('AbilityRows', [])
            if ability_rows:
                first_row = ability_rows[0]
                abilities = first_row.get('abilities', [])
                costs = first_row.get('costs', [])
                
                if abilities:
                    base_ability_key = abilities[0]  # Get the first ability key
                    base_description = self._get_sig_ability_node_description(base_ability_key)
                    
                    # Try to parse skill check from base description first (original format)
                    if base_description:
                        skill, difficulty = self._parse_skill_check_from_description(base_description)
                    
                    # If no skill found in base description, try main description (original format)
                    if skill == "None" and original_description:
                        skill, difficulty = self._parse_skill_check_from_description(original_description)
                    
                    # Set the skill and difficulty if found
                    if skill != "None":
                        mapped_data['skill'] = skill
                    if difficulty != "None":
                        mapped_data['difficulty'] = difficulty
                    
                    # Convert description to rich text format AFTER parsing skill check
                    if original_description:
                        mapped_data['description'] = self._convert_oggdude_format_to_rich_text(original_description)
                        
                        # Add the base description to the main description
                        if base_description:
                            base_description_rich = self._convert_oggdude_format_to_rich_text(base_description)
                            mapped_data['description'] += f"<br><br><strong>Base Ability:</strong> {base_description_rich}"
                    elif base_description:
                        base_description_rich = self._convert_oggdude_format_to_rich_text(base_description)
                        mapped_data['description'] = f"<strong>Base Ability:</strong> {base_description_rich}"
                    
                    # Calculate base cost as the highest cost in the first row
                    if costs:
                        base_cost = max(costs)
                        mapped_data['cost'] = base_cost
                    else:
                        mapped_data['cost'] = 0
            else:
                # No ability rows, but still need to convert description and try to parse skill
                if original_description:
                    skill, difficulty = self._parse_skill_check_from_description(original_description)
                    if skill != "None":
                        mapped_data['skill'] = skill
                    if difficulty != "None":
                        mapped_data['difficulty'] = difficulty
                    
                    mapped_data['description'] = self._convert_oggdude_format_to_rich_text(original_description)
            
            # Find the career for this signature ability
            careers = raw_data.get('Careers', [])
            if careers:
                career_key = careers[0]  # Get the first career key
                career_name = self._get_career_name(career_key)
                if career_name:
                    mapped_data['career'] = career_name
                else:
                    mapped_data['career'] = career_key
            else:
                mapped_data['career'] = ''
            
            # Process ability rows and convert to Realm VTT format
            if ability_rows:
                self._process_ability_rows(mapped_data, ability_rows)
            
            # Process directions and convert to Realm VTT format
            if ability_rows:
                matching_nodes = raw_data.get('MatchingNodes', [])
                self._process_sig_ability_directions(mapped_data, ability_rows, matching_nodes)
            
            # Clean up fields that shouldn't be sent to Realm
            mapped_data.pop('matchingNodes', None)
            mapped_data.pop('abilityRows', None)
            mapped_data.pop('AbilityRows', None)
            mapped_data.pop('CareerSkills', None)
            mapped_data.pop('TalentRows', None)
            mapped_data.pop('Directions', None)
            
            # Get sources and convert to category
            sources = self._get_sources(sig_ability_elem)
            category = self._get_category_from_sources(sources)
            
            sig_ability = {
                'recordType': 'signature_abilities',
                'name': mapped_data.get('name', 'Unknown Signature Ability'),
                'description': mapped_data.get('description', ''),
                'sources': sources,  # Store sources for filtering
                'category': category,
                'data': mapped_data,
                'unidentifiedName': 'Unknown Signature Ability',
                'locked': True,
                'key': sig_ability_key  # Store the key for duplicate checking
            }
            return sig_ability
            
        except Exception as e:
            print(f"Error extracting signature ability data: {e}")
            return None
    
    def _extract_ability_rows(self, elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract ability rows from signature ability XML"""
        ability_rows = []
        
        # If the element is already AbilityRows, process it directly
        if elem.tag == 'AbilityRows':
            ability_rows_elem = elem
        else:
            ability_rows_elem = self._find_with_namespace(elem, 'AbilityRows')
        
        if ability_rows_elem is not None:
            for row_elem in self._findall_with_namespace(ability_rows_elem, 'AbilityRow'):
                row_data = {
                    'index': self._get_int(row_elem, 'Index', 0),
                    'abilities': [],
                    'directions': [],
                    'spans': [],
                    'costs': []
                }
                
                # Extract abilities
                abilities_elem = self._find_with_namespace(row_elem, 'Abilities')
                if abilities_elem:
                    for ability in self._findall_with_namespace(abilities_elem, 'Key'):
                        if ability.text:
                            row_data['abilities'].append(ability.text)
                
                # Extract directions
                directions_elem = self._find_with_namespace(row_elem, 'Directions')
                if directions_elem:
                    for direction in self._findall_with_namespace(directions_elem, 'Direction'):
                        direction_data = {
                            'up': self._get_bool(direction, 'Up', False),
                            'down': self._get_bool(direction, 'Down', False),
                            'left': self._get_bool(direction, 'Left', False),
                            'right': self._get_bool(direction, 'Right', False)
                        }
                        row_data['directions'].append(direction_data)
                
                # Extract spans
                spans_elem = self._find_with_namespace(row_elem, 'AbilitySpan')
                if spans_elem:
                    for span in self._findall_with_namespace(spans_elem, 'Span'):
                        if span.text:
                            row_data['spans'].append(int(span.text))
                
                # Extract costs
                costs_elem = self._find_with_namespace(row_elem, 'Costs')
                if costs_elem:
                    for cost in self._findall_with_namespace(costs_elem, 'Cost'):
                        if cost.text:
                            row_data['costs'].append(int(cost.text))
                
                ability_rows.append(row_data)
        
        # Sort ability rows by index
        ability_rows.sort(key=lambda x: x['index'])
        return ability_rows
    
    def _extract_careers_from_sig_ability(self, elem: ET.Element) -> List[str]:
        """Extract careers from signature ability XML"""
        careers = []
        careers_elem = self._find_with_namespace(elem, 'Careers')
        if careers_elem:
            for career in self._findall_with_namespace(careers_elem, 'Key'):
                if career.text:
                    careers.append(career.text)
        return careers
    
    def _extract_matching_nodes(self, elem: ET.Element) -> List[bool]:
        """Extract matching nodes from signature ability XML"""
        matching_nodes = []
        matching_nodes_elem = self._find_with_namespace(elem, 'MatchingNodes')
        if matching_nodes_elem:
            for node in self._findall_with_namespace(matching_nodes_elem, 'Node'):
                if node.text:
                    matching_nodes.append(node.text.lower() == 'true')
        return matching_nodes
    
    def _get_sig_ability_node_description(self, ability_key: str) -> Optional[str]:
        """Get signature ability node description by key"""
        try:
            # Load signature ability nodes if not already loaded
            if not hasattr(self, '_sig_ability_nodes') or not self._sig_ability_nodes:
                self._load_sig_ability_nodes()
            
            # Check if we have the node data stored
            node_data = self._sig_ability_nodes.get(ability_key)
            if node_data and isinstance(node_data, dict):
                description = node_data.get('description', '')
                if description:
                    # Convert to rich text
                    return self._convert_oggdude_format_to_rich_text(description)
            
            return None
            
        except Exception as e:
            print(f"Error getting signature ability node description for key {ability_key}: {e}")
            return None
    
    def _load_sig_ability_nodes(self):
        """Load SigAbilityNodes.xml into memory"""
        try:
            oggdata_dir = self._find_oggdata_directory()
            if oggdata_dir is None:
                print("Warning: OggData directory not found, signature ability node resolution will not work")
                return
            
            # Find all SigAbilityNodes.xml files recursively
            sig_ability_nodes_files = self._find_xml_files_recursively(oggdata_dir, 'SigAbilityNodes.xml')
            
            if not sig_ability_nodes_files:
                print("Warning: SigAbilityNodes.xml not found in OggData directory, signature ability node resolution will not work")
                return
            
            print(f"Loading signature ability nodes from {len(sig_ability_nodes_files)} SigAbilityNodes.xml file(s)")
            
            self._sig_ability_nodes = {}
            
            for sig_ability_nodes_path in sig_ability_nodes_files:
                print(f"  Loading from: {sig_ability_nodes_path}")
                tree = ET.parse(sig_ability_nodes_path)
                root = tree.getroot()
                
                # Parse all signature ability nodes and store key -> data mapping
                for node_elem in self._findall_with_namespace(root, 'SigAbilityNode'):
                    node_data = self._extract_sig_ability_node_data(node_elem)
                    if node_data:
                        key = node_data.get('key')
                        if key:
                            self._sig_ability_nodes[key] = node_data
            
            print(f"Loaded {len(self._sig_ability_nodes)} signature ability nodes")
            
        except Exception as e:
            print(f"Error loading signature ability nodes: {e}")
            self._sig_ability_nodes = {}
    
    def _extract_sig_ability_node_data(self, node_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract signature ability node data from XML element"""
        try:
            node_key = self._get_text(node_elem, 'Key')
            node_name = self._get_text(node_elem, 'Name')
            node_description = self._get_text(node_elem, 'Description')
            
            if node_key:
                return {
                    'key': node_key,
                    'name': node_name,
                    'description': node_description
                }
            
            return None
            
        except Exception as e:
            print(f"Error extracting signature ability node data: {e}")
            return None
    
    def _get_career_name(self, career_key: str) -> Optional[str]:
        """Get career name from key"""
        try:
            # Load careers if not already loaded
            if not hasattr(self, '_careers') or not self._careers:
                self._load_careers()
            
            return self._careers.get(career_key)
            
        except Exception as e:
            print(f"Error getting career name for key {career_key}: {e}")
            return None
    
    def _process_ability_rows(self, mapped_data: Dict[str, Any], ability_rows: List[Dict[str, Any]]):
        """Process ability rows and convert to Realm VTT format"""
        try:
            # Get the base cost from the mapped_data (calculated in _extract_sig_ability_data)
            base_cost = mapped_data.get('cost', 0)
            
            # Skip the first row (base abilities) - we don't create talent0_* fields for the first row
            # Only process the upgrade rows (rows 2 and 3)
            talent_rows = ability_rows[1:] if len(ability_rows) > 1 else []
            
            # Check if all rows have the same index (especially index 0)
            # If so, use the order in which they appear in the XML
            all_same_index = len(set(row.get('index', 0) for row in talent_rows)) == 1
            
            for row_index, row_data in enumerate(talent_rows, 1):
                if all_same_index:
                    # Use the order in XML when all rows have the same index
                    realm_row_index = row_index
                else:
                    # Use the index from the XML
                    xml_index = row_data.get('index', 0)
                    if xml_index == 0:
                        # No index specified, this is row 1
                        realm_row_index = 1
                    else:
                        # Index specified, this is row (index + 1)
                        realm_row_index = xml_index + 1
                
                abilities = row_data.get('abilities', [])
                costs = row_data.get('costs', [])
                
                for col_index, ability_key in enumerate(abilities, 1):
                    # Get the ability data
                    ability_data = self._get_sig_ability_data_by_key(ability_key)
                    if ability_data:
                        # Create a copy of the ability data to avoid sharing references
                        ability_data_copy = ability_data.copy()
                        if 'data' in ability_data_copy and isinstance(ability_data_copy['data'], dict):
                            ability_data_copy['data'] = ability_data_copy['data'].copy()
                            # Set the cost from the row for upgrades
                            if col_index <= len(costs):
                                ability_data_copy['data']['cost'] = costs[col_index - 1]
                            else:
                                ability_data_copy['data']['cost'] = 0
                            # Mark as signature ability upgrade
                            ability_data_copy['data']['signatureAbilityUpgrade'] = "yes"
                        
                        # Set the ability in the correct position
                        ability_field = f"talent{realm_row_index}_{col_index}"
                        mapped_data[ability_field] = [ability_data_copy]
                    else:
                        # If ability not found, create a placeholder
                        placeholder_ability = {
                            "_id": f"placeholder-{ability_key}",
                            "name": ability_key,
                            "recordType": "talents",
                            "identified": True,
                            "data": {
                                "name": ability_key,
                                "description": f"Ability {ability_key} not found",
                                "cost": costs[col_index - 1] if col_index <= len(costs) else 0,
                                "signatureAbilityUpgrade": "yes"
                            },
                            "unidentifiedName": "Unknown Ability",
                            "icon": "IconStar"
                        }
                        ability_field = f"talent{realm_row_index}_{col_index}"
                        mapped_data[ability_field] = [placeholder_ability]
                        
        except Exception as e:
            print(f"Error processing ability rows: {e}")
    
    def _get_sig_ability_data_by_key(self, ability_key: str) -> Optional[Dict[str, Any]]:
        """Get signature ability data by key"""
        try:
            # Load signature ability nodes if not already loaded
            if not hasattr(self, '_sig_ability_nodes') or not self._sig_ability_nodes:
                self._load_sig_ability_nodes()
            
            # Check if we have the node data stored
            node_data = self._sig_ability_nodes.get(ability_key)
            if node_data and isinstance(node_data, dict):
                node_name = node_data.get('name', ability_key)
                node_description = node_data.get('description', '')
                
                # Convert description to rich text if it exists
                if node_description:
                    node_description = self._convert_oggdude_format_to_rich_text(node_description)
                
                # Check if there's a ranked field in the node data (for exceptions)
                ranked = "yes"  # Default to "yes" for all signature ability upgrades
                if 'ranked' in node_data:
                    ranked = self._convert_boolean_to_yes_no(node_data['ranked'])
                
                # Create the full ability structure
                ability_data = {
                    "_id": f"sig-ability-{ability_key}",
                    "name": node_name,
                    "recordType": "talents",
                    "identified": True,
                    "data": {
                        "name": node_name,
                        "description": node_description,
                        "activation": "Passive",
                        "ranked": ranked,
                        "forceTalent": "no",
                        "specializationTrees": []
                    },
                    "unidentifiedName": "Unknown Ability",
                    "icon": "IconStar"
                }
                
                return ability_data
            
            # Fallback: create a basic ability structure (also default to "yes" for ranked)
            ability_data = {
                "_id": f"sig-ability-{ability_key}",
                "name": ability_key,
                "recordType": "talents",
                "identified": True,
                "data": {
                    "name": ability_key,
                    "description": f"Description for {ability_key}",
                    "activation": "Passive",
                    "ranked": "yes",  # Default to "yes" for all signature ability upgrades
                    "forceTalent": "no",
                    "specializationTrees": []
                },
                "unidentifiedName": "Unknown Ability",
                "icon": "IconStar"
            }
            
            return ability_data
            
        except Exception as e:
            print(f"Error getting signature ability data for key {ability_key}: {e}")
            return None
    
    def _process_sig_ability_directions(self, mapped_data: Dict[str, Any], ability_rows: List[Dict[str, Any]], matching_nodes: List[bool]):
        """Process directions for signature abilities and convert to Realm VTT format"""
        try:
            # Process base connectors (connector0_1 to connector0_4) using MatchingNodes
            for col_index in range(1, 5):  # Columns 1-4
                connector_field = f"connector0_{col_index}"
                if col_index - 1 < len(matching_nodes):
                    # Use MatchingNodes to determine base connectors
                    mapped_data[connector_field] = "Yes" if matching_nodes[col_index - 1] else "No"
                else:
                    mapped_data[connector_field] = "No"
            
            # Process vertical connectors between rows (connector1_1 to connector2_4)
            for row_index in range(1, 3):  # Rows 1-2 (upgrade rows)
                for col_index in range(1, 5):  # Columns 1-4
                    connector_field = f"connector{row_index}_{col_index}"
                    
                    # Check if there's a direction pointing down from the previous row
                    if row_index > 0 and row_index - 1 < len(ability_rows):
                        prev_row = ability_rows[row_index - 1]
                        prev_directions = prev_row.get('directions', [])
                        if col_index - 1 < len(prev_directions):
                            prev_direction = prev_directions[col_index - 1]
                            if prev_direction.get('down', False):
                                mapped_data[connector_field] = "Yes"
                            else:
                                mapped_data[connector_field] = "No"
                        else:
                            mapped_data[connector_field] = "No"
                    else:
                        mapped_data[connector_field] = "No"
            
            # Process horizontal connectors (h_connector1_2 to h_connector2_4)
            for row_index in range(1, 3):  # Rows 1-2 (upgrade rows)
                for col_index in range(2, 5):  # Columns 2-4
                    h_connector_field = f"h_connector{row_index}_{col_index}"
                    
                    # Check if there's a direction pointing right from the previous column or left from the current column
                    # For h_connector1_*, use row 1 (index 1) - first upgrade row
                    # For h_connector2_*, use row 2 (index 2) - second upgrade row
                    actual_row_index = row_index
                    if actual_row_index < len(ability_rows):
                        current_row = ability_rows[actual_row_index]
                        current_directions = current_row.get('directions', [])
                        
                        # Check if previous column (col_index - 1) has right direction
                        # or current column (col_index) has left direction
                        prev_col_index = col_index - 2  # Convert to 0-based index for previous column
                        current_col_index = col_index - 1  # Convert to 0-based index for current column
                        
                        has_connection = False
                        if prev_col_index >= 0 and prev_col_index < len(current_directions):
                            prev_directions = current_directions[prev_col_index]
                            if prev_directions.get('right', False):
                                has_connection = True
                        
                        if not has_connection and current_col_index < len(current_directions):
                            current_directions_obj = current_directions[current_col_index]
                            if current_directions_obj.get('left', False):
                                has_connection = True
                        
                        mapped_data[h_connector_field] = "Yes" if has_connection else "No"
                        
        except Exception as e:
            print(f"Error processing signature ability directions: {e}")