import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class JSONParser:
    def __init__(self):
        self.sources_config = self._load_sources_config()
        self._items_loader = None  # Will be initialized when needed
        # Cache of adversary definition files per base directory
        self._defs_cache = {}
    
    def _load_sources_config(self) -> Dict[str, Any]:
        """Load sources configuration"""
        try:
            with open('config/sources.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: sources.json not found, using default sources")
            return {"sources": []}
    
    def parse_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a single JSON file and extract records
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of dictionaries containing parsed records
        """
        try:
            # Try different encodings
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            data = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        data = json.load(f)
                    break
                except UnicodeDecodeError:
                    continue
                except json.JSONDecodeError:
                    continue
            
            if data is None:
                print(f"Error: Could not parse {file_path} with any supported encoding")
                return []
            
            records = []
            base_dir = Path(file_path).parent
            adversary_defs = self._load_adversary_definitions(base_dir)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # If the file contains a list of records (adversaries format)
                filename = Path(file_path).stem
                for item in data:
                    # Add filename as subtype info
                    item['_filename'] = filename
                    # Attach adversary definitions so downstream can use them
                    item['definitions'] = adversary_defs
                    record = self._extract_npc_data(item)
                    if record:
                        records.append(record)
            elif isinstance(data, dict):
                # If the file contains a single record or structured data
                if 'npcs' in data:
                    for npc in data['npcs']:
                        if isinstance(npc, dict):
                            npc['definitions'] = adversary_defs
                        record = self._extract_npc_data(npc)
                        if record:
                            records.append(record)
                else:
                    # Assume it's a single NPC record
                    if isinstance(data, dict):
                        data['definitions'] = adversary_defs
                    record = self._extract_npc_data(data)
                    if record:
                        records.append(record)
            
            return records
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file {file_path}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error parsing {file_path}: {e}")
            return []
    
    def _extract_npc_data(self, npc_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract NPC data from JSON object"""
        try:
            # Handle different NPC data structures
            name = npc_data.get('name') or npc_data.get('Name') or 'Unknown NPC'
            description = npc_data.get('description') or npc_data.get('Description') or ''
            notes = npc_data.get('notes', '')
            
            # Extract type and subtype for adversaries format
            npc_type = npc_data.get('type', 'Rival')
            filename = npc_data.get('_filename', '')
            subtype = filename.replace('-', ' ').title() if filename else ''
            
            # Extract source from tags or direct source field
            source = ''
            tags = npc_data.get('tags', [])
            if isinstance(tags, list):
                # Look for source-related tags
                for tag in tags:
                    if isinstance(tag, str) and (tag.startswith('source:') or tag.startswith('adventure:') or tag.startswith('book:')):
                        source = tag
                        break
            
            # If no source found in tags, try direct source field
            if not source:
                source = npc_data.get('source') or npc_data.get('Source') or ''
            
            # Extract characteristics
            characteristics = self._extract_characteristics(npc_data)
            
            # Extract skills
            skills = self._extract_skills(npc_data)
            
            # Extract talents
            talents = self._extract_talents(npc_data)
            
            # Extract abilities (can be strings or objects with name/description)
            abilities = self._extract_abilities(npc_data)
            
            # Extract equipment
            equipment = self._extract_equipment(npc_data)
            
            # Extract weapons
            weapons = self._extract_weapons(npc_data)
            
            # Extract armor
            armor = self._extract_armor(npc_data)
            
            # Extract derived stats for adversaries format
            derived = npc_data.get('derived', {})
            
            # Pull through attached definition maps if present
            definitions = npc_data.get('definitions') if isinstance(npc_data, dict) else None

            npc = {
                'recordType': 'npcs',
                'name': name,
                'description': description,
                'notes': notes,
                'source': source,
                'data': {
                    'type': npc_type,
                    'subtype': subtype,
                    'characteristics': characteristics,
                    'derived': derived,
                    'skills': skills,
                    'talents': talents,
                    'abilities': abilities,
                    'equipment': equipment,
                    'weapons': weapons,
                    'armor': armor,
                    'gear': npc_data.get('gear', []),
                    'tags': tags,
                    'definitions': definitions,
                    'woundThreshold': npc_data.get('woundThreshold', npc_data.get('WoundThreshold', derived.get('wounds', 10))),
                    'strainThreshold': npc_data.get('strainThreshold', npc_data.get('StrainThreshold', derived.get('strain', 10))),
                    'soak': npc_data.get('soak', npc_data.get('Soak', derived.get('soak', 0))),
                    'defense': npc_data.get('defense', npc_data.get('Defense', derived.get('defence', 0))),
                    'species': npc_data.get('species', npc_data.get('Species', '')),
                    'career': npc_data.get('career', npc_data.get('Career', '')),
                    'specialization': npc_data.get('specialization', npc_data.get('Specialization', '')),
                },
                'unidentifiedName': 'Unknown NPC',
                'locked': True
            }
            
            return npc
            
        except Exception as e:
            print(f"Error extracting NPC data: {e}")
            return None
    
    def _extract_characteristics(self, npc_data: Dict[str, Any]) -> Dict[str, int]:
        """Extract characteristics from NPC data"""
        characteristics = {}
        
        # Try different possible field names
        chars_data = (
            npc_data.get('characteristics') or 
            npc_data.get('Characteristics') or 
            npc_data.get('chars') or 
            npc_data.get('Chars') or 
            {}
        )
        
        if isinstance(chars_data, dict):
            for char in ['brawn', 'agility', 'intellect', 'cunning', 'willpower', 'presence']:
                characteristics[char] = chars_data.get(char, chars_data.get(char.title(), 1))
        else:
            # Fallback to individual fields
            characteristics = {
                'brawn': npc_data.get('brawn', npc_data.get('Brawn', 1)),
                'agility': npc_data.get('agility', npc_data.get('Agility', 1)),
                'intellect': npc_data.get('intellect', npc_data.get('Intellect', 1)),
                'cunning': npc_data.get('cunning', npc_data.get('Cunning', 1)),
                'willpower': npc_data.get('willpower', npc_data.get('Willpower', 1)),
                'presence': npc_data.get('presence', npc_data.get('Presence', 1))
            }
        
        return characteristics
    
    def _extract_skills(self, npc_data: Dict[str, Any]) -> Dict[str, int]:
        """Extract skills from NPC data"""
        skills = {}
        
        # Try different possible field names
        skills_data = (
            npc_data.get('skills') or 
            npc_data.get('Skills') or 
            {}
        )
        
        if isinstance(skills_data, dict):
            for skill, rank in skills_data.items():
                if isinstance(rank, int):
                    skills[skill] = rank
                elif isinstance(rank, str):
                    try:
                        skills[skill] = int(rank)
                    except ValueError:
                        skills[skill] = 0
        elif isinstance(skills_data, list):
            # Handle skills as a list (e.g., ["Athletics", "Discipline", "Melee"])
            for skill in skills_data:
                if isinstance(skill, str):
                    skills[skill] = 1  # Default rank of 1 for list format
        
        return skills
    
    def _extract_talents(self, npc_data: Dict[str, Any]) -> List[str]:
        """Extract talents from NPC data"""
        talents = []
        
        # Try different possible field names
        talents_data = (
            npc_data.get('talents') or 
            npc_data.get('Talents') or 
            npc_data.get('talent') or 
            npc_data.get('Talent') or 
            []
        )
        
        if isinstance(talents_data, list):
            for talent in talents_data:
                if isinstance(talent, str):
                    talents.append(talent)
                elif isinstance(talent, dict):
                    talent_name = talent.get('name') or talent.get('Name') or talent.get('key') or talent.get('Key')
                    if talent_name:
                        talents.append(talent_name)
        elif isinstance(talents_data, str):
            # Single talent as string
            talents.append(talents_data)
        
        return talents

    def _extract_abilities(self, npc_data: Dict[str, Any]) -> List[Any]:
        """Extract abilities from NPC data (strings or objects with name/description)"""
        abilities: List[Any] = []
        abilities_data = (
            npc_data.get('abilities') or
            npc_data.get('Abilities') or
            []
        )
        if isinstance(abilities_data, list):
            for ability in abilities_data:
                if isinstance(ability, str):
                    abilities.append(ability)
                elif isinstance(ability, dict):
                    name = ability.get('name') or ability.get('Name')
                    description = ability.get('description') or ability.get('Description') or ''
                    if name:
                        abilities.append({'name': name, 'description': description})
        elif isinstance(abilities_data, str):
            abilities.append(abilities_data)
        return abilities
    
    def _extract_equipment(self, npc_data: Dict[str, Any]) -> List[str]:
        """Extract equipment from NPC data"""
        equipment = []
        
        # Try different possible field names
        equipment_data = (
            npc_data.get('equipment') or 
            npc_data.get('Equipment') or 
            npc_data.get('gear') or 
            npc_data.get('Gear') or 
            []
        )
        
        if isinstance(equipment_data, list):
            for item in equipment_data:
                if isinstance(item, str):
                    equipment.append(item)
                elif isinstance(item, dict):
                    item_name = item.get('name') or item.get('Name') or item.get('key') or item.get('Key')
                    if item_name:
                        equipment.append(item_name)
        elif isinstance(equipment_data, str):
            # Single equipment item as string
            equipment.append(equipment_data)
        
        return equipment
    
    def _extract_weapons(self, npc_data: Dict[str, Any]) -> List[str]:
        """Extract weapons from NPC data"""
        weapons = []
        
        # Try different possible field names
        weapons_data = (
            npc_data.get('weapons') or 
            npc_data.get('Weapons') or 
            npc_data.get('weapon') or 
            npc_data.get('Weapon') or 
            []
        )
        
        if isinstance(weapons_data, list):
            for weapon in weapons_data:
                if isinstance(weapon, str):
                    weapons.append(weapon)
                elif isinstance(weapon, dict):
                    weapon_name = weapon.get('name') or weapon.get('Name') or weapon.get('key') or weapon.get('Key')
                    if weapon_name:
                        weapons.append(weapon_name)
        elif isinstance(weapons_data, str):
            # Single weapon as string
            weapons.append(weapons_data)
        
        return weapons
    
    def _extract_armor(self, npc_data: Dict[str, Any]) -> List[str]:
        """Extract armor from NPC data"""
        armor = []
        
        # Try different possible field names
        armor_data = (
            npc_data.get('armor') or 
            npc_data.get('Armor') or 
            []
        )
        
        if isinstance(armor_data, list):
            for item in armor_data:
                if isinstance(item, str):
                    armor.append(item)
                elif isinstance(item, dict):
                    item_name = item.get('name') or item.get('Name') or item.get('key') or item.get('Key')
                    if item_name:
                        armor.append(item_name)
        elif isinstance(armor_data, str):
            # Single armor item as string
            armor.append(armor_data)
        
        return armor
    
    def filter_by_sources(self, records: List[Dict[str, Any]], selected_sources: List[str]) -> List[Dict[str, Any]]:
        """Filter records by selected sources"""
        if not selected_sources:
            return records
        
        filtered_records = []
        for record in records:
            # Check if record has tags (adversaries format) or source field (OggDude format)
            record_tags = record.get('data', {}).get('tags', [])
            record_source = record.get('source', '')
            
            # Ensure record_source is a string
            if not isinstance(record_source, str):
                record_source = str(record_source) if record_source else ''
            
            record_matched = False
            for source_config in self.sources_config['sources']:
                if source_config['key'] in selected_sources:
                    # Check adversaries sources in tags
                    for adversaries_source in source_config['adversaries_sources']:
                        if isinstance(record_tags, list) and adversaries_source in record_tags:
                            filtered_records.append(record)
                            record_matched = True
                            break
                        # Also check in source field for backwards compatibility
                        elif isinstance(adversaries_source, str) and adversaries_source.lower() in record_source.lower():
                            filtered_records.append(record)
                            record_matched = True
                            break
                    
                    if record_matched:
                        break
        
        return filtered_records
    
    def scan_directory(self, directory_path: str, selected_sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scan directory for JSON files and parse them
        
        Args:
            directory_path: Path to directory to scan
            selected_sources: List of selected source keys to filter by
            
        Returns:
            List of NPC records
        """
        all_records = []
        
        directory = Path(directory_path)
        if not directory.exists():
            print(f"Directory {directory_path} does not exist")
            return all_records
        
        # Scan for JSON files recursively (exclude definition files)
        json_files_all = list(directory.rglob('*.json'))
        def_names = {'talents.json', 'abilities.json', 'force-powers.json'}
        json_files = [p for p in json_files_all if p.name.lower() not in def_names]
        print(f"Found {len(json_files)} JSON files in {directory_path}")
        
        for json_file in json_files:
            print(f"Parsing {json_file}")
            records = self.parse_json_file(str(json_file))
            
            # Filter by sources if specified
            if selected_sources:
                records = self.filter_by_sources(records, selected_sources)
            
            all_records.extend(records)
        
        return all_records 
    
    def get_items_loader(self):
        """Get or create ItemsLoader for looking up items from XML"""
        if self._items_loader is None:
            from xml_parser import XMLParser
            from items_loader import ItemsLoader
            xml_parser = XMLParser()
            self._items_loader = ItemsLoader(xml_parser)
            self._items_loader.load_all_items()
        return self._items_loader
    
    def get_item_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get an item by key from XML files (for NPC weapon lookup)
        
        Args:
            key: The item key to look up
            
        Returns:
            Item data or None if not found
        """
        items_loader = self.get_items_loader()
        return items_loader.get_item_by_key(key)

    def _load_adversary_definitions(self, base_dir: Path) -> Dict[str, Dict[str, Any]]:
        """Load talents.json, abilities.json, force-powers.json under base_dir (recursively) and index by name."""
        try:
            base_key = str(base_dir.resolve())
        except Exception:
            base_key = str(base_dir)
        if base_key in self._defs_cache:
            return self._defs_cache[base_key]

        talents_map: Dict[str, Dict[str, Any]] = {}
        abilities_map: Dict[str, Dict[str, Any]] = {}
        force_powers_map: Dict[str, Dict[str, Any]] = {}

        def index_list(obj, target_map):
            try:
                if isinstance(obj, list):
                    for entry in obj:
                        if isinstance(entry, dict):
                            name = entry.get('name') or entry.get('Name')
                            desc = entry.get('description') or entry.get('Description') or ''
                            if isinstance(name, str):
                                target_map[name.strip().lower()] = {'name': name.strip(), 'description': desc}
                elif isinstance(obj, dict):
                    for k, v in obj.items():
                        if not isinstance(k, str):
                            continue
                        key = k.strip().lower()
                        if isinstance(v, str):
                            target_map[key] = {'name': k.strip(), 'description': v}
                        elif isinstance(v, dict):
                            name = (v.get('name') or k).strip()
                            desc = v.get('description') or ''
                            target_map[key] = {'name': name, 'description': desc}
            except Exception:
                pass

        try:
            for p in base_dir.rglob('*.json'):
                name = p.name.lower()
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                except Exception:
                    continue
                if name == 'talents.json':
                    index_list(content, talents_map)
                elif name == 'abilities.json':
                    index_list(content, abilities_map)
                elif name == 'force-powers.json':
                    index_list(content, force_powers_map)
        except Exception:
            pass

        defs = {
            'talents': talents_map,
            'abilities': abilities_map,
            'force_powers': force_powers_map,
        }
        self._defs_cache[base_key] = defs
        return defs