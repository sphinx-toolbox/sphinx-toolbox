#!/usr/bin/env python3

# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import os
import re
import sys

# 3rd party
from sphinx_pyproject import SphinxConfig

sys.path.append('.')

config = SphinxConfig(globalns=globals())
project = config["project"]
author = config["author"]
documentation_summary = config.description

github_url = "https://github.com/{github_username}/{github_repository}".format_map(config)

rst_prolog = f""".. |pkgname| replace:: sphinx-toolbox
.. |pkgname2| replace:: ``sphinx-toolbox``
.. |browse_github| replace:: `Browse the GitHub Repository <{github_url}>`__
"""

slug = re.sub(r'\W+', '-', project.lower())
release = version = config.version

sphinx_builder = os.environ.get("SPHINX_BUILDER", "html").lower()
todo_include_todos = int(os.environ.get("SHOW_TODOS", 0)) and sphinx_builder != "latex"

intersphinx_mapping = {
		"python": ("https://docs.python.org/3/", None),
		"sphinx": ("https://www.sphinx-doc.org/en/stable/", None),
		"pytest": ("https://docs.pytest.org/en/stable", None),
		"pytest-regressions": ("https://pytest-regressions.readthedocs.io/en/latest/", None),
		"coincidence": ("https://coincidence.readthedocs.io/en/latest", None),
		"autodocsumm": ("https://autodocsumm.readthedocs.io/en/latest", None),
		}

html_theme_options = {"logo_only": False}

html_context = {
		"display_github": True,
		"github_user": "sphinx-toolbox",
		"github_repo": "sphinx-toolbox",
		"github_version": "master",
		"conf_py_path": "/doc-source/",
		}
htmlhelp_basename = slug

latex_documents = [("index", f'{slug}.tex', project, author, "manual")]
man_pages = [("index", slug, project, [author], 1)]
texinfo_documents = [("index", slug, project, author, slug, project, "Miscellaneous")]

toctree_plus_types = set(config["toctree_plus_types"])

autodoc_default_options = {
		"members": None,  # Include all members (methods).
		"special-members": None,
		"autosummary": None,
		"show-inheritance": None,
		"exclude-members": ','.join(config["autodoc_exclude_members"]),
		}

latex_elements = {
		"printindex": "\\begin{flushleft}\n\\printindex\n\\end{flushleft}",
		"tableofcontents": "\\pdfbookmark[0]{\\contentsname}{toc}\\sphinxtableofcontents",
		}


def setup(app):
	# 3rd party
	from sphinx_toolbox.latex import better_header_layout

	app.connect("config-inited", lambda app, config: better_header_layout(config))


html_logo = "../sphinx_toolbox.png"
toctree_plus_types.add("fixture")
sys.path.append(os.path.abspath(".."))
latex_elements["preamble"] = r"\usepackage{multicol}"
nitpicky = True
needspace_amount = r"4\baselineskip"
