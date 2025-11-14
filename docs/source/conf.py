# docs/source/conf.py

import os
import sys


sys.path.insert(0, os.path.abspath('../..'))

project = 'Financial Tracker'
copyright = '2025, Dima Dadykacd docs'
author = 'Your Name'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []
language = 'ru'

# Google-style докстринги
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# Настройки для autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'show-inheritance': True,
}

#Настройки для HTML
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']