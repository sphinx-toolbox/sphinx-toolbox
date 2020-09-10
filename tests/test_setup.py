# 3rd party
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox import assets, code, config, installation, shields, source, wikipedia
from sphinx_toolbox.issues import IssueNode, depart_issue_node, issue_role, pull_role, visit_issue_node
from sphinx_toolbox.rest_example import rest_example_purger, reSTExampleDirective
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(sphinx_toolbox.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}
	assert roles == {
			"source": source.source_role,
			"issue": issue_role,
			"pr": pull_role,
			"pull": pull_role,
			"wikipedia": wikipedia.make_wikipedia_link,
			"asset": assets.asset_role,
			}

	assert additional_nodes == {IssueNode, assets.AssetNode}

	assert app.registry.translation_handlers == {
			"html": {
					"IssueNode": (visit_issue_node, depart_issue_node),
					"AssetNode": (assets.visit_asset_node, assets.depart_asset_node),
					}
			}

	assert app.config.values["source_link_target"] == ("Sphinx", "env", [str])
	assert app.config.values["github_username"] == (None, "env", [str])
	assert app.config.values["github_repository"] == (None, "env", [str])
	assert app.config.values["conda_channels"] == ([], "env", [list])
	assert app.config.values["wikipedia_lang"] == ("en", "env", [str])
	assert app.config.values["assets_dir"] == ("./assets", "env", [str])

	assert app.events.listeners == {
			"config-inited": [EventListener(id=0, handler=config.validate_config, priority=850)],
			"env-purge-doc": [
					EventListener(id=1, handler=installation.installation_node_purger.purge_nodes, priority=500),
					EventListener(id=2, handler=rest_example_purger.purge_nodes, priority=500),
					EventListener(id=3, handler=installation.extensions_node_purger.purge_nodes, priority=500),
					],
			}

	assert directives == {
			"installation": installation.InstallationDirective,
			"rest-example": reSTExampleDirective,
			"code-block": code.CodeBlock,
			"sourcecode": code.CodeBlock,
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
			"extensions": installation.ExtensionsDirective,
			}

	expected = (
			"{'restructuredtext': <class 'sphinx_toolbox.setup.<locals>.CustomRSTParser'>, "
			"'rst': <class 'sphinx_toolbox.setup.<locals>.CustomRSTParser'>, "
			"'rest': <class 'sphinx_toolbox.setup.<locals>.CustomRSTParser'>, "
			"'restx': <class 'sphinx_toolbox.setup.<locals>.CustomRSTParser'>, "
			"'rtxt': <class 'sphinx_toolbox.setup.<locals>.CustomRSTParser'>, "
			"'rstx': <class 'sphinx_toolbox.setup.<locals>.CustomRSTParser'>}"
			)

	assert str(app.registry.source_parsers) == expected
