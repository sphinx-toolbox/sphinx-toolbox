#!/usr/bin/env python3
#
#  shields.py
"""
Directives for shield/badge images.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Based on public domain code from Docutils
#

# stdlib
from typing import List
from urllib.parse import quote

# 3rd party
from apeye.url import URL
from docutils import nodes
from docutils.nodes import fully_normalize_name, whitespace_normalize_name
from docutils.parsers.rst import directives, states
from docutils.parsers.rst.roles import set_classes
from sphinx.util.docutils import SphinxDirective

# this package
from sphinx_toolbox.utils import OptionSpec, flag, make_github_url

__all__ = [
		"Shield",
		"RTFDShield",
		"GitHubBackedShield",
		"TravisShield",
		"GitHubActionsShield",
		"RequiresIOShield",
		"CoverallsShield",
		"CodefactorShield",
		"PyPIShield",
		"GitHubShield",
		"MaintainedShield",
		"PreCommitShield",
		"SHIELDS_IO",
		"shield_default_option_spec",
		]

#: Base URL for shields.io
SHIELDS_IO = URL("https://img.shields.io")

#: Options common to all shields.
shield_default_option_spec: OptionSpec = {
		"alt": directives.unchanged,
		"height": directives.length_or_unitless,
		"width": directives.length_or_percentage_or_unitless,
		"scale": directives.percentage,
		"name": directives.unchanged,
		"class": directives.class_option,
		}


class Shield(SphinxDirective):
	"""
	Directive for `shields.io <https://shields.io>`_ shields/badges.
	"""

	required_arguments = 1
	optional_arguments = 0
	final_argument_whitespace = True
	option_spec: OptionSpec = {  # type: ignore
		"target": directives.unchanged_required,
		**shield_default_option_spec,
		}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		if "class" in self.options:
			self.options["class"].append("sphinx_toolbox_shield")
		else:
			self.options["class"] = ["sphinx_toolbox_shield"]

		self.arguments = [str(x) for x in self.arguments]

		messages = []
		reference = directives.uri(self.arguments[0])
		self.options["uri"] = reference
		reference_node = None

		if "target" in self.options:
			block = states.escape2null(self.options["target"]).splitlines()  # type: ignore
			block = [line for line in block]

			target_type, data = self.state.parse_target(block, self.block_text, self.lineno)  # type: ignore

			if target_type == "refuri":
				reference_node = nodes.reference(refuri=data)
			elif target_type == "refname":  # pragma: no cover
				reference_node = nodes.reference(
						refname=fully_normalize_name(data),
						name=whitespace_normalize_name(data),
						)
				reference_node.indirect_reference_name = data  # type: ignore
				self.state.document.note_refname(reference_node)
			else:  # pragma: no cover
				# malformed target
				# data is a system message
				messages.append(data)

			del self.options["target"]

		set_classes(self.options)
		image_node = nodes.image(self.block_text, **self.options)
		self.add_name(image_node)

		if reference_node:
			reference_node += image_node
			return messages + [reference_node]
		else:
			return messages + [image_node]


class RTFDShield(Shield):
	"""
	Shield to show the `ReadTheDocs <https://readthedocs.org/>`_ documentation build status.
	"""

	required_arguments = 0
	option_spec: OptionSpec = {
			"project": directives.unchanged_required,
			"version": str,
			**shield_default_option_spec,
			}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		project = self.options.pop("project")
		version = self.options.pop("version", "latest")

		image = SHIELDS_IO / "readthedocs" / project / f"{version}?logo=read-the-docs"
		self.arguments = [image]
		self.options["target"] = f"https://{project}.readthedocs.io/en/{version}/"

		return super().run()


class GitHubBackedShield(Shield):
	"""
	Base class for badges that are based around GitHub.
	"""

	required_arguments = 0
	option_spec: OptionSpec = {
			"username": str,  # Defaults to "github_username" if undefined
			"repository": str,  # Defaults to "github_repository" if undefined
			**shield_default_option_spec,
			}

	def get_repo_details(self):
		"""
		Process the content of the shield directive.
		"""

		username = self.options.pop("username", self.env.config.github_username)
		repository = self.options.pop("repository", self.env.config.github_repository)

		return username, repository


class TravisShield(GitHubBackedShield):
	"""
	Shield to show the `Travis CI <https://travis-ci.com/>`_ build status.
	"""

	option_spec: OptionSpec = {
			"username": str,  # Defaults to "github_username" if undefined
			"repository": str,  # Defaults to "github_repository" if undefined
			"branch": str,
			"travis-site": str,  # either com or org, default com
			**shield_default_option_spec,
			}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		username, repository = self.get_repo_details()

		branch = self.options.pop("branch", "master")
		site = self.options.pop("travis-site", "com")

		if site == "com":
			self.arguments = [SHIELDS_IO / "travis" / "com" / username / repository / f"{branch}?logo=travis"]
		else:
			self.arguments = [SHIELDS_IO / "travis" / username / repository / f"{branch}?logo=travis"]

		self.options["target"] = f"https://travis-ci.com/{username}/{repository}"

		return super().run()


class GitHubActionsShield(GitHubBackedShield):
	"""
	Shield to show the *GitHub Actions* build status.
	"""

	option_spec: OptionSpec = {
			"username": str,  # Defaults to "github_username" if undefined
			"repository": str,  # Defaults to "github_repository" if undefined
			"workflow": directives.unchanged_required,  # The name of the workflow
			**shield_default_option_spec,
			}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		username, repository = self.get_repo_details()
		workflow = quote(self.options["workflow"])

		self.arguments = [str(make_github_url(username, repository) / "workflows" / workflow / "badge.svg")]
		self.options["target"] = str(
				make_github_url(username, repository) / f"actions?query=workflow%3A%22{workflow}%22"
				)

		return super().run()


class RequiresIOShield(GitHubBackedShield):
	"""
	Shield to show the *Requires.io* status.
	"""

	option_spec: OptionSpec = {
			"username": str,  # Defaults to "github_username" if undefined
			"repository": str,  # Defaults to "github_repository" if undefined
			"branch": str,
			**shield_default_option_spec,
			}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		username, repository = self.get_repo_details()
		branch = self.options.pop("branch", "master")
		base_url = URL("https://requires.io/github/") / username / repository

		self.arguments = [base_url / f"requirements.svg?branch={branch}"]
		self.options["target"] = str(base_url / f"requirements/?branch={branch}")

		return super().run()


class CoverallsShield(GitHubBackedShield):
	"""
	Shield to show the code coverage from `Coveralls.io <https://coveralls.io/>`_.
	"""

	option_spec: OptionSpec = {
			"username": str,  # Defaults to "github_username" if undefined
			"repository": str,  # Defaults to "github_repository" if undefined
			"branch": str,
			**shield_default_option_spec,
			}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		username, repository = self.get_repo_details()
		branch = self.options.pop("branch", "master")

		self.arguments = [SHIELDS_IO / "coveralls" / "github" / username / repository / f"{branch}?logo=coveralls"]
		self.options["target"] = f"https://coveralls.io/github/{username}/{repository}?branch={branch}"

		return super().run()


class CodefactorShield(GitHubBackedShield):
	"""
	Shield to show the code quality from `Codefactor <https://www.codefactor.io>`_.
	"""

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		username, repository = self.get_repo_details()

		url = SHIELDS_IO / "codefactor" / "grade" / "github" / username / f"{repository}?logo=codefactor"
		self.arguments = [url]
		self.options["target"] = f"https://codefactor.io/repository/github/{username}/{repository}"

		return super().run()


class PyPIShield(Shield):
	"""
	Shield to show information about the project on `PyPI <https://pypi.org/>`_.
	"""

	required_arguments = 0
	option_spec: OptionSpec = {
			"project": directives.unchanged_required,
			"version": flag,  # Show the package version.
			"py-versions": flag,  # Show the supported python versions.
			"implementations": flag,  # Show the supported python implementations.
			"wheel": flag,  # Show whether the package has a wheel on PyPI.
			"license": flag,  # Show the license listed on PyPI.
			"downloads": str,  # Show the downloads for the given period (day / week / month).
			**shield_default_option_spec,
			}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		base_url = SHIELDS_IO / "pypi"

		project = self.options.pop("project", self.env.config.github_repository)

		self.options["target"] = f"https://pypi.org/project/{project}"

		info = {
				"v": self.options.pop("version", False),
				"py-versions": self.options.pop("py-versions", False),
				"implementation": self.options.pop("implementations", False),
				"wheel": self.options.pop("wheel", False),
				"l": self.options.pop("license", False),
				"downloads": self.options.pop("downloads", False),
				}

		n_info_options: int = len([k for k, v in info.items() if v])

		if n_info_options > 1:
			raise ValueError("Only one information option is allowed for the 'pypi-badge' directive.")
		elif n_info_options == 0:
			raise ValueError("An information option is required for the 'pypi-badge' directive.")

		for option in {"v", "implementation", "wheel", "l"}:
			if info[option]:
				self.arguments = [base_url / option / project]
				break

		if info["py-versions"]:
			self.arguments = [str(base_url / "pyversions" / f"{project}?logo=python&logoColor=white")]

		elif info["downloads"]:
			if info["downloads"] in {"week", "dw"}:
				self.arguments = [base_url / "dw" / project]
			elif info["downloads"] in {"month", "dm"}:
				self.arguments = [base_url / "dm" / project]
			elif info["downloads"] in {"day", "dd"}:
				self.arguments = [base_url / "dd" / project]
			else:
				raise ValueError("Unknown time period for the PyPI download statistics.")

		return super().run()


class GitHubShield(GitHubBackedShield):
	"""
	Shield to show information about a GitHub repository.
	"""

	option_spec: OptionSpec = {
			"username": str,  # Defaults to "github_username" if undefined
			"repository": str,  # Defaults to "github_repository" if undefined
			"branch": str,
			"contributors": flag,  # Show the number of contributors.
			"commits-since": str,  # Show the number of commits since the given tag.
			"last-commit": flag,  # Show the date of the last commit.
			"top-language": flag,  # Show the top language and %
			"license": flag,
			**shield_default_option_spec,
			}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		base_url = "https://img.shields.io/github"
		username, repository = self.get_repo_details()
		branch = self.options.pop("branch", "master")

		info = {
				"contributors": self.options.pop("contributors", False),
				"commits-since": self.options.pop("commits-since", False),
				"last-commit": self.options.pop("last-commit", False),
				"top-language": self.options.pop("top-language", False),
				"license": self.options.pop("license", False),
				}

		n_info_options: int = len([k for k, v in info.items() if v])

		if n_info_options > 1:
			raise ValueError("Only one information option is allowed for the 'github-badge' directive.")
		elif n_info_options == 0:
			raise ValueError("An information option is required for the 'github-badge' directive.")

		if info["contributors"]:
			self.arguments = [f"{base_url}/contributors/{username}/{repository}"]
			self.options["target"] = f"https://github.com/{username}/{repository}/graphs/contributors"

		elif info["commits-since"]:
			self.arguments = [f"{base_url}/commits-since/{username}/{repository}/{info['commits-since']}/{branch}"]
			self.options["target"] = f"https://github.com/{username}/{repository}/pulse"

		elif info["last-commit"]:
			self.arguments = [f"{base_url}/last-commit/{username}/{repository}/{branch}"]
			self.options["target"] = f"https://github.com/{username}/{repository}/commit/{branch}"

		elif info["top-language"]:
			self.arguments = [f"{base_url}/languages/top/{username}/{repository}"]

		elif info["license"]:
			self.arguments = [f"{base_url}/license/{username}/{repository}"]
			self.options["target"] = f"https://github.com/{username}/{repository}/blob/master/LICENSE"

		return super().run()


class MaintainedShield(Shield):
	"""
	Shield to indicate whether the project is maintained.
	"""

	required_arguments = 1  # The year
	option_spec = dict(shield_default_option_spec)

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		self.arguments = [f"https://img.shields.io/maintenance/yes/{self.arguments[0]}"]
		return super().run()


class PreCommitShield(Shield):
	"""
	Shield to indicate that the project uses `pre-commit <https://pre-commit.com/>`_.
	"""

	required_arguments = 0
	option_spec = dict(shield_default_option_spec)

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the shield directive.
		"""

		self.arguments = [
				"https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white"
				]
		self.options["target"] = "https://github.com/pre-commit/pre-commit"
		return super().run()
