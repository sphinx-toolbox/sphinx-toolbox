# stdlib
import copy
from typing import Any, Callable, Dict, List, Tuple, Type, Union

# 3rd party
from docutils import nodes
# For type annotation
from docutils.nodes import Node  # NOQA
from docutils.nodes import Element, TextElement
from docutils.parsers.rst import Directive, roles
from docutils.transforms import Transform
from pygments.lexer import Lexer
from sphinx.builders import Builder
from sphinx.config import Config
from sphinx.domains import Domain, Index
from sphinx.environment.collectors import EnvironmentCollector
from sphinx.events import EventManager
from sphinx.highlighting import lexer_classes
from sphinx.registry import SphinxComponentRegistry
from sphinx.roles import XRefRole
from sphinx.util import docutils
from sphinx.util.typing import RoleFunction, TitleGetter

__all__ = ["Sphinx", "do_test_setup"]


class FakeBuilder(Builder):
	pass


class Sphinx:

	registry: SphinxComponentRegistry
	config: Config
	events: EventManager
	html_themes: Dict[str, str]
	builder: Builder

	def __init__(self, buildername: str = "html"):
		self.registry = SphinxComponentRegistry()
		self.config = Config({}, {})
		self.events = EventManager(self)
		self.html_themes: Dict[str, str] = {}
		# self.builder = self.registry.create_builder(self, buildername)

	def add_builder(self, builder: Type[Builder], override: bool = False) -> None:
		"""
		Register a new builder.
		"""

		self.registry.add_builder(builder, override=override)

	def add_config_value(
			self,
			name: str,
			default: Any,
			rebuild: Union[bool, str],
			types: Any = (),
			) -> None:
		"""
		Register a configuration value.
		"""

		if rebuild in {False, True}:
			rebuild = 'env' if rebuild else ''

		self.config.add(name, default, rebuild, types)

	def add_event(self, name: str) -> None:
		"""
		Register an event called *name*.
		"""

		self.events.add(name)

	def set_translator(
			self,
			name: str,
			translator_class: Type[nodes.NodeVisitor],
			override: bool = False,
			) -> None:
		"""
		Register or override a Docutils translator class.
		"""

		self.registry.add_translator(name, translator_class, override=override)

	def add_node(
			self,
			node: Type[Element],
			override: bool = False,
			**kwargs: Tuple[Callable, Callable],
			) -> None:
		"""
		Register a Docutils node class.
		"""

		if not override and docutils.is_node_registered(node):
			raise ValueError(
					f'node class {node.__name__!r} is already registered, its visitors will be overridden'
					)

		docutils.register_node(node)
		self.registry.add_translation_handlers(node, **kwargs)

	def add_enumerable_node(
			self,
			node: Type[Element],
			figtype: str,
			title_getter: TitleGetter = None,
			override: bool = False,
			**kwargs: Tuple[Callable, Callable],
			) -> None:
		"""
		Register a Docutils node class as a numfig target.
		"""

		self.registry.add_enumerable_node(node, figtype, title_getter, override=override)
		self.add_node(node, override=override, **kwargs)

	def add_directive(self, name: str, cls: Type[Directive], override: bool = False) -> None:
		"""
		Register a Docutils directive.
		"""

		if not override and docutils.is_directive_registered(name):
			raise ValueError(f'directive {name!r} is already registered, it will be overridden')

		docutils.register_directive(name, cls)

	def add_role(self, name: str, role: Any, override: bool = False) -> None:
		"""
		Register a Docutils role.
		"""

		if not override and docutils.is_role_registered(name):
			raise ValueError(f'role {name!r} is already registered, it will be overridden')

		docutils.register_role(name, role)

	def add_generic_role(self, name: str, nodeclass: Any, override: bool = False) -> None:
		"""
		Register a generic Docutils role.
		"""

		if not override and docutils.is_role_registered(name):
			raise ValueError(f'role {name!r} is already registered, it will be overridden')

		role = roles.GenericRole(name, nodeclass)

		docutils.register_role(name, role)

	def add_domain(
			self,
			domain: Type[Domain],
			override: bool = False,
			) -> None:
		"""
		Register a domain.
		"""

		self.registry.add_domain(domain, override=override)

	def add_directive_to_domain(
			self,
			domain: str,
			name: str,
			cls: Type[Directive],
			override: bool = False,
			) -> None:
		"""
		Register a Docutils directive in a domain.
		"""

		self.registry.add_directive_to_domain(domain, name, cls, override=override)

	def add_role_to_domain(
			self,
			domain: str,
			name: str,
			role: Union[RoleFunction, XRefRole],
			override: bool = False,
			) -> None:
		"""
		Register a Docutils role in a domain.
		"""

		self.registry.add_role_to_domain(domain, name, role, override=override)

	def add_index_to_domain(
			self,
			domain: str,
			index: Type[Index],
			override: bool = False,
			) -> None:
		"""
		Register a custom index for a domain.
		"""

		self.registry.add_index_to_domain(domain, index)

	def add_object_type(
			self,
			directivename: str,
			rolename: str,
			indextemplate: str = '',
			parse_node: Callable = None,
			ref_nodeclass: Type[TextElement] = None,
			objname: str = '',
			doc_field_types: List = [],
			override: bool = False,
			) -> None:
		"""
		Register a new object type.
		"""

		self.registry.add_object_type(
				directivename,
				rolename,
				indextemplate,
				parse_node,
				ref_nodeclass,
				objname,
				doc_field_types,
				override=override,
				)

	def add_crossref_type(
			self,
			directivename: str,
			rolename: str,
			indextemplate: str = '',
			ref_nodeclass: Type[TextElement] = None,
			objname: str = '',
			override: bool = False,
			) -> None:
		"""
		Register a new crossref object type.
		"""

		self.registry.add_crossref_type(
				directivename,
				rolename,
				indextemplate,
				ref_nodeclass,
				objname,
				override=override,
				)

	def add_transform(self, transform: Type[Transform]) -> None:
		"""
		Register a Docutils transform to be applied after parsing.

		Add the standard docutils :class:`Transform` subclass *transform* to
		the list of transforms that are applied after Sphinx parses a reST document.
		"""

		self.registry.add_transform(transform)

	def add_post_transform(self, transform: Type[Transform]) -> None:
		"""
		Register a Docutils transform to be applied before writing.

		Add the standard docutils :class:`Transform` subclass *transform* to
		the list of transforms that are applied before Sphinx writes a
		document.
		"""

		self.registry.add_post_transform(transform)

	#
	# def add_js_file(self, filename: str, **kwargs: str) -> None:
	# 	"""
	# 	Register a JavaScript file to include in the HTML output.
	# 	"""
	#
	# 	self.registry.add_js_file(filename, **kwargs)
	# 	if hasattr(self.builder, 'add_js_file'):
	# 		self.builder.add_js_file(filename, **kwargs)  # type: ignore
	#
	# def add_css_file(self, filename: str, **kwargs: str) -> None:
	# 	"""
	# 	Register a stylesheet to include in the HTML output.
	# 	"""
	#
	# 	self.registry.add_css_files(filename, **kwargs)
	# 	if hasattr(self.builder, 'add_css_file'):
	# 		self.builder.add_css_file(filename, **kwargs)  # type: ignore

	def add_latex_package(
			self,
			packagename: str,
			options: str = None,
			after_hyperref: bool = False,
			) -> None:
		"""
		Register a package to include in the LaTeX source code.
		"""

		self.registry.add_latex_package(packagename, options, after_hyperref)

	def add_lexer(self, alias: str, lexer: Type[Lexer]) -> None:
		"""
		Register a new lexer for source code.
		"""

		if isinstance(lexer, Lexer):
			raise TypeError('app.add_lexer() API changed; Please give lexer class instead instance')
		else:
			lexer_classes[alias] = lexer

	def add_autodocumenter(self, cls: Any, override: bool = False) -> None:
		"""
		Register a new documenter class for the autodoc extension.
		"""

		# 3rd party
		from sphinx.ext.autodoc.directive import AutodocDirective
		self.registry.add_documenter(cls.objtype, cls)
		self.add_directive('auto' + cls.objtype, AutodocDirective, override=override)

	def add_autodoc_attrgetter(
			self,
			typ: Type,
			getter: Callable[[Any, str, Any], Any],
			) -> None:
		"""
		Register a new ``getattr``-like function for the autodoc extension.
		"""

		self.registry.add_autodoc_attrgetter(typ, getter)

	def add_source_suffix(self, suffix: str, filetype: str, override: bool = False) -> None:
		"""
		Register a suffix of source files.
		"""

		self.registry.add_source_suffix(suffix, filetype, override=override)

	def add_source_parser(self, *args: Any, **kwargs: Any) -> None:
		"""
		Register a parser class.
		"""

		self.registry.add_source_parser(*args, **kwargs)

	def add_env_collector(self, collector: Type[EnvironmentCollector]) -> None:
		"""
		Register an environment collector class.
		"""

		collector().enable(self)

	def add_html_theme(self, name: str, theme_path: str) -> None:
		"""
		Register an HTML Theme.
		"""

		self.html_themes[name] = theme_path

	def add_html_math_renderer(
			self,
			name: str,
			inline_renderers: Tuple[Callable, Callable] = None,
			block_renderers: Tuple[Callable, Callable] = None,
			) -> None:
		"""
		Register a math renderer for HTML.
		"""

		self.registry.add_html_math_renderer(name, inline_renderers, block_renderers)

	# event interface
	def connect(self, event: str, callback: Callable, priority: int = 500) -> int:
		"""
		Register *callback* to be called when *event* is emitted.
		"""

		listener_id = self.events.connect(event, callback, priority)
		return listener_id


def do_test_setup(setup_func: Callable[[Sphinx], Dict[str, Any]], buildername: str = "html"):
	app = Sphinx(buildername)

	with docutils.docutils_namespace():
		setup_ret = setup_func(app)
		directives = copy.copy(docutils.directives._directives)
		roles = copy.copy(docutils.roles._roles)
		additional_nodes = copy.copy(docutils.additional_nodes)

	return setup_ret, directives, roles, additional_nodes, app
