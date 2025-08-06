#!/usr/bin/env python3
"""
Test script for incidental activation type conversion
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_incidental_activation_conversion():
    """Test that incidental activation types convert to Active"""
    try:
        parser = XMLParser()
        
        print("Testing incidental activation type conversion...")
        
        # Test cases for different incidental activation types
        test_cases = [
            {
                'input': 'taIncidental',
                'expected': 'Active',
                'description': 'Standard incidental activation'
            },
            {
                'input': 'taIncidentalOOT',
                'expected': 'Active', 
                'description': 'Out-of-turn incidental activation'
            },
            {
                'input': 'Incidental',
                'expected': 'Active',
                'description': 'Incidental without ta prefix'
            },
            {
                'input': 'IncidentalOOT',
                'expected': 'Active',
                'description': 'Out-of-turn incidental without ta prefix'
            },
            {
                'input': 'taPassive',
                'expected': 'Passive',
                'description': 'Passive activation (control test)'
            },
            {
                'input': 'taAction',
                'expected': 'Active',
                'description': 'Action activation (control test)'
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            input_value = test_case['input']
            expected = test_case['expected']
            description = test_case['description']
            
            actual = parser._convert_activation_value(input_value)
            
            if actual == expected:
                print(f"  ✓ {description}: '{input_value}' -> '{actual}'")
            else:
                print(f"  ✗ {description}: '{input_value}' -> expected '{expected}', got '{actual}'")
                all_passed = False
        
        if all_passed:
            print("  ✓ All incidental activation conversion tests passed!")
            return True
        else:
            print("  ✗ Some incidental activation conversion tests failed!")
            return False
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_incidental_activation_conversion()
    if success:
        print("\n🎉 All incidental activation tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some incidental activation tests failed!")
        sys.exit(1)