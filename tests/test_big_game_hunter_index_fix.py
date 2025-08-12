#!/usr/bin/env python3
"""
Test for Big-Game Hunter specialization with all index 0 talent rows.
This tests the fix for Ogg Dude's problematic XML where all TalentRow elements have Index>0<.
"""

import os
import sys
import tempfile
import shutil

# Add the src directory to the path so we can import the parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xml_parser import XMLParser

def test_big_game_hunter_index_fix():
    """Test that Big-Game Hunter specialization with all index 0 talent rows works correctly"""
    print("Testing Big-Game Hunter specialization index fix...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the OggData structure
        oggdata_dir = os.path.join(temp_dir, 'OggData')
        os.makedirs(oggdata_dir)
        
        # Create a minimal Talents.xml file
        talents_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Talents>
  <Talent>
    <Key>FORAG</Key>
    <Name>Forager</Name>
    <Description>Test description for Forager</Description>
  </Talent>
  <Talent>
    <Key>GRIT</Key>
    <Name>Grit</Name>
    <Description>Test description for Grit</Description>
  </Talent>
  <Talent>
    <Key>STALK</Key>
    <Name>Stalker</Name>
    <Description>Test description for Stalker</Description>
  </Talent>
  <Talent>
    <Key>OUTDOOR</Key>
    <Name>Outdoorsman</Name>
    <Description>Test description for Outdoorsman</Description>
  </Talent>
  <Talent>
    <Key>TOUGH</Key>
    <Name>Tough</Name>
    <Description>Test description for Tough</Description>
  </Talent>
  <Talent>
    <Key>CONF</Key>
    <Name>Confidence</Name>
    <Description>Test description for Confidence</Description>
  </Talent>
  <Talent>
    <Key>SWIFT</Key>
    <Name>Swift</Name>
    <Description>Test description for Swift</Description>
  </Talent>
  <Talent>
    <Key>NATHUN</Key>
    <Name>Natural Hunter</Name>
    <Description>Test description for Natural Hunter</Description>
  </Talent>
  <Talent>
    <Key>EXTRACK</Key>
    <Name>Expert Tracker</Name>
    <Description>Test description for Expert Tracker</Description>
  </Talent>
  <Talent>
    <Key>HEIGHT</Key>
    <Name>Heightened Awareness</Name>
    <Description>Test description for Heightened Awareness</Description>
  </Talent>
  <Talent>
    <Key>HUNTERQUARRY</Key>
    <Name>Hunter's Quarry</Name>
    <Description>Test description for Hunter's Quarry</Description>
  </Talent>
  <Talent>
    <Key>QUICKST</Key>
    <Name>Quick Strike</Name>
    <Description>Test description for Quick Strike</Description>
  </Talent>
  <Talent>
    <Key>BRNGITDWN</Key>
    <Name>Bring It Down</Name>
    <Description>Test description for Bring It Down</Description>
  </Talent>
  <Talent>
    <Key>HUNTQIMP</Key>
    <Name>Hunter's Quarry Improved</Name>
    <Description>Test description for Hunter's Quarry Improved</Description>
  </Talent>
  <Talent>
    <Key>DEDI</Key>
    <Name>Dedication</Name>
    <Description>Test description for Dedication</Description>
  </Talent>
  <Talent>
    <Key>SUPREF</Key>
    <Name>Supreme</Name>
    <Description>Test description for Supreme</Description>
  </Talent>
</Talents>'''
        
        with open(os.path.join(oggdata_dir, 'Talents.xml'), 'w') as f:
            f.write(talents_xml)
        
        # Create a minimal Skills.xml file
        skills_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Skills>
  <Skill>
    <Key>RANGHVY</Key>
    <Name>Ranged (Heavy)</Name>
  </Skill>
  <Skill>
    <Key>STEAL</Key>
    <Name>Stealth</Name>
  </Skill>
  <Skill>
    <Key>SURV</Key>
    <Name>Survival</Name>
  </Skill>
  <Skill>
    <Key>XEN</Key>
    <Name>Knowledge (Xenology)</Name>
  </Skill>
</Skills>'''
        
        with open(os.path.join(oggdata_dir, 'Skills.xml'), 'w') as f:
            f.write(skills_xml)
        
        # Create the Big-Game Hunter specialization XML with all index 0
        big_game_hunter_xml = '''<?xml version='1.0' encoding='utf-8'?>
<Specialization>
  <Key>BGMHUNTER</Key>
  <Name>Big-Game Hunter</Name>
  <Description>Test description for Big-Game Hunter</Description>
  <Source Page="27">Enter the Unknown</Source>
  <Custom>DescOnly</Custom>
  <CareerSkills>
    <Key>RANGHVY</Key>
    <Key>STEAL</Key>
    <Key>SURV</Key>
    <Key>XEN</Key>
  </CareerSkills>
  <TalentRows>
    <TalentRow>
      <Index>0</Index>
      <Cost>5</Cost>
      <Talents>
        <Key>FORAG</Key>
        <Key>GRIT</Key>
        <Key>STALK</Key>
        <Key>OUTDOOR</Key>
      </Talents>
      <Directions>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>false</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>false</Up>
          <Down>false</Down>
        </Direction>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>false</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>false</Up>
          <Down>true</Down>
        </Direction>
      </Directions>
    </TalentRow>
    <TalentRow>
      <Index>0</Index>
      <Cost>10</Cost>
      <Talents>
        <Key>TOUGH</Key>
        <Key>OUTDOOR</Key>
        <Key>CONF</Key>
        <Key>SWIFT</Key>
      </Talents>
      <Directions>
        <Direction>
          <Left>false</Left>
          <Right>true</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>true</Right>
          <Up>false</Up>
          <Down>false</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>false</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>true</Up>
          <Down>false</Down>
        </Direction>
      </Directions>
    </TalentRow>
    <TalentRow>
      <Index>0</Index>
      <Cost>15</Cost>
      <Talents>
        <Key>STALK</Key>
        <Key>NATHUN</Key>
        <Key>EXTRACK</Key>
        <Key>HEIGHT</Key>
      </Talents>
      <Directions>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>true</Up>
          <Down>false</Down>
        </Direction>
        <Direction>
          <Left>false</Left>
          <Right>true</Right>
          <Up>false</Up>
          <Down>false</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>true</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>false</Right>
          <Up>false</Up>
          <Down>true</Down>
        </Direction>
      </Directions>
    </TalentRow>
    <TalentRow>
      <Index>0</Index>
      <Cost>20</Cost>
      <Talents>
        <Key>GRIT</Key>
        <Key>HUNTERQUARRY</Key>
        <Key>QUICKST</Key>
        <Key>EXTRACK</Key>
      </Talents>
      <Directions>
        <Direction>
          <Left>false</Left>
          <Right>true</Right>
          <Up>false</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>true</Right>
          <Up>false</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>false</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>true</Up>
          <Down>true</Down>
        </Direction>
      </Directions>
    </TalentRow>
    <TalentRow>
      <Index>0</Index>
      <Cost>25</Cost>
      <Talents>
        <Key>BRNGITDWN</Key>
        <Key>HUNTQIMP</Key>
        <Key>DEDI</Key>
        <Key>SUPREF</Key>
      </Talents>
      <Directions>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>true</Up>
          <Down>false</Down>
        </Direction>
        <Direction>
          <Left>false</Left>
          <Right>false</Right>
          <Up>true</Up>
          <Down>false</Down>
        </Direction>
        <Direction>
          <Left>false</Left>
          <Right>true</Right>
          <Up>true</Up>
          <Down>false</Down>
        </Direction>
        <Direction>
          <Left>true</Left>
          <Right>false</Right>
          <Up>true</Up>
          <Down>false</Down>
        </Direction>
      </Directions>
    </TalentRow>
  </TalentRows>
  <Universal>false</Universal>
</Specialization>'''
        
        with open(os.path.join(oggdata_dir, 'Big-Game Hunter.xml'), 'w') as f:
            f.write(big_game_hunter_xml)
        
        # Create a minimal ItemDescriptors.xml file
        item_descriptors_xml = '''<?xml version='1.0' encoding='utf-8'?>
<ItemDescriptors>
  <ItemDescriptor>
    <Key>TEST</Key>
    <Name>Test</Name>
  </ItemDescriptor>
</ItemDescriptors>'''
        
        with open(os.path.join(oggdata_dir, 'ItemDescriptors.xml'), 'w') as f:
            f.write(item_descriptors_xml)
        
        # Create a minimal Force Abilities.xml file
        force_abilities_xml = '''<?xml version='1.0' encoding='utf-8'?>
<ForceAbilities>
  <ForceAbility>
    <Key>TEST</Key>
    <Name>Test</Name>
  </ForceAbility>
</ForceAbilities>'''
        
        with open(os.path.join(oggdata_dir, 'Force Abilities.xml'), 'w') as f:
            f.write(force_abilities_xml)
        
        # Create a minimal VehActions.xml file
        veh_actions_xml = '''<?xml version='1.0' encoding='utf-8'?>
<VehActions>
  <VehAction>
    <Key>TEST</Key>
    <Name>Test</Name>
  </VehAction>
</VehActions>'''
        
        with open(os.path.join(oggdata_dir, 'VehActions.xml'), 'w') as f:
            f.write(veh_actions_xml)
        
        # Create a minimal specialization tree file
        spec_tree_xml = '''<?xml version='1.0' encoding='utf-8'?>
<SpecializationTree>
  <Key>BGMHUNTER</Key>
  <Name>Big-Game Hunter</Name>
  <Talents>
    <Talent>
      <Key>FORAG</Key>
      <Row>1</Row>
      <Column>1</Column>
    </Talent>
    <Talent>
      <Key>GRIT</Key>
      <Row>1</Row>
      <Column>2</Column>
    </Talent>
    <Talent>
      <Key>STALK</Key>
      <Row>1</Row>
      <Column>3</Column>
    </Talent>
    <Talent>
      <Key>OUTDOOR</Key>
      <Row>1</Row>
      <Column>4</Column>
    </Talent>
    <Talent>
      <Key>TOUGH</Key>
      <Row>2</Row>
      <Column>1</Column>
    </Talent>
    <Talent>
      <Key>OUTDOOR</Key>
      <Row>2</Row>
      <Column>2</Column>
    </Talent>
    <Talent>
      <Key>CONF</Key>
      <Row>2</Row>
      <Column>3</Column>
    </Talent>
    <Talent>
      <Key>SWIFT</Key>
      <Row>2</Row>
      <Column>4</Column>
    </Talent>
    <Talent>
      <Key>STALK</Key>
      <Row>3</Row>
      <Column>1</Column>
    </Talent>
    <Talent>
      <Key>NATHUN</Key>
      <Row>3</Row>
      <Column>2</Column>
    </Talent>
    <Talent>
      <Key>EXTRACK</Key>
      <Row>3</Row>
      <Column>3</Column>
    </Talent>
    <Talent>
      <Key>HEIGHT</Key>
      <Row>3</Row>
      <Column>4</Column>
    </Talent>
    <Talent>
      <Key>GRIT</Key>
      <Row>4</Row>
      <Column>1</Column>
    </Talent>
    <Talent>
      <Key>HUNTERQUARRY</Key>
      <Row>4</Row>
      <Column>2</Column>
    </Talent>
    <Talent>
      <Key>QUICKST</Key>
      <Row>4</Row>
      <Column>3</Column>
    </Talent>
    <Talent>
      <Key>EXTRACK</Key>
      <Row>4</Row>
      <Column>4</Column>
    </Talent>
    <Talent>
      <Key>BRNGITDWN</Key>
      <Row>5</Row>
      <Column>1</Column>
    </Talent>
    <Talent>
      <Key>HUNTQIMP</Key>
      <Row>5</Row>
      <Column>2</Column>
    </Talent>
    <Talent>
      <Key>DEDI</Key>
      <Row>5</Row>
      <Column>3</Column>
    </Talent>
    <Talent>
      <Key>SUPREF</Key>
      <Row>5</Row>
      <Column>4</Column>
    </Talent>
  </Talents>
</SpecializationTree>'''
        
        with open(os.path.join(oggdata_dir, 'Big-Game Hunter Tree.xml'), 'w') as f:
            f.write(spec_tree_xml)
        
        # Initialize the parser with our test data directory
        parser = XMLParser(temp_dir)
        
        # Parse the Big-Game Hunter specialization
        spec_file = os.path.join(oggdata_dir, 'Big-Game Hunter.xml')
        results = parser.parse_xml_file(spec_file)
        
        if not results:
            print("❌ No results returned from parsing")
            return False
        
        spec_data = results[0]
        
        # Test that the specialization was parsed correctly
        if spec_data.get('name') != 'Big-Game Hunter':
            print(f"❌ Expected name 'Big-Game Hunter', got '{spec_data.get('name')}'")
            return False
        
        print("  ✓ Name correctly extracted: Big-Game Hunter")
        
        # Test that talent fields were generated in the correct order
        # Since all rows have index 0, they should use XML order: 1, 2, 3, 4, 5
        expected_talent_fields = [
            'talent1_1', 'talent1_2', 'talent1_3', 'talent1_4',  # Row 1 (cost 5)
            'talent2_1', 'talent2_2', 'talent2_3', 'talent2_4',  # Row 2 (cost 10)
            'talent3_1', 'talent3_2', 'talent3_3', 'talent3_4',  # Row 3 (cost 15)
            'talent4_1', 'talent4_2', 'talent4_3', 'talent4_4',  # Row 4 (cost 20)
            'talent5_1', 'talent5_2', 'talent5_3', 'talent5_4'   # Row 5 (cost 25)
        ]
        
        # The talent fields are stored in the data subdictionary
        data = spec_data.get('data', {})
        
        for field in expected_talent_fields:
            if field not in data:
                print(f"❌ Expected talent field '{field}' not found in data")
                return False
        
        print("  ✓ All expected talent fields generated")
        
        # Test that the first row has the correct talents (cost 5)
        if 'talent1_1' in data and data['talent1_1']:
            first_talent = data['talent1_1'][0]
            if first_talent.get('name') != 'Forager':
                print(f"❌ Expected talent1_1 to be 'Forager', got '{first_talent.get('name')}'")
                return False
            if first_talent.get('data', {}).get('cost') != 5:
                print(f"❌ Expected talent1_1 cost to be 5, got '{first_talent.get('data', {}).get('cost')}'")
                return False
            print("  ✓ First row (cost 5) correctly processed")
        
        # Test that the second row has the correct talents (cost 10)
        if 'talent2_1' in data and data['talent2_1']:
            second_talent = data['talent2_1'][0]
            if second_talent.get('name') != 'Tough':
                print(f"❌ Expected talent2_1 to be 'Tough', got '{second_talent.get('name')}'")
                return False
            if second_talent.get('data', {}).get('cost') != 10:
                print(f"❌ Expected talent2_1 cost to be 10, got '{second_talent.get('data', {}).get('cost')}'")
                return False
            print("  ✓ Second row (cost 10) correctly processed")
        
        # Test that the third row has the correct talents (cost 15)
        if 'talent3_1' in data and data['talent3_1']:
            third_talent = data['talent3_1'][0]
            if third_talent.get('name') != 'Stalker':
                print(f"❌ Expected talent3_1 to be 'Stalker', got '{third_talent.get('name')}'")
                return False
            if third_talent.get('data', {}).get('cost') != 15:
                print(f"❌ Expected talent3_1 cost to be 15, got '{third_talent.get('data', {}).get('cost')}'")
                return False
            print("  ✓ Third row (cost 15) correctly processed")
        
        # Test that the fourth row has the correct talents (cost 20)
        if 'talent4_1' in data and data['talent4_1']:
            fourth_talent = data['talent4_1'][0]
            if fourth_talent.get('name') != 'Grit':
                print(f"❌ Expected talent4_1 to be 'Grit', got '{fourth_talent.get('name')}'")
                return False
            if fourth_talent.get('data', {}).get('cost') != 20:
                print(f"❌ Expected talent4_1 cost to be 20, got '{fourth_talent.get('data', {}).get('cost')}'")
                return False
            print("  ✓ Fourth row (cost 20) correctly processed")
        
        # Test that the fifth row has the correct talents (cost 25)
        if 'talent5_1' in data and data['talent5_1']:
            fifth_talent = data['talent5_1'][0]
            if fifth_talent.get('name') != 'Bring It Down':
                print(f"❌ Expected talent5_1 to be 'Bring It Down', got '{fifth_talent.get('name')}'")
                return False
            if fifth_talent.get('data', {}).get('cost') != 25:
                print(f"❌ Expected talent5_1 cost to be 25, got '{fifth_talent.get('data', {}).get('cost')}'")
                return False
            print("  ✓ Fifth row (cost 25) correctly processed")
        
        print("  ✓ All Big-Game Hunter specialization index fix tests passed!")
        return True

if __name__ == '__main__':
    success = test_big_game_hunter_index_fix()
    if success:
        print("\n🎉 All Big-Game Hunter specialization index fix tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
