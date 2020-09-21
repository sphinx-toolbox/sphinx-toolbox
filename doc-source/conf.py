#!/usr/bin/env python3

# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import os
import re
import sys

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))

from __pkginfo__ import __version__

# User-configurable lines
# End of user-configurable lines

github_username = "domdfcoding"
github_repository = "sphinx-toolbox"
github_url = f"https://github.com/{github_username}/{github_repository}"


rst_prolog = f""".. |pkgname| replace:: sphinx-toolbox
.. |pkgname2| replace:: ``sphinx-toolbox``
.. |browse_github| replace:: `Browse the GitHub Repository <{github_url}>`__
"""

author = "Dominic Davis-Foster"
project = "sphinx-toolbox"
slug = re.sub(r'\W+', '-', project.lower())
release = version = __version__
copyright = "2020 Dominic Davis-Foster"  # pylint: disable=redefined-builtin
language = 'en'
package_root = "sphinx_toolbox"

extensions = [
	'sphinx_toolbox',
	'sphinx_toolbox.more_autodoc',
	'sphinx_toolbox.more_autosummary',
	'sphinx_toolbox.tweaks.param_dash',
	'sphinx.ext.intersphinx',
	'sphinx.ext.mathjax',
	'sphinxcontrib.httpdomain',
	'sphinxcontrib.extras_require',
	'sphinx.ext.todo',
	'sphinxemoji.sphinxemoji',
	'notfound.extension',
	'sphinx_copybutton',
	'sphinxcontrib.default_values',
	'sphinxcontrib.toctree_plus',
	'seed_intersphinx_mapping',
	'sphinx_removed_in',
	'sphinx_toolbox.tweaks.param_dash',
	]

sphinxemoji_style = 'twemoji'
todo_include_todos = bool(os.environ.get("SHOW_TODOS", 0))
gitstamp_fmt = "%d %b %Y"

templates_path = ['_templates']
html_static_path = ['_static']
source_suffix = '.rst'
exclude_patterns = []

master_doc = 'index'
suppress_warnings = ['image.nonlocal_uri']
pygments_style = 'default'

intersphinx_mapping = {
		'python': ('https://docs.python.org/3/', None),
		'sphinx': ('https://www.sphinx-doc.org/en/stable/', None),
		'rtd': ('https://docs.readthedocs.io/en/latest/', None),
		"h5py": ('https://docs.h5py.org/en/latest/', None),
		"sarge": ('https://sarge.readthedocs.io/en/latest/', None),
		}

html_theme = 'domdf_sphinx_theme'
html_theme_options = {
		'logo_only': False,
		}
html_theme_path = ["../.."]
html_show_sourcelink = True  # True will show link to source

html_context = {
		'display_github': True,
		'github_user': 'domdfcoding',
		'github_repo': 'sphinx-toolbox',
		'github_version': 'master',
		'conf_py_path': '/doc-source/',
		}

htmlhelp_basename = slug

latex_documents = [('index', f'{slug}.tex', project, author, 'manual')]
man_pages = [('index', slug, project, [author], 1)]
texinfo_documents = [('index', slug, project, author, slug, project, 'Miscellaneous')]

toctree_plus_types = {
		"class",
		"function",
		"method",
		"data",
		"enum",
		"flag",
		"confval",
		"directive",
		"role",
		"confval",
		"protocol",
		"typeddict",
		"namedtuple",
		}

add_module_names = False


autodoc_default_options = {
		'members': None,  # Include all members (methods).
		'special-members': None,
		"autosummary": None,
		"show-inheritance": None,
		'exclude-members': ','.join([   # Exclude "standard" methods.
				"__dict__",
				"__class__",
				"__dir__",
				"__weakref__",
				"__module__",
				"__annotations__",
				"__orig_bases__",
				"__parameters__",
				"__subclasshook__",
				"__init_subclass__",
				"__attrs_attrs__",
				"__init__",
				"__new__",
				"__getnewargs__",
				"__abstractmethods__",
				"__hash__",
				]),
		}


hide_none_rtype = True
