import re
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
        record_type = oggdude_record.get('recordType', 'unknown')
        
        if record_type == 'items':
            return self._convert_item(oggdude_record, campaign_id, category)
        elif record_type == 'species':
            return self._convert_species(oggdude_record, campaign_id, category)
        elif record_type == 'careers':
            return self._convert_career(oggdude_record, campaign_id, category)
        elif record_type == 'specializations':
            return self._convert_specialization(oggdude_record, campaign_id, category)
        elif record_type == 'talents':
            return self._convert_talent(oggdude_record, campaign_id, category)
        elif record_type == 'force_powers':
            return self._convert_force_power(oggdude_record, campaign_id, category)
        elif record_type == 'skills':
            return self._convert_skill(oggdude_record, campaign_id, category)
        elif record_type == 'vehicles':
            return self._convert_vehicle(oggdude_record, campaign_id, category)
        elif record_type == 'npcs':
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
        item_type = item.get('type', data.get('type', 'gear'))
        
        # Convert description and add to data
        if 'description' in item:
            data['description'] = self._convert_description(item['description'])
        
        # Handle weapon-specific conversions (check for both 'weapon' and 'ranged weapon'/'melee weapon')
        if item_type == 'weapon' or (item_type in ['ranged weapon', 'melee weapon']):
            data = self._convert_weapon_data(data, item)
        elif item_type == 'gear':
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
        # Get the original type from the item data
        original_type = item.get('data', {}).get('type', 'Gear')
        
        # Set type to 'general' for gear items
        data['type'] = 'general'
        
        # Set subtype to the original OggDude Type value
        data['subtype'] = original_type
    
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
        weapon_type = data.get('type', '')
        skill_key = data.get('weaponSkill', '')
        original_skill_key = data.get('originalSkillKey', skill_key)  # Use original if available
        original_type = data.get('originalType', weapon_type)  # Use original type if available
        
        if original_type == 'Vehicle':
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
            data['subtype'] = original_type
        
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
        data = power.get('data', {})
        
        realm_record = {
            'name': power.get('name', 'Unknown Force Power'),
            'category': category or 'Force and Destiny Core Rulebook',
            'campaignId': campaign_id,
            'recordType': 'force_powers',
            'data': {
                'name': power.get('name', 'Unknown Force Power'),
                'description': self._convert_description(power.get('description', '')),
                'activation': data.get('activation', ''),
                'forcePowerType': data.get('forcePowerType', ''),
                'upgrades': data.get('upgrades', [])
            },
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
        
        # Convert description and add to data
        if 'description' in vehicle:
            data['description'] = self._convert_description(vehicle['description'])
        
        # Convert restricted field from true/false to yes/no
        if 'restricted' in data:
            data['restricted'] = self._convert_restricted_value(data['restricted'])
        
        realm_vehicle = {
            "name": vehicle.get('name', 'Unknown Vehicle'),
            "recordType": "vehicles",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Vehicle",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": data
        }
        
        return realm_vehicle
    
    def _convert_npc(self, npc: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert NPC to Realm VTT format"""
        # Get the data and ensure it's a dict
        data = npc.get('data', {})
        if not isinstance(data, dict):
            data = {}
        
        # Convert description and add to data
        if 'description' in npc:
            data['description'] = self._convert_description(npc['description'])
        
        realm_npc = {
            "name": npc.get('name', 'Unknown NPC'),
            "recordType": "npcs",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown NPC",
            "identified": False,
            "shared": False,
            "locked": True,
            "data": data
        }
        
        # Link equipment to existing items
        equipment = realm_npc['data'].get('equipment', [])
        linked_equipment = []
        for item_name in equipment:
            item_id = self.get_item_id(item_name)
            if item_id:
                linked_equipment.append({
                    "_id": item_id,
                    "name": item_name,
                    "campaignId": campaign_id,
                    "recordType": "items",
                    "identified": True,
                    "category": category,
                    "unidentifiedName": "Unidentified Items"
                })
            else:
                # Create a placeholder item if not found
                linked_equipment.append({
                    "name": item_name,
                    "campaignId": campaign_id,
                    "recordType": "items",
                    "identified": False,
                    "category": category,
                    "unidentifiedName": "Unidentified Items",
                    "data": {
                        "type": "gear",
                        "price": "0",
                        "encumbrance": 0,
                        "rarity": 0,
                        "restricted": "no"
                    }
                })
        
        realm_npc['data']['equipment'] = linked_equipment
        
        # Link weapons to existing items
        weapons = realm_npc['data'].get('weapons', [])
        linked_weapons = []
        for weapon_name in weapons:
            weapon_id = self.get_item_id(weapon_name)
            if weapon_id:
                linked_weapons.append({
                    "_id": weapon_id,
                    "name": weapon_name,
                    "campaignId": campaign_id,
                    "recordType": "items",
                    "identified": True,
                    "category": category,
                    "unidentifiedName": "Unidentified Items"
                })
            else:
                # Create a placeholder weapon if not found
                linked_weapons.append({
                    "name": weapon_name,
                    "campaignId": campaign_id,
                    "recordType": "items",
                    "identified": False,
                    "category": category,
                    "unidentifiedName": "Unidentified Items",
                    "data": {
                        "type": "ranged weapon",
                        "price": "0",
                        "encumbrance": 0,
                        "rarity": 0,
                        "weaponSkill": "Ranged (Light)",
                        "damage": 0,
                        "crit": 0,
                        "range": "Short",
                        "hardpoints": 0,
                        "restricted": "no",
                        "special": []
                    }
                })
        
        realm_npc['data']['weapons'] = linked_weapons
        
        # Link armor to existing items
        armor = realm_npc['data'].get('armor', [])
        linked_armor = []
        for armor_name in armor:
            armor_id = self.get_item_id(armor_name)
            if armor_id:
                linked_armor.append({
                    "_id": armor_id,
                    "name": armor_name,
                    "campaignId": campaign_id,
                    "recordType": "items",
                    "identified": True,
                    "category": category,
                    "unidentifiedName": "Unidentified Items"
                })
            else:
                # Create a placeholder armor if not found
                linked_armor.append({
                    "name": armor_name,
                    "campaignId": campaign_id,
                    "recordType": "items",
                    "identified": False,
                    "category": category,
                    "unidentifiedName": "Unidentified Items",
                    "data": {
                        "type": "armor",
                        "price": "0",
                        "encumbrance": 0,
                        "rarity": 0,
                        "restricted": "no",
                        "soak": 0,
                        "defense": 0,
                        "hardpoints": 0
                    }
                })
        
        realm_npc['data']['armor'] = linked_armor
        
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