#!/usr/bin/env python3
"""
Test script for dice notation conversion
"""

import sys, os
import re

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_dice_conversion():
    """Test that dice notation is converted correctly for TipTap extension"""
    try:
        from src.data_mapper import DataMapper
        
        print("Testing dice notation conversion...")
        
        # Create data mapper
        mapper = DataMapper()
        
        # Test cases with various dice notations
        test_cases = [
            # Basic dice
            ("Roll [AB] + [DI] for this check", "Roll <span class=\"ability\" data-dice-type=\"ability\" contenteditable=\"false\" style=\"display: inline-block;\"></span> + <span class=\"difficulty\" data-dice-type=\"difficulty\" contenteditable=\"false\" style=\"display: inline-block;\"></span> for this check"),
            
            # Success/Failure symbols
            ("You get [SU] and [AD] but also [TH]", "You get <span class=\"success\" data-dice-type=\"success\" contenteditable=\"false\" style=\"display: inline-block;\"></span> and <span class=\"advantage\" data-dice-type=\"advantage\" contenteditable=\"false\" style=\"display: inline-block;\"></span> but also <span class=\"threat\" data-dice-type=\"threat\" contenteditable=\"false\" style=\"display: inline-block;\"></span>"),
            
            # Triumph/Despair
            ("Critical [TR] or [DE]", "Critical <span class=\"triumph\" data-dice-type=\"triumph\" contenteditable=\"false\" style=\"display: inline-block;\"></span> or <span class=\"despair\" data-dice-type=\"despair\" contenteditable=\"false\" style=\"display: inline-block;\"></span>"),
            
            # Force dice
            ("Use [FO] to determine [LI] or [DA]", "Use <span class=\"force\" data-dice-type=\"force\" contenteditable=\"false\" style=\"display: inline-block;\"></span> to determine <span class=\"light\" data-dice-type=\"light\" contenteditable=\"false\" style=\"display: inline-block;\"></span> or <span class=\"dark\" data-dice-type=\"dark\" contenteditable=\"false\" style=\"display: inline-block;\"></span>"),
            
            # Mixed content with other formatting
            ("<strong>Roll [PR] vs [CH]</strong> and get [BO] or [SE]", "<strong>Roll <span class=\"proficiency\" data-dice-type=\"proficiency\" contenteditable=\"false\" style=\"display: inline-block;\"></span> vs <span class=\"challenge\" data-dice-type=\"challenge\" contenteditable=\"false\" style=\"display: inline-block;\"></span></strong> and get <span class=\"boost\" data-dice-type=\"boost\" contenteditable=\"false\" style=\"display: inline-block;\"></span> or <span class=\"setback\" data-dice-type=\"setback\" contenteditable=\"false\" style=\"display: inline-block;\"></span>"),
            
            # Full words
            ("Roll [ABILITY] vs [DIFFICULTY]", "Roll <span class=\"ability\" data-dice-type=\"ability\" contenteditable=\"false\" style=\"display: inline-block;\"></span> vs <span class=\"difficulty\" data-dice-type=\"difficulty\" contenteditable=\"false\" style=\"display: inline-block;\"></span>"),
            
            # Light/Dark side variations
            ("[LIGHTSIDE] and [DARKSIDE] points", "<span class=\"light\" data-dice-type=\"light\" contenteditable=\"false\" style=\"display: inline-block;\"></span> and <span class=\"dark\" data-dice-type=\"dark\" contenteditable=\"false\" style=\"display: inline-block;\"></span> points"),
        ]
        
        for i, (input_text, expected_output) in enumerate(test_cases):
            result = mapper._convert_description(input_text)
            # Accept both with and without <p> wrapping
            result_clean = re.sub(r'\s+', ' ', result.strip())
            expected_clean = re.sub(r'\s+', ' ', expected_output.strip())
            # Accept <p>...</p> or ...
            if result_clean == expected_clean or result_clean == f'<p>{expected_clean}</p>':
                print(f"✓ Test case {i+1} passed")
            else:
                print(f"✗ Test case {i+1} failed")
                print(f"  Input: {input_text}")
                print(f"  Expected: {expected_clean}")
                print(f"  Got: {result_clean}")
                return False
        
        print("✓ All dice conversion tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Dice conversion test failed: {e}")
        return False

def test_tiptap_compatibility():
    """Test that the output is compatible with TipTap extension"""
    try:
        from src.data_mapper import DataMapper
        
        print("Testing TipTap extension compatibility...")
        
        mapper = DataMapper()
        
        # Test that the output contains the required attributes
        test_input = "Roll [AB] + [DI] for [SU] or [FA]"
        result = mapper._convert_description(test_input)
        
        # Check for required TipTap attributes
        required_attributes = [
            'data-dice-type=',
            'contenteditable="false"',
            'style="display: inline-block;"'
        ]
        
        for attr in required_attributes:
            if attr not in result:
                print(f"✗ Missing required attribute: {attr}")
                return False
        
        # Check for correct class names
        expected_classes = ['ability', 'difficulty', 'success', 'failure']
        for class_name in expected_classes:
            if f'class="{class_name}"' not in result:
                print(f"✗ Missing expected class: {class_name}")
                return False
        
        print("✓ TipTap extension compatibility verified")
        return True
        
    except Exception as e:
        print(f"✗ TipTap compatibility test failed: {e}")
        return False

def main():
    """Run dice conversion tests"""
    print("Running dice conversion tests")
    print("=" * 40)
    
    tests = [
        test_dice_conversion,
        test_tiptap_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Dice conversion tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All dice conversion tests passed!")
        return 0
    else:
        print("✗ Some dice conversion tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 