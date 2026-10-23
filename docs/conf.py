# Configuration file for the Sphinx documentation builder.
# Автоматически сгенерировано скриптом setup_docs.py

import os
import sys

# Добавляем корень проекта в путь, чтобы autodoc нашёл модули
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'Софт контроль'
copyright = '2026, Команда разработки'
author = 'Команда разработки'
version = '1.0'
release = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',        # автогенерация из docstrings
    'sphinx.ext.viewcode',       # ссылки на исходный код
    'sphinx.ext.napoleon',       # поддержка Google/NumPy-стиля docstrings
    'sphinx.ext.autosummary',    # краткие сводки модулей
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'ru'

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'
html_static_path = ['_static']
html_title = 'Софт контроль'

# -- Options for autodoc -----------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': False,
    'show-inheritance': True,
}

autodoc_mock_imports = ['PyQt5']  # чтобы не требовать PyQt5 при сборке
