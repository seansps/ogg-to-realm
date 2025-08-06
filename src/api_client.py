import requests
import json
import urllib.parse
from typing import Optional, Dict, Any, List
from datetime import datetime

class RealmVTTClient:
    def __init__(self, base_url: str = "https://utilities.realmvtt.com"):
        self.base_url = base_url
        self.token = None
        self.campaign_id = None
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def set_campaign_id(self, campaign_id: str):
        """Set the campaign ID for API requests"""
        self.campaign_id = campaign_id
    
    def login(self, email: str, password: str, two_fa_code: Optional[str] = None) -> dict:
        """
        Login to Realm VTT and get JWT token
        
        Args:
            email: User email
            password: User password  
            two_fa_code: Optional 2FA code if user has 2FA enabled
            
        Returns:
            dict: Authentication response with accessToken
        """
        auth_data = {
            "strategy": "local",
            "email": email,
            "password": password
        }
        
        # Add 2FA code if provided
        if two_fa_code:
            auth_data["code"] = two_fa_code
        
        try:
            response = requests.post(
                f"{self.base_url}/authentication",
                json=auth_data,
                headers=self.headers
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Store the token for future requests
            self.token = result.get('accessToken')
            if self.token:
                self.headers['Authorization'] = f'Bearer {self.token}'
            
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                error_msg = e.response.json().get('message', 'Authentication failed')
                raise Exception(f"Login failed: {error_msg}")
            else:
                raise Exception(f"HTTP error: {e}")
        except Exception as e:
            raise Exception(f"Login error: {e}")
    
    def get_campaign_id(self, invite_code: str) -> Optional[str]:
        """
        Get campaign ID by invite code
        
        Args:
            invite_code: The invite code to look up
            
        Returns:
            str: Campaign ID if found, None if not found
        """
        if not self.token:
            raise Exception("Not authenticated. Call login() first.")
        
        try:
            response = requests.get(
                f"{self.base_url}/campaigns",
                params={"inviteCode": invite_code},
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('data') and len(result['data']) > 0:
                return result['data'][0]['_id']
            return None
            
        except requests.exceptions.HTTPError:
            return None
        except Exception:
            return None
    
    def create_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record
        
        Args:
            record_data: Dictionary containing record data
            
        Returns:
            dict: Created record with _id and other fields
        """
        if not self.token:
            raise Exception("Authentication token required. Call login() first.")
        
        try:
            response = requests.post(
                f"{self.base_url}/records",
                json=record_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('message', 'Failed to create record')
            raise Exception(f"Record creation failed: {error_msg}")
        except Exception as e:
            raise Exception(f"Request error: {e}")
    
    def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new item record
        
        Args:
            item_data: Dictionary containing item data
            
        Returns:
            dict: Created item with _id and other fields
        """
        if not self.token:
            raise Exception("Authentication token required. Call login() first.")
        
        # Ensure recordType is set to 'items'
        if 'recordType' not in item_data:
            item_data['recordType'] = 'items'
        
        try:
            response = requests.post(
                f"{self.base_url}/records",
                json=item_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('message', 'Failed to create item')
            raise Exception(f"Item creation failed: {error_msg}")
        except Exception as e:
            raise Exception(f"Request error: {e}")
    
    def create_npc(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new NPC record
        
        Args:
            npc_data: Dictionary containing NPC data
            
        Returns:
            dict: Created NPC with _id and other fields
        """
        if not self.token:
            raise Exception("Authentication token required. Call login() first.")
        
        # Ensure recordType is set to 'npcs'
        if 'recordType' not in npc_data:
            npc_data['recordType'] = 'npcs'
        
        try:
            response = requests.post(
                f"{self.base_url}/npcs",
                json=npc_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('message', 'Failed to create NPC')
            raise Exception(f"NPC creation failed: {error_msg}")
        except Exception as e:
            raise Exception(f"Request error: {e}")
    
    def make_authenticated_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """
        Make an authenticated request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/users', '/vtt-modules')
            data: Request data for POST/PATCH requests
            
        Returns:
            dict: API response
        """
        if not self.token:
            raise Exception("Not authenticated. Call login() first.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=self.headers)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data, headers=self.headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise Exception(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            raise Exception(f"API request failed: {e}")
        except Exception as e:
            raise Exception(f"Request error: {e}")
    
    def find_records(self, record_type: str, query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Find records of a specific type with optional query parameters"""
        if not self.token:
            raise Exception("Authentication token required. Call login() first.")
        
        try:
            params = query or {}
            
            # Add campaignId parameter which is required by the API
            if 'campaignId' not in params and self.campaign_id:
                params['campaignId'] = self.campaign_id
            
            # Use the correct endpoint based on record type
            if record_type == 'npcs':
                endpoint = f"{self.base_url}/npcs"
            else:
                endpoint = f"{self.base_url}/records"
                # Add recordType parameter for non-npc records
                params['recordType'] = record_type
            
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            return result
            
        except requests.exceptions.HTTPError as e:
            print(f"DEBUG: HTTP error in find_records: {e}")
            raise Exception(f"Failed to find {record_type}: {e}")
    
    def find_record_by_name(self, record_type: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a record by name
        
        Args:
            record_type: Type of record ('items', 'npcs', 'careers', etc.)
            name: Name of the record to find
            
        Returns:
            dict: Record if found, None if not found
        """
        if not self.token:
            raise Exception("Authentication token required. Call login() first.")
        
        try:
            # Query directly by name and record type
            params = {'name': name}
            
            # Add campaignId parameter which is required by the API
            if self.campaign_id:
                params['campaignId'] = self.campaign_id
            
            # Use the correct endpoint based on record type
            if record_type == 'npcs':
                endpoint = f"{self.base_url}/npcs"
            else:
                endpoint = f"{self.base_url}/records"
                # Add recordType parameter for non-npc records
                params['recordType'] = record_type
            
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            # Return the first matching record if any
            if result.get('data') and len(result['data']) > 0:
                return result['data'][0]
            else:
                return None
            
        except Exception as e:
            print(f"DEBUG: Exception in find_record_by_name: {e}")
            raise Exception(f"Error finding {record_type} with name '{name}': {e}")
    
    def patch_record(self, record_type: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Patch (update) an existing record
        
        Args:
            record_type: Type of record ('records', 'npcs', etc.)
            record_id: ID of the record to update
            data: Data to update the record with
            
        Returns:
            dict: Updated record
        """
        if not self.token:
            raise Exception("Authentication token required. Call login() first.")
        
        try:
            # Use the appropriate endpoint based on record type
            if record_type == 'npcs':
                endpoint = f"{self.base_url}/npcs/{record_id}"
            else:
                endpoint = f"{self.base_url}/records/{record_id}"
            
            response = requests.patch(endpoint, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('message', 'Failed to patch record')
            raise Exception(f"Record patch failed: {error_msg}")
        except Exception as e:
            raise Exception(f"Request error: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated"""
        return self.token is not None 