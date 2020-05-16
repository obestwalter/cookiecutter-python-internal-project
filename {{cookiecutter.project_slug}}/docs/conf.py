"""Configuration file for the Sphinx documentation builder.
all options: http://www.sphinx-doc.org/en/master/config
"""
import datetime
import os
import socket
import sys

sys.path.insert(0, os.path.abspath("..{{ cookiecutter.project_slug }}"))

import {{ cookiecutter.importable_name }}

project = "{{ cookiecutter.project_slug }}"
# replace this with your own versioning or leave it to see when docs where last build
version = f"{datetime.datetime.today():%Y-%d-%m (%H:%M:%S)}"
extensions = [
    "recommonmark",
    "sphinx.ext.todo",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
master_doc = "index"
highlight_language = "python3"
pygments_style = None

html_theme = "sphinx_rtd_theme"
html_show_copyright = False
html_show_sourcelink = True
html_show_sphinx = False
html_static_path = ["_static"]
html_templates_path = ["_templates"]

todo_include_todos = True
# TODO adjust for your organisation
#  replace the domain here with where your CI is running
#  This ensures that you have local links to todos during writing of the docs
#  but if the docs are built by CI they are not shown in published docs
todo_link_only = "example.com" in socket.getfqdn()
