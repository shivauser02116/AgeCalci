# conftest.py — ensure age_calculator/ is on sys.path for all tests
import sys
import os

# Add the age_calculator directory (parent of tests/) to sys.path so that
# `from age_logic import ...` works regardless of where pytest is invoked from.
sys.path.insert(0, os.path.dirname(__file__))
