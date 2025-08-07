import re
import uuid
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
            "shared": False,
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