# 3rd party
from pprint36 import pformat
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from sphinx_toolbox.testing import run_setup
from sphinx_toolbox.tweaks import tabsize


def test_setup(file_regression: FileRegressionFixture):
	setup_ret, directives, roles, additional_nodes, app = run_setup(tabsize.setup)

	file_regression.check(
			pformat(
					app.registry.source_parsers,
					sort_dicts=True,
					),
			extension=".dict",
			encoding="UTF-8",
			)
