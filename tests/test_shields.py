# this package
import sphinx_toolbox
from sphinx_toolbox import shields
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(shields.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert additional_nodes == set()
	assert app.registry.translation_handlers == {}
	assert app.events.listeners == {}

	assert directives == {
			"rtfd-shield": shields.RTFDShield,
			"travis-shield": shields.TravisShield,
			"actions-shield": shields.GitHubActionsShield,
			"requires-io-shield": shields.RequiresIOShield,
			"coveralls-shield": shields.CoverallsShield,
			"codefactor-shield": shields.CodefactorShield,
			"pypi-shield": shields.PyPIShield,
			"github-shield": shields.GitHubShield,
			"maintained-shield": shields.MaintainedShield,
			"pre-commit-shield": shields.PreCommitShield,
			"pre-commit-ci-shield": shields.PreCommitCIShield,
			}
