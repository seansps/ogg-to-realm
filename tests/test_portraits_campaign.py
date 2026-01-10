#!/usr/bin/env python3
"""
Test script for portraits campaign feature
"""

import sys
import os
import unittest
from unittest.mock import Mock, MagicMock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from import_manager import ImportManager

class TestPortraitsCampaign(unittest.TestCase):
    """Test the portraits campaign feature"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock API client
        self.mock_api_client = Mock()
        self.mock_api_client.campaign_id = "test_campaign_id"
        self.import_manager = ImportManager(self.mock_api_client)

    def test_set_portraits_campaign_id(self):
        """Test setting portraits campaign ID"""
        portraits_campaign_id = "portraits_campaign_123"
        self.import_manager.set_portraits_campaign_id(portraits_campaign_id)
        self.assertEqual(self.import_manager.portraits_campaign_id, portraits_campaign_id)

    def test_get_portrait_from_cache_no_campaign(self):
        """Test getting portrait when no portraits campaign is set"""
        result = self.import_manager._get_portrait_from_cache('items', 'Test Item')
        self.assertIsNone(result)

    def test_get_portrait_from_cache_with_campaign(self):
        """Test getting portrait from portraits campaign"""
        # Set up portraits campaign
        self.import_manager.set_portraits_campaign_id("portraits_campaign_123")

        # Mock the API client to return a record with portrait
        mock_record = {
            '_id': 'item123',
            'name': 'Test Item',
            'img': 'https://example.com/portrait.jpg'
        }
        self.mock_api_client.find_record_by_name = Mock(return_value=mock_record)

        # Get portrait from cache
        result = self.import_manager._get_portrait_from_cache('items', 'Test Item')

        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result['img'], 'https://example.com/portrait.jpg')
        self.assertNotIn('token', result)

        # Verify API was called with correct parameters
        self.mock_api_client.find_record_by_name.assert_called_once_with('items', 'Test Item')

    def test_get_portrait_from_cache_with_npc(self):
        """Test getting portrait and token for an NPC"""
        # Set up portraits campaign
        self.import_manager.set_portraits_campaign_id("portraits_campaign_123")

        # Mock the API client to return an NPC record with portrait and token
        mock_record = {
            '_id': 'npc123',
            'name': 'Test NPC',
            'img': 'https://example.com/npc_portrait.jpg',
            'token': 'https://example.com/npc_token.png'
        }
        self.mock_api_client.find_record_by_name = Mock(return_value=mock_record)

        # Get portrait from cache for adversaries (which are NPCs)
        result = self.import_manager._get_portrait_from_cache('adversaries', 'Test NPC')

        # Verify the result includes both img and token
        self.assertIsNotNone(result)
        self.assertEqual(result['img'], 'https://example.com/npc_portrait.jpg')
        self.assertEqual(result['token'], 'https://example.com/npc_token.png')

        # Verify API was called with correct parameters (adversaries maps to 'npcs')
        self.mock_api_client.find_record_by_name.assert_called_once_with('npcs', 'Test NPC')

    def test_get_portrait_from_cache_no_match(self):
        """Test getting portrait when no matching record exists"""
        # Set up portraits campaign
        self.import_manager.set_portraits_campaign_id("portraits_campaign_123")

        # Mock the API client to return None (no record found)
        self.mock_api_client.find_record_by_name = Mock(return_value=None)

        # Get portrait from cache
        result = self.import_manager._get_portrait_from_cache('items', 'Nonexistent Item')

        # Verify the result is None
        self.assertIsNone(result)

        # Verify it was cached as None to avoid repeated lookups
        self.assertIn('items', self.import_manager.portraits_cache)
        self.assertIn('Nonexistent Item', self.import_manager.portraits_cache['items'])
        self.assertIsNone(self.import_manager.portraits_cache['items']['Nonexistent Item'])

    def test_get_portrait_from_cache_uses_cache(self):
        """Test that subsequent calls use the cache"""
        # Set up portraits campaign
        self.import_manager.set_portraits_campaign_id("portraits_campaign_123")

        # Pre-populate the cache
        self.import_manager.portraits_cache = {
            'items': {
                'Cached Item': {
                    'img': 'https://example.com/cached.jpg'
                }
            }
        }

        # Mock the API client (should not be called)
        self.mock_api_client.find_record_by_name = Mock()

        # Get portrait from cache
        result = self.import_manager._get_portrait_from_cache('items', 'Cached Item')

        # Verify the result came from cache
        self.assertIsNotNone(result)
        self.assertEqual(result['img'], 'https://example.com/cached.jpg')

        # Verify API was NOT called (cache was used)
        self.mock_api_client.find_record_by_name.assert_not_called()

    def test_get_portrait_restores_campaign_id(self):
        """Test that original campaign ID is restored after lookup"""
        # Set up both campaign IDs
        original_campaign_id = "original_campaign_123"
        portraits_campaign_id = "portraits_campaign_456"

        self.mock_api_client.campaign_id = original_campaign_id
        self.import_manager.set_portraits_campaign_id(portraits_campaign_id)

        # Mock the API client
        self.mock_api_client.find_record_by_name = Mock(return_value=None)

        # Get portrait from cache
        self.import_manager._get_portrait_from_cache('items', 'Test Item')

        # Verify the campaign ID was restored
        self.assertEqual(self.mock_api_client.campaign_id, original_campaign_id)


if __name__ == '__main__':
    unittest.main()
