#!/usr/bin/env python3
"""
Test talent prerequisite expansion for adversaries.
When an adversary has Improved/Supreme talents, base talents should be auto-added.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_mapper import DataMapper


def test_improved_talent_adds_base():
    """Test that Improved talent adds base talent if missing"""
    mapper = DataMapper()

    talents = ["Scathing Tirade (Improved)"]
    result = mapper._expand_talent_prerequisites(talents)

    assert len(result) == 2, f"Expected 2 talents, got {len(result)}: {result}"
    assert result[0] == "Scathing Tirade", f"Expected base talent first, got {result[0]}"
    assert result[1] == "Scathing Tirade (Improved)", f"Expected improved talent second, got {result[1]}"

    print("PASSED: test_improved_talent_adds_base")


def test_supreme_talent_adds_base_and_improved():
    """Test that Supreme talent adds both base and improved talents if missing"""
    mapper = DataMapper()

    talents = ["Scathing Tirade (Supreme)"]
    result = mapper._expand_talent_prerequisites(talents)

    assert len(result) == 3, f"Expected 3 talents, got {len(result)}: {result}"
    assert result[0] == "Scathing Tirade", f"Expected base talent first, got {result[0]}"
    assert result[1] == "Scathing Tirade (Improved)", f"Expected improved talent second, got {result[1]}"
    assert result[2] == "Scathing Tirade (Supreme)", f"Expected supreme talent third, got {result[2]}"

    print("PASSED: test_supreme_talent_adds_base_and_improved")


def test_base_already_present():
    """Test that base talent is not duplicated if already present"""
    mapper = DataMapper()

    talents = ["Scathing Tirade", "Scathing Tirade (Improved)"]
    result = mapper._expand_talent_prerequisites(talents)

    assert len(result) == 2, f"Expected 2 talents, got {len(result)}: {result}"
    assert result[0] == "Scathing Tirade", f"Expected base talent first, got {result[0]}"
    assert result[1] == "Scathing Tirade (Improved)", f"Expected improved talent second, got {result[1]}"

    print("PASSED: test_base_already_present")


def test_improved_already_present_for_supreme():
    """Test that improved is not duplicated if already present when supreme is added"""
    mapper = DataMapper()

    talents = ["Scathing Tirade (Improved)", "Scathing Tirade (Supreme)"]
    result = mapper._expand_talent_prerequisites(talents)

    # Should add base before improved, then improved and supreme stay as-is
    assert len(result) == 3, f"Expected 3 talents, got {len(result)}: {result}"
    assert result[0] == "Scathing Tirade", f"Expected base talent first, got {result[0]}"
    assert result[1] == "Scathing Tirade (Improved)", f"Expected improved talent second, got {result[1]}"
    assert result[2] == "Scathing Tirade (Supreme)", f"Expected supreme talent third, got {result[2]}"

    print("PASSED: test_improved_already_present_for_supreme")


def test_all_already_present():
    """Test that nothing is added if all talents already present"""
    mapper = DataMapper()

    talents = ["Scathing Tirade", "Scathing Tirade (Improved)", "Scathing Tirade (Supreme)"]
    result = mapper._expand_talent_prerequisites(talents)

    assert len(result) == 3, f"Expected 3 talents, got {len(result)}: {result}"
    assert result == talents, f"Expected unchanged list, got {result}"

    print("PASSED: test_all_already_present")


def test_mixed_talents():
    """Test with mix of regular and improved talents"""
    mapper = DataMapper()

    talents = ["Adversary 2", "Scathing Tirade (Improved)", "Skilled Jockey 1"]
    result = mapper._expand_talent_prerequisites(talents)

    assert len(result) == 4, f"Expected 4 talents, got {len(result)}: {result}"
    assert result[0] == "Adversary 2", f"Expected Adversary first, got {result[0]}"
    assert result[1] == "Scathing Tirade", f"Expected base Scathing Tirade second, got {result[1]}"
    assert result[2] == "Scathing Tirade (Improved)", f"Expected improved third, got {result[2]}"
    assert result[3] == "Skilled Jockey 1", f"Expected Skilled Jockey fourth, got {result[3]}"

    print("PASSED: test_mixed_talents")


def test_multiple_improved_talents():
    """Test with multiple different improved talents"""
    mapper = DataMapper()

    talents = ["Scathing Tirade (Improved)", "Inspiring Rhetoric (Improved)"]
    result = mapper._expand_talent_prerequisites(talents)

    assert len(result) == 4, f"Expected 4 talents, got {len(result)}: {result}"
    assert result[0] == "Scathing Tirade", f"Expected Scathing Tirade base first, got {result[0]}"
    assert result[1] == "Scathing Tirade (Improved)", f"Expected Scathing Tirade improved second, got {result[1]}"
    assert result[2] == "Inspiring Rhetoric", f"Expected Inspiring Rhetoric base third, got {result[2]}"
    assert result[3] == "Inspiring Rhetoric (Improved)", f"Expected Inspiring Rhetoric improved fourth, got {result[3]}"

    print("PASSED: test_multiple_improved_talents")


def test_empty_list():
    """Test with empty talent list"""
    mapper = DataMapper()

    talents = []
    result = mapper._expand_talent_prerequisites(talents)

    assert result == [], f"Expected empty list, got {result}"

    print("PASSED: test_empty_list")


def test_no_improved_or_supreme():
    """Test that regular talents are unchanged"""
    mapper = DataMapper()

    talents = ["Adversary 2", "Skilled Jockey 1", "Durable"]
    result = mapper._expand_talent_prerequisites(talents)

    assert result == talents, f"Expected unchanged list, got {result}"

    print("PASSED: test_no_improved_or_supreme")


def run_tests():
    """Run all tests"""
    test_improved_talent_adds_base()
    test_supreme_talent_adds_base_and_improved()
    test_base_already_present()
    test_improved_already_present_for_supreme()
    test_all_already_present()
    test_mixed_talents()
    test_multiple_improved_talents()
    test_empty_list()
    test_no_improved_or_supreme()

    print("\n✅ All talent prerequisite tests passed!")


if __name__ == '__main__':
    run_tests()
