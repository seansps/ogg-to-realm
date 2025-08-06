import unittest
import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xml_parser import XMLParser

class TestSpeciesParsing(unittest.TestCase):
    def setUp(self):
        self.parser = XMLParser()
    
    def test_species_parsing(self):
        """Test species parsing with all the new features"""
        test_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Species>
    <Key>WOOK</Key>
    <Name>Wookiee</Name>
    <Description>[H4]Wookies[h4] Strong, intelligent, and fierce in battle, Wookiees make the best of friends for those to whom they are loyal—and the worst of enemies for anyone to whom they are not.</Description>
    <Source Page="52">Edge of the Empire Core Rulebook</Source>
    <StartingChars>
        <Brawn>3</Brawn>
        <Agility>2</Agility>
        <Intellect>2</Intellect>
        <Cunning>2</Cunning>
        <Willpower>1</Willpower>
        <Presence>2</Presence>
    </StartingChars>
    <StartingAttrs>
        <WoundThreshold>14</WoundThreshold>
        <StrainThreshold>8</StrainThreshold>
        <Experience>90</Experience>
    </StartingAttrs>
    <SkillModifiers>
        <SkillModifier>
            <Key>BRAWL</Key>
            <RankStart>1</RankStart>
            <RankLimit>2</RankLimit>
        </SkillModifier>
    </SkillModifiers>
    <OptionChoices>
        <OptionChoice>
            <Key>WOOKAB</Key>
            <Name>Rage</Name>
            <Options>
                <Option>
                    <Key>WOOKABRAGE</Key>
                    <Name>Rages when Wounded</Name>
                    <Description>When a Wookiee has suffered any wounds, he deals +1 damage to Brawl and Melee attacks.  When a Wookiee is Critically Injured, he instead deals +2 damage to Brawl and Melee attacks.</Description>
                </Option>
            </Options>
        </OptionChoice>
    </OptionChoices>
</Species>'''
        
        root = ET.fromstring(test_xml)
        species = self.parser._extract_species_data(root)
        
        self.assertIsNotNone(species)
        self.assertEqual(species['name'], 'Wookiee')
        self.assertEqual(species['recordType'], 'species')
        
        # Check data fields
        data = species['data']
        self.assertEqual(data['brawn'], 3)
        self.assertEqual(data['agility'], 2)
        self.assertEqual(data['intellect'], 2)
        self.assertEqual(data['cunning'], 2)
        self.assertEqual(data['willpower'], 1)
        self.assertEqual(data['presence'], 2)
        self.assertEqual(data['woundThreshold'], 14)
        self.assertEqual(data['strainThreshold'], 8)
        self.assertEqual(data['startingXp'], 90)
        
        # Check starting skills
        self.assertIn('Begin the game with 1 rank in Brawl', data['startingSkills'])
        self.assertIn('They still may not train Brawl above rank 2 during character creation', data['startingSkills'])
        
        # Check features
        self.assertEqual(len(data['features']), 1)
        feature = data['features'][0]
        self.assertEqual(feature['name'], 'Rages when Wounded')
        self.assertEqual(feature['unidentifiedName'], 'Feature')
        self.assertEqual(feature['recordType'], 'records')
        self.assertTrue(feature['identified'])
        self.assertIn('_id', feature)
        self.assertIsInstance(feature['_id'], str)
        self.assertIn('data', feature)
        self.assertIn('description', feature['data'])
        self.assertIn('<p>', feature['data']['description'])
        
        # Check sources
        self.assertIn('sources', species)
        self.assertIsInstance(species['sources'], list)
        
        # Check key
        self.assertIn('key', species)
        self.assertEqual(species['key'], 'WOOK')

if __name__ == '__main__':
    unittest.main() 