#!/usr/bin/env python3
"""
Test script for OggDude error handling functionality
"""

import sys, os
import re

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_tag_order_fixes():
    """Test that tag order issues are fixed"""
    try:
        from src.data_mapper import DataMapper
        
        print("Testing tag order fixes...")
        
        mapper = DataMapper()
        
        # Test cases for common OggDude errors
        test_cases = [
            # Tag order issues
            ("[B][P]This is bold text[/P][/B]", "<p><strong>This is bold text</strong></p>"),
            
            # Typo fixes
            ("[p]This should be bold[/p]", "<strong>This should be bold</strong>"),
            
            # Special character fixes
            ("&lt;b&gt;Bold text&lt;/b&gt;", "<strong>Bold text</strong>"),
            ("&lt;p&gt;Paragraph&lt;/p&gt;", "<p>Paragraph</p>"),
            
            # Bold tag with colon
            ("[B]Name[/B]: Description", "<strong>Name</strong>: Description"),
            
            # Unclosed tags
            ("<p>Unclosed paragraph", "<p>Unclosed paragraph</p>"),
            ("<li>Unclosed list item", "<li>Unclosed list item</li>"),
            
            # List structure issues
            ("</ul>", "<ul>"),
            
            # Mixed content with errors
            ("[B][P]Bold paragraph[/P][/B] with [p]typo[/p]", "<p><strong>Bold paragraph</strong></p> with <strong>typo</strong>"),
        ]
        
        for i, (input_text, expected_output) in enumerate(test_cases):
            result = mapper._convert_description(input_text)
            
            # Clean up whitespace for comparison
            result_clean = re.sub(r'\s+', ' ', result.strip())
            expected_clean = re.sub(r'\s+', ' ', expected_output.strip())
            
            if result_clean == expected_clean:
                print(f"✓ Test case {i+1} passed")
            else:
                print(f"✗ Test case {i+1} failed")
                print(f"  Input: {input_text}")
                print(f"  Expected: {expected_clean}")
                print(f"  Got: {result_clean}")
                return False
        
        print("✓ All tag order fix tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Tag order fix test failed: {e}")
        return False

def test_html_structure_fixes():
    """Test that HTML structure issues are fixed"""
    try:
        from src.data_mapper import DataMapper
        
        print("Testing HTML structure fixes...")
        
        mapper = DataMapper()
        
        # Test cases for HTML structure issues
        test_cases = [
            # Unclosed paragraph
            ("<p>This paragraph is not closed", "<p>This paragraph is not closed</p>"),
            
            # Unclosed list item
            ("<li>This list item is not closed", "<li>This list item is not closed</li>"),
            
            # Missing paragraph tags
            ("This text needs paragraphs", "<p>This text needs paragraphs</p>"),
            
            # List structure issues
            ("</ul>", "<ul>"),
            
            # Bold tag issues
            ("<strong>Unclosed bold", "<strong>Unclosed bold</strong>"),
            ("<strong>Duplicate</strong><strong>bold</strong>", "<strong>Duplicate</strong><strong>bold</strong>"),
        ]
        
        for i, (input_text, expected_output) in enumerate(test_cases):
            result = mapper._fix_html_structure(input_text)
            
            # Clean up whitespace for comparison
            result_clean = re.sub(r'\s+', ' ', result.strip())
            expected_clean = re.sub(r'\s+', ' ', expected_output.strip())
            
            if result_clean == expected_clean:
                print(f"✓ Test case {i+1} passed")
            else:
                print(f"✗ Test case {i+1} failed")
                print(f"  Input: {input_text}")
                print(f"  Expected: {expected_clean}")
                print(f"  Got: {result_clean}")
                return False
        
        print("✓ All HTML structure fix tests passed")
        return True
        
    except Exception as e:
        print(f"✗ HTML structure fix test failed: {e}")
        return False

def test_bold_tag_fixes():
    """Test that bold tag issues are fixed"""
    try:
        from src.data_mapper import DataMapper
        
        print("Testing bold tag fixes...")
        
        mapper = DataMapper()
        
        # Test cases for bold tag issues
        test_cases = [
            # Unclosed bold tag
            ("<strong>Unclosed bold", "<strong>Unclosed bold</strong>"),
            
            # Duplicate opening tags
            ("<strong>First</strong><strong>Second</strong>", "<strong>First</strong><strong>Second</strong>"),
            
            # Closing tag without opening
            ("Text</strong>", "Text</strong>"),
            
            # Mixed issues
            ("<strong>Open<strong>Nested</strong>", "<strong>Open<strong>Nested</strong></strong>"),
        ]
        
        for i, (input_text, expected_output) in enumerate(test_cases):
            result = mapper._fix_bold_tags(input_text)
            
            # Clean up whitespace for comparison
            result_clean = re.sub(r'\s+', ' ', result.strip())
            expected_clean = re.sub(r'\s+', ' ', expected_output.strip())
            
            if result_clean == expected_clean:
                print(f"✓ Test case {i+1} passed")
            else:
                print(f"✗ Test case {i+1} failed")
                print(f"  Input: {input_text}")
                print(f"  Expected: {expected_clean}")
                print(f"  Got: {result_clean}")
                return False
        
        print("✓ All bold tag fix tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Bold tag fix test failed: {e}")
        return False

def test_complex_error_scenarios():
    """Test complex scenarios with multiple errors"""
    try:
        from src.data_mapper import DataMapper
        
        print("Testing complex error scenarios...")
        
        mapper = DataMapper()
        
        # Complex test case with multiple issues
        complex_input = """[B][P]Bold paragraph[/P][/B]
This line needs paragraphs
<p>Unclosed paragraph
<li>Unclosed list item
[p]Typo bold[/p]
&lt;b&gt;Encoded bold&lt;/b&gt;"""
        
        result = mapper._convert_description(complex_input)
        
        # Check that the result contains proper HTML structure
        expected_elements = [
            '<p><strong>Bold paragraph</strong></p>',
            '<p>This line needs paragraphs</p>',
            '<p>Unclosed paragraph</p>',
            '<li>Unclosed list item</li>',
            '<strong>Typo bold</strong>',
            '<strong>Encoded bold</strong>'
        ]
        
        for element in expected_elements:
            if element not in result and f'<p>{element}</p>' not in result:
                print(f"✗ Missing expected element: {element}")
                return False
        
        print("✓ Complex error scenario test passed")
        return True
        
    except Exception as e:
        print(f"✗ Complex error scenario test failed: {e}")
        return False

def main():
    """Run error handling tests"""
    print("Running OggDude error handling tests")
    print("=" * 50)
    
    tests = [
        test_tag_order_fixes,
        test_html_structure_fixes,
        test_bold_tag_fixes,
        test_complex_error_scenarios
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Error handling tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All error handling tests passed!")
        return 0
    else:
        print("✗ Some error handling tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 