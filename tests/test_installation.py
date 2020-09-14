# 3rd party
import pytest

# this package
from sphinx_toolbox.installation import make_installation_instructions
from tests.common import AttrDict


class FakeBuildEnvironment(AttrDict):

	def __init__(self, tab_width: int):
		config = AttrDict({
				"docutils_tab_width": tab_width,
				"github_username": "octocat",
				"github_repository": "hello_world",
				"conda_channels": [],
				})
		super().__init__({"config": config})


def test_make_installation_instructions_errors():

	with pytest.warns(UserWarning) as w:
		assert make_installation_instructions({}, FakeBuildEnvironment(4)) == []  # type: ignore

	assert len(w) == 1
	assert w[0].message.args[0] == "No installation source specified. No installation instructions will be shown."

	with pytest.raises(ValueError, match="No username supplied for the PyPI installation instructions."):
		make_installation_instructions({"pypi": True}, FakeBuildEnvironment(4))  # type: ignore

	with pytest.raises(ValueError, match="No username supplied for the Anaconda installation instructions."):
		make_installation_instructions({"anaconda": True}, FakeBuildEnvironment(4))  # type: ignore


def test_make_installation_instructions():

	assert make_installation_instructions(
			{"pypi": True, "project_name": "my_project"},
			FakeBuildEnvironment(4),  # type: ignore
			) == [
					".. tabs::",
					'',
					"    .. tab:: from PyPI",
					'',
					"        .. prompt:: bash",
					'',
					"            python3 -m pip install my_project --user",
					]

	assert make_installation_instructions(
			{"pypi": True, "project_name": "my_project", "pypi-name": "my-project"},
			FakeBuildEnvironment(4),  # type: ignore
			) == [
					".. tabs::",
					'',
					"    .. tab:: from PyPI",
					'',
					"        .. prompt:: bash",
					'',
					"            python3 -m pip install my-project --user",
					]

	assert make_installation_instructions(
			{"anaconda": True, "project_name": "my_project"},
			FakeBuildEnvironment(4),  # type: ignore
			) == [
					".. tabs::",
					'',
					"    .. tab:: from Anaconda",
					'',
					"        .. prompt:: bash",
					'',
					"            conda install my_project",
					'',
					]

	assert make_installation_instructions(
			{"anaconda": True, "project_name": "my_project", "conda-name": "my-project"},
			FakeBuildEnvironment(4),  # type: ignore
			) == [
					".. tabs::",
					'',
					"    .. tab:: from Anaconda",
					'',
					"        .. prompt:: bash",
					'',
					"            conda install my-project",
					'',
					]

	assert make_installation_instructions(
			{"anaconda": True, "project_name": "my_project", "pypi-name": "pypi-project"},
			FakeBuildEnvironment(4),  # type: ignore
			) == [
					".. tabs::",
					'',
					"    .. tab:: from Anaconda",
					'',
					"        .. prompt:: bash",
					'',
					"            conda install pypi-project",
					'',
					]

	assert make_installation_instructions(
			{"github": True, "project_name": "my_project"},
			FakeBuildEnvironment(4),  # type: ignore
			) == [
					".. tabs::",
					'',
					"    .. tab:: from GitHub",
					'',
					"        .. prompt:: bash",
					'',
					"            python3 -m pip install git+https://github.com/octocat/hello_world@master --user",
					]

	assert make_installation_instructions(
			{
					"anaconda": True,
					"conda-channels": "foo,bar",
					"project_name": "my_project",
					},
			FakeBuildEnvironment(4),  # type: ignore
			) == [
					".. tabs::",
					'',
					"    .. tab:: from Anaconda",
					'',
					"        First add the required channels",
					'',
					"        .. prompt:: bash",
					'',
					"            conda config --add channels https://conda.anaconda.org/foo",
					"            conda config --add channels https://conda.anaconda.org/bar",
					'',
					"        Then install",
					'',
					"        .. prompt:: bash",
					'',
					"            conda install my_project",
					'',
					]

	# Testd whitespace
	assert make_installation_instructions(
			{
					"anaconda": True,
					"conda-channels": "  foo ,    bar ",
					"project_name": "my_project",
					},
			FakeBuildEnvironment(4),  # type: ignore
			) == [
					".. tabs::",
					'',
					"    .. tab:: from Anaconda",
					'',
					"        First add the required channels",
					'',
					"        .. prompt:: bash",
					'',
					"            conda config --add channels https://conda.anaconda.org/foo",
					"            conda config --add channels https://conda.anaconda.org/bar",
					'',
					"        Then install",
					'',
					"        .. prompt:: bash",
					'',
					"            conda install my_project",
					'',
					]
