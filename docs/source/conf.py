# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

# Project information
project = "PSyTran"
copyright = "Crown Copyright 2023, Met Office"
author = "Joseph Wallwork"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
]
templates_path = ["_templates"]
exclude_patterns = []

# Options for HTML output
html_theme = "alabaster"
html_static_path = ["_static"]

# Configure Intersphinx
intersphinx_mapping = {
    "psyclone": ("https://psyclone.readthedocs.io/en/stable", None),
    "python": ("https://docs.python.org/3", None),
}
