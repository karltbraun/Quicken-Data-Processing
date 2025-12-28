# Perplexity Project Requirements

## Overview

This is a requirements document for my Perplexity chat on creating this project.

**Update (Dec 27, 2025):** Primary input method changed from PDF to CSV export. PDF parsing remains available as alternative/backup method.

## General Development Requirements

- Python
  - Use Python 3.12 or higher.
  - Follow PEP 8 coding standards.
  - Blank lines should only contain a newline character, no spaces or tabs.
  - We will use the 'uv' package for environment management.
    - Create a virtual environment named `env`.
    - Ensure all dependencies are installed within this environment.
- Project Folder
  - We will be using git and will eventually host this on GitHub.
  - GitHub repository name: `Quicken-Data-Processing`
  - GitHub Account: 'karltbraun'
  - I will have provided (below) a sample .gitignore file for you to use.
    - Review it for accuracy and completeness.
- Project overview
  - Primary Method: Parse Quicken CSV export files to produce structured data format
    - CSV export provides complete expense data (75+ categories)
    - More reliable and complete than PDF parsing
    - See csv_requirements.md for CSV-specific requirements
  - Alternative Method: Parse PDF reports (when CSV not available)
    - PDF parsing provides partial data (~19 categories visible)
    - Uses layout-based text extraction
  - We will then write some 'alpha' or 'beta' level code to test out our methods.
    - these should be modular enough that we can use them in a more production quality codebase later.
  - Eventually (but not initially) we will write a font-end that will allow the configuration of parameters:
    - Input file selection
    - Data Range
    - Specific categories on which to report
    - etc.

``` text
## Sample .gitignore File

# My adds

aa*
Archive
Archive/*
mqtt_secrets.py
data/*
Data/*
log/*
logs/*
Log/*
Logs/*
myenv/*

# *.json

### macOS ###
# General
.DS_Store
.AppleDouble
.LSOverride

# Icon must end with two \r
Icon


# Thumbnails
._*

# Files that might appear in the root of a volume
.DocumentRevisions-V100
.fseventsd
.Spotlight-V100
.TemporaryItems
.Trashes
.VolumeIcon.icns
.com.apple.timemachine.donotpresent

# Directories potentially created on remote AFP share
.AppleDB
.AppleDesktop
Network Trash Folder
Temporary Items
.apdisk

### macOS Patch ###
# iCloud generated files
*.icloud

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
# config/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py


# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Environment files (exclude all .env* files except templates/examples)
.env*
!.env.template*
!.env.example*
!.env.sample*

# Python virtual environments
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
x.tmp

```
