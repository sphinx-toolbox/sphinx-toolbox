# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox import shields
from sphinx_toolbox.shields import copy_asset_files
from sphinx_toolbox.testing import check_asset_copy, run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(shields.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert additional_nodes == set()
	assert app.registry.translation_handlers == {}
	assert app.events.listeners == {"build-finished": [EventListener(0, copy_asset_files, 500)]}

	assert directives == {
			"rtfd-shield": shields.RTFDShield,
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


def test_copy_asset_files(tmp_pathplus, advanced_file_regression: AdvancedFileRegressionFixture):
	check_asset_copy(
			copy_asset_files,
			"_static/toolbox-shields.css",
			file_regression=advanced_file_regression,
			)
