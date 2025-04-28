# stdlib
from typing import List

# 3rd party
import pytest
from sphinx.events import EventListener

# this package
from sphinx_toolbox import installation
from sphinx_toolbox.installation import make_installation_instructions
from sphinx_toolbox.testing import run_setup
from tests.common import AttrDict, get_app_config_values


class FakeBuildEnvironment(AttrDict):

	def __init__(self, tab_width: int):
		config = AttrDict({
				"docutils_tab_width": tab_width,
				"github_username": "octocat",
				"github_repository": "hello_world",
				"conda_channels": [],
				})
		app = AttrDict(extensions=[
				"sphinx_toolbox.installation",
				"sphinx_toolbox.github",
				])
		super().__init__({"config": config, "app": app})


def test_make_installation_instructions_errors():

	with pytest.warns(UserWarning) as w:
		assert make_installation_instructions({}, FakeBuildEnvironment(4)) == []  # type: ignore[arg-type]

	assert len(w) == 1
	args: List[str] = w[0].message.args  # type: ignore[union-attr, assignment]
	assert args[0] == "No installation source specified. No installation instructions will be shown."

	with pytest.raises(ValueError, match="No PyPI project name supplied for the PyPI installation instructions."):
		make_installation_instructions({"pypi": True}, FakeBuildEnvironment(4))  # type: ignore[arg-type]

	with pytest.raises(ValueError, match="No username supplied for the Anaconda installation instructions."):
		make_installation_instructions({"anaconda": True}, FakeBuildEnvironment(4))  # type: ignore[arg-type]


def test_make_installation_instructions():

	assert make_installation_instructions(
			{"pypi": True, "project_name": "my_project"},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			) == [
					".. container:: st-installation",
					'',
					"    .. tabs::",
					'',
					"        .. tab:: from PyPI",
					'',
					"            .. prompt:: bash",
					'',
					"                python3 -m pip install my_project --user",
					]

	assert make_installation_instructions(
			{"pypi": True, "project_name": "my_project", "pypi-name": "my-project"},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			) == [
					".. container:: st-installation",
					'',
					"    .. tabs::",
					'',
					"        .. tab:: from PyPI",
					'',
					"            .. prompt:: bash",
					'',
					"                python3 -m pip install my-project --user",
					]

	assert make_installation_instructions(
			{"anaconda": True, "project_name": "my_project"},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			) == [
					".. container:: st-installation",
					'',
					"    .. tabs::",
					'',
					"        .. tab:: from Anaconda",
					'',
					"            .. prompt:: bash",
					'',
					"                conda install my_project",
					'',
					]

	assert make_installation_instructions(
			{"anaconda": True, "project_name": "my_project", "conda-name": "my-project"},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			) == [
					".. container:: st-installation",
					'',
					"    .. tabs::",
					'',
					"        .. tab:: from Anaconda",
					'',
					"            .. prompt:: bash",
					'',
					"                conda install my-project",
					'',
					]

	assert make_installation_instructions(
			{"anaconda": True, "project_name": "my_project", "pypi-name": "pypi-project"},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			) == [
					".. container:: st-installation",
					'',
					"    .. tabs::",
					'',
					"        .. tab:: from Anaconda",
					'',
					"            .. prompt:: bash",
					'',
					"                conda install pypi-project",
					'',
					]

	assert make_installation_instructions(
			{"github": "stable", "project_name": "my_project"},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			) == [
					".. container:: st-installation",
					'',
					"    .. tabs::",
					'',
					"        .. tab:: from GitHub",
					'',
					"            .. prompt:: bash",
					'',
					"                python3 -m pip install git+https://github.com/octocat/hello_world@stable --user",
					]

	assert make_installation_instructions(
			{
					"anaconda": True,
					"conda-channels": "foo,bar",
					"project_name": "my_project",
					},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			) == [
					".. container:: st-installation",
					'',
					"    .. tabs::",
					'',
					"        .. tab:: from Anaconda",
					'',
					"            First add the required channels",
					'',
					"            .. prompt:: bash",
					'',
					"                conda config --add channels https://conda.anaconda.org/foo",
					"                conda config --add channels https://conda.anaconda.org/bar",
					'',
					"            Then install",
					'',
					"            .. prompt:: bash",
					'',
					"                conda install my_project",
					'',
					]

	# Testd whitespace
	assert make_installation_instructions(
			{
					"anaconda": True,
					"conda-channels": "  foo ,    bar ",
					"project_name": "my_project",
					},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			) == [
					".. container:: st-installation",
					'',
					"    .. tabs::",
					'',
					"        .. tab:: from Anaconda",
					'',
					"            First add the required channels",
					'',
					"            .. prompt:: bash",
					'',
					"                conda config --add channels https://conda.anaconda.org/foo",
					"                conda config --add channels https://conda.anaconda.org/bar",
					'',
					"            Then install",
					'',
					"            .. prompt:: bash",
					'',
					"                conda install my_project",
					'',
					]


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(installation.setup)

	assert app.events.listeners == {
			"env-purge-doc": [
					EventListener(id=1, handler=installation.extensions_node_purger.purge_nodes, priority=500),
					],
			"env-get-outdated": [
					EventListener(
							id=0,
							handler=installation.installation_node_purger.get_outdated_docnames,
							priority=500
							),
					],
			"build-finished": [EventListener(id=3, handler=installation.copy_asset_files, priority=500)],
			"config-inited": [EventListener(id=2, handler=installation._on_config_inited, priority=510)],
			}

	assert get_app_config_values(app.config.values["conda_channels"]) == ([], "env", [list])

	assert directives == {
			"installation": installation.InstallationDirective,
			"extensions": installation.ExtensionsDirective,
			}
	assert app.registry.source_parsers == {}

	assert app.registry.css_files == []
	assert app.registry.js_files == []

	installation._on_config_inited(app, app.config)  # type: ignore[arg-type]
	assert app.registry.css_files == [("sphinx_toolbox_installation.css", {})]
	assert app.registry.js_files == [("sphinx_toolbox_installation.js", {})]
