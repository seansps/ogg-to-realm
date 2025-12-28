import re
import uuid
import copy
from typing import Dict, List, Any, Optional

class DataMapper:
    def __init__(self):
        self.item_map = {}  # Maps item names to Realm VTT IDs
        self.talent_map = {}  # Maps talent names to Realm VTT IDs
        self.species_map = {}  # Maps species names to Realm VTT IDs
        self.career_map = {}  # Maps career names to Realm VTT IDs
        self.spec_map = {}  # Maps specialization names to Realm VTT IDs
        self.force_power_map = {}  # Maps force power names to Realm VTT IDs
    
    def add_item_mapping(self, name: str, realm_id: str):
        """Add an item name to Realm VTT ID mapping"""
        self.item_map[name] = realm_id
    
    def add_talent_mapping(self, name: str, realm_id: str):
        """Add a talent name to Realm VTT ID mapping"""
        self.talent_map[name] = realm_id
    
    def add_species_mapping(self, name: str, realm_id: str):
        """Add a species name to Realm VTT ID mapping"""
        self.species_map[name] = realm_id
    
    def add_career_mapping(self, name: str, realm_id: str):
        """Add a career name to Realm VTT ID mapping"""
        self.career_map[name] = realm_id
    
    def add_spec_mapping(self, name: str, realm_id: str):
        """Add a specialization name to Realm VTT ID mapping"""
        self.spec_map[name] = realm_id
    
    def add_force_power_mapping(self, name: str, realm_id: str):
        """Add a force power name to Realm VTT ID mapping"""
        self.force_power_map[name] = realm_id
    
    def get_item_id(self, name: str) -> Optional[str]:
        """Get Realm VTT ID for an item name"""
        return self.item_map.get(name)
    
    def get_talent_id(self, name: str) -> Optional[str]:
        """Get Realm VTT ID for a talent name"""
        return self.talent_map.get(name)
    
    def get_species_id(self, name: str) -> Optional[str]:
        """Get Realm VTT ID for a species name"""
        return self.species_map.get(name)
    
    def get_career_id(self, name: str) -> Optional[str]:
        """Get Realm VTT ID for a career name"""
        return self.career_map.get(name)
    
    def get_spec_id(self, name: str) -> Optional[str]:
        """Get Realm VTT ID for a specialization name"""
        return self.spec_map.get(name)
    
    def get_force_power_id(self, name: str) -> Optional[str]:
        """Get Realm VTT ID for a force power name"""
        return self.force_power_map.get(name)
    
    def convert_oggdude_to_realm_vtt(self, oggdude_record: Dict[str, Any], campaign_id: str, category: str = "") -> Dict[str, Any]:
        """
        Convert OggDude record to Realm VTT format
        
        Args:
            oggdude_record: OggDude record data
            campaign_id: Realm VTT campaign ID
            category: Source category for the record
            
        Returns:
            Realm VTT formatted record
        """
        # Remove the key field as it's not valid in Realm VTT
        oggdude_record = oggdude_record.copy()
        oggdude_record.pop('key', None)
        
        record_type = oggdude_record.get('recordType', 'unknown')
        
        if record_type == 'items':
            return self._convert_item(oggdude_record, campaign_id, category)
        elif record_type == 'species':
            return self._convert_species(oggdude_record, campaign_id, category)
        elif record_type == 'careers':
            return self._convert_career(oggdude_record, campaign_id, category)
        elif record_type == 'specializations':
            return self._convert_specialization(oggdude_record, campaign_id, category)
        elif record_type == 'signature_abilities':
            return self._convert_sig_ability(oggdude_record, campaign_id, category)
        elif record_type == 'talents':
            return self._convert_talent(oggdude_record, campaign_id, category)
        elif record_type == 'force_powers':
            return self._convert_force_power(oggdude_record, campaign_id, category)
        elif record_type == 'skills':
            return self._convert_skill(oggdude_record, campaign_id, category)
        elif record_type == 'npcs':
            # Check if this is a vehicle (npcs with data.type == "vehicle")
            data = oggdude_record.get('data', {})
            if isinstance(data, dict) and data.get('type') == 'vehicle':
                return self._convert_vehicle(oggdude_record, campaign_id, category)
            else:
                return self._convert_npc(oggdude_record, campaign_id, category)
        else:
            print(f"Warning: Unknown record type '{record_type}' for record '{oggdude_record.get('name', 'Unknown')}' - skipping")
            return None
    
    def _convert_item(self, item: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert item to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = item.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Get item type from either the top level or the data field
        item_type = item.get('type', data.get('type', 'general'))
        
        # Convert description and add to data
        if 'description' in item:
            data['description'] = self._convert_description(item['description'])
        
        # Handle weapon-specific conversions (check for both 'weapon' and 'ranged weapon'/'melee weapon')
        if item_type == 'weapon' or (item_type in ['ranged weapon', 'melee weapon']):
            data = self._convert_weapon_data(data, item)
        elif item_type == 'gear' or item_type == 'general':
            data = self._convert_gear_data(data, item)
        elif item_type == 'armor':
            data = self._convert_armor_data(data, item)
        elif item_type in ['weapon attachment', 'armor attachment', 'vehicle attachment']:
            data = self._convert_attachment_data(data, item)
        
        realm_item = {
            "name": item.get('name', 'Unknown Item'),
            "recordType": "items",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unidentified Item",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": data,
            "fields": item.get('fields', {})
        }
        
        return realm_item
    
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
    
    def _convert_armor_data(self, data: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert armor-specific data"""
        # Set type to 'armor' for armor items
        data['type'] = 'armor'
        
        # Convert qualities - check both 'qualities' and 'special' fields
        qualities = data.get('qualities', data.get('special', []))
        if qualities:
            mapped_qualities, quality_counts = self._map_qualities_with_counts(qualities)
            data['special'] = mapped_qualities
            
            # Set quality count fields
            for quality_name, count in quality_counts.items():
                data[quality_name] = count
            
            # Remove the old qualities field if it exists
            data.pop('qualities', None)
        else:
            data['special'] = []
        
        # Convert restricted field from true/false to yes/no
        if 'restricted' in data:
            data['restricted'] = self._convert_restricted_value(data['restricted'])
        
        # Set default values for missing fields
        defaults = {
            'modifiers': [],
            'consumable': False,
            'hasUseBtn': False,
            'attachments': [],
            'slotsUsed': 0
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return data
    
    def _convert_gear_data(self, data: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert gear-specific data"""
        # Get the original type from the item data (already mapped to subtype by field mapping)
        original_type = data.get('subtype', 'Gear')
        item_name = item.get('name', '')
        
        # Set type to 'general' for gear items
        data['type'] = 'general'
        
        # Set subtype to the original OggDude Type value, or "General" if not defined
        if original_type and original_type != 'Gear':
            # If the original type is "general" (lowercase), convert to "General" (uppercase)
            if original_type == 'general':
                data['subtype'] = 'General'
            else:
                data['subtype'] = original_type
        else:
            data['subtype'] = 'General'
        
        # Custom handling for specific items
        if item_name == 'Stimpack':
            data['consumable'] = True
            data['hasUseBtn'] = True
            data['healing'] = '5'
            data['countsAsHealing'] = True
    
        # Convert restricted field from true/false to yes/no
        if 'restricted' in data:
            data['restricted'] = self._convert_restricted_value(data['restricted'])
        
        # Set default values for missing fields
        defaults = {
            'modifiers': [],
            'hasUseBtn': False,
            'attachments': [],
            'slotsUsed': 0
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return data
    
    def _convert_weapon_data(self, data: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert weapon-specific data"""
        # Handle weapon type and subtype based on Type and SkillKey
        weapon_type = data.get('subtype', '')
        skill_key = data.get('weaponSkill', '')
        original_skill_key = data.get('originalSkillKey', skill_key)  # Use original if available
        original_type = data.get('originalType', weapon_type)  # Use original type if available
        
        if weapon_type == 'Vehicle' or original_type == 'Vehicle':
            data['type'] = 'ranged weapon'
            data['subtype'] = 'Vehicle Weapon'
        else:
            # Check original SkillKey and current weaponSkill for melee weapons
            if (original_skill_key in ['MELEE', 'BRAWL', 'LIGHTSABER', 'LTSABER'] or 
                skill_key in ['Melee', 'Brawl', 'Lightsaber']):
                data['type'] = 'melee weapon'
            else:
                data['type'] = 'ranged weapon'
            
            # Set subtype to the original OggDude Type for non-vehicle weapons
            data['subtype'] = weapon_type if weapon_type else original_type
        
        # Map weaponSkill to proper Realm VTT values (if not already mapped)
        if skill_key and not skill_key.startswith('Ranged') and not skill_key in ['Melee', 'Brawl', 'Lightsaber', 'Gunnery']:
            data['weaponSkill'] = self._map_skill_key(skill_key)
        
        # Remove the original skill key and type as they're not needed in final output
        data.pop('originalSkillKey', None)
        data.pop('originalType', None)
        
        # Convert range values
        if 'range' in data and data['range']:
            data['range'] = self._map_range_value(data['range'])
        
        # Convert qualities - check both 'qualities' and 'special' fields
        qualities = data.get('qualities', data.get('special', []))
        if qualities:
            mapped_qualities, quality_counts = self._map_qualities_with_counts(qualities)
            data['special'] = mapped_qualities
            
            # Set quality count fields
            for quality_name, count in quality_counts.items():
                data[quality_name] = count
            
            # Remove the old qualities field if it exists
            data.pop('qualities', None)
        else:
            data['special'] = []
        
        # Convert restricted field from true/false to yes/no
        if 'restricted' in data:
            data['restricted'] = self._convert_restricted_value(data['restricted'])
        
        # Set default values for missing fields
        defaults = {
            'modifiers': [],
            'equipEffect': None,
            'stun': 0,
            'consumable': False,
            'hasUseBtn': False,
            'attachments': [],
            'slotsUsed': 0,
            'hardpoints': data.get('hardpoints', 0)
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return data
    
    def _map_range_value(self, range_value: str) -> str:
        """Map OggDude range values to Realm VTT range names"""
        range_mapping = {
            'wrEngaged': 'Engaged',
            'wrClose': 'Engaged',
            'wrShort': 'Short',
            'wrMedium': 'Medium',
            'wrLong': 'Long',
            'wrExtreme': 'Extreme'
        }
        return range_mapping.get(range_value, range_value)
    
    def _map_qualities_with_counts(self, qualities: List[Any]) -> tuple[List[str], Dict[str, int]]:
        """Map OggDude quality keys to Realm VTT quality values and return counts"""
        quality_mapping = {
            'ACCURATE': 'accurate',
            'AUTOFIRE': 'auto-fire',
            'BREACH': 'breach',
            'BURN': 'burn',
            'BLAST': 'blast',
            'CONCUSSIVE': 'concussive',
            'CORTOSIS': 'cortosis',
            'CUMBERSOME': 'cumbersome',
            'DEFENSIVE': 'defensive',
            'DEFLECTION': 'deflection',
            'DISORIENT': 'disorient',
            'ENSNARE': 'ensnare',
            'GUIDED': 'guided',
            'KNOCKDOWN': 'knockdown',
            'INACCURATE': 'inaccurate',
            'INFERIOR': 'inferior',
            'ION': 'ion',
            'LIMITEDAMMO': 'limited-ammo',
            'LINKED': 'linked',
            'PIERCE': 'pierce',
            'PREPARE': 'prepare',
            'SLOWFIRING': 'slow-firing',
            'STUN': 'stun',
            'STUNDAMAGE': 'stun-damage',
            'STUNDAMAGEDROID': 'stun-damage-droid',
            'STUNSETTING': 'stun-setting',
            'SUNDER': 'sunder',
            'SUPERIOR': 'superior',
            'TRACTOR': 'tractor',
            'VICIOUS': 'vicious',
            'UNARMED': 'unarmed'
        }
        
        # Field name mapping for quality counts
        quality_count_fields = {
            'ACCURATE': 'accurate',
            'AUTOFIRE': 'auto-fire',
            'BREACH': 'breach',
            'BURN': 'burn',
            'BLAST': 'blast',
            'CONCUSSIVE': 'concussive',
            'CORTOSIS': 'cortosis',
            'CUMBERSOME': 'cumbersome',
            'DEFENSIVE': 'defensive',
            'DEFLECTION': 'deflection',
            'DISORIENT': 'disorient',
            'ENSNARE': 'ensnare',
            'GUIDED': 'guided',
            'KNOCKDOWN': 'knockdown',
            'INACCURATE': 'inaccurate',
            'INFERIOR': 'inferior',
            'ION': 'ion',
            'LIMITEDAMMO': 'limitedAmmo',
            'LINKED': 'linked',
            'PIERCE': 'pierce',
            'PREPARE': 'prepare',
            'SLOWFIRING': 'slowFiring',
            'STUN': 'stun',
            'STUNDAMAGE': 'stun-damage',
            'STUNDAMAGEDROID': 'stun-damage-droid',
            'STUNSETTING': 'stun-setting',
            'SUNDER': 'sunder',
            'SUPERIOR': 'superior',
            'TRACTOR': 'tractor',
            'VICIOUS': 'vicious',
            'UNARMED': 'unarmed'
        }
        
        mapped_qualities = []
        quality_counts = {}
        
        for quality in qualities:
            if isinstance(quality, str):
                mapped_quality = quality_mapping.get(quality.upper(), quality.lower())
                mapped_qualities.append(mapped_quality)
                # Set count to 1 for string qualities
                count_field = quality_count_fields.get(quality.upper())
                if count_field:
                    quality_counts[count_field] = 1
            elif isinstance(quality, dict):
                # Handle quality objects with Key and Count
                key = quality.get('Key', '')
                count = quality.get('Count', 1)
                if key:
                    mapped_quality = quality_mapping.get(key.upper(), key.lower())
                    mapped_qualities.append(mapped_quality)
                    
                    # Set count field
                    count_field = quality_count_fields.get(key.upper())
                    if count_field:
                        quality_counts[count_field] = count
        
        return mapped_qualities, quality_counts
    
    def _map_qualities(self, qualities: List[Any]) -> List[str]:
        """Map OggDude quality keys to Realm VTT quality values (backward compatibility)"""
        mapped_qualities, _ = self._map_qualities_with_counts(qualities)
        return mapped_qualities
    
    def _convert_species(self, species: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert species to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = species.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Convert description and add to data
        if 'description' in species:
            data['description'] = self._convert_description(species['description'])
        
        realm_species = {
            "name": species.get('name', 'Unknown Species'),
            "recordType": "species",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Species",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": data
        }
        
        return realm_species
    
    def _convert_career(self, career: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert career to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = career.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Convert description and add to data
        if 'description' in career:
            data['description'] = self._convert_description(career['description'])
        
        realm_career = {
            "name": career.get('name', 'Unknown Career'),
            "recordType": "careers",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Career",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": data
        }
        
        return realm_career
    
    def _convert_specialization(self, spec: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert specialization to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = spec.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Convert description and add to data
        if 'description' in spec:
            data['description'] = self._convert_description(spec['description'])
        
        realm_spec = {
            "name": spec.get('name', 'Unknown Specialization'),
            "recordType": "specializations",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Specialization",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": data
        }
        
        return realm_spec
    
    def _convert_sig_ability(self, sig_ability: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert signature ability to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = sig_ability.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Convert description and add to data
        if 'description' in sig_ability:
            data['description'] = self._convert_description(sig_ability['description'])
        
        realm_sig_ability = {
            "name": sig_ability.get('name', 'Unknown Signature Ability'),
            "recordType": "signature_abilities",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Signature Ability",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": data
        }
        
        return realm_sig_ability
    
    def _convert_talent(self, talent: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert talent to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = talent.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Convert description and add to data
        if 'description' in talent:
            data['description'] = self._convert_description(talent['description'])
        
        realm_talent = {
            "name": talent.get('name', 'Unknown Talent'),
            "recordType": "talents",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Talent",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": data
        }
        
        return realm_talent
    
    def _convert_force_power(self, power: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert force power to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = power.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Convert description and add to data - but preserve existing data
        converted_data = data.copy()  # Start with all existing data
        converted_data['name'] = power.get('name', 'Unknown Force Power')
        if 'description' in power:
            converted_data['description'] = self._convert_description(power['description'])
        elif 'description' in data:
            converted_data['description'] = self._convert_description(data['description'])
        
        realm_record = {
            'name': power.get('name', 'Unknown Force Power'),
            'category': category or 'Star Wars RPG',
            'campaignId': campaign_id,
            'recordType': 'force_powers',
            'data': converted_data,  # Use all the data including talents, connectors, cost, prereqs, etc.
            'fields': power.get('fields', {}),  # Include fields for UI hiding
            'unidentifiedName': 'Unknown Force Power',
            'locked': True
        }
        
        return realm_record
    
    def _convert_skill(self, skill: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert skill to Realm VTT format"""
        data = skill.get('data', {})
        
        # Convert skill name to handle hyphens (e.g., "Piloting - Planetary" -> "Piloting (Planetary)")
        skill_name = skill.get('name', 'Unknown Skill')
        converted_name = self._convert_skill_name(skill_name)
        
        realm_record = {
            'name': converted_name,
            'category': category or 'Edge of the Empire Core Rulebook',
            'campaignId': campaign_id,
            'recordType': 'skills',
            'data': {
                'name': converted_name,
                'description': self._convert_description(skill.get('description', '')),
                'stat': data.get('stat', 'agility'),
                'group': data.get('group', 'General')
            },
            'unidentifiedName': 'Unknown Skill',
            'locked': True
        }
        
        return realm_record
    
    def _convert_skill_name(self, skill_name: str) -> str:
        """Convert skill name to handle hyphens (e.g., 'Piloting - Planetary' -> 'Piloting (Planetary)')"""
        if ' - ' in skill_name:
            # Split on ' - ' and convert to parentheses format
            parts = skill_name.split(' - ', 1)
            if len(parts) == 2:
                return f"{parts[0]} ({parts[1]})"
        return skill_name
    
    def _convert_vehicle(self, vehicle: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert vehicle to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = vehicle.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Create a copy to avoid modifying the original
        realm_data = data.copy()
        
        # Convert description and add to data
        if 'description' in vehicle:
            realm_data['description'] = self._convert_description(vehicle['description'])
        
        # Convert restricted field from true/false to yes/no
        if 'restricted' in realm_data:
            realm_data['restricted'] = self._convert_restricted_value(realm_data['restricted'])
        
        # Field mappings for vehicles
        if 'encumbrance' in realm_data:
            realm_data['encumbranceCapacity'] = realm_data.pop('encumbrance')
        
        # Convert defense object to individual fields, ignore 0 values
        if 'defense' in realm_data and isinstance(realm_data['defense'], dict):
            defense = realm_data.pop('defense')
            if defense.get('fore', 0) > 0:
                realm_data['defFore'] = defense['fore']
            if defense.get('aft', 0) > 0:
                realm_data['defAft'] = defense['aft']
            if defense.get('port', 0) > 0:
                realm_data['defPort'] = defense['port']
            if defense.get('starboard', 0) > 0:
                realm_data['defStarboard'] = defense['starboard']
        
        # Convert armor to soakValue
        if 'armor' in realm_data:
            realm_data['soakValue'] = realm_data.pop('armor')
        
        # Convert hullTrauma to woundThreshold and set woundsRemaining
        if 'hullTrauma' in realm_data:
            hull_trauma = realm_data.pop('hullTrauma')
            realm_data['woundThreshold'] = hull_trauma
            realm_data['woundsRemaining'] = hull_trauma
        
        # Convert systemStrain to strainThreshold and set strainRemaining
        if 'systemStrain' in realm_data:
            system_strain = realm_data.pop('systemStrain')
            realm_data['strainThreshold'] = system_strain
            realm_data['strainRemaining'] = system_strain
        
        # Convert silhouette to size
        if 'silhouette' in realm_data:
            realm_data['size'] = realm_data.pop('silhouette')
        
        # Process inventory items through item converter
        if 'inventory' in realm_data:
            converted_inventory = []
            for item in realm_data['inventory']:
                # Store the firing arc before conversion
                firing_arc = item.get('data', {}).get('firingArc', {})
                
                # Convert the item through the item data mapper
                converted_item = self._convert_item(item, campaign_id, category)
                
                # Add UUID and ensure firing arc is preserved
                converted_item['_id'] = str(uuid.uuid4())
                # Set icon on vehicle inventory items
                self._set_inventory_item_icon(converted_item)
                if firing_arc and 'data' in converted_item:
                    # Check if firing arc contains all directions
                    all_directions = {'fore', 'aft', 'port', 'starboard', 'dorsal', 'ventral'}
                    firing_arc_set = set(firing_arc) if isinstance(firing_arc, list) else set()
                    
                    if firing_arc_set == all_directions:
                        # Replace with ["all"] if all directions are present
                        converted_item['data']['firingArc'] = ['all']
                    else:
                        # Keep the original firing arc
                        converted_item['data']['firingArc'] = firing_arc
                
                # Add animation for vehicle weapons with "Blaster" or "Laser" in the name
                item_name = converted_item.get('name', '')
                if ('Blaster' in item_name or 'Laser' in item_name) and 'data' in converted_item:
                    # Check if vehicle name contains "TIE" to determine hue color
                    vehicle_name = vehicle.get('name', '')
                    hue = 129 if 'TIE' in vehicle_name else 360
                    
                    converted_item['data']['animation'] = {
                        "animationName": "bolt_3",
                        "moveToDestination": True,
                        "stretchToDestination": False,
                        "destinationOnly": False,
                        "startAtCenter": False,
                        "scale": 0.75,
                        "opacity": 1,
                        "animationSpeed": 12,
                        "rotation": -90,
                        "hue": hue,
                        "contrast": None,
                        "brightness": None,
                        "moveSpeed": 2,
                        "sound": "laser_2",
                        "count": 1
                    }
                
                converted_inventory.append(converted_item)
            
            realm_data['inventory'] = converted_inventory
        
        # Process features to add proper structure
        if 'features' in realm_data and isinstance(realm_data['features'], list):
            converted_features = []
            for feature in realm_data['features']:
                if isinstance(feature, dict):
                    # Parse skill and difficulty from description
                    description = feature.get('description', '')
                    skill, difficulty = self._parse_skill_and_difficulty(description)
                    
                    converted_feature = {
                        "_id": str(uuid.uuid4()),
                        "name": feature.get('name', 'Unknown Action'),
                        "unidentifiedName": feature.get('name', 'Unknown Action'),
                        "recordType": "records",
                        "identified": True,
                        "data": {
                            "actionModifiersAccordion": None,
                            "skill": skill,
                            "difficulty": difficulty,
                            "actionDetailsAccordion": None,
                            "description": self._convert_description(description) if description else "",
                            "descriptionAcc": None
                        }
                    }
                    converted_features.append(converted_feature)
            
            realm_data['features'] = converted_features
        
        realm_vehicle = {
            "name": vehicle.get('name', 'Unknown Vehicle'),
            "recordType": "npcs",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Vehicle",
            "identified": True,
            "shared": True,
            "locked": True,
            "data": realm_data
        }

        return realm_vehicle
    
    def _parse_skill_and_difficulty(self, description: str) -> tuple[str, str]:
        """Parse skill check from description text
        
        Returns:
            tuple: (skill, difficulty) - both as Realm VTT values or (None, None) if not found
        """
        if not description:
            return (None, None)
        
        # First, clean BBCode and HTML tags from the description
        clean_description = re.sub(r'<[^>]*>', '', description)
        clean_description = re.sub(r'\[/?[BbIiUu]\]', '', clean_description)
        clean_description = re.sub(r'\[DI\]', '', clean_description)
        
        # Pattern to match skill checks - more flexible approach
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
            return (None, None)
        
        # Map difficulty to Realm VTT format
        difficulty_mapping = {
            "easy": "Easy",
            "average": "Average", 
            "hard": "Hard",
            "daunting": "Daunting",
            "formidable": "Formidable"
        }
        difficulty = difficulty_mapping.get(difficulty_text.lower(), None)
        
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
            skill = knowledge_mapping.get(knowledge_type.lower(), None)
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
                "ranged - heavy": "Ranged (Heavy)",
                "ranged - light": "Ranged (Light)",
                "piloting (planetary)": "Piloting (Planetary)",
                "piloting (space)": "Piloting (Space)",
                "ranged (heavy)": "Ranged (Heavy)",
                "ranged (light)": "Ranged (Light)",
                "resilience": "Resilience",
                "skulduggery": "Skulduggery",
                "stealth": "Stealth",
                "streetwise": "Streetwise",
                "survival": "Survival",
                "vigilance": "Vigilance"
            }
            skill = skill_mapping.get(skill_text.lower(), None)
        
        return (skill, difficulty)
    
    def _convert_npc(self, npc: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert NPC to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = npc.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Check if this is an adversary format (has type, characteristics, derived)
        if 'type' in data and 'characteristics' in data:
            return self._convert_adversary(npc, campaign_id, category)
        
        # Convert description and add to data
        if 'description' in npc:
            data['description'] = self._convert_description(npc['description'])
        
        # Convert restricted field from true/false to yes/no if present
        if 'restricted' in data:
            data['restricted'] = self._convert_restricted_value(data['restricted'])
        
        realm_npc = {
            "name": npc.get('name', 'Unknown NPC'),
            "recordType": "npcs", 
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": npc.get('unidentifiedName', 'Unknown NPC'),
            "identified": npc.get('identified', True),
            "shared": False,
            "locked": npc.get('locked', True),
            "data": data
        }
        
        return realm_npc
    
    def _convert_adversary(self, npc: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert adversary to Realm VTT format with proper skills structure"""
        data = npc.get('data', {})
        
        # Get basic info
        name = npc.get('name', 'Unknown Adversary')
        description = npc.get('description', '')
        notes = npc.get('notes', '')
        npc_type = data.get('type', 'rival').lower()
        subtype = data.get('subtype', '')

        # Extract species from tags (format: "species:Gamorrean") or direct field
        species_name = data.get('species', '')
        if not species_name:
            tags = data.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str) and tag.startswith('species:'):
                        species_name = tag[8:]  # Remove "species:" prefix
                        break

        # Extract silhouette from abilities (format: "Silhouette 3" or "Silhouette: 3")
        # Realm VTT expects format "Silhouette X" as string
        silhouette = "Silhouette 1"  # Default silhouette
        abilities = data.get('abilities', [])
        if isinstance(abilities, list):
            for ability in abilities:
                ability_str = ''
                if isinstance(ability, str):
                    ability_str = ability
                elif isinstance(ability, dict):
                    ability_str = ability.get('name', '')
                if ability_str.lower().startswith('silhouette'):
                    # Parse "Silhouette 3" or "Silhouette: 3" or "Silhouette 3."
                    import re
                    match = re.search(r'silhouette[:\s]+(\d+)', ability_str.lower())
                    if match:
                        silhouette = f"Silhouette {match.group(1)}"
                    break

        # Get characteristics
        characteristics = data.get('characteristics', {})
        brawn = characteristics.get('Brawn', characteristics.get('brawn', 1))
        agility = characteristics.get('Agility', characteristics.get('agility', 1))
        intellect = characteristics.get('Intellect', characteristics.get('intellect', 1))
        cunning = characteristics.get('Cunning', characteristics.get('cunning', 1))
        willpower = characteristics.get('Willpower', characteristics.get('willpower', 1))
        presence = characteristics.get('Presence', characteristics.get('presence', 1))
        
        # Get derived stats
        derived = data.get('derived', {})
        soak = derived.get('soak', 0)
        wounds = derived.get('wounds', 10)
        strain = derived.get('strain', 10)
        
        # Handle wounds and strain based on NPC type
        if npc_type == 'minion':
            wounds_per_minion = wounds
            number_in_group = 3  # Default group size
            wound_threshold = wounds_per_minion * number_in_group
            wounds_remaining = wound_threshold
            strain_threshold = 0
            strain_remaining = 0
        elif npc_type == 'rival':
            wounds_per_minion = 0
            number_in_group = 0
            wound_threshold = wounds
            wounds_remaining = wounds
            strain_threshold = 0
            strain_remaining = 0
        else:  # nemesis
            wounds_per_minion = 0
            number_in_group = 0
            wound_threshold = wounds
            wounds_remaining = wounds
            strain_threshold = strain
            strain_remaining = strain
        
        # Create comprehensive skills list
        skills = self._create_full_skills_list(data.get('skills', []), npc_type)
        
        # Convert weapons and gear to inventory items
        inventory = self._convert_adversary_inventory(data.get('weapons', []), data.get('gear', []))
        
        realm_data = {
            "skills": skills,
            "type": npc_type,
            "brawn": brawn,
            "agility": agility,
            "intellect": intellect,
            "cunning": cunning,
            "willpower": willpower,
            "presence": presence,
            "defenseMelee": 0,
            "defenseRanged": 0,
            "encumbranceThreshold": brawn + 5,  # Standard calculation
            "soakValue": soak,
            "strainRemaining": strain_remaining,
            "strainThreshold": strain_threshold,
            "strainThresholdBonus": 0,
            "woundThreshold": wound_threshold,
            "woundThresholdBonus": 0,
            "woundsRemaining": wounds_remaining,
            "speciesName": species_name,  # From species: tag or empty
            "subtype": subtype,
            "silhouette": silhouette,  # From "Silhouette X" ability or default 1
            "wounds": 0,
            "strain": 0,
            "rangeBand": "Medium",
            "inventory": inventory
        }
        
        # Add minion-specific fields
        if npc_type == 'minion':
            realm_data["woundsPerMinion"] = wounds_per_minion
            realm_data["numberInGroup"] = number_in_group
        
        # Convert description with special adversary format
        if description:
            realm_data['description'] = self._convert_adversary_description(description, name)

        # Convert talents (lookup from OggDude XML by name and apply rank)
        adversary_talents = data.get('talents', [])
        if isinstance(adversary_talents, list) and adversary_talents:
            talents_list: List[Dict[str, Any]] = []
            # Track force rating if provided via talent string
            found_force_rating: Optional[int] = None
            # Optional definition maps provided by JSON parser
            definition_maps = data.get('definitions') if isinstance(data, dict) else None
            talents_defs = None
            if isinstance(definition_maps, dict):
                talents_defs = definition_maps.get('talents')
            for raw_talent in adversary_talents:
                if not isinstance(raw_talent, str):
                    continue
                talent_name, talent_rank = self._parse_talent_name_and_rank(raw_talent)
                # Handle Force Rating special case: do not add as a talent
                if talent_name.strip().lower() == 'force rating':
                    found_force_rating = max(found_force_rating or 0, talent_rank or 1)
                    continue
                looked_up_talent = self._get_talent_by_name(talent_name)
                if looked_up_talent:
                    # Deep copy and annotate rank
                    talent_copy = copy.deepcopy(looked_up_talent)
                    talent_copy['_id'] = str(uuid.uuid4())
                    if 'data' not in talent_copy or not isinstance(talent_copy['data'], dict):
                        talent_copy['data'] = {}
                    talent_copy['data']['rank'] = talent_rank
                    # Special handling: if Adversary, scale modifier value to rank
                    if talent_copy.get('name', '').lower() == 'adversary':
                        modifiers = talent_copy['data'].get('modifiers', [])
                        if isinstance(modifiers, list):
                            for mod in modifiers:
                                if isinstance(mod, dict):
                                    mod_data = mod.get('data', {})
                                    if isinstance(mod_data, dict) and mod_data.get('type') == 'upgradeDifficultyOfAttacksTargetingYou':
                                        mod_data['value'] = str(talent_rank)
                    talents_list.append(talent_copy)
                else:
                    # Try JSON-defined talents as fallback
                    if isinstance(talents_defs, dict):
                        tdef = talents_defs.get(talent_name.strip().lower())
                    else:
                        tdef = None
                    if isinstance(tdef, dict):
                        description_html = self._convert_description(tdef.get('description', '') or '')
                        talents_list.append({
                            '_id': str(uuid.uuid4()),
                            'name': tdef.get('name', talent_name),
                            'recordType': 'talents',
                            'identified': True,
                            'unidentifiedName': 'Unknown Talent',
                            'icon': 'IconStar',
                            'data': {
                                'name': tdef.get('name', talent_name),
                                'description': description_html,
                                'activation': 'Passive',
                                'ranked': 'no',
                                'forceTalent': 'no',
                                'rank': talent_rank
                            }
                        })
                    else:
                        # Fallback minimal talent structure
                        talents_list.append({
                            '_id': str(uuid.uuid4()),
                            'name': talent_name,
                            'recordType': 'talents',
                            'identified': True,
                            'unidentifiedName': 'Unknown Talent',
                            'icon': 'IconStar',
                            'data': {
                                'name': talent_name,
                                'description': f'Talent {talent_name}',
                                'activation': 'Passive',
                                'ranked': 'no',
                                'rank': talent_rank
                            }
                        })
            if talents_list:
                realm_data['talents'] = talents_list
            # Apply force rating if found
            if found_force_rating is not None:
                fr_value = int(found_force_rating) if found_force_rating > 0 else 1
                realm_data['forceRating'] = fr_value
                realm_data['remainingForce'] = fr_value

        # Convert abilities to features list with skill/difficulty parsing
        adversary_abilities = data.get('abilities', [])
        definition_maps = data.get('definitions') if isinstance(data, dict) else None
        features_from_abilities = self._convert_adversary_abilities(adversary_abilities, definition_maps)
        if features_from_abilities:
            # Merge with any existing features
            existing_features = realm_data.get('features', [])
            realm_data['features'] = existing_features + features_from_abilities
        
        # Ensure unarmed attack is included as equipped inventory item
        unarmed_item = self._create_unarmed_attack()
        if isinstance(unarmed_item, dict):
            unarmed_item['_id'] = str(uuid.uuid4())
            # enforce equipped
            if 'data' in unarmed_item:
                unarmed_item['data']['carried'] = 'equipped'
            inventory.insert(0, unarmed_item)

        realm_npc = {
            "name": name,
            "recordType": "npcs",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Adversary",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": realm_data
        }
        
        return realm_npc

    def _parse_talent_name_and_rank(self, text: str) -> tuple[str, int]:
        """Parse a talent string like 'Skilled Jockey 1' into (name, rank). Defaults rank to 1."""
        if not text:
            return ('', 1)
        match = re.match(r'^\s*(.*?)\s*(\d+)?\s*$', str(text))
        if match:
            name = match.group(1).strip()
            rank_str = match.group(2)
            try:
                rank = int(rank_str) if rank_str is not None else 1
            except ValueError:
                rank = 1
            return (name, rank if rank > 0 else 1)
        return (str(text).strip(), 1)

    def _convert_adversary_abilities(self, abilities: Any, definition_maps: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Convert adversary abilities into Realm VTT features with dice and skill/difficulty parsing."""
        features: List[Dict[str, Any]] = []
        if not isinstance(abilities, list):
            return features
        for ability in abilities:
            if isinstance(ability, str):
                name = ability.strip()
                description = ''
                # If definitions provided, enrich description
                if isinstance(definition_maps, dict):
                    abilities_defs = definition_maps.get('abilities', {}) or {}
                    force_defs = definition_maps.get('force_powers', {}) or {}
                    # Derive lookup key: for names like "Force Power: Enhance", also try stripped token
                    key = name.lower()
                    lookup = abilities_defs.get(key) or force_defs.get(key)
                    if not lookup and key.startswith('force power:'):
                        short = key.split(':', 1)[1].strip()
                        lookup = force_defs.get(short)
                    if isinstance(lookup, dict):
                        description = lookup.get('description', '') or ''
            elif isinstance(ability, dict):
                name = str(ability.get('name', 'Ability')).strip()
                description = str(ability.get('description', '') or '')
            else:
                continue

            is_force_power = name.lower().startswith('force power')

            # Convert dice tokens including :forcepip:
            converted_desc = self._convert_colon_dice_tokens(description)

            # Parse skill and difficulty from description
            skill, difficulty = self._parse_ability_skill_and_difficulty(description)

            feature_record = {
                "_id": str(uuid.uuid4()),
                "name": name,
                "unidentifiedName": "Ability",
                "recordType": "records",
                "identified": True,
                "data": {
                    "isForcePower": bool(is_force_power),
                    "description": converted_desc,
                }
            }

            if skill:
                feature_record["data"]["skill"] = skill
            if difficulty:
                feature_record["data"]["difficulty"] = difficulty

            features.append(feature_record)

        return features

    def _convert_colon_dice_tokens(self, text: str) -> str:
        """Convert colon-form dice tokens like :difficulty:, :boost:, :forcepip: to rich text spans."""
        if not text:
            return ""
        converted = text
        dice_mappings = {
            ':boost:': ('boost', 'boost'),
            ':setback:': ('setback', 'setback'),
            ':advantage:': ('advantage', 'advantage'),
            ':threat:': ('threat', 'threat'),
            ':success:': ('success', 'success'),
            ':failure:': ('failure', 'failure'),
            ':triumph:': ('triumph', 'triumph'),
            ':despair:': ('despair', 'despair'),
            ':force:': ('force', 'force'),
            ':darkside:': ('dark', 'dark'),
            ':lightside:': ('light', 'light'),
            ':difficulty:': ('difficulty', 'difficulty'),
            ':challenge:': ('challenge', 'challenge'),
            ':ability:': ('ability', 'ability'),
            ':proficiency:': ('proficiency', 'proficiency'),
            ':forcepip:': ('forcepoint', 'forcepoint'),
            # difficulty words handled below
        }
        for token, (css, dice_type) in dice_mappings.items():
            if dice_type:
                converted = converted.replace(token, f'<span class="{css}" data-dice-type="{dice_type}" contenteditable="false" style="display: inline-block;"></span>')
        # Replace difficulty-word tokens with label and repeated difficulty dice spans
        def diff_spans(count: int) -> str:
            span = '<span class="difficulty" data-dice-type="difficulty" contenteditable="false" style="display: inline-block;"></span>'
            return ''.join([span for _ in range(count)])
        replacements = [
            (':easy:', 'Easy', 1),
            (':average:', 'Average', 2),
            (':hard:', 'Hard', 3),
            (':daunting:', 'Daunting', 4),
            (':formidable:', 'Formidable', 5),
        ]
        for token, label, count in replacements:
            if token in converted:
                converted = converted.replace(token, f'{label} ({diff_spans(count)})')
        return converted

    def _normalize_skill_name_for_text(self, skill_text: str) -> Optional[str]:
        if not skill_text:
            return None
        s = skill_text.strip()
        # Normalize Piloting/Ranged colon & hyphen variants
        replacements = {
            'ranged: heavy': 'Ranged (Heavy)',
            'ranged heavy': 'Ranged (Heavy)',
            'ranged - heavy': 'Ranged (Heavy)',
            'ranged: light': 'Ranged (Light)',
            'ranged light': 'Ranged (Light)',
            'ranged - light': 'Ranged (Light)',
            'piloting: planetary': 'Piloting (Planetary)',
            'piloting planetary': 'Piloting (Planetary)',
            'piloting - planetary': 'Piloting (Planetary)',
            'piloting: space': 'Piloting (Space)',
            'piloting space': 'Piloting (Space)',
            'piloting - space': 'Piloting (Space)'
        }
        key = s.lower()
        # Fix common misspelling
        key = key.replace('plantary', 'planetary')
        # Map Knowledge (X) -> X specific knowledge skill
        knowledge_match = re.search(r'^knowledge\s*\(([^)]+)\)\s*$', key, flags=re.IGNORECASE)
        if knowledge_match:
            k = knowledge_match.group(1).strip().lower()
            knowledge_map = {
                'core worlds': 'Core Worlds',
                'education': 'Education',
                'lore': 'Lore',
                'outer rim': 'Outer Rim',
                'underworld': 'Underworld',
                'xenology': 'Xenology',
            }
            return knowledge_map.get(k, knowledge_match.group(1).strip().title())
        if key in replacements:
            return replacements[key]
        # Title-case single words; keep parentheses if present
        return s

    def _parse_ability_skill_and_difficulty(self, description: str) -> tuple[Optional[str], Optional[str]]:
        """Parse skill and colon-token difficulty from ability descriptions."""
        if not description:
            return (None, None)
        text = description
        # Find difficulty token
        diff_match = re.search(r':(easy|average|hard|daunting|formidable):', text, flags=re.IGNORECASE)
        difficulty = None
        if diff_match:
            diff_key = diff_match.group(1).lower()
            diff_map = {
                'easy': 'Easy',
                'average': 'Average',
                'hard': 'Hard',
                'daunting': 'Daunting',
                'formidable': 'Formidable'
            }
            difficulty = diff_map.get(diff_key)
            # Search for skill after the difficulty token, before the word 'check'
            remainder = text[diff_match.end():]
            skill_match = re.search(r'([A-Za-z]+(?:\s*[:\-]\s*[A-Za-z]+)?(?:\s*\([^)]+\))?)\s+check', remainder, flags=re.IGNORECASE)
            if skill_match:
                raw_skill = skill_match.group(1).strip()
                skill = self._normalize_skill_name_for_text(raw_skill)
                return (skill, difficulty)
        # Fallback to generic parser
        return self._parse_skill_and_difficulty(description)

    def _get_talent_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Lookup a talent from OggDude Talents.xml by its display name and return full Realm VTT talent data."""
        if not name:
            return None
        # Lazy init XML parser and load talents index
        if not hasattr(self, '_xml_parser'):
            from xml_parser import XMLParser
            self._xml_parser = XMLParser()
        xmlp = self._xml_parser
        # Ensure talents loaded
        if not hasattr(xmlp, '_talents') or not xmlp._talents:
            try:
                xmlp._load_talents()
            except Exception:
                return None
        search_name = name.strip().lower()
        # Exact, case-insensitive match against loaded talents
        for key, talent in getattr(xmlp, '_talents', {}).items():
            try:
                tname = talent.get('name', '')
            except AttributeError:
                continue
            if isinstance(tname, str) and tname.strip().lower() == search_name:
                return xmlp._get_talent_data_by_key(key)
        return None
    
    def _create_full_skills_list(self, adversary_skills: List[str], npc_type: str) -> List[Dict[str, Any]]:
        """Create the complete skills list with proper UUIDs and stats"""
        # All skills with their stats and groups (from the user's example)
        all_skills = [
            {"name": "Astrogation", "stat": "intellect", "group": "General"},
            {"name": "Athletics", "stat": "brawn", "group": "General"},
            {"name": "Brawl", "stat": "brawn", "group": "Combat"},
            {"name": "Charm", "stat": "presence", "group": "General"},
            {"name": "Coercion", "stat": "willpower", "group": "General"},
            {"name": "Computers", "stat": "intellect", "group": "General"},
            {"name": "Cool", "stat": "presence", "group": "General"},
            {"name": "Coordination", "stat": "agility", "group": "General"},
            {"name": "Core Worlds", "stat": "intellect", "group": "Knowledge"},
            {"name": "Deception", "stat": "cunning", "group": "General"},
            {"name": "Discipline", "stat": "willpower", "group": "General"},
            {"name": "Education", "stat": "intellect", "group": "Knowledge"},
            {"name": "Gunnery", "stat": "agility", "group": "Combat"},
            {"name": "Leadership", "stat": "presence", "group": "General"},
            {"name": "Lightsaber", "stat": "brawn", "group": "Combat"},
            {"name": "Lore", "stat": "intellect", "group": "Knowledge"},
            {"name": "Mechanics", "stat": "intellect", "group": "General"},
            {"name": "Medicine", "stat": "intellect", "group": "General"},
            {"name": "Melee", "stat": "brawn", "group": "Combat"},
            {"name": "Negotiation", "stat": "presence", "group": "General"},
            {"name": "Outer Rim", "stat": "intellect", "group": "Knowledge"},
            {"name": "Perception", "stat": "cunning", "group": "General"},
            {"name": "Piloting (Planetary)", "stat": "agility", "group": "General"},
            {"name": "Piloting (Space)", "stat": "agility", "group": "General"},
            {"name": "Ranged (Heavy)", "stat": "agility", "group": "Combat"},
            {"name": "Ranged (Light)", "stat": "agility", "group": "Combat"},
            {"name": "Resilience", "stat": "brawn", "group": "General"},
            {"name": "Skulduggery", "stat": "cunning", "group": "General"},
            {"name": "Stealth", "stat": "agility", "group": "General"},
            {"name": "Streetwise", "stat": "cunning", "group": "General"},
            {"name": "Survival", "stat": "cunning", "group": "General"},
            {"name": "Underworld", "stat": "intellect", "group": "Knowledge"},
            {"name": "Vigilance", "stat": "willpower", "group": "General"},
            {"name": "Xenology", "stat": "intellect", "group": "Knowledge"}
        ]
        
        # Create skill name mappings for common variations
        skill_mappings = {
            "ranged: heavy": "Ranged (Heavy)",
            "ranged: light": "Ranged (Light)", 
            "ranged heavy": "Ranged (Heavy)",
            "ranged light": "Ranged (Light)",
            "ranged: heavy": "Ranged (Heavy)",
            "ranged: light": "Ranged (Light)",
            "piloting planetary": "Piloting (Planetary)",
            "piloting space": "Piloting (Space)",
            "piloting: planetary": "Piloting (Planetary)",
            "piloting: space": "Piloting (Space)"
        }
        
        # Normalize adversary skills list and preserve ranks
        normalized_skills = {}
        if isinstance(adversary_skills, list):
            for skill in adversary_skills:
                if isinstance(skill, str):
                    # Check if it needs mapping
                    mapped_skill = skill_mappings.get(skill.lower(), skill)
                    normalized_skills[mapped_skill] = 1  # Default rank
                elif isinstance(skill, dict):
                    # Handle dict format with ranks
                    for skill_name, rank in skill.items():
                        mapped_skill = skill_mappings.get(skill_name.lower(), skill_name)
                        normalized_skills[mapped_skill] = rank
        elif isinstance(adversary_skills, dict):
            # Handle dict format directly
            for skill_name, rank in adversary_skills.items():
                mapped_skill = skill_mappings.get(skill_name.lower(), skill_name)
                normalized_skills[mapped_skill] = rank
        
        skills_list = []
        for skill_info in all_skills:
            skill_name = skill_info["name"]
            
            # Determine rank based on NPC type and if skill is trained
            if skill_name in normalized_skills:
                if npc_type == 'minion':
                    rank = 2  # Group skill for minions always rank 2
                    career_or_minion_skill = True
                else:
                    rank = normalized_skills[skill_name]  # Use actual rank for rivals/nemesis
                    career_or_minion_skill = True
            else:
                rank = 0  # Untrained
                career_or_minion_skill = False
            
            skill_record = {
                "_id": str(uuid.uuid4()),
                "name": skill_name,
                "unidentifiedName": skill_name,
                "recordType": "skill",
                "identified": True,
                "icon": "IconTools",
                "data": {
                    "group": skill_info["group"],
                    "stat": skill_info["stat"],
                    "rank": rank
                }
            }
            
            if career_or_minion_skill:
                skill_record["data"]["careerOrMinionSkill"] = True
            
            skills_list.append(skill_record)
        
        return skills_list
    
    def _create_unarmed_attack(self) -> Dict[str, Any]:
        """Create standard unarmed attack item"""
        return {
            "unidentifiedName": "Unarmed Combat",
            "recordType": "items",
            "portrait": "/images/bc390eaa-d17a-4022-a1ca-fa388c12e498_29.webp",
            "_id": str(uuid.uuid4()),
            "name": "Unarmed Combat",
            "identified": True,
            "icon": "IconBox",
            "data": {
                "damage": 0,
                "crit": 5,
                "carried": "equipped",
                "type": "melee weapon",
                "range": "Engaged",
                "skill": "Brawl",
                "weaponSkill": "Brawl",
                "special": ["unarmed", "disorient", "knockdown"],
                "disorient": 1,
                "description": "Unarmed attacks use the Brawl skill and Brawn for base damage. Damage can be done to strain instead of wounds."
            }
        }
    
    def _convert_adversary_description(self, description: str, npc_name: str) -> str:
        """Convert adversary description format to Realm VTT richtext format"""
        if not description:
            return ""
        
        # Start with NPC name as H2
        converted = f"<h2>{npc_name}</h2>\n\n"
        
        # Add the description
        converted += description
        
        # Convert dice symbols from :symbol: format to proper spans
        dice_mappings = {
            ':boost:': '<span class="boost" data-dice-type="boost" contenteditable="false" style="display: inline-block;"></span>',
            ':setback:': '<span class="setback" data-dice-type="setback" contenteditable="false" style="display: inline-block;"></span>',
            ':advantage:': '<span class="advantage" data-dice-type="advantage" contenteditable="false" style="display: inline-block;"></span>',
            ':threat:': '<span class="threat" data-dice-type="threat" contenteditable="false" style="display: inline-block;"></span>',
            ':success:': '<span class="success" data-dice-type="success" contenteditable="false" style="display: inline-block;"></span>',
            ':failure:': '<span class="failure" data-dice-type="failure" contenteditable="false" style="display: inline-block;"></span>',
            ':triumph:': '<span class="triumph" data-dice-type="triumph" contenteditable="false" style="display: inline-block;"></span>',
            ':despair:': '<span class="despair" data-dice-type="despair" contenteditable="false" style="display: inline-block;"></span>',
            ':force:': '<span class="force" data-dice-type="force" contenteditable="false" style="display: inline-block;"></span>',
            ':darkside:': '<span class="dark" data-dice-type="dark" contenteditable="false" style="display: inline-block;"></span>',
            ':lightside:': '<span class="light" data-dice-type="light" contenteditable="false" style="display: inline-block;"></span>',
            ':difficulty:': '<span class="difficulty" data-dice-type="difficulty" contenteditable="false" style="display: inline-block;"></span>',
            ':challenge:': '<span class="challenge" data-dice-type="challenge" contenteditable="false" style="display: inline-block;"></span>',
            ':ability:': '<span class="ability" data-dice-type="ability" contenteditable="false" style="display: inline-block;"></span>',
            ':proficiency:': '<span class="proficiency" data-dice-type="proficiency" contenteditable="false" style="display: inline-block;"></span>'
        }
        
        # Apply all dice symbol conversions
        for old_symbol, new_span in dice_mappings.items():
            converted = converted.replace(old_symbol, new_span)
        
        return converted
    
    def _find_item_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find an item by name (case-insensitive) in the OGG database"""
        # Initialize items loader if needed
        if not hasattr(self, '_items_loader'):
            from json_parser import JSONParser
            json_parser = JSONParser()
            self._items_loader = json_parser.get_items_loader()
        
        # Search all items for case-insensitive name match
        all_items = self._items_loader.load_all_items()
        search_name = name.lower().strip()
        
        for key, item in all_items.items():
            item_name = item.get('name', '').lower().strip()
            if item_name == search_name:
                return item
        
        return None
    
    def _parse_item_count(self, item_text: str) -> tuple[int, str]:
        """Parse count from item text like '2 Frag grenades' -> (2, 'Frag grenade')"""
        import re
        
        # Look for number at the start
        match = re.match(r'^(\d+)\s+(.+)', item_text.strip())
        if match:
            count = int(match.group(1))
            name = match.group(2)
            # Attempt to singularize the name
            singular_name = self._singularize_name(name)
            return count, singular_name
        
        return 1, item_text.strip()
    
    def _singularize_name(self, name: str) -> str:
        """Simple singularization of item names"""
        name = name.strip()
        
        # Special cases that don't follow normal rules
        special_cases = {
            'glasses': 'glasses',  # Don't singularize
            'credits': 'credit',
            'grenades': 'grenade',
            'rifles': 'rifle',
        }
        
        name_lower = name.lower()
        for plural, singular in special_cases.items():
            if name_lower.endswith(plural):
                # Preserve original case
                prefix = name[:-len(plural)]
                if name_lower == plural:
                    # Whole word matches, preserve case
                    if name.isupper():
                        return prefix + singular.upper()
                    elif name.istitle():
                        return prefix + singular.capitalize()
                    else:
                        return prefix + singular
                else:
                    # Partial match, preserve case
                    return prefix + singular
        
        # Common plural patterns
        if name_lower.endswith('ves'):
            # knives -> knife
            return name[:-3] + 'fe'
        elif name_lower.endswith('ies'):
            # batteries -> battery
            return name[:-3] + 'y'
        elif name_lower.endswith('es') and not name_lower.endswith(('ses', 'ches', 'shes', 'xes', 'zes')):
            # boxes -> box, but not glasses, churches, dishes, fixes, buzzes
            return name[:-2]
        elif name_lower.endswith('s') and not name_lower.endswith('ss'):
            # blasters -> blaster, but not glass -> glas
            return name[:-1]
        
        return name
    
    def _parse_armor_stats(self, item_text: str) -> tuple[str, int, int]:
        """Parse armor stats from text like 'Armoured clothing (+1 Soak, +1 Defence)' -> ('Armored clothing', 1, 1)"""
        import re
        
        # Look for pattern: name (stats in parentheses)
        match = re.match(r'^(.+?)\s*\(([^)]+)\)', item_text.strip())
        if not match:
            return item_text.strip(), 0, 0
        
        name = match.group(1).strip()
        stats_text = match.group(2)
        
        # Convert British to American spelling (case-insensitive)
        import re
        name = re.sub(r'\bArmoured\b', 'Armored', name, flags=re.IGNORECASE)
        name = re.sub(r'\bArmour\b', 'Armor', name, flags=re.IGNORECASE)
        name = re.sub(r'\bDefence\b', 'Defense', name, flags=re.IGNORECASE)
        name = re.sub(r'\bColour\b', 'Color', name, flags=re.IGNORECASE)
        
        soak = 0
        defense = 0
        
        # Look for soak values
        soak_match = re.search(r'[+]?(\d+)\s*(?:Soak|soak)', stats_text)
        if soak_match:
            soak = int(soak_match.group(1))
        
        # Look for defense values (both Defence and Defense)
        defense_match = re.search(r'[+]?(\d+)\s*(?:Defence|Defense|defence|defense)', stats_text)
        if defense_match:
            defense = int(defense_match.group(1))
        
        return name, soak, defense
    
    def _create_adhoc_weapon(self, weapon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an ad-hoc weapon item from adversary weapon object"""
        name = weapon_data.get('name', 'Unknown Weapon')
        skill = weapon_data.get('skill', 'Ranged (Heavy)')
        damage = weapon_data.get('damage', weapon_data.get('plus-damage', 0))
        critical = weapon_data.get('critical', 3)
        weapon_range = weapon_data.get('range', 'Short')
        
        # Determine weapon type based on skill
        if skill.lower() in ['brawl', 'melee', 'lightsaber']:
            weapon_type = 'melee weapon'
        else:
            weapon_type = 'ranged weapon'
        
        return {
            'recordType': 'items',
            'name': name,
            'unidentifiedName': 'Unidentified Item',
            'identified': True,
            'locked': True,
            '_id': str(uuid.uuid4()),
            'data': {
                'type': weapon_type,
                'subtype': skill,
                'damage': damage,
                'crit': critical,
                'range': weapon_range,
                'weaponSkill': skill,
                'skill': skill,
                'carried': 'equipped',
                'count': 1
            }
        }
    
    def _create_adhoc_armor(self, name: str, soak: int, defense: int) -> Dict[str, Any]:
        """Create an ad-hoc armor item"""
        # Apply British to American spelling conversion (case-insensitive)
        import re
        american_name = name
        american_name = re.sub(r'\bArmoured\b', 'Armored', american_name, flags=re.IGNORECASE)
        american_name = re.sub(r'\bArmour\b', 'Armor', american_name, flags=re.IGNORECASE)
        american_name = re.sub(r'\bDefence\b', 'Defense', american_name, flags=re.IGNORECASE)
        american_name = re.sub(r'\bColour\b', 'Color', american_name, flags=re.IGNORECASE)
        
        return {
            'recordType': 'items',
            'name': american_name,
            'unidentifiedName': 'Unidentified Item', 
            'identified': True,
            'locked': True,
            '_id': str(uuid.uuid4()),
            'data': {
                'type': 'armor',
                'soakBonus': soak,
                'defense': defense,
                'carried': 'equipped',
                'count': 1
            }
        }
    
    def _create_adhoc_gear(self, name: str, count: int = 1) -> Dict[str, Any]:
        """Create an ad-hoc gear item"""
        return {
            'recordType': 'items',
            'name': name,
            'unidentifiedName': 'Unidentified Item',
            'identified': True,
            'locked': True,
            '_id': str(uuid.uuid4()),
            'data': {
                'type': 'general',
                'carried': 'equipped',
                'count': count
            }
        }
    
    def _create_credits_item(self, amount: int) -> Dict[str, Any]:
        """Create a credits item as pack type with cash field"""
        return {
            'recordType': 'items',
            'name': 'Credits',
            'unidentifiedName': 'Credits',
            'identified': True,
            'locked': True,
            '_id': str(uuid.uuid4()),
            'data': {
                'type': 'pack',
                'cash': amount,
                'carried': 'equipped',
                'count': 1
            }
        }
    
    def _is_credits_item(self, name: str) -> tuple[bool, int]:
        """Check if item is credits and return amount"""
        import re
        name_lower = name.lower().strip()
        
        # Look for patterns like "500 credits", "1000 credit", "Credits", etc.
        credit_match = re.match(r'^(\d+)\s+credits?$', name_lower)
        if credit_match:
            return True, int(credit_match.group(1))
        
        # Just "credits" or "credit" with no number
        if name_lower in ['credits', 'credit']:
            return True, 100  # Default amount
        
        return False, 0
    
    def _convert_adversary_inventory(self, weapons: List[Any], gear: List[Any]) -> List[Dict[str, Any]]:
        """Convert adversary weapons and gear to Realm VTT inventory items"""
        inventory = []
        # Track items by normalized name for merging duplicate entries (e.g., Frag Grenade from weapons and gear)
        name_to_index: Dict[str, int] = {}

        def _normalize_item_name_for_index(item_obj: Dict[str, Any]) -> str:
            return str(item_obj.get('name', '')).strip().lower()

        def _set_ammo_if_applicable(item_obj: Dict[str, Any]) -> None:
            try:
                name_l = str(item_obj.get('name', '')).lower()
                data = item_obj.get('data', {})
                if isinstance(data, dict):
                    count_val = data.get('count', 1)
                    data['ammo'] = count_val
            except Exception:
                pass

        def _add_or_merge(item_obj: Dict[str, Any]) -> None:
            key = _normalize_item_name_for_index(item_obj)
            if key and key in name_to_index:
                existing = inventory[name_to_index[key]]
                # Merge counts
                existing_count = existing.get('data', {}).get('count', 1)
                incoming_count = item_obj.get('data', {}).get('count', 1)
                try:
                    merged = int(existing_count) + int(incoming_count)
                except Exception:
                    merged = existing_count
                if 'data' not in existing or not isinstance(existing['data'], dict):
                    existing['data'] = {}
                existing['data']['count'] = merged
                # Keep equipped
                existing['data']['carried'] = 'equipped'
                _set_ammo_if_applicable(existing)
            else:
                # New entry
                idx = len(inventory)
                inventory.append(item_obj)
                name_to_index[key] = idx
                _set_ammo_if_applicable(item_obj)
        
        # Process weapons
        for weapon in weapons:
            if isinstance(weapon, str):
                # Parse count if present
                count, weapon_name = self._parse_item_count(weapon)
                
                # Try to find in OGG database using singularized name, then original name
                singular_name = self._singularize_name(weapon_name)
                ogg_item = self._find_item_by_name(singular_name)
                if not ogg_item and singular_name != weapon_name:
                    # Try original name if singularized didn't work
                    ogg_item = self._find_item_by_name(weapon_name)
                if ogg_item:
                    # Convert OGG item to Realm VTT format
                    realm_item = self._convert_item(ogg_item, '', '')
                    realm_item['_id'] = str(uuid.uuid4())
                    realm_item['data']['count'] = count
                    realm_item['data']['carried'] = 'equipped'
                    self._set_inventory_item_icon(realm_item)
                    _add_or_merge(realm_item)
                else:
                    # Create ad-hoc gear item (simple string weapons become gear)
                    adhoc_item = self._create_adhoc_gear(weapon_name, count)
                    self._set_inventory_item_icon(adhoc_item)
                    _add_or_merge(adhoc_item)
            
            elif isinstance(weapon, dict):
                # Create ad-hoc weapon from object
                adhoc_weapon = self._create_adhoc_weapon(weapon)
                self._set_inventory_item_icon(adhoc_weapon)
                _add_or_merge(adhoc_weapon)
        
        # Process gear
        for gear_item in gear:
            if isinstance(gear_item, str):
                # Check if this is credits first
                is_credits, credit_amount = self._is_credits_item(gear_item)
                if is_credits:
                    credits_item = self._create_credits_item(credit_amount)
                    self._set_inventory_item_icon(credits_item)
                    _add_or_merge(credits_item)
                    continue
                
                # Parse count if present
                count, gear_name = self._parse_item_count(gear_item)
                
                # Check if the parsed name is credits (after count parsing)
                is_credits_parsed, credit_amount_parsed = self._is_credits_item(gear_name)
                if is_credits_parsed:
                    # Use the count as the credit amount if it was parsed
                    final_amount = credit_amount_parsed
                    if count > 1:
                        final_amount = count
                    credits_item = self._create_credits_item(final_amount)
                    self._set_inventory_item_icon(credits_item)
                    _add_or_merge(credits_item)
                    continue
                
                # Try to parse armor stats from parentheses
                parsed_name, soak, defense = self._parse_armor_stats(gear_name)
                
                # Try to find in OGG database first using singularized name, then original name
                singular_name = self._singularize_name(parsed_name)
                ogg_item = self._find_item_by_name(singular_name)
                if not ogg_item and singular_name != parsed_name:
                    # Try original name if singularized didn't work
                    ogg_item = self._find_item_by_name(parsed_name)
                if ogg_item:
                    # Convert OGG item to Realm VTT format
                    realm_item = self._convert_item(ogg_item, '', '')
                    realm_item['_id'] = str(uuid.uuid4())
                    realm_item['data']['count'] = count
                    realm_item['data']['carried'] = 'equipped'
                    self._set_inventory_item_icon(realm_item)
                    _add_or_merge(realm_item)
                else:
                    # Create ad-hoc item based on stats
                    if soak > 0 or defense > 0:
                        # Has armor stats, create armor item
                        adhoc_item = self._create_adhoc_armor(parsed_name, soak, defense)
                        adhoc_item['data']['count'] = count
                    else:
                        # No armor stats, create general gear
                        adhoc_item = self._create_adhoc_gear(parsed_name, count)
                    self._set_inventory_item_icon(adhoc_item)
                    _add_or_merge(adhoc_item)
        
        # Reconciliation pass: for grenade-like items, prefer counts from gear list over weapons list
        try:
            # Precompute parsed counts from source text (separately for weapons and gear)
            weapon_counts: Dict[str, int] = {}
            gear_counts: Dict[str, int] = {}
            def add_count(target: Dict[str, int], name: str, cnt: int):
                key = str(name).strip().lower()
                target[key] = target.get(key, 0) + max(int(cnt), 0)

            # From weapons list (strings only)
            for weapon in weapons:
                if isinstance(weapon, str):
                    cnt, nm = self._parse_item_count(weapon)
                    nm_s = self._singularize_name(nm)
                    add_count(weapon_counts, nm_s, cnt)
            # From gear list
            for gear_item in gear:
                if isinstance(gear_item, str):
                    cnt, nm = self._parse_item_count(gear_item)
                    nm_s = self._singularize_name(nm)
                    add_count(gear_counts, nm_s, cnt)

            for item in inventory:
                name_key = str(item.get('name', '')).strip().lower()
                # Prefer the count specified in gear list if present; otherwise use weapons list
                resolved = None
                if name_key in gear_counts and gear_counts[name_key] > 0:
                    resolved = gear_counts[name_key]
                elif name_key in weapon_counts and weapon_counts[name_key] > 0:
                    resolved = weapon_counts[name_key]
                if resolved is not None:
                    if 'data' not in item or not isinstance(item['data'], dict):
                        item['data'] = {}
                    item['data']['count'] = resolved
                    # Mirror ammo to count for stackables/limited use items
                    item['data']['ammo'] = item['data']['count']
        except Exception:
            pass

        return inventory

    def _set_inventory_item_icon(self, item: Dict[str, Any]) -> None:
        """Set the top-level icon for an inventory item. Weapons get IconBox. Others default to IconBox too."""
        try:
            data = item.get('data', {}) if isinstance(item, dict) else {}
            item_type = (data.get('type') or '').lower() if isinstance(data, dict) else ''
            if 'weapon' in item_type:
                item['icon'] = 'IconBox'
            else:
                item['icon'] = 'IconBox'
        except Exception:
            # Fail-safe: ensure icon exists
            item['icon'] = 'IconBox'
    
    def _convert_restricted_value(self, restricted_value: Any) -> str:
        """Convert OggDude restricted value (true/false) to Realm VTT format (yes/no)"""
        if isinstance(restricted_value, str):
            restricted_value = restricted_value.lower()
        
        if restricted_value in [True, 'true', 'yes', 1]:
            return 'yes'
        else:
            return 'no'
    
    def _convert_attachment_data(self, data: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert attachment-specific data"""
        # The type should already be set correctly (weapon attachment, armor attachment, vehicle attachment)
        # Just ensure it's set
        if 'type' not in data:
            data['type'] = item.get('type', 'weapon attachment')
        
        # Convert restricted field from true/false to yes/no
        if 'restricted' in data:
            data['restricted'] = self._convert_restricted_value(data['restricted'])
        
        # Set default values for missing fields
        defaults = {
            'modifiers': [],
            'equipEffect': None,
            'consumable': False,
            'hasUseBtn': False,
            'attachments': [],
            'slots': 0
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return data
    
    def _convert_description(self, description: str) -> str:
        """
        Convert OggDude description format to Realm VTT HTML format
        Handles various OggDude data errors and inconsistencies
        
        Args:
            description: OggDude formatted description
            
        Returns:
            Realm VTT HTML formatted description
        """
        if not description:
            return ""
        
        # Convert OggDude tags to HTML
        html = description
        
        # Fix common OggDude errors first
        # Fix typos: [p] should be [b] (OggDude typo) - only lowercase [p] and [/p]
        html = re.sub(r'\[p\]', '[b]', html)
        html = re.sub(r'\[/p\]', '[/b]', html)
        
        # Fix tag order issues: [B][P] should be [P][B]
        html = re.sub(r'\[B\]\[P\]', '[P][B]', html)
        
        # Also fix the closing tag order: [/P][/B] should be [/B][/P]
        html = re.sub(r'\[/P\]\[/B\]', '[/B][/P]', html)
        
        # Fix special character encoding issues
        html = html.replace('&lt;h&gt;', '<h>')
        html = html.replace('&lt;/h&gt;', '</h>')
        html = html.replace('&lt;b&gt;', '<b>')
        html = html.replace('&lt;/b&gt;', '</b>')
        html = html.replace('&lt;p&gt;', '<p>')
        html = html.replace('&lt;/p&gt;', '</p>')
        html = html.replace('&amp;#', '&#')
        html = html.replace('&lt;ul&gt;', '<ul>')
        html = html.replace('&lt;/ul&gt;', '</ul>')
        html = html.replace('&lt;li&gt;', '<li>')
        html = html.replace('&lt;/li&gt;', '</li>')
        html = html.replace('&lt;ol&gt;', '<ul>')  # Convert ordered lists to unordered
        html = html.replace('&lt;/ol&gt;', '</ul>')
        # Normalize <b> tags to <strong>
        html = re.sub(r'<b>', '<strong>', html, flags=re.IGNORECASE)
        html = re.sub(r'</b>', '</strong>', html, flags=re.IGNORECASE)
        
        # Headers - handle both proper and improper closing tags
        html = re.sub(r'\[H(\d+)\](.*?)\[/H\1\]', r'<h\1>\2</h\1>', html)
        html = re.sub(r'\[H(\d+)\](.*?)\[h\1\]', r'<h\1>\2</h\1>', html)
        
        # Bold - handle both proper and improper closing tags
        html = re.sub(r'\[B\](.*?)\[/B\]', r'<strong>\1</strong>', html)
        html = re.sub(r'\[B\](.*?)\[b\]', r'<strong>\1</strong>', html)
        
        # Fix bold tag with colon: [b]: should be :</b>
        html = re.sub(r'\[b\]:', ':</b>', html)
        
        # Italics - handle both proper and improper closing tags
        html = re.sub(r'\[I\](.*?)\[/I\]', r'<em>\1</em>', html)
        html = re.sub(r'\[I\](.*?)\[i\]', r'<em>\1</em>', html)
        
        # Paragraphs and line breaks - handle both opening and closing tags
        html = html.replace('[P]', '\n<p>')
        html = html.replace('[/P]', '</p>')
        html = html.replace('[BR]', '\n<p>')
        
        # Lists - handle both proper and improper closing tags
        html = re.sub(r'\[UL\](.*?)\[/UL\]', r'<ul>\1</ul>', html)
        html = re.sub(r'\[UL\](.*?)\[ul\]', r'<ul>\1</ul>', html)
        html = re.sub(r'\[LI\](.*?)\[/LI\]', r'<li>\1</li>', html)
        html = re.sub(r'\[LI\](.*?)\[li\]', r'<li>\1</li>', html)
        
        # Convert dice notation for TipTap extension
        # Map of OggDude dice tags to TipTap dice types
        dice_mapping = {
            # Ability dice
            r'\[ABILITY\]': 'ability',
            r'\[AB\]': 'ability',
            # Difficulty dice
            r'\[DIFFICULTY\]': 'difficulty',
            r'\[DI\]': 'difficulty',
            # Proficiency dice
            r'\[PROFICIENCY\]': 'proficiency',
            r'\[PR\]': 'proficiency',
            # Challenge dice
            r'\[CHALLENGE\]': 'challenge',
            r'\[CH\]': 'challenge',
            # Boost dice
            r'\[BOOST\]': 'boost',
            r'\[BO\]': 'boost',
            # Setback dice
            r'\[SETBACK\]': 'setback',
            r'\[SE\]': 'setback',
            # Force dice
            r'\[FORCE\]': 'force',
            r'\[FO\]': 'force',
            # Light side
            r'\[LIGHTSIDE\]': 'light',
            r'\[LIGHTSIDEPOINT\]': 'light',
            r'\[LIGHTPOINT\]': 'light',
            r'\[LI\]': 'light',
            # Dark side
            r'\[DARKSIDE\]': 'dark',
            r'\[DARKSIDEPOINT\]': 'dark',
            r'\[DARKPOINT\]': 'dark',
            r'\[DA\]': 'dark',
            # FP
            r'\[FP\]': 'forcepoint',
            r'\[FORCEPOINT\]': 'forcepoint',
            # Success
            r'\[SUCCESS\]': 'success',
            r'\[SU\]': 'success',
            # Advantage
            r'\[ADVANTAGE\]': 'advantage',
            r'\[AD\]': 'advantage',
            # Failure
            r'\[FAILURE\]': 'failure',
            r'\[FA\]': 'failure',
            # Threat
            r'\[THREAT\]': 'threat',
            r'\[TH\]': 'threat',
            # Triumph
            r'\[TRIUMPH\]': 'triumph',
            r'\[TR\]': 'triumph',
            # Despair
            r'\[DESPAIR\]': 'despair',
            r'\[DE\]': 'despair',
        }
        
        # Apply dice notation conversions
        for pattern, dice_type in dice_mapping.items():
            html = re.sub(
                pattern, 
                f'<span class="{dice_type}" data-dice-type="{dice_type}" contenteditable="false" style="display: inline-block;"></span>', 
                html
            )
        
        # Convert [b] and [B] (and closing tags) to <strong> (case-insensitive)
        html = re.sub(r'\[(b|B)\](.*?)\[/(b|B)\]', r'<strong>\2</strong>', html)
        html = re.sub(r'\[(b|B)\](.*?)\[(b|B)\]', r'<strong>\2</strong>', html)
        
        # Post-process the HTML to fix structural issues
        html = self._fix_html_structure(html)
        
        # Handle any remaining unclosed tags
        html = re.sub(r'\[([A-Z]+)\]', r'<span class="oggdude-tag">[\1]</span>', html)
        
        return html
    
    def _fix_html_structure(self, html: str) -> str:
        """
        Fix common HTML structure issues in OggDude data
        Based on error handling patterns from the old OGG to FG conversion script
        """
        # Split into lines for processing
        lines = html.split('\n')
        fixed_lines = []
        found_list = False
        
        for i, line in enumerate(lines):
            # Fix list structure issues
            if '<ul>' in line:
                found_list = True
            if '</ul>' in line:
                if not found_list:
                    # Convert this to a <ul> (OggDude sometimes has </ul> without <ul>)
                    line = line.replace('</ul>', '<ul>')
                    found_list = True
                else:
                    found_list = False
            
            # Fix bold tag issues (unclosed or duplicate tags)
            if '<strong>' in line or '</strong>' in line:
                line = self._fix_bold_tags(line)
            
            # Fix unclosed paragraph tags
            if '<p>' in line and '</p>' not in line:
                line = f"{line}</p>"
            
            # Add paragraph tags to lines that need them (but be more careful)
            elif (not '<p>' in line and len(line.strip()) > 0 
                  and not '<li>' in line 
                  and not '<ul>' in line
                  and not '</ul>' in line 
                  and not '<ol>' in line
                  and not '</ol>' in line
                  and not '<h' in line
                  and not '</h' in line
                  and not '<strong>' in line
                  and not '</strong>' in line
                  and not line.strip().startswith('<')
                  and not line.strip().endswith('>')):
                line = f"<p>{line}</p>"
            
            # Fix unclosed list item tags
            if '<li>' in line and '</li>' not in line:
                line = f"{line}</li>"
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_bold_tags(self, line: str) -> str:
        """
        Fix bold tag issues (unclosed, duplicate, or malformed tags)
        Based on the fix_b_tags function from the old script
        """
        stack = []
        result = []
        
        # Find all bold tags
        tags = list(re.finditer(r'<(/?)(strong|b)>', line))
        tag_positions = set(tag.start() for tag in tags)
        
        i = 0
        while i < len(line):
            if i in tag_positions:
                tag = tags.pop(0)
                tag_type = tag.group(1)
                tag_name = tag.group(2)
                
                if tag_type == '/' and (not stack or stack[-1] != f'<{tag_name}>'):
                    # Keep closing tag even without opening tag (might be from external source)
                    result.append(tag.group(0))
                elif tag_type == '' and (stack and stack[-1] == f'<{tag_name}>'):
                    # Allow nested tags (like <strong><strong>text</strong></strong>)
                    stack.append(f'<{tag_name}>')
                    result.append(tag.group(0))
                else:
                    if tag_type == '/':
                        if stack:  # Ensure stack is not empty before popping
                            stack.pop()
                        result.append(tag.group(0))  # Always include closing tags
                    else:
                        stack.append(f'<{tag_name}>')
                        result.append(tag.group(0))
                i = tag.end()
            else:
                result.append(line[i])
                i += 1
        
        # Close any unclosed bold tags
        while stack:
            stack.pop()
            result.append('</strong>')
        
        return ''.join(result)
    
    def get_record_counts(self, all_records: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        """Get counts of all record types"""
        counts = {}
        for record_type, records in all_records.items():
            counts[record_type] = len(records)
        return counts
    
    def build_talent_trees_map(self, specializations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build a map of talent names to the trees they appear in"""
        talent_trees = {}
        
        for spec in specializations:
            spec_name = spec.get('name', '')
            talents = spec.get('data', {}).get('talents', [])
            
            for talent in talents:
                if talent not in talent_trees:
                    talent_trees[talent] = []
                talent_trees[talent].append(spec_name)
        
        return talent_trees 