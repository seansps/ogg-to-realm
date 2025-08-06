#!/usr/bin/env python3
"""
Test for update existing records functionality
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api_client import RealmVTTClient
from import_manager import ImportManager

class TestUpdateExisting(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_client = RealmVTTClient()
        self.api_client.token = "test_token"
        self.api_client.campaign_id = "test_campaign_123"
        self.api_client.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test_token'
        }
        
        self.import_manager = ImportManager(self.api_client)
    
    def test_find_record_by_name_items(self):
        """Test finding an item record by name"""
        with patch('requests.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': [{
                    '_id': 'test_id_123',
                    'name': 'Test Item',
                    'recordType': 'items'
                }]
            }
            mock_get.return_value = mock_response
            
            # Test finding an item
            result = self.api_client.find_record_by_name('items', 'Test Item')
            
            # Verify the request was made correctly (using records endpoint with name, recordType, and campaignId)
            mock_get.assert_called_once_with(
                'https://utilities.realmvtt.com/records',
                params={'name': 'Test Item', 'recordType': 'items', 'campaignId': 'test_campaign_123'},
                headers=self.api_client.headers
            )
            
            # Verify the result
            self.assertIsNotNone(result)
            self.assertEqual(result['_id'], 'test_id_123')
            self.assertEqual(result['name'], 'Test Item')
    
    def test_find_record_by_name_npcs(self):
        """Test finding an NPC record by name"""
        with patch('requests.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'data': [{
                    '_id': 'npc_id_456',
                    'name': 'Test NPC',
                    'recordType': 'npcs'
                }]
            }
            mock_get.return_value = mock_response
            
            # Test finding an NPC
            result = self.api_client.find_record_by_name('npcs', 'Test NPC')
            
            # Verify the request was made correctly (using npcs endpoint with name and campaignId)
            mock_get.assert_called_once_with(
                'https://utilities.realmvtt.com/npcs',
                params={'name': 'Test NPC', 'campaignId': 'test_campaign_123'},
                headers=self.api_client.headers
            )
            
            # Verify the result
            self.assertIsNotNone(result)
            self.assertEqual(result['_id'], 'npc_id_456')
            self.assertEqual(result['name'], 'Test NPC')
    
    def test_find_record_by_name_not_found(self):
        """Test finding a record that doesn't exist"""
        with patch('requests.get') as mock_get:
            # Mock response with no data
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'data': []}
            mock_get.return_value = mock_response
            
            # Test finding a non-existent record
            result = self.api_client.find_record_by_name('items', 'Non Existent Item')
            
            # Verify the result is None
            self.assertIsNone(result)
    
    def test_patch_record_items(self):
        """Test patching an item record"""
        with patch('requests.patch') as mock_patch:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                '_id': 'test_id_123',
                'name': 'Updated Item',
                'recordType': 'items'
            }
            mock_patch.return_value = mock_response
            
            # Test data to update
            update_data = {
                'name': 'Updated Item',
                'description': 'Updated description'
            }
            
            # Test patching an item
            result = self.api_client.patch_record('items', 'test_id_123', update_data)
            
            # Verify the request was made correctly
            mock_patch.assert_called_once_with(
                'https://utilities.realmvtt.com/records/test_id_123',
                json=update_data,
                headers=self.api_client.headers
            )
            
            # Verify the result
            self.assertIsNotNone(result)
            self.assertEqual(result['_id'], 'test_id_123')
            self.assertEqual(result['name'], 'Updated Item')
    
    def test_patch_record_npcs(self):
        """Test patching an NPC record"""
        with patch('requests.patch') as mock_patch:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                '_id': 'npc_id_456',
                'name': 'Updated NPC',
                'recordType': 'npcs'
            }
            mock_patch.return_value = mock_response
            
            # Test data to update
            update_data = {
                'name': 'Updated NPC',
                'description': 'Updated description'
            }
            
            # Test patching an NPC
            result = self.api_client.patch_record('npcs', 'npc_id_456', update_data)
            
            # Verify the request was made correctly
            mock_patch.assert_called_once_with(
                'https://utilities.realmvtt.com/npcs/npc_id_456',
                json=update_data,
                headers=self.api_client.headers
            )
            
            # Verify the result
            self.assertIsNotNone(result)
            self.assertEqual(result['_id'], 'npc_id_456')
            self.assertEqual(result['name'], 'Updated NPC')
    
    def test_import_manager_update_existing_setting(self):
        """Test that the import manager correctly stores the update existing setting"""
        # Test default value
        self.assertFalse(self.import_manager.update_existing)
        
        # Test setting to True
        self.import_manager.set_update_existing(True)
        self.assertTrue(self.import_manager.update_existing)
        
        # Test setting to False
        self.import_manager.set_update_existing(False)
        self.assertFalse(self.import_manager.update_existing)

if __name__ == "__main__":
    unittest.main() 