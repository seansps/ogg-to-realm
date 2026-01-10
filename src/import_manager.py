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
        self.data_mapper = DataMapper(api_client=api_client)
        self.campaign_id = None
        self.portraits_campaign_id = None  # Optional campaign ID to copy portraits from
        self.portraits_cache = {}  # Cache of records from portraits campaign
        self.selected_sources = []
        self.selected_record_types = []  # All record types by default
        self.max_import_limit = 0  # No limit by default
        self.update_existing = False  # Don't update existing by default
        self.category = ""  # No category by default
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

    def set_portraits_campaign_id(self, portraits_campaign_id: str):
        """Set the portraits campaign ID for copying portraits/tokens"""
        self.portraits_campaign_id = portraits_campaign_id
    
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
    
    def set_category(self, category: str):
        """Set the category for all imported records"""
        self.category = category
    
    def set_oggdude_directory(self, directory: str):
        """Set the OggDude directory path"""
        self.oggdude_directory = directory
        # Update the XML parser with the new directory
        if self.xml_parser:
            self.xml_parser.set_data_directory(directory)
    
    def set_adversaries_directory(self, directory: str):
        """Set the Adversaries directory path"""
        self.adversaries_directory = directory

    def _load_portraits_from_campaign(self, record_types: List[str]):
        """
        Load portraits and tokens from the portraits campaign for the specified record types

        Args:
            record_types: List of record types to load portraits for
        """
        if not self.portraits_campaign_id:
            return

        self._log_status(f"Loading portraits from campaign {self.portraits_campaign_id}...")

        # Save the current campaign ID
        original_campaign_id = self.api_client.campaign_id

        # Temporarily switch to the portraits campaign
        self.api_client.set_campaign_id(self.portraits_campaign_id)

        try:
            # Initialize portraits cache structure
            self.portraits_cache = {}

            for record_type in record_types:
                self.portraits_cache[record_type] = {}

                # Note: We'll populate this cache on-demand during import
                # to avoid fetching all records upfront (which could be expensive)

        finally:
            # Restore the original campaign ID
            self.api_client.set_campaign_id(original_campaign_id)

        self._log_status(f"Portraits campaign configured for on-demand portrait loading")

    def _get_portrait_from_cache(self, record_type: str, record_name: str) -> Optional[Dict[str, Any]]:
        """
        Get portrait and token from the portraits campaign for a specific record

        Args:
            record_type: Type of record ('items', 'npcs', etc.)
            record_name: Name of the record

        Returns:
            Dictionary with 'img' and optionally 'token' fields, or None
        """
        if not self.portraits_campaign_id:
            return None

        # Check if we've already looked up this record
        if record_type in self.portraits_cache:
            if record_name in self.portraits_cache[record_type]:
                return self.portraits_cache[record_type][record_name]

        # Save the current campaign ID
        original_campaign_id = self.api_client.campaign_id

        try:
            # Temporarily switch to the portraits campaign
            self.api_client.set_campaign_id(self.portraits_campaign_id)

            # Map record_type to API endpoint type
            api_record_type = 'npcs' if record_type in ('adversaries', 'vehicles') else record_type

            # Try to find the record by name
            portrait_record = self.api_client.find_record_by_name(api_record_type, record_name)

            if portrait_record:
                # Extract img and token fields
                result = {}
                if 'img' in portrait_record:
                    result['img'] = portrait_record['img']
                if 'token' in portrait_record:
                    result['token'] = portrait_record['token']

                # Cache the result
                if record_type not in self.portraits_cache:
                    self.portraits_cache[record_type] = {}
                self.portraits_cache[record_type][record_name] = result if result else None

                return result if result else None

            # Cache the negative result to avoid repeated lookups
            if record_type not in self.portraits_cache:
                self.portraits_cache[record_type] = {}
            self.portraits_cache[record_type][record_name] = None

            return None

        except Exception as e:
            # Log error but don't fail the import
            self._log_status(f"Warning: Could not fetch portrait for {record_name}: {e}")
            return None

        finally:
            # Restore the original campaign ID
            self.api_client.set_campaign_id(original_campaign_id)
    
    def parse_files(self) -> Dict[str, int]:
        """
        Parse all files and return record counts
        
        Returns:
            Dictionary mapping record types to counts
        """
        self._log_status("Starting file parsing...")

        all_records = {
            'adversaries': [],
            'vehicles': [],
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

            # Merge XML records into all_records, splitting NPCs into adversaries/vehicles
            for record_type, records in xml_records.items():
                if record_type == 'npcs':
                    # Split NPCs into adversaries and vehicles based on data.type
                    for record in records:
                        if record.get('data', {}).get('type') == 'vehicle':
                            all_records['vehicles'].append(record)
                        else:
                            all_records['adversaries'].append(record)
                elif record_type in all_records:
                    all_records[record_type].extend(records)

        # Parse Adversaries JSON files (these are adversaries, not vehicles)
        if self.adversaries_directory:
            self._log_status(f"Parsing Adversaries files from: {self.adversaries_directory}")
            json_records = self.json_parser.scan_directory(self.adversaries_directory, self.selected_sources)
            all_records['adversaries'].extend(json_records)
        
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
                'adversaries': [],
                'vehicles': [],
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
                # Split NPCs into adversaries and vehicles based on data.type
                for record_type, records in xml_records.items():
                    if record_type == 'npcs':
                        for record in records:
                            if record.get('data', {}).get('type') == 'vehicle':
                                all_records['vehicles'].append(record)
                            else:
                                all_records['adversaries'].append(record)
                    elif record_type in all_records:
                        all_records[record_type].extend(records)

            # Parse Adversaries JSON files (these are adversaries, not vehicles)
            if self.adversaries_directory:
                json_records = self.json_parser.scan_directory(self.adversaries_directory, self.selected_sources)
                all_records['adversaries'].extend(json_records)
            
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
            
            # Step 2: Import in order (Items first, then others, then NPCs/Vehicles last)
            import_order = [
                ('items', 'Items'),
                ('species', 'Species'),
                ('talents', 'Talents'),
                ('specializations', 'Specializations'),
                ('careers', 'Careers'),
                ('force_powers', 'Force Powers'),
                ('skills', 'Skills'),
                ('signature_abilities', 'Signature Abilities'),
                ('adversaries', 'NPCs/Adversaries'),
                ('vehicles', 'Vehicles')
            ]
            
            # Track whether we've loaded campaign caches for NPC inventory/talent reuse
            _campaign_caches_loaded = False

            # Initialize portraits campaign if configured
            if self.portraits_campaign_id:
                record_types_to_import = [rt for rt, _ in import_order if rt in limited_records and limited_records[rt]]
                self._load_portraits_from_campaign(record_types_to_import)

            for record_type, display_name in import_order:
                if not self.is_importing:
                    break

                # Load campaign caches before processing NPCs/Vehicles (which have inventory and talents)
                # This allows NPC/Vehicle inventory items and talents to reuse existing campaign records
                if record_type in ('adversaries', 'vehicles') and not _campaign_caches_loaded:
                    self._log_status("Loading campaign items and talents for reuse...")
                    self.data_mapper.load_campaign_caches()
                    _campaign_caches_loaded = True

                # Only process record types that exist in limited_records
                if record_type not in limited_records or not limited_records[record_type]:
                    continue

                records = limited_records[record_type]
                self._log_status(f"Importing {display_name}...")
                
                for i, record in enumerate(records):
                    if not self.is_importing:
                        break
                    
                    realm_record = None
                    try:
                        # Convert record to Realm VTT format
                        realm_record = self.data_mapper.convert_oggdude_to_realm_vtt(
                            record, self.campaign_id, self._get_category_for_record(record)
                        )
                        
                        # Use the converted name for lookups (important for skills with hyphens)
                        record_name = realm_record.get('name', '') if realm_record else record.get('name', '')

                        # Copy portrait/token from portraits campaign if available
                        if self.portraits_campaign_id and record_name:
                            portrait_data = self._get_portrait_from_cache(record_type, record_name)
                            if portrait_data:
                                if 'img' in portrait_data:
                                    realm_record['img'] = portrait_data['img']
                                if 'token' in portrait_data and record_type in ('adversaries', 'vehicles'):
                                    realm_record['token'] = portrait_data['token']

                        # Map record_type to API endpoint type (adversaries and vehicles are both NPCs)
                        api_record_type = 'npcs' if record_type in ('adversaries', 'vehicles') else record_type

                        # Check if we should update existing records
                        if self.update_existing and record_name:
                            # Try to find existing record by name (using converted name)
                            existing_record = self.api_client.find_record_by_name(api_record_type, record_name)

                            if existing_record:
                                # Update existing record
                                updated_record = self.api_client.patch_record(api_record_type, existing_record['_id'], realm_record)
                                created_record = updated_record
                                self._log_status(f"Updated existing {record_type}: {record_name}")
                            else:
                                # Create new record
                                self._log_status(f"No existing {record_type} found, creating new one: {record_name}")
                                if api_record_type == 'npcs':
                                    created_record = self.api_client.create_npc(realm_record)
                                elif api_record_type == 'items':
                                    created_record = self.api_client.create_item(realm_record)
                                else:
                                    created_record = self.api_client.create_record(realm_record)
                                self._log_status(f"Created new {record_type}: {record_name}")
                        else:
                            # Always create new records
                            if api_record_type == 'npcs':
                                created_record = self.api_client.create_npc(realm_record)
                            elif api_record_type == 'items':
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
                        # Use converted name for error logging if available
                        error_name = realm_record.get('name', '') if realm_record else record.get('name', 'Unknown')
                        self._log_status(f"Error importing {error_name}: {e}")
                        current_record += 1
                        self._update_progress(
                            f"Failed to import {error_name}",
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
        """Get the category for a record - now simply returns the category setting"""
        return self.category if self.category else "Star Wars RPG"
    
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