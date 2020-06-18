# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Project information -----------------------------------------------------

project = 'Web3 Foundation Research'
copyright = '2019, Web3 Foundation'
author = 'Web3 Foundation'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = ''


# -- General configuration ---------------------------------------------------

# For markdown support see https://gist.github.com/johncrossland/9f6f54d559e9136773172aa0a429b46f

import sphinx_material

extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.graphviz',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.githubpages',
    'sphinx_material',
]

templates_path = ['_templates']

master_doc = 'index'

exclude_patterns = ['papers/**']


# -- Options for HTML output -------------------------------------------------

html_static_path = ['_static']
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}
html_title = "Research at W3F"
html_logo = '_static/images/w3f_logo.svg'
html_show_copyright = False
html_css_files = [
    'stylesheets/extra.css',
]

html_theme = 'sphinx_material'
html_theme_path = sphinx_material.html_theme_path()
html_context = sphinx_material.get_html_context()
html_theme_options = {
    'color_primary': 'deep-orange',
    'color_accent': 'deep-orange',
    'globaltoc_depth': -1,
}

mathjax_config = {
    'extensions': ["tex2jax.js"],
    'jax': ["input/TeX", "output/HTML-CSS"],
    'tex2jax': {
      'inlineMath': [ ['$','$'], ["\\(","\\)"] ],
      'displayMath': [ ['$$','$$'], ["\\[","\\]"] ],
      'processEscapes': True
    },
    "HTML-CSS": { 'fonts': ["TeX"] }
}

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

from sphinx_markdown_parser.parser import MarkdownParser

def setup(app):
    app.add_source_suffix('.md', 'markdown')
    app.add_source_parser(MarkdownParser)
    app.add_config_value('markdown_parser_config', {
        'extensions': [
            'extra',
            'admonition',
            'codehilite',
            'pymdownx.arithmatex',
        ],
    }, True)
