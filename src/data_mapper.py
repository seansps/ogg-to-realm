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
        elif record_type == 'vehicles':
            return self._convert_vehicle(oggdude_record, campaign_id, category)
        elif record_type == 'npcs':
            return self._convert_npc(oggdude_record, campaign_id, category)
        else:
            return self._convert_generic(oggdude_record, campaign_id, category)
    
    def _convert_item(self, item: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert item to Realm VTT format"""
        item_type = item.get('type', 'gear')
        
        realm_item = {
            "name": item.get('name', 'Unknown Item'),
            "recordType": "items",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unidentified Items",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": item.get('data', {}),
            "fields": item.get('fields', {})
        }
        
        # Convert description
        if 'description' in item:
            realm_item['description'] = self._convert_description(item['description'])
        
        return realm_item
    
    def _convert_species(self, species: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert species to Realm VTT format"""
        realm_species = {
            "name": species.get('name', 'Unknown Species'),
            "recordType": "species",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Species",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": species.get('data', {})
        }
        
        # Convert description
        if 'description' in species:
            realm_species['description'] = self._convert_description(species['description'])
        
        return realm_species
    
    def _convert_career(self, career: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert career to Realm VTT format"""
        realm_career = {
            "name": career.get('name', 'Unknown Career'),
            "recordType": "careers",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Career",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": career.get('data', {})
        }
        
        # Convert description
        if 'description' in career:
            realm_career['description'] = self._convert_description(career['description'])
        
        return realm_career
    
    def _convert_specialization(self, spec: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert specialization to Realm VTT format"""
        realm_spec = {
            "name": spec.get('name', 'Unknown Specialization'),
            "recordType": "specializations",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Specialization",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": spec.get('data', {})
        }
        
        # Convert description
        if 'description' in spec:
            realm_spec['description'] = self._convert_description(spec['description'])
        
        return realm_spec
    
    def _convert_talent(self, talent: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert talent to Realm VTT format"""
        realm_talent = {
            "name": talent.get('name', 'Unknown Talent'),
            "recordType": "talents",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Talent",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": talent.get('data', {})
        }
        
        # Convert description
        if 'description' in talent:
            realm_talent['description'] = self._convert_description(talent['description'])
        
        return realm_talent
    
    def _convert_force_power(self, power: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert force power to Realm VTT format"""
        realm_power = {
            "name": power.get('name', 'Unknown Force Power'),
            "recordType": "force_powers",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Force Power",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": power.get('data', {})
        }
        
        # Convert description
        if 'description' in power:
            realm_power['description'] = self._convert_description(power['description'])
        
        return realm_power
    
    def _convert_vehicle(self, vehicle: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert vehicle to Realm VTT format"""
        realm_vehicle = {
            "name": vehicle.get('name', 'Unknown Vehicle'),
            "recordType": "vehicles",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown Vehicle",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": vehicle.get('data', {})
        }
        
        # Convert description
        if 'description' in vehicle:
            realm_vehicle['description'] = self._convert_description(vehicle['description'])
        
        return realm_vehicle
    
    def _convert_npc(self, npc: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert NPC to Realm VTT format"""
        realm_npc = {
            "name": npc.get('name', 'Unknown NPC'),
            "recordType": "npcs",
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": "Unknown NPC",
            "identified": False,
            "shared": False,
            "locked": True,
            "data": npc.get('data', {})
        }
        
        # Convert description
        if 'description' in npc:
            realm_npc['description'] = self._convert_description(npc['description'])
        
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
    
    def _convert_generic(self, record: Dict[str, Any], campaign_id: str, category: str) -> Dict[str, Any]:
        """Convert generic record to Realm VTT format"""
        realm_record = {
            "name": record.get('name', 'Unknown Record'),
            "recordType": record.get('recordType', 'records'),
            "campaignId": campaign_id,
            "category": category,
            "unidentifiedName": f"Unknown {record.get('recordType', 'Record')}",
            "identified": True,
            "shared": False,
            "locked": True,
            "data": record.get('data', {})
        }
        
        # Convert description
        if 'description' in record:
            realm_record['description'] = self._convert_description(record['description'])
        
        return realm_record
    
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