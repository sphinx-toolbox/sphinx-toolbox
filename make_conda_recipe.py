#!/usr/bin/python3

# This file is managed by `repo_helper`. Don't edit it directly.

# this package
from __pkginfo__ import *  # pylint: disable=wildcard-import

recipe_dir = repo_root / "conda"

if not recipe_dir.exists():
	recipe_dir.mkdir()

# TODO: entry_points, manifest

all_requirements = install_requires[:]

if isinstance(extras_require, dict):
	for requires in extras_require.values():
		all_requirements += requires

all_requirements = {x.replace(" ", '') for x in set(all_requirements)}
requirements_block = "\n".join(f"    - {req}" for req in all_requirements if req)

description_block = conda_description.replace('"', '\\"')

(recipe_dir / "meta.yaml").write_text(
		encoding="UTF-8",
		data=f"""\
package:
  name: "{pypi_name.lower()}"
  version: "{__version__}"

source:
  url: "https://pypi.io/packages/source/{pypi_name[0]}/{pypi_name}/{pypi_name}-{__version__}.tar.gz"

build:
#  entry_points:
#    - {import_name} = {import_name}:main
#  skip_compile_pyc:
#    - "*/templates/*.py"          # These should not (and cannot) be compiled
  noarch: python
  script: "{{{{ PYTHON }}}} -m pip install . -vv"

requirements:
  build:
    - python
    - setuptools
    - wheel
  host:
    - pip
    - python
{requirements_block}
  run:
    - python
{requirements_block}

test:
  imports:
    - {import_name}

about:
  home: "{web}"
  license: "{__license__}"
  # license_family: LGPL
  # license_file: LICENSE
  summary: "{short_desc}"
  description: "{description_block}"
  doc_url: {project_urls["Documentation"]}
  dev_url: {project_urls["Source Code"]}

extra:
  maintainers:
    - {author}
    - github.com/{github_username}

""")

print(f"Wrote recipe to {recipe_dir / 'meta.yaml'}")
