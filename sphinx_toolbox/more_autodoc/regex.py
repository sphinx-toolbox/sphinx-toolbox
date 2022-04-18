#!/usr/bin/env python3
#
#  regex.py
r"""
Specialized Documenter for regular expression variables, similar to :rst:dir:`autodata`.

.. versionadded:: 1.2.0
.. extensions:: sphinx_toolbox.more_autodoc.regex

Usage
-------

.. rst:directive:: autoregex

	Directive to automatically document a regular expression variable.

	The output is based on the :rst:dir:`autodata` directive, and takes all of its options except ``:annotation:``.

	.. rst:directive:option:: no-value

		Don't show the value of the variable.

	.. rst:directive:option:: value: value
		:type: string

		Show this instead of the value taken from the Python source code.

	.. rst:directive:option:: no-type

		Don't show the type of the variable.

	.. rst:directive:option:: no-flags

		Don't show the flags of the :class:`~typing.Pattern` object.

	.. rst:directive:option:: flags: flags
		:type: string

		Show this instead of the flags taken from the :class:`~typing.Pattern` object.
		This should be correctly formatted for insertion into reStructuredText, such as ``:py:data:`re.ASCII```.


	.. versionchanged:: 2.7.0

		The flags :py:data:`re.DEBUG` and :py:data:`re.VERBOSE` are now hidden
		as they don't affect the regex itself.

.. latex:clearpage::

.. rst:role:: regex

	Formats a regular expression with coloured output.

	.. rest-example::

		:regex:`^Hello\s+[Ww]orld[.,](Lovely|Horrible) weather, isn't it (.*)?`

	.. versionchanged:: 2.11.0  Now generates coloured output with the LaTeX builder.

"""
#
#  Copyright © 2020-2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Parts based on https://github.com/sphinx-doc/sphinx
#  |  Copyright (c) 2007-2020 by the Sphinx team (see AUTHORS file).
#  |  BSD Licensed
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without
#  |  modification, are permitted provided that the following conditions are
#  |  met:
#  |
#  |  * Redistributions of source code must retain the above copyright
#  |   notice, this list of conditions and the following disclaimer.
#  |
#  |  * Redistributions in binary form must reproduce the above copyright
#  |   notice, this list of conditions and the following disclaimer in the
#  |   documentation and/or other materials provided with the distribution.
#  |
#  |  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  |  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  |  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  |  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  |  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  |  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  |  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  |  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  |  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  |  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  |  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
import itertools
import re
import sre_parse
from sre_constants import (
		ANY,
		AT,
		AT_BEGINNING,
		AT_BEGINNING_STRING,
		AT_BOUNDARY,
		AT_END,
		AT_END_STRING,
		AT_NON_BOUNDARY,
		BRANCH,
		CATEGORY,
		CATEGORY_DIGIT,
		CATEGORY_NOT_DIGIT,
		CATEGORY_NOT_SPACE,
		CATEGORY_NOT_WORD,
		CATEGORY_SPACE,
		CATEGORY_WORD,
		IN,
		LITERAL,
		MAX_REPEAT,
		MAXREPEAT,
		MIN_REPEAT,
		RANGE,
		SUBPATTERN
		)
from textwrap import dedent
from typing import Any, Callable, List, Optional, Pattern, Tuple

# 3rd party
import dict2css
from docutils import nodes
from docutils.nodes import Node, system_message
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from sphinx.application import Sphinx
from sphinx.ext.autodoc import UNINITIALIZED_ATTR, ModuleDocumenter
from sphinx.util import texescape
from sphinx.util.docutils import SphinxRole
from sphinx.writers.html import HTMLTranslator

# this package
from sphinx_toolbox import _css
from sphinx_toolbox.more_autodoc.variables import VariableDocumenter
from sphinx_toolbox.utils import Config, SphinxExtMetadata, add_nbsp_substitution, flag, metadata_add_version

__all__ = [
		"RegexDocumenter",
		"RegexParser",
		"TerminalRegexParser",
		"HTMLRegexParser",
		"LaTeXRegexParser",
		"parse_regex_flags",
		"no_formatting",
		"span",
		"latex_textcolor",
		"copy_asset_files",
		"setup",
		]


class RegexDocumenter(VariableDocumenter):
	"""
	Specialized Documenter subclass for regex patterns.
	"""

	directivetype = "data"
	objtype = "regex"
	priority = VariableDocumenter.priority + 1
	option_spec = {
			**VariableDocumenter.option_spec,
			"no-flag": flag,
			"flag": str,
			}
	del option_spec["type"]
	del option_spec["annotation"]

	@classmethod
	def can_document_member(
			cls,
			member: Any,
			membername: str,
			isattr: bool,
			parent: Any,
			) -> bool:
		"""
		Called to see if a member can be documented by this documenter.

		:param member: The member being checked.
		:param membername: The name of the member.
		:param isattr:
		:param parent: The parent of the member.
		"""

		return isinstance(parent, ModuleDocumenter) and isattr and isinstance(member, Pattern)

	def add_content(self, more_content: Any, no_docstring: bool = False):
		"""
		Add content from docstrings, attribute documentation and the user.

		:param more_content:
		:param no_docstring:
		"""

		# set sourcename and add content from attribute documentation
		sourcename = self.get_sourcename()

		if self.analyzer:
			attr_docs = self.analyzer.find_attr_docs()
			if self.objpath:
				key = ('.'.join(self.objpath[:-1]), self.objpath[-1])
				if key in attr_docs:
					no_docstring = True
					# make a copy of docstring for attributes to avoid cache
					# the change of autodoc-process-docstring event.
					docstrings = [list(attr_docs[key])]

					for i, line in enumerate(self.process_doc(docstrings)):
						self.add_line(line, sourcename, i)

		# add content from docstrings
		if not no_docstring:
			docstrings = self.get_doc() or []
			if not docstrings:
				# append at least a dummy docstring, so that the event
				# autodoc-process-docstring is fired and can add some
				# content if desired
				docstrings.append([])

			if docstrings == [["Compiled regular expression objects", '']] or docstrings == [[]]:
				docstrings = [["Compiled regular expression object.", '']]

			for i, line in enumerate(self.process_doc(docstrings)):
				self.add_line(line, sourcename, i)

		# add additional content (e.g. from document), if present
		if more_content:
			for line, src in zip(more_content.data, more_content.items):
				self.add_line(line, src[0], src[1])

		no_value = self.options.get("no-value", False)
		no_flag = self.options.get("no-flag", False)

		if self.object is not UNINITIALIZED_ATTR and (not no_value or not no_flag):

			self.add_line('', sourcename)
			self.add_line('', sourcename)

			the_flag: Optional[str] = None

			if not no_flag:
				if "flag" in self.options:
					the_flag = self.options["flag"]
				else:
					raw_flags = self.object.flags
					raw_flags = (raw_flags & ~re.DEBUG) & ~re.VERBOSE
					the_flag = parse_regex_flags(raw_flags)

			if no_value and not the_flag:
				return

			self.add_line(".. csv-table::", sourcename)
			self.add_line("     :widths: auto", sourcename)
			self.add_line("     :stub-columns: 1", sourcename)
			self.add_line('', sourcename)

			if not no_value:

				if "value" in self.options:
					the_pattern = self.options["value"]
				else:
					the_pattern = self.object.pattern

				the_pattern = the_pattern.replace('`', r"\`")

				leading_spaces = len(tuple(itertools.takewhile(str.isspace, the_pattern)))
				trailing_spaces = len(tuple(itertools.takewhile(str.isspace, the_pattern[::-1])))
				the_pattern = the_pattern.strip(' ')

				if leading_spaces > 1:
					the_pattern = f"[ ]{leading_spaces}{the_pattern}"
				elif leading_spaces == 1:
					the_pattern = f"[ ]{the_pattern}"

				if trailing_spaces > 1:
					the_pattern += f" {trailing_spaces}"
				elif trailing_spaces == 1:
					the_pattern += "[ ]"

				self.add_line(f'     **Pattern**, ":regex:`{the_pattern}`"', sourcename)

			if the_flag:
				self.add_line(f"     **Flags**, {the_flag}", sourcename)

			self.add_line('', sourcename)

	def add_directive_header(self, sig: str):
		"""
		Add the directive's header.

		:param sig:
		"""

		user_no_value = self.options.get("no-value", False)
		self.options["no-value"] = True
		super().add_directive_header(sig)
		self.options["no-value"] = user_no_value


def parse_regex_flags(flags: int) -> str:
	"""
	Convert regex flags into "bitwise-or'd" Sphinx xrefs.

	:param flags:
	"""

	buf = []

	if flags & re.ASCII:
		buf.append("ASCII")
	if flags & re.DEBUG:
		buf.append("DEBUG")
	if flags & re.IGNORECASE:
		buf.append("IGNORECASE")
	if flags & re.LOCALE:
		buf.append("LOCALE")
	if flags & re.MULTILINE:
		buf.append("MULTILINE")
	if flags & re.DOTALL:
		buf.append("DOTALL")
	if flags & re.VERBOSE:
		buf.append("VERBOSE")

	return " ``|`` ".join(f":py:data:`re.{x}`" for x in buf)


def no_formatting(value: Any) -> str:
	"""
	No-op that returns the value as a string.

	Used for unformatted output.
	"""

	return str(value)


class RegexParser:
	r"""
	Parser for regular expressions that outputs coloured output.

	The formatting is controlled by the following callable attributes:

	* ``AT_COLOUR`` -- Used for e.g. :regex:`^\A\b\B\Z$`
	* ``SUBPATTERN_COLOUR`` -- Used for the parentheses around subpatterns, e.g. :regex:`(Hello) World`
	* ``IN_COLOUR`` -- Used for the square brackets around character sets, e.g. :regex:`[Hh]ello`
	* ``REPEAT_COLOUR`` -- Used for repeats, e.g. :regex:`A?B+C*D{2,4}E{5}`
	* ``REPEAT_BRACE_COLOUR`` -- Used for the braces around numerical repeats.
	* ``CATEGORY_COLOUR`` -- Used for categories, e.g. :regex:`\d\D\s\D\w\W`
	* ``BRANCH_COLOUR`` -- Used for branches, e.g. :regex:`(Lovely|Horrible) Weather`
	* ``LITERAL_COLOUR`` -- Used for literal characters.
	* ``ANY_COLOUR`` -- Used for the "any" dot.

	These are all :class:`~typing.Callable`\[[:class:`~typing.Any`], :class:`str`\].

	By default no formatting is performed.
	Subclasses should set these attributes to appropriate functions.
	"""

	# Colours
	AT_COLOUR: Callable[[Any], str] = no_formatting
	SUBPATTERN_COLOUR: Callable[[Any], str] = no_formatting
	IN_COLOUR: Callable[[Any], str] = no_formatting
	REPEAT_COLOUR: Callable[[Any], str] = no_formatting
	REPEAT_BRACE_COLOUR: Callable[[Any], str] = no_formatting
	CATEGORY_COLOUR: Callable[[Any], str] = no_formatting
	BRANCH_COLOUR: Callable[[Any], str] = no_formatting
	LITERAL_COLOUR: Callable[[Any], str] = no_formatting
	ANY_COLOUR: Callable[[Any], str] = no_formatting

	def parse_pattern(self, regex: Pattern) -> str:
		"""
		Parse the given regular expression and return the formatted pattern.

		:param regex:
		"""

		buf = []

		def _parse_pattern(pattern):

			for what, content in pattern:
				# print(what, content)

				if what is AT:
					if content is AT_BEGINNING:
						buf.append(type(self).AT_COLOUR('^'))
						continue
					elif content is AT_END:
						buf.append(type(self).AT_COLOUR('$'))
						continue
					elif content is AT_BEGINNING_STRING:
						buf.append(type(self).AT_COLOUR(r"\A"))
						continue
					elif content is AT_BOUNDARY:
						buf.append(type(self).AT_COLOUR(r"\b"))
						continue
					elif content is AT_NON_BOUNDARY:
						buf.append(type(self).AT_COLOUR(r"\B"))
						continue
					elif content is AT_END_STRING:
						buf.append(type(self).AT_COLOUR(r"\Z"))
						continue

				if what is SUBPATTERN:
					buf.append(type(self).SUBPATTERN_COLOUR('('))
					group, add_flags, del_flags, subpattern = content
					# print(group, add_flags, del_flags)
					_parse_pattern(subpattern)
					buf.append(type(self).SUBPATTERN_COLOUR(')'))
					continue

				if what is LITERAL:
					# TODO: escape characters that have meaning to avoid ambiguity
					buf.append(type(self).LITERAL_COLOUR(chr(content)))
					continue

				if what is IN:
					if len(content) > 1 or content[0][0] is RANGE:
						buf.append(type(self).IN_COLOUR('['))

					_parse_pattern(content)

					if len(content) > 1 or content[0][0] is RANGE:
						buf.append(type(self).IN_COLOUR(']'))
					continue

				if what is MAX_REPEAT or what is MIN_REPEAT:
					min_, max_, item = content
					_parse_pattern(item)

					if min_ == 0 and max_ is MAXREPEAT:
						buf.append(type(self).REPEAT_COLOUR('*'))
					elif min_ == 1 and max_ is MAXREPEAT:
						buf.append(type(self).REPEAT_COLOUR('+'))
					elif min_ == 0 and max_ == 1:
						buf.append(type(self).REPEAT_COLOUR('?'))
					elif min_ == max_:
						buf.append(type(self).REPEAT_BRACE_COLOUR('{'))
						buf.append(type(self).REPEAT_COLOUR(str(min_)))
						buf.append(type(self).REPEAT_BRACE_COLOUR('}'))
					else:
						buf.append(type(self).REPEAT_BRACE_COLOUR('{'))
						buf.append(type(self).REPEAT_COLOUR(str(min_)))
						buf.append(type(self).LITERAL_COLOUR(','))
						buf.append(type(self).REPEAT_COLOUR(str(max_)))
						buf.append(type(self).REPEAT_BRACE_COLOUR('}'))
					if what is MIN_REPEAT:
						buf.append(type(self).REPEAT_COLOUR('?'))

					continue
				#
				# if what is MIN_REPEAT:
				# 	min_, max_, item = content
				# 	_parse_pattern(item)
				# 	print(min_, max_, item)
				# 	input(">>>")

				if what is CATEGORY:
					if content is CATEGORY_DIGIT:
						buf.append(type(self).CATEGORY_COLOUR(r"\d"))
						continue
					elif content is CATEGORY_NOT_DIGIT:
						buf.append(type(self).CATEGORY_COLOUR(r"\D"))
						continue
					elif content is CATEGORY_SPACE:
						buf.append(type(self).CATEGORY_COLOUR(r"\s"))
						continue
					elif content is CATEGORY_NOT_SPACE:
						buf.append(type(self).CATEGORY_COLOUR(r"\S"))
						continue
					elif content is CATEGORY_WORD:
						buf.append(type(self).CATEGORY_COLOUR(r"\w"))
						continue
					elif content is CATEGORY_NOT_WORD:
						buf.append(type(self).CATEGORY_COLOUR(r"\W"))
						continue

				if what is BRANCH:
					for branch in content[1]:
						_parse_pattern(branch)
						buf.append(type(self).BRANCH_COLOUR('|'))
					buf.pop(-1)
					continue

				if what is RANGE:
					buf.append(type(self).LITERAL_COLOUR(chr(content[0])))
					buf.append(type(self).AT_COLOUR('-'))
					buf.append(type(self).LITERAL_COLOUR(chr(content[1])))
					continue

				if what is ANY:
					buf.append(type(self).ANY_COLOUR('.'))
					continue

				print(what, content)  # pragma: no cover

		pattern = regex.pattern.replace('\t', r"\t")

		# Remove leading and trailing spaces from the pattern. They will be added back at the end.
		leading_spaces = len(tuple(itertools.takewhile(str.isspace, pattern)))
		trailing_spaces = len(tuple(itertools.takewhile(str.isspace, pattern[::-1])))
		pattern = pattern.strip(' ')

		tokens: List = list(sre_parse.parse(pattern, regex.flags))  # type: ignore[call-overload]

		if not leading_spaces:
			while tokens[0] == (LITERAL, ord(' ')):
				leading_spaces += 1
				tokens.pop(0)

		if not trailing_spaces:
			while tokens[-1] == (LITERAL, ord(' ')):
				trailing_spaces += 1
				tokens.pop(-1)

		if leading_spaces:
			buf.append(type(self).IN_COLOUR('['))
			buf.append(type(self).LITERAL_COLOUR(' '))
			buf.append(type(self).IN_COLOUR(']'))
			if leading_spaces > 1:
				buf.append(type(self).REPEAT_BRACE_COLOUR('{'))
				buf.append(type(self).REPEAT_COLOUR(str(leading_spaces)))
				buf.append(type(self).REPEAT_BRACE_COLOUR('}'))

		_parse_pattern(tokens)

		if trailing_spaces == 1:
			buf.append(type(self).IN_COLOUR('['))
			buf.append(type(self).LITERAL_COLOUR(' '))
			buf.append(type(self).IN_COLOUR(']'))
		elif trailing_spaces > 1:
			buf.append(type(self).LITERAL_COLOUR(' '))
			buf.append(type(self).REPEAT_BRACE_COLOUR('{'))
			buf.append(type(self).REPEAT_COLOUR(str(trailing_spaces)))
			buf.append(type(self).REPEAT_BRACE_COLOUR('}'))

		return ''.join(buf)


def span(css_class: str) -> Callable[[Any], str]:
	"""
	Returns a function that wraps a value in a ``span`` tag with the given class.

	:param css_class:
	"""

	def f(value: Any) -> str:
		return f'<span class="{css_class}">{value}</span>'

	return f


def latex_textcolor(colour_name: str) -> Callable[[Any], str]:
	"""
	Returns a function that wraps a value in a LaTeX ``textcolor`` command for the given colour.

	.. versionadded:: 2.11.0

	:param colour_name:
	"""

	def f(value: Any) -> str:
		if value == ' ':
			return "\\enspace"
		return f'\\textcolor{{{colour_name}}}{{{texescape.escape(value)}}}'

	return f


class HTMLRegexParser(RegexParser):
	r"""
	:class:`~.RegexParser` that outputs styled HTML.

	The formatting is controlled by the following functions, which
	wrap the character in a ``span`` tag with an appropriate CSS class:

	* ``AT_COLOUR`` -> ``regex_at`` -- Used for e.g. :regex:`^\A\b\B\Z$`
	* ``SUBPATTERN_COLOUR`` -> ``regex_subpattern`` -- Used for the parentheses around subpatterns, e.g. :regex:`(Hello) World`
	* ``IN_COLOUR`` -> ``regex_in`` -- Used for the square brackets around character sets, e.g. :regex:`[Hh]ello`
	* ``REPEAT_COLOUR`` -> ``regex_repeat`` -- Used for repeats, e.g. :regex:`A?B+C*D{2,4}E{5}`
	* ``REPEAT_BRACE_COLOUR`` -> ``regex_repeat_brace`` -- Used for the braces around numerical repeats.
	* ``CATEGORY_COLOUR`` -> ``regex_category`` -- Used for categories, e.g. :regex:`\d\D\s\D\w\W`
	* ``BRANCH_COLOUR`` -> ``regex_branch`` -- Used for branches, e.g. :regex:`(Lovely|Horrible) Weather`
	* ``LITERAL_COLOUR`` -> ``regex_literal`` -- Used for literal characters.
	* ``ANY_COLOUR`` -> ``regex_any`` -- Used for the "any" dot.

	Additionally, all ``span`` tags the ``regex`` class,
	and the surrounding ``code`` tag has the following classes:
	``docutils literal notranslate regex``.
	"""

	# Colours
	AT_COLOUR = span("regex regex_at")
	SUBPATTERN_COLOUR = span("regex regex_subpattern")
	IN_COLOUR = span("regex regex_in")
	REPEAT_COLOUR = span("regex regex_repeat")
	REPEAT_BRACE_COLOUR = span("regex regex_repeat_brace")
	CATEGORY_COLOUR = span("regex regex_category")
	BRANCH_COLOUR = span("regex regex_branch")
	LITERAL_COLOUR = span("regex regex_literal")
	ANY_COLOUR = span("regex regex_any")

	def parse_pattern(self, regex: Pattern) -> str:
		"""
		Parse the given regular expression and return the formatted pattern.

		:param regex:
		"""

		return dedent(
				f"""
		<code class="docutils literal notranslate regex">
		{super().parse_pattern(regex)}
		</code>
		"""
				)


class LaTeXRegexParser(RegexParser):
	r"""
	:class:`~.RegexParser` that outputs styled LaTeX.

	The formatting is controlled by the following functions, which
	wrap the character in a LaTeX ``textcolor`` command for an appropriate colour:

	* ``AT_COLOUR`` -> ``regex_at`` -- Used for e.g. :regex:`^\A\b\B\Z$`
	* ``SUBPATTERN_COLOUR`` -> ``regex_subpattern`` -- Used for the parentheses around subpatterns, e.g. :regex:`(Hello) World`
	* ``IN_COLOUR`` -> ``regex_in`` -- Used for the square brackets around character sets, e.g. :regex:`[Hh]ello`
	* ``REPEAT_COLOUR`` -> ``regex_repeat`` -- Used for repeats, e.g. :regex:`A?B+C*D{2,4}E{5}`
	* ``REPEAT_BRACE_COLOUR`` -> ``regex_repeat_brace`` -- Used for the braces around numerical repeats.
	* ``CATEGORY_COLOUR`` -> ``regex_category`` -- Used for categories, e.g. :regex:`\d\D\s\D\w\W`
	* ``BRANCH_COLOUR`` -> ``regex_branch`` -- Used for branches, e.g. :regex:`(Lovely|Horrible) Weather`
	* ``LITERAL_COLOUR`` -> ``regex_literal`` -- Used for literal characters.
	* ``ANY_COLOUR`` -> ``regex_any`` -- Used for the "any" dot.

	.. versionadded:: 2.11.0
	"""

	# Colours
	AT_COLOUR = latex_textcolor("regex_at")
	SUBPATTERN_COLOUR = latex_textcolor("regex_subpattern")
	IN_COLOUR = latex_textcolor("regex_in")
	REPEAT_COLOUR = latex_textcolor("regex_repeat")
	REPEAT_BRACE_COLOUR = latex_textcolor("regex_repeat_brace")
	CATEGORY_COLOUR = latex_textcolor("regex_category")
	BRANCH_COLOUR = latex_textcolor("regex_branch")
	LITERAL_COLOUR = latex_textcolor("regex_literal")
	ANY_COLOUR = latex_textcolor("regex_any")

	def parse_pattern(self, regex: Pattern) -> str:
		"""
		Parse the given regular expression and return the formatted pattern.

		:param regex:
		"""

		return f"\\sphinxcode{{\\sphinxupquote{{{super().parse_pattern(regex)}}}}}"


class TerminalRegexParser(RegexParser):
	r"""
	:class:`~.RegexParser` that outputs ANSI coloured output for the terminal.


	The formatting is controlled by the following callable attributes,
	which set ANSI escape codes for the appropriate colour:

	* ``AT_COLOUR`` -> YELLOW, Used for e.g. :regex:`^\A\b\B\Z$`
	* ``SUBPATTERN_COLOUR`` -> LIGHTYELLOW_EX, Used for the parentheses around subpatterns, e.g. :regex:`(Hello) World`
	* ``IN_COLOUR`` -> LIGHTRED_EX, Used for the square brackets around character sets, e.g. :regex:`[Hh]ello`
	* ``REPEAT_COLOUR`` -> LIGHTBLUE_EX, Used for repeats, e.g. :regex:`A?B+C*D{2,4}E{5}`
	* ``REPEAT_BRACE_COLOUR`` -> YELLOW, Used for the braces around numerical repeats.
	* ``CATEGORY_COLOUR`` -> LIGHTYELLOW_EX, Used for categories, e.g. :regex:`\d\D\s\D\w\W`
	* ``BRANCH_COLOUR`` -> YELLOW, Used for branches, e.g. :regex:`(Lovely|Horrible) Weather`
	* ``LITERAL_COLOUR`` -> GREEN, Used for literal characters.
	* ``ANY_COLOUR`` -> YELLOW, Used for the "any" dot.
	"""

	# Colours

	@staticmethod
	def AT_COLOUR(s):  # noqa: D102
		return f"\x1b[33m{s}\x1b[39m"

	@staticmethod
	def SUBPATTERN_COLOUR(s):  # noqa: D102
		return f"\x1b[93m{s}\x1b[39m"

	@staticmethod
	def IN_COLOUR(s):  # noqa: D102
		return f"\x1b[91m{s}\x1b[39m"

	@staticmethod
	def REPEAT_COLOUR(s):  # noqa: D102
		return f"\x1b[94m{s}\x1b[39m"

	@staticmethod
	def LITERAL_COLOUR(s):  # noqa: D102
		return f"\x1b[32m{s}\x1b[39m"

	REPEAT_BRACE_COLOUR = BRANCH_COLOUR = ANY_COLOUR = AT_COLOUR
	CATEGORY_COLOUR = SUBPATTERN_COLOUR


class RegexNode(nodes.literal):
	"""
	Docutils Node to show a highlighted regular expression.
	"""

	def __init__(self, rawsource='', text='', *children, **attributes):
		super().__init__(rawsource, text, *children, **attributes)
		self.pattern = re.compile(':'.join(rawsource.split(':')[2:])[1:-1])


class Regex(SphinxRole):
	"""
	Docutils role to show a highlighted regular expression.
	"""

	def run(self) -> Tuple[List[Node], List[system_message]]:
		"""
		Process the content of the regex role.
		"""

		options = self.options.copy()

		return [RegexNode(self.rawtext, self.text, **options)], []


def visit_regex_node(translator: HTMLTranslator, node: RegexNode):
	"""
	Visit an :class:`~.RegexNode`.

	:param translator:
	:param node: The node being visited.
	"""

	translator.body.append(regex_parser.parse_pattern(node.pattern))


def depart_regex_node(translator: HTMLTranslator, node: RegexNode):
	"""
	Depart an :class:`~.RegexNode`.

	:param translator:
	:param node: The node being visited.
	"""

	translator.body.pop(-1)


def visit_regex_node_latex(translator: HTMLTranslator, node: RegexNode):
	"""
	Visit an :class:`~.RegexNode` with the LaTeX builder.

	.. versionadded:: 2.11.0

	:param translator:
	:param node: The node being visited.
	"""

	translator.body.append(latex_regex_parser.parse_pattern(node.pattern))


def depart_regex_node_latex(translator: HTMLTranslator, node: RegexNode):
	"""
	Depart an :class:`~.RegexNode` with the LaTeX builder.

	.. versionadded:: 2.11.0

	:param translator:
	:param node: The node being visited.
	"""

	translator.body.pop(-1)


def copy_asset_files(app: Sphinx, exception: Optional[Exception] = None):
	"""
	Copy additional stylesheets into the HTML build directory.

	:param app: The Sphinx application.
	:param exception: Any exception which occurred and caused Sphinx to abort.
	"""

	if exception:  # pragma: no cover
		return

	if app.builder is None or app.builder.format.lower() != "html":  # pragma: no cover
		return

	static_dir = PathPlus(app.outdir) / "_static"
	static_dir.maybe_make(parents=True)
	dict2css.dump(_css.regex_styles, static_dir / "regex.css", minify=True)


regex_parser = HTMLRegexParser()
latex_regex_parser = LaTeXRegexParser()


def configure(app: Sphinx, config: Config):
	"""
	Configure :mod:`sphinx_toolbox.code`.

	.. versionadded:: 2.11.0

	:param app: The Sphinx application.
	:param config:
	"""

	latex_elements = getattr(app.config, "latex_elements", {})

	latex_preamble = StringList(latex_elements.get("preamble", ''))
	latex_preamble.blankline()
	latex_preamble.append(r"\definecolor{regex_literal}{HTML}{696969}")
	latex_preamble.append(r"\definecolor{regex_at}{HTML}{FF4500}")
	latex_preamble.append(r"\definecolor{regex_repeat_brace}{HTML}{FF4500}")
	latex_preamble.append(r"\definecolor{regex_branch}{HTML}{FF4500}")
	latex_preamble.append(r"\definecolor{regex_subpattern}{HTML}{1e90ff}")
	latex_preamble.append(r"\definecolor{regex_in}{HTML}{ff8c00}")
	latex_preamble.append(r"\definecolor{regex_category}{HTML}{8fbc8f}")
	latex_preamble.append(r"\definecolor{regex_repeat}{HTML}{FF4500}")
	latex_preamble.append(r"\definecolor{regex_any}{HTML}{FF4500}")

	latex_elements["preamble"] = str(latex_preamble)
	app.config.latex_elements = latex_elements  # type: ignore[attr-defined]
	add_nbsp_substitution(config)


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.regex`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx.ext.autodoc")
	app.setup_extension("sphinx_toolbox._css")

	app.connect("config-inited", configure)

	app.add_autodocumenter(RegexDocumenter)

	app.add_role("regex", Regex())
	app.add_node(
			RegexNode,
			html=(visit_regex_node, depart_regex_node),
			latex=(visit_regex_node_latex, depart_regex_node_latex)
			)

	return {"parallel_read_safe": True}
