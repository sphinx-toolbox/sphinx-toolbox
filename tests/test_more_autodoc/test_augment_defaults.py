# 3rd party
import pytest
from sphinx.errors import ExtensionError

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import augment_defaults
from sphinx_toolbox.testing import Sphinx, run_setup


def test_setup():
	try:
		Sphinx.extensions = []  # type: ignore[attr-defined]

		setup_ret, directives, roles, additional_nodes, app = run_setup(augment_defaults.setup)

		assert setup_ret == {"parallel_read_safe": True, "version": __version__}

		assert directives == {}
		assert roles == {}
		assert additional_nodes == set()

	finally:
		del Sphinx.extensions  # type: ignore[attr-defined]


def test_setup_wrong_order():
	try:
		Sphinx.extensions = ["sphinx.ext.autodoc"]  # type: ignore[attr-defined]

		with pytest.raises(
				ExtensionError,
				match="'sphinx_toolbox.more_autodoc.augment_defaults' "
				"must be loaded before 'sphinx.ext.autodoc'.",
				):
			run_setup(augment_defaults.setup)

	finally:
		del Sphinx.extensions  # type: ignore[attr-defined]
