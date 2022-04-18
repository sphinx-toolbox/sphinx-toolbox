# 3rd party
from autodocsumm import AutoSummModuleDocumenter  # type: ignore[import]
from sphinx.events import EventListener
from sphinx.ext.autodoc import ModuleDocumenter

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import sourcelink
from sphinx_toolbox.more_autosummary import PatchedAutoSummModuleDocumenter
from sphinx_toolbox.testing import run_setup
from sphinx_toolbox.utils import flag


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(sourcelink.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert "sourcelink" in ModuleDocumenter.option_spec
	assert ModuleDocumenter.option_spec["sourcelink"] is flag

	assert "sourcelink" in AutoSummModuleDocumenter.option_spec
	assert AutoSummModuleDocumenter.option_spec["sourcelink"] is flag

	assert "sourcelink" in PatchedAutoSummModuleDocumenter.option_spec
	assert PatchedAutoSummModuleDocumenter.option_spec["sourcelink"] is flag

	assert app.events.listeners == {
			"autodoc-process-docstring": [
					EventListener(id=0, handler=sourcelink.sourcelinks_process_docstring, priority=500),
					],
			}
	assert app.config.values["autodoc_show_sourcelink"] == (False, "env", [bool])

	assert directives == {}
	assert roles == {}
	assert additional_nodes == set()
