"""
Shared utility for loading items from OggDude XML files.
This can be used by both XMLParser and JSONParser for consistent item lookup.
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional


class ItemsLoader:
    """Utility class for loading items from OggDude XML files"""
    
    def __init__(self, xml_parser_instance=None):
        """
        Initialize the items loader
        
        Args:
            xml_parser_instance: XMLParser instance to use for parsing
        """
        self.xml_parser = xml_parser_instance
        self._items = {}  # Cache for all items by key
    
    def load_all_items(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all items from OggDude XML files and return them as a dictionary keyed by item key
        
        Returns:
            Dictionary mapping item keys to item data
        """
        if self._items:
            return self._items  # Return cached items if already loaded
        
        if not self.xml_parser:
            print("Warning: No XMLParser instance provided to ItemsLoader")
            return {}
        
        try:
            oggdata_dir = self.xml_parser._find_oggdata_directory()
            
            if oggdata_dir is None:
                print("Warning: OggData directory not found, item lookup will not work")
                return {}
            
            # Find all XML files recursively
            xml_files = []
            for root, dirs, files in os.walk(oggdata_dir):
                for file in files:
                    if file.endswith('.xml'):
                        xml_files.append(os.path.join(root, file))
            
            print(f"Scanning {len(xml_files)} XML file(s) for items")
            
            self._items = {}
            files_with_items = 0
            
            for xml_file in xml_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    
                    # Check if this file contains items by looking for known item structures
                    items_found = False
                    
                    # Check for <Weapons><Weapon> structure
                    if root.tag == 'Weapons':
                        items = self.xml_parser._parse_weapons(root)
                        for item in items:
                            key = item.get('key')
                            if key:
                                self._items[key] = item
                                items_found = True
                    
                    # Check for <Armors><Armor> structure  
                    elif root.tag == 'Armors':
                        items = self.xml_parser._parse_armor(root)
                        for item in items:
                            key = item.get('key')
                            if key:
                                self._items[key] = item
                                items_found = True
                    
                    # Check for <Gears><Gear> structure
                    elif root.tag == 'Gears':
                        items = self.xml_parser._parse_gear(root)
                        for item in items:
                            key = item.get('key')
                            if key:
                                self._items[key] = item
                                items_found = True
                    
                    # Check for <Attachments><Attachment> structure  
                    elif root.tag == 'Attachments':
                        items = self.xml_parser._parse_item_attachments(root)
                        for item in items:
                            key = item.get('key')
                            if key:
                                self._items[key] = item
                                items_found = True
                    
                    if items_found:
                        files_with_items += 1
                        
                except Exception as e:
                    # Silently skip files that can't be parsed - they're probably not item files
                    continue
            
            print(f"Loaded {len(self._items)} items from {files_with_items} file(s)")
            return self._items
            
        except Exception as e:
            print(f"Error loading items: {e}")
            return {}
    
    def get_item_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get an item by its key
        
        Args:
            key: The item key to look up
            
        Returns:
            Item data dictionary or None if not found
        """
        if not self._items:
            self.load_all_items()
        
        return self._items.get(key)
    
    def get_all_items(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all loaded items
        
        Returns:
            Dictionary mapping item keys to item data
        """
        if not self._items:
            self.load_all_items()
        
        return self._items.copy()