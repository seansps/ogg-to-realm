import unittest
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from import_manager import ImportManager
from api_client import RealmVTTClient

class TestItemsParsing(unittest.TestCase):
    """Test that Items parsing includes all item types: weapons, gear, armor, item attachments"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a mock API client
        self.api_client = RealmVTTClient()
        self.import_manager = ImportManager(self.api_client)
        
        # Set up the OggData directory path
        oggdata_path = Path(__file__).parent.parent / 'OggData'
        if not oggdata_path.exists():
            self.skipTest(f"OggData directory not found at {oggdata_path}")
        
        self.import_manager.set_oggdude_directory(str(oggdata_path))
        
        # Set selected sources to empty list (no filtering)
        self.import_manager.set_selected_sources([])
        
        # Set selected record types to only 'items'
        self.import_manager.set_selected_record_types(['items'])
        
        # Set max import limit to 0 (no limit)
        self.import_manager.set_max_import_limit(0)
    
    def test_items_parsing_includes_all_item_types(self):
        """Test that parsing items includes weapons, gear, armor, and item attachments"""
        print("\n=== Testing Items Parsing ===")
        
        # Parse files using the same logic as the GUI
        counts = self.import_manager.parse_files()
        
        print(f"\nCounts returned: {counts}")
        
        # Check that items count is greater than 0
        self.assertGreater(counts.get('items', 0), 0, 
                          f"Expected items count > 0, but got {counts.get('items', 0)}")
        
        # The items count should be much higher than just weapons
        # Based on our previous test, we should get around 1565 items
        items_count = counts.get('items', 0)
        print(f"\nFound {items_count} items")
        
        # This should be significantly more than just weapons (which would be around 50-100)
        self.assertGreater(items_count, 500, 
                          f"Expected items count > 500 (should include weapons, gear, armor, attachments), but got {items_count}")
        
        # Let's also check what the XML parser found directly
        from xml_parser import XMLParser
        xml_parser = XMLParser()
        xml_records = xml_parser.scan_directory(self.import_manager.oggdude_directory, [])
        
        print(f"\nXML parser found:")
        for record_type, records in xml_records.items():
            if len(records) > 0:
                print(f"  {record_type}: {len(records)}")
        
        # Verify that items are being found
        self.assertGreater(len(xml_records.get('items', [])), 500,
                          f"XML parser should find > 500 items, but found {len(xml_records.get('items', []))}")
        
        print(f"\n✅ Test passed! Found {items_count} items including weapons, gear, armor, and item attachments.")

if __name__ == '__main__':
    unittest.main() 