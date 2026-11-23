"""Configuration file for Sphinx documentation builder."""
from importlib.metadata import version

project = "chief"
copyright = "2026 Vadim Schultz"
author = "Vadim Schultz"
release = version = version("chief")

extensions = [
    "sphinx.ext.autodoc",  # Automatically documents modules etc.
    "sphinx.ext.napoleon",  # Parses the docstrings Google style
    "myst_parser",  # Allows the use of .md files instead of .rst files
    "autoapi.extension",  # Automatically create API documentation out of code
    "sphinx.ext.viewcode",  # Includes the source code and links in documentation (must be after autoapi extension!)
]
autoapi_add_toctree_entry = False
autoapi_dirs = ["../src/chief"]
autoapi_ignore = [
    "*/bundle/*",  # Skill-pack scripts are not package API; they have no toctree entry
]
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_python_class_content = "both"  # Display class and __init__ docstring
autoclass_content = "both"  # Display class and __init__ docstring
autodoc_typehints = "description"  # Move type annotations to description
myst_enable_extensions = [
    "tasklist",
]
myst_heading_anchors = 3
suppress_warnings = ["myst.header"]
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    'navigation_depth': -1,
}
