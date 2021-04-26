# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture
from pprint36 import pformat

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.testing import run_setup
from sphinx_toolbox.tweaks import tabsize


def test_setup(advanced_file_regression: AdvancedFileRegressionFixture):
	setup_ret, directives, roles, additional_nodes, app = run_setup(tabsize.setup)

	assert setup_ret == {"version": __version__, "parallel_read_safe": True}

	advanced_file_regression.check(
			pformat(
					app.registry.source_parsers,
					sort_dicts=True,
					),
			extension=".dict",
			encoding="UTF-8",
			)
