# 3rd party
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox.config import validate_config
from sphinx_toolbox.issues import IssueNode, depart_issue_node, issue_role, pull_role, visit_issue_node
from sphinx_toolbox.source import source_role
from sphinx_toolbox.testing import do_test_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = do_test_setup(sphinx_toolbox.setup)

	assert setup_ret == {'version': sphinx_toolbox.__version__, 'parallel_read_safe': True}
	assert roles == {
			'source': source_role,
			'issue': issue_role,
			'pr': pull_role,
			'pull': pull_role,
			}

	assert additional_nodes == {IssueNode}

	assert app.registry.translation_handlers == {"html": {"IssueNode": (visit_issue_node, depart_issue_node)}}

	assert app.config.values["source_link_target"] == ("Sphinx", "env", [str])
	assert app.config.values["github_username"] == (None, "env", [str])
	assert app.config.values["github_repository"] == (None, "env", [str])

	assert app.events.listeners["config-inited"] == [EventListener(id=0, handler=validate_config, priority=850)]
