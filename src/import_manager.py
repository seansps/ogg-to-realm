import threading
import time
from typing import Dict, List, Any, Optional, Callable
from api_client import RealmVTTClient
from xml_parser import XMLParser
from json_parser import JSONParser
from data_mapper import DataMapper

class ImportManager:
    def __init__(self, api_client: RealmVTTClient):
        self.api_client = api_client
        self.xml_parser = XMLParser()
        self.json_parser = JSONParser()
        self.data_mapper = DataMapper()
        self.campaign_id = None
        self.selected_sources = []
        self.selected_record_types = []  # All record types by default
        self.max_import_limit = 0  # No limit by default
        self.update_existing = False  # Don't update existing by default
        self.oggdude_directory = ""
        self.adversaries_directory = ""
        self.progress_callback = None
        self.status_callback = None
        self.is_importing = False
        self.import_thread = None
        
        # Progress tracking variables
        self.current_progress = 0
        self.total_progress = 0
        self.current_operation = ""
        self.progress_lock = threading.Lock()
        
    def set_progress_callback(self, callback: Callable[[str, int, int], None]):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def _log_status(self, message: str):
        """Log status message"""
        if self.status_callback:
            self.status_callback(message)
        print(message)
    
    def _update_progress(self, message: str, current: int, total: int):
        """Update progress"""
        with self.progress_lock:
            self.current_progress = current
            self.total_progress = total
            self.current_operation = message
        
        if self.progress_callback:
            self.progress_callback(message, current, total)
    
    def set_campaign_id(self, campaign_id: str):
        """Set the campaign ID for imports"""
        self.campaign_id = campaign_id
        # Also set the campaign ID in the API client
        self.api_client.set_campaign_id(campaign_id)
    
    def set_selected_sources(self, sources: List[str]):
        """Set the selected sources for filtering"""
        self.selected_sources = sources
    
    def set_selected_record_types(self, record_types: List[str]):
        """Set the selected record types for import"""
        self.selected_record_types = record_types
    
    def set_max_import_limit(self, limit: int):
        """Set the maximum number of records to import per type (for testing)"""
        self.max_import_limit = limit
    
    def set_update_existing(self, update_existing: bool):
        """Set whether to update existing records instead of creating new ones"""
        self.update_existing = update_existing
    
    def set_oggdude_directory(self, directory: str):
        """Set the OggDude directory path"""
        self.oggdude_directory = directory
    
    def set_adversaries_directory(self, directory: str):
        """Set the Adversaries directory path"""
        self.adversaries_directory = directory
    
    def parse_files(self) -> Dict[str, int]:
        """
        Parse all files and return record counts
        
        Returns:
            Dictionary mapping record types to counts
        """
        self._log_status("Starting file parsing...")
        
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
        
        # Parse OggDude XML files
        if self.oggdude_directory:
            self._log_status(f"Parsing OggDude files from: {self.oggdude_directory}")
            xml_records = self.xml_parser.scan_directory(self.oggdude_directory, self.selected_sources)
            
            # Merge XML records into all_records
            for record_type, records in xml_records.items():
                if record_type in all_records:
                    all_records[record_type].extend(records)
        
        # Parse Adversaries JSON files
        if self.adversaries_directory:
            self._log_status(f"Parsing Adversaries files from: {self.adversaries_directory}")
            json_records = self.json_parser.scan_directory(self.adversaries_directory, self.selected_sources)
            all_records['npcs'].extend(json_records)
        
        # Filter by selected record types (if any are selected)
        if self.selected_record_types:
            filtered_records = {}
            for record_type in self.selected_record_types:
                if record_type in all_records:
                    filtered_records[record_type] = all_records[record_type]
        else:
            # If no record types selected, use all records
            filtered_records = all_records
        
        # Apply max import limit
        limited_records = {}
        for record_type, records in filtered_records.items():
            if self.max_import_limit > 0 and len(records) > self.max_import_limit:
                limited_records[record_type] = records[:self.max_import_limit]
            else:
                limited_records[record_type] = records
        
        # Get counts
        counts = self.data_mapper.get_record_counts(limited_records)
        
        # Debug: Print what we found
        print(f"DEBUG: Import manager found records:")
        for record_type, records in limited_records.items():
            print(f"  {record_type}: {len(records)}")
        
        self._log_status(f"Parsing complete. Found:")
        for record_type, count in counts.items():
            if count > 0:
                self._log_status(f"  {record_type}: {count}")
        
        return counts
    
    def start_import(self):
        """Start the import process in a separate thread"""
        if self.is_importing:
            self._log_status("Import already in progress")
            return
        
        if not self.campaign_id:
            self._log_status("Error: No campaign ID set")
            return
        
        # Reset progress
        with self.progress_lock:
            self.current_progress = 0
            self.total_progress = 0
            self.current_operation = "Starting import..."
        
        self.is_importing = True
        self.import_thread = threading.Thread(target=self._import_process)
        self.import_thread.daemon = True
        self.import_thread.start()
    
    def stop_import(self):
        """Stop the import process"""
        self.is_importing = False
        self._log_status("Import stopped by user")
    
    def _import_process(self):
        """Main import process"""
        try:
            self._log_status("Starting import process...")
            
            # Step 1: Parse all files
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
            
            # Parse OggDude XML files
            if self.oggdude_directory:
                xml_records = self.xml_parser.scan_directory(self.oggdude_directory, self.selected_sources)
                for record_type, records in xml_records.items():
                    if record_type in all_records:
                        all_records[record_type].extend(records)
            
            # Parse Adversaries JSON files
            if self.adversaries_directory:
                json_records = self.json_parser.scan_directory(self.adversaries_directory, self.selected_sources)
                all_records['npcs'].extend(json_records)
            
            # Filter by selected record types (if any are selected)
            if self.selected_record_types:
                filtered_records = {}
                for record_type in self.selected_record_types:
                    if record_type in all_records:
                        filtered_records[record_type] = all_records[record_type]
            else:
                # If no record types selected, use all records
                filtered_records = all_records
            
            # Apply max import limit
            limited_records = {}
            for record_type, records in filtered_records.items():
                if self.max_import_limit > 0 and len(records) > self.max_import_limit:
                    limited_records[record_type] = records[:self.max_import_limit]
                else:
                    limited_records[record_type] = records
            
            # Calculate total records
            total_records = sum(len(records) for records in limited_records.values())
            current_record = 0
            
            # Step 2: Import in order (Items first, then others, then NPCs last)
            import_order = [
                ('items', 'Items'),
                ('species', 'Species'),
                ('talents', 'Talents'),
                ('specializations', 'Specializations'),
                ('careers', 'Careers'),
                ('force_powers', 'Force Powers'),
                ('skills', 'Skills'),
                ('signature_abilities', 'Signature Abilities'),
                ('npcs', 'NPCs')
            ]
            
            for record_type, display_name in import_order:
                if not self.is_importing:
                    break
                
                # Only process record types that exist in limited_records
                if record_type not in limited_records or not limited_records[record_type]:
                    continue
                
                records = limited_records[record_type]
                self._log_status(f"Importing {display_name}...")
                
                for i, record in enumerate(records):
                    if not self.is_importing:
                        break
                    
                    try:
                        # Convert record to Realm VTT format
                        realm_record = self.data_mapper.convert_oggdude_to_realm_vtt(
                            record, self.campaign_id, self._get_category_for_record(record)
                        )
                        
                        record_name = record.get('name', '')
                        
                        # Check if we should update existing records
                        if self.update_existing and record_name:
                            # Try to find existing record by name
                            existing_record = self.api_client.find_record_by_name(record_type, record_name)
                            
                            if existing_record:
                                # Update existing record
                                updated_record = self.api_client.patch_record(record_type, existing_record['_id'], realm_record)
                                created_record = updated_record
                                self._log_status(f"Updated existing {record_type}: {record_name}")
                            else:
                                # Create new record
                                if record_type == 'npcs':
                                    created_record = self.api_client.create_npc(realm_record)
                                elif record_type == 'items':
                                    created_record = self.api_client.create_item(realm_record)
                                else:
                                    created_record = self.api_client.create_record(realm_record)
                                self._log_status(f"Created new {record_type}: {record_name}")
                        else:
                            # Always create new records
                            if record_type == 'npcs':
                                created_record = self.api_client.create_npc(realm_record)
                            elif record_type == 'items':
                                created_record = self.api_client.create_item(realm_record)
                            else:
                                created_record = self.api_client.create_record(realm_record)
                        
                        # Store mapping for later use
                        if record_name:
                            if record_type == 'items':
                                self.data_mapper.add_item_mapping(record_name, created_record['_id'])
                            elif record_type == 'talents':
                                self.data_mapper.add_talent_mapping(record_name, created_record['_id'])
                            elif record_type == 'species':
                                self.data_mapper.add_species_mapping(record_name, created_record['_id'])
                            elif record_type == 'careers':
                                self.data_mapper.add_career_mapping(record_name, created_record['_id'])
                            elif record_type == 'specializations':
                                self.data_mapper.add_spec_mapping(record_name, created_record['_id'])
                            elif record_type == 'force_powers':
                                self.data_mapper.add_force_power_mapping(record_name, created_record['_id'])
                        
                        current_record += 1
                        self._update_progress(
                            f"Imported {record_name} ({record_type})",
                            current_record,
                            total_records
                        )
                        
                        # Small delay to avoid overwhelming the API
                        time.sleep(0.1)
                        
                    except Exception as e:
                        self._log_status(f"Error importing {record.get('name', 'Unknown')}: {e}")
                        current_record += 1
                        self._update_progress(
                            f"Failed to import {record.get('name', 'Unknown')}",
                            current_record,
                            total_records
                        )
                
                self._log_status(f"Completed importing {display_name}")
            
            if self.is_importing:
                self._log_status("Import process completed successfully!")
            else:
                self._log_status("Import process was stopped")
                
        except Exception as e:
            self._log_status(f"Import process failed: {e}")
        finally:
            self.is_importing = False
    
    def _get_category_for_record(self, record: Dict[str, Any]) -> str:
        """Get the category for a record based on its source"""
        source = record.get('source', '')
        
        # Map source to category based on selected sources
        for source_config in self.xml_parser.sources_config['sources']:
            if source_config['key'] in self.selected_sources:
                for oggdude_source in source_config['oggdude_sources']:
                    if oggdude_source.lower() in source.lower():
                        return source_config['name']
        
        # Default category
        return "Star Wars RPG"
    
    def is_import_running(self) -> bool:
        """Check if import is currently running"""
        return self.is_importing
    
    def get_import_progress(self) -> tuple:
        """Get current import progress (if available)"""
        with self.progress_lock:
            return (self.current_progress, self.total_progress)
    
    def get_current_operation(self) -> str:
        """Get the current operation being performed"""
        with self.progress_lock:
            return self.current_operation
    
    def get_progress_percentage(self) -> float:
        """Get progress as a percentage (0.0 to 100.0)"""
        with self.progress_lock:
            if self.total_progress > 0:
                return (self.current_progress / self.total_progress) * 100.0
            return 0.0 