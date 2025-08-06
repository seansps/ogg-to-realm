# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Running the Application
- `python run.py` - Recommended launcher that auto-handles virtual environment setup
- `python main.py` - Direct application launch (requires manual venv activation)

### Testing
- `python tests/run_all_tests.py` - Run all test files in the tests directory
- Individual tests: `python tests/test_*.py`
- **Note:** Tests and other commands require virtual environment activation first:
  - `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)

### Dependencies
- `pip install -r requirements.txt` - Install Python dependencies
- Dependencies: `requests>=2.31.0`, `xmltodict>=0.13.0`

## Architecture Overview

This is a Python GUI application that imports Star Wars RPG data from OggDude's Character Creator files into Realm VTT. The application follows a modular architecture with clear separation of concerns:

### Core Components

**GUI Layer** (`src/gui.py`)
- Tkinter-based interface for user authentication and configuration
- Handles login, campaign setup, source selection, and import progress

**API Client** (`src/api_client.py`) 
- Manages authentication with Realm VTT API
- Handles campaign lookup and data upload operations
- JWT token management and HTTP request handling

**Import Manager** (`src/import_manager.py`)
- Orchestrates the import process with threading for UI responsiveness  
- Coordinates between parsers, data mapper, and API client
- Progress tracking and status reporting

**Data Parsers**
- `xml_parser.py` - Parses OggDude XML files (characters, items, species, etc.)
- `json_parser.py` - Parses Adversaries JSON files

**Data Mapper** (`src/data_mapper.py`)
- Transforms parsed OggDude data into Realm VTT format
- Handles field mapping, type conversions, and data validation

### Data Flow

1. User configures authentication and campaign details via GUI
2. Import Manager coordinates file parsing from OggData/ and Adversaries/ directories
3. XML/JSON parsers extract structured data from OggDude files
4. Data Mapper transforms OggDude format to Realm VTT API format
5. API Client uploads transformed records to Realm VTT campaign
6. GUI displays progress and status updates throughout the process

### Key Features

- Source filtering based on `config/sources.json` configuration
- Field mapping configuration via `config/field_mapping.json`
- Comprehensive test suite covering parsing, conversion, and API operations
- Virtual environment auto-management via `run.py` launcher
- Progress tracking and threaded operations for responsive UI

## Development Notes

- The application expects OggDude XML files in `OggData/` directory
- Adversaries JSON files should be in `Adversaries/` directory  
- Configuration files are in `config/` directory
- All source code is in `src/` directory
- Tests use custom runner that sets up PYTHONPATH automatically