# MusicFlow Organizer - Usage Guide

## 🚀 Quick Start

### Activating Virtual Environment

```bash
# Navigate to project directory
cd /path/to/MusicFlow_Organizer

# Activate virtual environment
source venv_musicflow/bin/activate
```

### Running the Application

#### Option 1: Using Shell Script (Recommended)
```bash
# Launch GUI (default)
./musicflow.sh

# Run demo
./musicflow.sh demo

# Run tests
./musicflow.sh test

# Interactive console
./musicflow.sh console

# Install dependencies
./musicflow.sh install
```

#### Option 2: Using Python Directly
```bash
# Launch GUI
python run_musicflow.py

# Run demo
python run_musicflow.py --demo

# Run tests  
python run_musicflow.py --test

# Interactive console
python run_musicflow.py --console

# Skip environment check
python run_musicflow.py --no-env-check
```

#### Option 3: Legacy Main Script
```bash
# Original GUI (requires librosa for full functionality)
python main.py
```

## 📋 Available Executables

### Primary Executables

| File | Purpose | Recommended Use |
|------|---------|-----------------|
| `./musicflow.sh` | Shell launcher | **Primary way to run** |
| `run_musicflow.py` | Python launcher | Direct Python execution |
| `main.py` | Original GUI | Legacy interface |

### Demo & Testing

| File | Purpose | Usage |
|------|---------|-------|
| `demo_virtual_env.py` | SOLID demo | `python demo_virtual_env.py` |
| `test_solid_components.py` | Component tests | `python test_solid_components.py` |

### Virtual Environment

| Path | Purpose |
|------|---------|
| `venv_musicflow/bin/python` | Python executable |
| `venv_musicflow/bin/activate` | Environment activation |

## 🎯 Application Modes

### 1. GUI Mode (Default)
```bash
./musicflow.sh
# or
python run_musicflow.py --gui
```
- **Purpose**: Full graphical interface
- **Features**: Complete music library organization
- **Best for**: Regular users, visual workflow

### 2. Demo Mode
```bash
./musicflow.sh demo
# or  
python run_musicflow.py --demo
```
- **Purpose**: Showcase SOLID architecture
- **Features**: Component validation, performance stats
- **Best for**: Developers, architecture review

### 3. Test Mode
```bash
./musicflow.sh test
# or
python run_musicflow.py --test
```
- **Purpose**: Run comprehensive test suite
- **Features**: 8 component tests, validation
- **Best for**: Development, CI/CD

### 4. Console Mode
```bash
./musicflow.sh console
# or
python run_musicflow.py --console
```
- **Purpose**: Interactive Python console
- **Features**: Direct component access
- **Best for**: Developers, scripting, debugging

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set log level
export MUSICFLOW_LOG_LEVEL=DEBUG

# Optional: Set cache directory
export MUSICFLOW_CACHE_DIR=~/.musicflow_cache
```

### Dependencies
**Required:**
- Python 3.8+
- PySide6 (GUI framework)
- NumPy (numerical computing)
- Scikit-learn (machine learning)

**Optional:**
- librosa (advanced audio analysis)
- mutagen (metadata reading)
- pytest (testing)

### Installing Dependencies
```bash
# Automatic installation
./musicflow.sh install

# Manual installation
source venv_musicflow/bin/activate
pip install PySide6 numpy scikit-learn pytest
```

## 📊 Performance & Features

### Supported Audio Formats
- **MP3, FLAC, WAV, AIFF** (primary)
- **M4A, OGG, WMA, AAC** (additional)
- **OPUS, ALAC** (extended)

### Organization Schemes
- **by_genre**: Genre-based organization
- **by_bpm**: BPM range grouping
- **by_key**: Camelot wheel organization
- **by_energy**: Energy level grouping
- **by_year**: Year-based organization
- **dj_workflow**: Comprehensive DJ structure

### Filter Types
- **Text search**: Multi-field searching
- **Genre filtering**: Primary/secondary genres
- **BPM range**: Configurable ranges
- **Key filtering**: Camelot wheel compatible
- **Artist/Album**: Metadata filtering

## 🎛️ Console Mode Usage

When running in console mode, you have access to:

```python
# FileOrganizer instance
organizer = FileOrganizer()

# Scan a music library
results = organizer.scan_library('/path/to/music')

# Get statistics
stats = organizer.get_statistics()

# Find audio files
files = organizer.find_audio_files('/path/to/directory')

# Organization schemes
schemes = list(OrganizationScheme)

# Create organization plan
plan = organizer.create_organization_plan(
    source_dir='/path/to/source',
    target_dir='/path/to/target', 
    scheme=OrganizationScheme.BY_GENRE
)
```

## 🐛 Troubleshooting

### Common Issues

**Virtual environment not found:**
```bash
python3 -m venv venv_musicflow
source venv_musicflow/bin/activate
./musicflow.sh install
```

**Missing dependencies:**
```bash
./musicflow.sh install
```

**Permission denied:**
```bash
chmod +x musicflow.sh
```

**GUI not starting:**
```bash
# Check if display is available
echo $DISPLAY

# Try console mode instead
./musicflow.sh console
```

### Logs
Check `musicflow.log` for detailed logging information.

## 📈 Performance Tips

1. **Use virtual environment** for best isolation
2. **Run demo first** to validate setup
3. **Use console mode** for batch processing
4. **Enable caching** for large libraries
5. **Check logs** for performance insights

## 🤝 Development

### Running Tests
```bash
# Component tests
./musicflow.sh test

# Unit tests  
python -m pytest tests/unit/core/ -v

# Specific test file
python -m pytest tests/unit/core/test_library_scanner.py -v
```

### Code Structure
```
src/
├── core/           # SOLID components
├── ui/             # GUI components  
├── plugins/        # Plugin system
└── utils/          # Utilities

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── fixtures/       # Test data
```

---

**Developed by BlueSystemIO**  
For support and updates: https://github.com/FmBlueSystem/MusicFlowOrganizer