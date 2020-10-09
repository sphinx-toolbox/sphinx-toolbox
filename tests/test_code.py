# 3rd party
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from sphinx_toolbox import code
from sphinx_toolbox.testing import run_setup


def test_setup(file_regression: FileRegressionFixture):
	setup_ret, directives, roles, additional_nodes, app = run_setup(code.setup)

	assert directives == {
			"code-block": code.CodeBlock,
			"sourcecode": code.CodeBlock,
			}
