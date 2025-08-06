#!/usr/bin/env python3
"""
Test script for signature ability skill and difficulty parsing
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from xml_parser import XMLParser

def test_skill_difficulty_parsing():
    """Test skill and difficulty extraction from signature ability descriptions"""
    try:
        parser = XMLParser()
        
        # Create signature abilities with different skill check descriptions
        test_cases = [
            {
                'name': 'Always Get My Mark',
                'description': 'She spends 2 Destiny Points, and makes a [B]Hard ([DI][DI][DI]) Streetwise check[b]. If she succeeds, the character tracks down the chosen mark.',
                'expected_skill': 'Streetwise',
                'expected_difficulty': 'Hard'
            },
            {
                'name': 'Knowledge Test',
                'description': 'The character must make a Hard (---) Knowledge (Education) check to succeed.',
                'expected_skill': 'Education',
                'expected_difficulty': 'Hard'
            },
            {
                'name': 'Easy Check',
                'description': 'Make an Easy (-) Perception check to notice details.',
                'expected_skill': 'Perception',
                'expected_difficulty': 'Easy'
            },
            {
                'name': 'Average Coordination',
                'description': 'Requires an Average ([DI][DI]) Coordination check.',
                'expected_skill': 'Coordination',
                'expected_difficulty': 'Average'
            },
            {
                'name': 'Formidable Discipline',
                'description': 'Must make a Formidable (-----) Discipline check.',
                'expected_skill': 'Discipline',
                'expected_difficulty': 'Formidable'
            },
            {
                'name': 'No Skill Check',
                'description': 'This ability has no skill check requirement.',
                'expected_skill': None,
                'expected_difficulty': None
            }
        ]
        
        print("Testing skill and difficulty extraction from signature ability descriptions...")
        
        for i, test_case in enumerate(test_cases):
            print(f"\nTest {i+1}: {test_case['name']}")
            
            # Create XML with this test case
            sig_ability_xml = f'''<?xml version='1.0' encoding='utf-8'?>
<SigAbility>
    <Key>TEST{i}</Key>
    <Name>{test_case['name']}</Name>
    <Description>{test_case['description']}</Description>
    <Source>Test</Source>
    <Custom>DescOnly</Custom>
    <AbilityRows>
        <AbilityRow>
            <Abilities>
                <Key>TESTBASE{i}</Key>
            </Abilities>
            <Directions>
                <Direction>
                    <Down>false</Down>
                </Direction>
            </Directions>
            <AbilitySpan>
                <Span>1</Span>
            </AbilitySpan>
            <Costs>
                <Cost>30</Cost>
            </Costs>
        </AbilityRow>
    </AbilityRows>
    <Careers>
        <Key>TESTCAREER</Key>
    </Careers>
    <MatchingNodes>
        <Node>false</Node>
    </MatchingNodes>
</SigAbility>'''
            
            root = ET.fromstring(sig_ability_xml)
            sig_ability_data = parser._extract_sig_ability_data(root)
            
            if sig_ability_data is None:
                print(f"  ✗ Signature ability data extraction failed")
                return False
            
            data = sig_ability_data.get('data', {})
            
            # Check skill extraction
            actual_skill = data.get('skill')
            expected_skill = test_case['expected_skill']
            
            if actual_skill == expected_skill:
                print(f"  ✓ Skill correctly extracted: {actual_skill}")
            else:
                print(f"  ✗ Skill extraction failed: expected '{expected_skill}', got '{actual_skill}'")
                return False
            
            # Check difficulty extraction
            actual_difficulty = data.get('difficulty')
            expected_difficulty = test_case['expected_difficulty']
            
            if actual_difficulty == expected_difficulty:
                print(f"  ✓ Difficulty correctly extracted: {actual_difficulty}")
            else:
                print(f"  ✗ Difficulty extraction failed: expected '{expected_difficulty}', got '{actual_difficulty}'")
                return False
        
        print("\n  ✓ All skill and difficulty extraction tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_skill_difficulty_parsing()
    if success:
        print("\n🎉 All skill and difficulty parsing tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some skill and difficulty parsing tests failed!")
        sys.exit(1)